"""Database service settings."""

from pathlib import Path

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Settings for the database service."""
    ENVIRONMENT: str
    DATABASES_DIR: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


    @property
    def DB_PATH(self) -> Path:
        return Path(self.DATABASES_DIR).resolve() / "compta"

    @property
    def EXCEL_PATH(self) -> Path:
        return self.DB_PATH / "Blob" / "Legacy" / "REVOLUT AVRIL 2025.xlsx"

    @property
    def SQLITE_DEV_PATH(self) -> Path:
        return self.DB_PATH / "SQL" / "dev.db"

    @property
    def TABLE_NAME(self) -> str:
        return "transactions"

    
database_settings = DatabaseSettings()  # type: ignore


if __name__ == "__main__":
    print("Configuration paths:")
    print(f"Databases directory: {database_settings.DATABASES_DIR}")
    print(f"Database path: {database_settings.DB_PATH}")
    print(f"Excel path: {database_settings.EXCEL_PATH}")
    print(f"SQLite development path: {database_settings.SQLITE_DEV_PATH}")
    print(f"Table name: {database_settings.TABLE_NAME}")
    print(f"Environment: {database_settings.ENVIRONMENT}")
