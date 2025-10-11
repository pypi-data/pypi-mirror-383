import os
import shutil
from typing import Any, List, Mapping, Optional, Sequence, Union

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    Config,
    MaterializeResult,
    PartitionsDefinition,
    PipesSubprocessClient,
    asset,
    get_dagster_logger,
)
from databricks.sdk.service import jobs
from pydantic import Field

from ascii_library.orchestration.pipes import (
    LibraryConfig,
    LibraryKind,
    get_engine_by_value,
)
from ascii_library.orchestration.pipes.databricks import PipesDatabricksEnhancedClient
from ascii_library.orchestration.pipes.emr import PipesEmrEnhancedClient
from ascii_library.orchestration.pipes.instance_config import CloudInstanceConfig
from ascii_library.orchestration.pipes.spark_pipes import Engine, SparkPipesResource
from ascii_library.orchestration.resources.emr_constants import pipeline_bucket
from ascii_library.utils.determine_env import (
    get_dagster_deployment_environment,
)

deployment_env = get_dagster_deployment_environment()

# TODO: remove all the ignores on this script


def get_libs_dict(
    cfg: Optional[List[LibraryConfig]],
) -> List[Mapping[str, Union[str, Mapping]]]:
    libs_dict: List[Mapping[str, Union[str, Mapping]]] = []

    if cfg is not None:
        for lib in cfg:
            if lib.kind == LibraryKind.Pypi:
                package_str = (
                    f"{lib.name_id}{lib.version}" if lib.version else lib.name_id
                )
                libs_dict.append({lib.kind.value: {"package": package_str}})
            elif lib.kind == LibraryKind.Wheel:
                lib_name = f"s3://{pipeline_bucket}/{lib.name_id}"
                libs_dict.append({lib.kind.value: lib_name})

    return libs_dict


def update_spot_bid_price_percent(fleet_config, new_spot_bid_price_percent):  # noqa: C901
    if hasattr(fleet_config, "percentageOfOnDemandPrice"):
        fleet_config.percentageOfOnDemandPrice = new_spot_bid_price_percent
    return fleet_config


def generate_uploaded_script_paths(
    local_input_path: str, prefix: str = "dbfs:/"
) -> str:
    """Retrieve file name from path.
    construct full path as: "dbfs:/external_pipes/<<filename>>.py"
    """
    # TODO potential race condition (file in DBFS), in case of parallel runs
    # this is not yet including versioning. When launching more than 1 instance of a databricks spark job in parallel this file is overwritten

    filename_without_extension = os.path.splitext(os.path.basename(local_input_path))[0]
    new_path = f"{prefix}/{deployment_env}/{filename_without_extension}.py"
    return new_path


def get_engine_from_config(config, spark_pipes_client):
    if "config" in config.keys():
        if (
            "override_default_engine" in config["config"].keys()
            and config["config"]["override_default_engine"]
        ):
            override_engine = get_engine_by_value(
                config["config"]["override_default_engine"]
            )
            return spark_pipes_client.get_spark_pipes_client(
                override_engine
            ), override_engine
        else:
            return spark_pipes_client.get_spark_pipes_client(
                spark_pipes_client.engine
            ), spark_pipes_client.engine
    else:
        return spark_pipes_client.get_spark_pipes_client(
            spark_pipes_client.engine
        ), spark_pipes_client.engine


def spark_pipes_asset_factory(  # noqa: C901
    name: str,
    key_prefix: Sequence[str],
    spark_pipes_client: SparkPipesResource,
    external_script_file: str,
    partitions_def: Optional[PartitionsDefinition] = None,
    cfg=None,  # Optional[Config]
    deps: Optional[Sequence[AssetsDefinition]] = None,
    group_name: Optional[str] = None,
    local_spark_config: Optional[Mapping[str, str]] = None,
    libraries_to_build_and_upload: Sequence[str] = None,  # type: ignore
    databricks_cluster_config: Optional[dict[str, Any]] = None,
    libraries_config: Optional[List[LibraryConfig]] = None,
    emr_additional_libraries: Optional[List[LibraryConfig]] = None,
    dbr_additional_libraries: Optional[List[LibraryConfig]] = None,
    emr_job_config: Optional[dict] = None,
    fleet_filters: Optional[CloudInstanceConfig] = None,
    # TODO: in the future support IO manager perhaps for python reading directly from S3 io_manager_key:Optional[str]: None
    # but maybe we intend to keep the offline sync process
    # TODO: should we use asset KWARGS here instead for flexibility?
):
    """
    Construct dagster-pipes based Spark assets for multiple engines: local pyspark and databricks

    Automatically configure the right pipes clients.
    In the case of Databricks: Ensure dependencies and scripts are present and ready to be executed - automatically build the dependent libraries and upload these to DBFS.
    """

    engine_to_use = spark_pipes_client.engine
    # TODO: auto upload is a convenience feature for now in the future this should be a CI pipeline step with a defined version - this task should only be executed once on ci build and not per each task
    if cfg is None:

        @asset(
            name=name,
            compute_kind=engine_to_use.value,
            deps=deps,
            partitions_def=partitions_def,
            group_name=group_name,
            key_prefix=key_prefix,
        )
        def inner_spark_pipes_asset(
            context: AssetExecutionContext,
        ) -> MaterializeResult:
            client_params = handle_shared_parameters(context, {})
            client, real_engine = get_engine_from_config(
                client_params, spark_pipes_client
            )
            return handle_pipeline_modes(context, client_params, client, real_engine)  # type: ignore

    else:

        @asset(
            name=name,
            compute_kind=engine_to_use.value,
            deps=deps,
            partitions_def=partitions_def,
            group_name=group_name,
            key_prefix=key_prefix,
        )
        def inner_spark_pipes_asset(
            context: AssetExecutionContext,
            config: cfg,  # type: ignore
        ) -> MaterializeResult:
            client_params = handle_shared_parameters(context, config)
            client, real_engine = get_engine_from_config(
                client_params, spark_pipes_client
            )
            # TODO this produces a potential race condition?
            os.environ["SPARK_PIPES_ENGINE"] = real_engine.value
            return handle_pipeline_modes(context, client_params, client, real_engine)  # type: ignore

    def handle_pipeline_modes(
        context: AssetExecutionContext,
        client_params,
        client: Union[
            PipesSubprocessClient,
            PipesDatabricksEnhancedClient,
            PipesEmrEnhancedClient,
        ],
        real_engine,
    ):
        if real_engine == Engine.Local:
            return handle_local(client_params, context, client)  # type: ignore
        elif real_engine == Engine.Databricks:
            return handle_databricks(client_params, context, client)  # type: ignore
        elif real_engine == Engine.EMR:
            return handle_emr(client_params, context, fleet_filters, client)  # type: ignore
        else:
            raise ValueError(f"Unsupported engine mode: {real_engine.value}")

    def handle_emr(
        client_params, context, fleet_filters, client: PipesEmrEnhancedClient
    ):
        s3_script_path = generate_uploaded_script_paths(
            local_input_path=external_script_file, prefix="external_pipes"
        )
        step_config = {
            "Name": "Spark Step",
            "ActionOnFailure": "TERMINATE_JOB_FLOW",
            "HadoopJarStep": {
                "Jar": "command-runner.jar",
                "Args": ["spark-submit", f"s3://{pipeline_bucket}/{s3_script_path}"],
            },
        }

        emr_job_config["Name"] = client_params["job_name"]  # type: ignore
        if emr_additional_libraries is not None:
            engine_specific_libs = libraries_config.copy()  # type: ignore
            engine_specific_libs.extend(emr_additional_libraries)
        else:
            engine_specific_libs = libraries_config
        if (
            "config" in client_params.keys()
            and "spot_bid_price_percent" in client_params["config"].keys()
        ):
            if fleet_filters is not None:
                fleet_filters = update_spot_bid_price_percent(
                    fleet_filters, client_params["config"]["spot_bid_price_percent"]
                )
        return client.run(  # type: ignore
            context=context,
            emr_job_config=emr_job_config,  # type: ignore
            bucket=pipeline_bucket,
            local_file_path=external_script_file,
            s3_path=s3_script_path,
            step_config=step_config,
            libraries_to_build_and_upload=libraries_to_build_and_upload,  # type: ignore
            libraries=engine_specific_libs,
            extras=client_params,
            fleet_config=fleet_filters,
        ).get_results()

    def handle_databricks(
        client_params, context, client: PipesDatabricksEnhancedClient
    ):
        # we are using databricks engine
        script_file_path_after_upload = generate_uploaded_script_paths(
            external_script_file, prefix="dbfs:/external_pipes"
        )
        if dbr_additional_libraries is not None:
            engine_specific_libs = libraries_config.copy()  # type: ignore
            engine_specific_libs.extend(dbr_additional_libraries)  # type: ignore
        else:
            engine_specific_libs = libraries_config
        if (
            "config" in client_params.keys()
            and "spot_bid_price_percent" in client_params["config"].keys()
        ):
            databricks_cluster_config["spot_bid_price_percent"] = client_params[  # type: ignore
                "config"
            ]["spot_bid_price_percent"]
            databricks_cluster_config["cluster_log_conf"] = {  # type: ignore
                "dbfs": {"destination": "dbfs:/cluster-logs/dagster"}
            }  # type: ignore
            get_dagster_logger().debug(databricks_cluster_config)
        task = jobs.SubmitTask.from_dict(
            {
                "new_cluster": databricks_cluster_config,
                "libraries": get_libs_dict(engine_specific_libs),
                "task_key": "dagster-launched",
                "spark_python_task": {
                    "python_file": script_file_path_after_upload,
                    "source": jobs.Source.WORKSPACE,
                },
            }
        )
        return client.run(  # type: ignore
            task=task,
            context=context,
            env={
                "SPARK_PIPES_ENGINE": "databricks",
            },
            extras=client_params,
            libraries_to_build_and_upload=libraries_to_build_and_upload,  # type: ignore
            local_file_path=external_script_file,
            dbfs_path=script_file_path_after_upload,
        ).get_results()

    def handle_local(client_params, context, client: PipesSubprocessClient):
        cmd = [shutil.which("python"), external_script_file]
        client_params["local_spark_config"] = local_spark_config
        return client.run(  # type: ignore
            command=cmd,  # pyrefly: ignore
            context=context,
            extras=client_params,
        ).get_results()

    def handle_shared_parameters(context, cfg):
        client_params = {
            "execution_mode": spark_pipes_client.execution_mode.value,
            "engine": engine_to_use.value,
            "config": dict(cfg),  # type: ignore
        }
        if partitions_def is not None:
            client_params["partition_key"] = context.partition_key
            job_name = f"{name}_{deployment_env}_{spark_pipes_client.execution_mode.value}_{context.partition_key}"
        else:
            client_params["partition_key"] = None  # pyrefly: ignore
            job_name = (
                f"{name}_{spark_pipes_client.execution_mode.value}_{deployment_env}"
            )
        client_params["job_name"] = job_name
        return client_params

    return inner_spark_pipes_asset


class BaseConfig(Config):
    """Runtime knobs for Spark pipes.

    Fields:
      - ``spot_bid_price_percent``: percent of on-demand price to pay for spot (1–100).
      - ``override_default_engine``: override engine. One of ``pyspark``, ``emr``, ``databricks``.
    """

    spot_bid_price_percent: Optional[int] = Field(  # pyrefly: ignore
        default=90,
        description="Percent of on-demand price to pay (1–100).",
        gt=1,
        le=100,
    )
    override_default_engine: Optional[str] = Field(
        default=None,
        description="Override engine: 'pyspark', 'emr', or 'databricks'.",
    )
