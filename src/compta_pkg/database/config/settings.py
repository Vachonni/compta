"""Database service settings."""

from pathlib import Path

from compta_pkg.shared.config.settings import SharedSettings, shared_settings


class DatabaseSettings(SharedSettings):
    DB_DIR: Path = shared_settings.BASE_DIR.parents[1] / "Database" / "compta"
    EXCEL_PATH: Path = DB_DIR / "legacy" / "REVOLUT AVRIL 2025.xlsx"
    SQLITE_DEV_PATH: Path = DB_DIR / "dev_database.db"
    TABLE_NAME: str = "transactions"


database_settings = DatabaseSettings()  # type: ignore


if __name__ == "__main__":
    print("Configuration paths:")
    print(f"Database directory: {database_settings.DB_DIR}")
    print(f"Excel path: {database_settings.EXCEL_PATH}")
    print(f"SQLite development path: {database_settings.SQLITE_DEV_PATH}")
    print(f"Table name: {database_settings.TABLE_NAME}")
    print(f"Environment: {database_settings.ENVIRONMENT}")
