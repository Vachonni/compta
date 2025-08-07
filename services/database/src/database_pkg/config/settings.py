from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

from database_pkg.config.schemas import AppEnvEnum

env_file: str = f".env.{os.getenv('APP_ENV', 'local')}"


class DatabaseSettings(BaseSettings):
    """Settings for the database service."""

    SERVICE_NAME: str = "database"
    DATABASES_DIR_LOCAL: str = "/Users/nicholas/Databases"
    DATABASES_DIR_DOCKER: str = "/app/DatabasesMount"
    app_env: AppEnvEnum = Field(default=AppEnvEnum.LOCAL)

    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
    )

    @property
    def databases_dir(self) -> str:
        if self.app_env == AppEnvEnum.LOCAL:
            return self.DATABASES_DIR_LOCAL
        else:
            return self.DATABASES_DIR_DOCKER

    @property
    def log_level(self) -> str:
        if self.app_env == AppEnvEnum.PROD:
            return "INFO"
        else:
            return "DEBUG"

    @property
    def db_path(self) -> Path:
        return Path(self.databases_dir) / "compta"

    @property
    def blob_path(self) -> Path:
        if self.app_env == AppEnvEnum.PROD:
            return self.db_path / "blob" / "prod"
        else:
            return self.db_path / "blob" / "dev"

    @property
    def sqlite_path(self) -> Path:
        if self.app_env == AppEnvEnum.PROD:
            return self.db_path / "SQL" / "prod.db"
        else:
            return self.db_path / "SQL" / "dev.db"

    @property
    def excel_path(self) -> Path:
        return self.blob_path / "Legacy" / "REVOLUT AVRIL 2025.xlsx"


database_settings = DatabaseSettings()  # type: ignore


if __name__ == "__main__":
    print("Configuration paths:")
    print(f"Environment: {database_settings.app_env.value}")
    print(f"Databases directory: {database_settings.databases_dir}")
    print(f"Database path: {database_settings.db_path}")
    print(f"Blob path: {database_settings.blob_path}")
    print(f"SQLite development path: {database_settings.sqlite_path}")
    print(f"Excel path: {database_settings.excel_path}")
