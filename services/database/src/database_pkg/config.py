"""Database service settings."""

import os
from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings

env_file: str = f".env.{os.getenv('APP_ENV', 'dev')}"


# Enum for allowed APP_ENV values
class AppEnvEnum(str, Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"


class DatabaseSettings(BaseSettings):
    """Settings for the database service."""

    app_env: AppEnvEnum
    databases_dir: str

    model_config = {
        "env_file": env_file,
        "env_file_encoding": "utf-8",
    }

    @property
    def db_path(self) -> Path:
        return Path(self.databases_dir) / "compta"

    @property
    def excel_path(self) -> Path:
        return self.db_path / "Blob" / "Legacy" / "REVOLUT AVRIL 2025.xlsx"

    @property
    def sqlite_dev_path(self) -> Path:
        return self.db_path / "SQL" / f"{self.app_env.value}.db"

    @property
    def table_name(self) -> str:
        return "transactions"


database_settings = DatabaseSettings()  # type: ignore


if __name__ == "__main__":
    print("Configuration paths:")
    print(f"Environment: {database_settings.app_env.value}")
    print(f"Databases directory: {database_settings.databases_dir}")
    print(f"Database path: {database_settings.db_path}")
    print(f"Excel path: {database_settings.excel_path}")
    print(f"SQLite development path: {database_settings.sqlite_dev_path}")
    print(f"Table name: {database_settings.table_name}")
