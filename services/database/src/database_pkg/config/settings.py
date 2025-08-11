from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from database_pkg.config.schemas import AppEnvEnum


class DatabaseSettings(BaseSettings):
    """Settings for the database service."""

    SERVICE_NAME: str = "database"
    DOCKER_DATABASES_DIR: str
    LOCAL_DATABASES_DIR: str
    app_env: AppEnvEnum = Field(default=AppEnvEnum.LOCAL)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def log_level(self) -> str:
        if self.app_env == AppEnvEnum.PROD:
            return "INFO"
        else:
            return "DEBUG"

    @property
    def db_path(self) -> Path:
        if self.app_env == AppEnvEnum.LOCAL:
            return Path(self.LOCAL_DATABASES_DIR)
        else:
            return Path(self.DOCKER_DATABASES_DIR)

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
    print(f"Database path: {database_settings.db_path}")
    print(f"Blob path: {database_settings.blob_path}")
    print(f"SQLite development path: {database_settings.sqlite_path}")
    print(f"Excel path: {database_settings.excel_path}")
