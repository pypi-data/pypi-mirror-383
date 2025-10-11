import base64
import time
from typing import List, Optional, Union

from botocore.client import BaseClient
from botocore.exceptions import (
    ClientError,
    ConnectionError,
    ConnectTimeoutError,
    NoCredentialsError,
    ReadTimeoutError,
    ResponseStreamingError,
)
from dagster import (
    PipesClient,
    PipesContextInjector,
    PipesMessageReader,
    file_relative_path,
    get_dagster_logger,
)
from dagster_shared.check.functions import numeric_param, opt_inst_param
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import DatabricksError
from databricks.sdk.service import jobs
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
)

from ascii_library.orchestration.pipes.exceptions import CustomPipesException
from ascii_library.orchestration.resources.emr_constants import pipeline_bucket

from .utils import library_to_cloud_paths, package_library


def after_retry(retry_state: RetryCallState):
    """Function to log after each retry attempt."""
    if retry_state.next_action is not None:
        sleep_time = retry_state.next_action.sleep
    else:
        sleep_time = 0.0
    get_dagster_logger().debug(
        (
            f"Retry attempt: {retry_state.attempt_number}. Waiting {sleep_time} seconds before next try."
        )
    )


class _PipesBaseCloudClient(PipesClient):
    """
    Base class for Pipes clients, containing common methods and attributes.
    """

    def __init__(
        self,
        main_client: Union[BaseClient, WorkspaceClient],
        context_injector: Optional[PipesContextInjector] = None,
        message_reader: Optional[PipesMessageReader] = None,
        poll_interval_seconds: float = 5,
        **kwargs,
    ):
        self.poll_interval_seconds = numeric_param(
            poll_interval_seconds, "poll_interval_seconds"
        )
        self.message_reader = opt_inst_param(
            message_reader,
            "message_reader",
            PipesMessageReader,
        )
        self.main_client = main_client
        self.last_observed_state = None
        if (
            isinstance(main_client, BaseClient)
            and main_client.meta.service_model.service_name == "emr"
        ):
            self._s3_client = kwargs.get("s3_client")
            self.filesystem = ""
        elif isinstance(main_client, WorkspaceClient):
            self.filesystem = "dbfs"
            self._tagging_client = kwargs.get("tagging_client")

    @retry(
        stop=stop_after_delay(20) | stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, max=60),
        after=after_retry,
        retry=retry_if_exception_type(
            (
                ConnectTimeoutError,
                ReadTimeoutError,
                ResponseStreamingError,
                ConnectionError,
            )
        ),
    )
    def _retrieve_state_emr(self, cluster_id):
        return self.main_client.describe_cluster(ClusterId=cluster_id)  # type: ignore

    def _handle_emr_polling(self, cluster_id):
        description = self._retrieve_state_emr(cluster_id)
        state = description["Cluster"]["Status"]["State"]
        dns = description["Cluster"].get("MasterPublicDnsName")  # Correct this part
        if state != self.last_observed_state:
            if dns:
                get_dagster_logger().debug(f"dns: {dns}")
            get_dagster_logger().info(
                f"[pipes] EMR cluster id {cluster_id} observed state transition to {state}"
            )
            self.last_observed_state = state
        if state in ["TERMINATED", "TERMINATING", "TERMINATED_WITH_ERRORS"]:
            return self._handle_terminated_state_emr(
                job_flow=cluster_id, description=description, state=state
            )
        else:
            return True

    @retry(
        stop=stop_after_delay(20) | stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, max=60),
        after=after_retry,
        retry=retry_if_exception_type((DatabricksError)),
    )
    def _retrieve_state_dbr(self, run_id) -> jobs.Run:
        return self.main_client.jobs.get_run(run_id)  # pyrefly: ignore

    def _handle_dbr_polling(self, run_id):
        run = self._retrieve_state_dbr(run_id)
        state = run.state
        assert isinstance(state, jobs.RunState)
        if state.life_cycle_state != self.last_observed_state:
            get_dagster_logger().debug(
                f"[pipes] Databricks run {run_id} observed state transition to {state.life_cycle_state}"
            )
            self.last_observed_state = state.life_cycle_state  # pyrefly: ignore
        if state.life_cycle_state in (
            jobs.RunLifeCycleState.TERMINATED,
            jobs.RunLifeCycleState.SKIPPED,
            jobs.RunLifeCycleState.INTERNAL_ERROR,
            jobs.RunLifeCycleState.TERMINATING,
        ):
            get_dagster_logger().debug(f"Handling terminated state for run: {run_id}")
            return self._handle_terminated_state_dbr(run=run)
        else:
            return True

    def _poll_till_success(self, **kwargs):
        self._tagging_client = kwargs.get("tagging_client")
        cont = True
        if kwargs.get("extras") is not None:
            self.engine = kwargs.get("extras")["engine"]  # type: ignore
            self.executionMode = kwargs.get("extras")["execution_mode"]  # type: ignore
        while cont:
            if isinstance(self.main_client, BaseClient):
                cont = self._handle_emr_polling(kwargs.get("cluster_id"))
            elif isinstance(self.main_client, WorkspaceClient):
                cont = self._handle_dbr_polling(run_id=kwargs.get("run_id"))
            else:
                raise TypeError(
                    "main_client must be either EMRClient or WorkspaceClient"
                )
            time.sleep(self.poll_interval_seconds)

    def _handle_terminated_state_emr(self, job_flow, description, state):
        reason = description["Cluster"]["Status"].get("StateChangeReason", {}) or {}
        code = (reason.get("Code") or "").upper()
        message = reason.get("Message") or ""
        if (
            "error" in message.lower()
            or "failed" in message.lower()
            or state == "TERMINATED_WITH_ERRORS"
        ):
            raise CustomPipesException(
                message=f"Error running EMR job flow: {job_flow}"
            )
        elif (
            state == "TERMINATING" or state == "TERMINATED"
        ) and code == "ALL_STEPS_COMPLETED":
            return False
        else:
            return True

    def _handle_terminated_state_emr(self, job_flow, description, state):
        status = description["Cluster"]["Status"]
        reason = status.get("StateChangeReason", {}) or {}
        code = (reason.get("Code") or "").upper()
        message = reason.get("Message") or ""

        if state == "TERMINATED_WITH_ERRORS":
            raise CustomPipesException(
                message=f"EMR job {job_flow} failed: [{code}] {message}"
            )

        if state in ("TERMINATED", "TERMINATING"):
            if code == "ALL_STEPS_COMPLETED":
                return False  # success -> stop polling
            log_uri = description["Cluster"].get("LogUri") or ""
            hint = f" (logs: {log_uri})" if log_uri else ""
            raise CustomPipesException(
                message=f"EMR job {job_flow} ended in {state} unexpectedly: [{code}] {message}{hint}"
            )

        return True

    def _handle_terminated_state_dbr(self, run):
        client = self._tagging_client
        get_dagster_logger().debug(f"run: {run}")
        try:
            resources = client.get_resources(
                TagFilters=[
                    {
                        "Key": "JobId",
                        "Values": [
                            str(run.job_id),
                        ],
                    },
                ]
            )
            resource_arns = [
                item["ResourceARN"]  # type: ignore[index]
                for item in resources["ResourceTagMappingList"]
            ]
            if len(resource_arns) > 0:
                for arn in resource_arns:
                    client.tag_resources(
                        ResourceARNList=[arn],
                        Tags={
                            "jobId": str(run.job_id),
                            "engine": self.engine,
                            "executionMode": self.executionMode,
                        },
                    )
        except Exception as e:
            get_dagster_logger().debug(e)
            raise
        if run.state.result_state == jobs.RunResultState.SUCCESS:
            return False
        else:
            state_message = run.state.state_message or "Unknown reason"
            raise CustomPipesException(
                message=f"Error running Databricks job: {state_message}"
            )

    def _ensure_library_on_cloud(
        self,
        libraries_to_build_and_upload: Optional[List[str]],
        **kwargs,
    ):
        """
        Ensure that the specified library is available on S3.

        Args:
            dbfs_path (str): The S3 path where the library should reside.
            local_library_path (str): The local file system path to the library.
        """
        bucket = kwargs.get("bucket", pipeline_bucket)
        if libraries_to_build_and_upload is not None:
            for library in libraries_to_build_and_upload:
                path = library_to_cloud_paths(
                    lib_name=library, filesystem=self.filesystem
                )
                to_upload = package_library(
                    file_relative_path(__file__, f"../../../../{library}")
                )[0]
                self._upload_file_to_cloud(
                    local_file_path=to_upload, cloud_path=path, bucket=bucket
                )

    def _upload_file_to_cloud(self, local_file_path: str, cloud_path: str, **kwargs):
        try:
            if isinstance(self.main_client, BaseClient):
                self._upload_file_to_s3(local_file_path, cloud_path, **kwargs)
            elif (
                isinstance(self.main_client, WorkspaceClient)
                and "py" == local_file_path.split(".")[-1]
            ):
                self._upload_file_to_dbfs(local_file_path, cloud_path)
            elif (
                isinstance(self.main_client, WorkspaceClient)
                and "whl" == local_file_path.split(".")[-1]
            ):
                self._upload_file_to_s3(local_file_path, cloud_path, **kwargs)
            else:
                raise TypeError(
                    "main_client must be either EMRClient or WorkspaceClient"
                )
        except Exception as e:
            self.handle_exep(e)

    def handle_exep(self, e):
        if isinstance(e, FileNotFoundError):
            get_dagster_logger().error("The file was not found")
            raise e
        elif isinstance(e, NoCredentialsError):
            get_dagster_logger().error("Credentials not available")
            raise e
        elif isinstance(e, ClientError):
            get_dagster_logger().error("Client error while uploading")
            raise e

    def _upload_file_to_s3(self, local_file_path: str, cloud_path: str, **kwargs):
        bucket = kwargs.get("bucket")
        get_dagster_logger().debug(f"uploading: {cloud_path} into bucket: {bucket}")
        try:
            if self._s3_client is not None:
                self._s3_client.upload_file(local_file_path, bucket, cloud_path)
            else:  # noqa: E722
                get_dagster_logger().debug("fail to upload to S3")
        except Exception as e:
            get_dagster_logger().error(f"error: {e.with_traceback}")
            raise

    def _upload_file_to_dbfs(self, local_file_path: str, dbfs_path: str):
        get_dagster_logger().debug(
            f"uploading: {local_file_path} to DBFS at: {dbfs_path}"
        )
        try:
            assert isinstance(self.main_client, WorkspaceClient)
            with open(local_file_path, "rb") as file:
                encoded_string = base64.b64encode(file.read()).decode("utf-8")
            self.main_client.dbfs.put(
                path=dbfs_path, contents=encoded_string, overwrite=True
            )
        except Exception as e:
            get_dagster_logger().error(e.with_traceback)
            get_dagster_logger().error(e)
            raise
