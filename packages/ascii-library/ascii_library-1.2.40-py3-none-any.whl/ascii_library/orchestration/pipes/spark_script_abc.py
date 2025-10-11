import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from dagster_pipes import (
    PipesContext,
    PipesDbfsContextLoader,
    PipesDbfsMessageWriter,
    PipesDefaultContextLoader,
    PipesDefaultMessageWriter,
    PipesEnvVarParamsLoader,
    open_dagster_pipes,
)
from pyspark.sql import SparkSession

from ascii_library.orchestration.pipes import Engine, ExecutionMode


class SparkScriptPipes(ABC):
    @abstractmethod
    def execute_business_logic(
        self,
        context,
        execution_mode: ExecutionMode,
        partition_key: Optional[str],
        spark: SparkSession,
        engine: Engine,
    ):
        raise NotImplementedError()

    def get_base_path_seeds(
        self,
        execution_mode: ExecutionMode,
    ) -> str:  # pyrefly: ignore
        if execution_mode == ExecutionMode.SmallDevSampleS3:
            return f"s3a://{self.sample_data}/ascii_seeds"
        elif execution_mode == ExecutionMode.SmallDevSampleLocal:
            return Path(self.reference_data_path, "ascii_seeds").resolve().as_uri()
        elif execution_mode == ExecutionMode.Full:
            return f"s3a://{self.bucket_seed_nodes}/ascii_seeds"

    def get_base_path_IO(
        self,
        execution_mode: ExecutionMode,
    ) -> str:  # pyrefly: ignore
        if execution_mode == ExecutionMode.SmallDevSampleS3:
            return f"s3a://{self.bucket_cc_dev_results}"
        elif execution_mode == ExecutionMode.SmallDevSampleLocal:
            return Path("z_state/ascii_dev_pipeline").resolve().as_uri()
        elif execution_mode == ExecutionMode.Full:
            return f"s3a://{self.bucket_cc_results}"

    def get_base_path_commoncrawl(
        self,
        execution_mode: ExecutionMode,
    ) -> str:  # pyrefly: ignore
        if execution_mode == ExecutionMode.SmallDevSampleS3:
            return f"s3a://{self.sample_data}/"
        elif execution_mode == ExecutionMode.SmallDevSampleLocal:
            return (
                Path("../../../../reference-data/pipeline_sample_data/commoncrawl")
                .resolve()
                .as_uri()
            )
        elif execution_mode == ExecutionMode.Full:
            return "s3a://commoncrawl/"

    def __init__(self):
        engine = Engine(os.environ.get("SPARK_PIPES_ENGINE", "pyspark"))
        loader, writer, envvar = self.get_loader_writer(engine)
        with open_dagster_pipes(
            context_loader=loader, message_writer=writer, params_loader=envvar
        ):
            context = PipesContext.get()
            execution_mode = ExecutionMode(context.get_extra("execution_mode"))  # type: ignore
            partition_key: Optional[str] = context.get_extra("partition_key")  # type: ignore

            context.log.info(f"Partition key: {partition_key}")
            context.log.info(f"Execution mode: {execution_mode}")

            self.bucket_seed_nodes = os.environ.get(
                "BUCKET_SEED_NODES", "ascii-supply-chain-research-input"
            )
            self.bucket_cc_results = os.environ.get(
                "BUCKET_CC_RESULTS", "ascii-supply-chain-research-results"
            )
            self.bucket_cc_dev_results = os.environ.get(
                "BUCKET_CC_DEV_RESULTS", "ascii-supply-chain-research-dev-results"
            )
            self.sample_data = os.environ.get(
                "SAMPLE_DATA_BUCKET", "ascii-supply-chain-research-sample-data"
            )
            self.reference_data_path = os.environ.get(
                "REFERENCE_DATA_PATH",
                "../../../../reference-data/pipeline_sample_data/commoncrawl",
            )

            if engine == Engine.Local:
                local_spark_config = context.get_extra("local_spark_config")
                spark_cfg = local_spark_config["spark_conf"]
                builder = SparkSession.builder.appName("ascii").master(  # type: ignore
                    spark_cfg["spark.master"]
                )
                for key, value in spark_cfg.items():
                    builder = builder.config(key, value)
                spark = builder.getOrCreate()
                # spark.sparkContext.setLogLevel("ERROR")
            elif engine in [Engine.Databricks, Engine.EMR]:
                # we are on a remote cluster
                # it is already initialized
                spark = SparkSession.builder.getOrCreate()  # type: ignore
            else:
                raise ValueError(f"Unsupported engine mode: {engine.value}")

            self.execute_business_logic(
                context, execution_mode, partition_key, spark, engine
            )

    def get_loader_writer(self, engine):
        if engine == Engine.Local:
            loader = PipesDefaultContextLoader()
            writer = PipesDefaultMessageWriter()
            envvar = PipesEnvVarParamsLoader()
        elif engine == Engine.Databricks:
            # databricks execution mode is on
            loader = PipesDbfsContextLoader()
            writer = PipesDbfsMessageWriter()
            envvar = PipesEnvVarParamsLoader()
        elif engine == Engine.EMR:
            import boto3
            from dagster_pipes import PipesS3ContextLoader, PipesS3MessageWriter

            # for this to work an instance profile with the right permissions
            # must already be attached to the cluster
            # this only works inside AWS
            s3_client = boto3.client(
                "s3",
                region_name="us-east-1",
            )
            loader = PipesS3ContextLoader(client=s3_client)
            writer = PipesS3MessageWriter(client=s3_client)
            envvar = PipesEnvVarParamsLoader()
        else:
            raise ValueError(f"Unsupported engine mode: {engine}")
        return loader, writer, envvar


# sample usage for child classes
# if __name__ == "__main__":
#    SparkScriptPipes()
