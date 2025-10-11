import os
from contextlib import contextmanager
from typing import Generator, List, Literal, Tuple, Union

import dagster as dg
import duckdb  # pyrefly: ignore
from duckdb import DuckDBPyConnection  # pyrefly: ignore
from pydantic import Field
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection, Engine

from .duckdb_protocol import DuckDBConnectionProvider


class PostgresConfig(dg.Config):
    """Configuration for a Postgres metadata backend."""

    type: Literal["postgres"] = "postgres"
    host: str = Field(default=os.getenv("DUCKLAKE_PG_HOST", "localhost"))
    port: int = Field(default=5432)
    database: str
    user: str
    password: str

    def get_ducklake_sql_parts(self, alias: str) -> Tuple[str, str]:
        """Returns the SQL for the credential secret and the main METADATA parameter."""
        secret_name = f"secret_catalog_{alias}"
        secret_sql = f"""
            CREATE OR REPLACE SECRET {secret_name} (
                TYPE postgres, HOST '{self.host}', PORT {self.port},
                DATABASE '{self.database}', USER '{self.user}',
                PASSWORD '{self.password}'
            );
        """
        metadata_params_sql = (
            f"METADATA_PATH '', "
            f"METADATA_PARAMETERS MAP {{'TYPE': 'postgres', 'SECRET': '{secret_name}'}}"
        )
        return secret_sql, metadata_params_sql


class SqliteConfig(dg.Config):
    """Configuration for a local SQLite file metadata backend."""

    type: Literal["sqlite"] = "sqlite"
    path: str = Field(description="Path to the SQLite database file.")

    def get_ducklake_sql_parts(self, alias: str) -> Tuple[str, str]:
        """For file-based backends, no credential secret is needed."""
        return "", f"METADATA_PATH '{self.path}'"


class DuckDBConfig(dg.Config):
    """Configuration for a local DuckDB file metadata backend."""

    type: Literal["duckdb"] = "duckdb"
    path: str = Field(description="Path to the DuckDB database file.")

    def get_ducklake_sql_parts(self, alias: str) -> Tuple[str, str]:
        """For file-based backends, no credential secret is needed."""
        return "", f"METADATA_PATH '{self.path}'"


class S3Config(dg.Config):
    """Configuration for an S3-compatible storage backend."""

    type: Literal["s3"] = "s3"
    endpoint_url: str = Field(
        description="Endpoint URL for the S3-compatible object store."
    )
    bucket: str = Field(description="Name of the S3 bucket for data storage.")
    prefix: str | None = Field(
        default=None, description="Optional path prefix within the S3 bucket."
    )
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str = Field(default="us-east-1")
    use_ssl: bool = Field(default=True)
    url_style: str = Field(
        default="path", description="URL style for S3 ('path' or 'virtual')."
    )

    @property
    def full_data_path(self) -> str:
        """
        Handles the prefix gracefully. This is cleaner and more robust than a complex one-liner.
        It ensures a single trailing slash is present if a prefix is used.
        """
        path = f"s3://{self.bucket}"
        if self.prefix:
            clean_prefix = self.prefix.strip("/")
            return f"{path}/{clean_prefix}/"
        return f"{path}/"

    def get_ducklake_sql_parts(self, alias: str) -> Tuple[str, str]:
        """Returns the SQL for the credential secret and the main DATA_PATH parameter."""
        secret_name = f"secret_storage_{alias}"
        secret_sql = f"""
            CREATE OR REPLACE SECRET {secret_name} (
                TYPE S3, KEY_ID '{self.aws_access_key_id}',
                SECRET '{self.aws_secret_access_key}',
                ENDPOINT '{self.endpoint_url}', URL_STYLE '{self.url_style}',
                REGION '{self.region}', USE_SSL {"true" if self.use_ssl else "false"},
                SCOPE 's3://{self.bucket}'
            );
        """
        data_path_sql = f"DATA_PATH '{self.full_data_path}'"
        return secret_sql, data_path_sql


class DuckLakeLocalDirectory(dg.Config):
    """Configuration for a local filesystem storage directory."""

    type: Literal["local"] = "local"
    path: str = Field(description="Path to the local storage directory.")

    def get_ducklake_sql_parts(self, alias: str) -> Tuple[str, str]:
        """For local storage, no credential secret is needed."""
        return "", f"DATA_PATH '{self.path}'"


class DuckLakeResource(DuckDBConnectionProvider):
    """A highly configurable Dagster resource for interacting with DuckLake.

    Supports multiple metadata and storage backends.
    """

    metadata_backend: Union[PostgresConfig, SqliteConfig, DuckDBConfig] = Field(
        discriminator="type",
        description="Configuration for the metadata catalog backend.",
    )
    storage_backend: Union[S3Config, DuckLakeLocalDirectory] = Field(
        discriminator="type", description="Configuration for the data storage backend."
    )
    alias: str = Field(
        default="ducklake", description="Alias for the attached DuckLake instance."
    )
    plugins: List[str] = Field(
        default=["ducklake"],
        description="List of DuckDB plugins to install and load.",
    )

    def get_engine(self) -> Engine:
        engine = create_engine("duckdb:///:memory:")
        event.listen(engine, "connect", self._setup_ducklake_connection)
        return engine

    @contextmanager
    def connect(self) -> Generator[Connection, None, None]:
        """Yields a SQLAlchemy connection for use in a `with` statement."""
        with self.get_engine().connect() as conn:
            yield conn

    @contextmanager
    def duckdb_connect(self) -> Generator[DuckDBPyConnection, None, None]:
        """Yields a pre-configured native DuckDB connection for safe use."""
        conn = self.get_duckdb_connection()
        try:
            yield conn
        finally:
            conn.close()

    def get_duckdb_connection(self) -> DuckDBPyConnection:
        """Returns a new, pre-configured native duckdb connection object."""
        conn = duckdb.connect(database=":memory:")
        self._setup_ducklake_connection(conn, connection_record=None)
        return conn

    def _setup_ducklake_connection(self, dbapi_connection, connection_record):
        """
        Internal method to configure a DuckDB connection to use DuckLake.
        This now orchestrates SQL generation by calling its backend configs.
        """
        cursor = dbapi_connection.cursor()

        for plugin in self.plugins:
            cursor.execute(f"INSTALL {plugin}; LOAD {plugin};")

        metadata_secret_sql, metadata_params_sql = (
            self.metadata_backend.get_ducklake_sql_parts(self.alias)
        )
        storage_secret_sql, storage_data_path_sql = (
            self.storage_backend.get_ducklake_sql_parts(self.alias)
        )

        if metadata_secret_sql:
            cursor.execute(metadata_secret_sql)
        if storage_secret_sql:
            cursor.execute(storage_secret_sql)

        ducklake_secret_name = f"secret_{self.alias}"
        cursor.execute(f"""
            CREATE OR REPLACE SECRET {ducklake_secret_name} (
                TYPE DUCKLAKE,
                {metadata_params_sql},
                {storage_data_path_sql}
            );
        """)

        cursor.execute(f"ATTACH 'ducklake:{ducklake_secret_name}' AS {self.alias};")
        cursor.execute(f"USE {self.alias};")
        cursor.close()
