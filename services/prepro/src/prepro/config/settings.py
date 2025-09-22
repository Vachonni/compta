"""Settings for project prepro"""

import os
from prepro.config.schemas import AppEnvEnum

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the database service."""

    # Mapping of standardized columns to their possible equivalents (in various languages/providers)
    COLUMN_EQUIVALENTS: dict[str, list[str]] = {
        "Started Date": ["Started Date", "Date de début"],
        "Completed Date": ["Completed Date", "Date de fin"],
        "Type": ["Type"],
        "Product": ["Product", "Produit"],
        "Description": ["Description"],
        "Amount": ["Amount", "Montant"],
        "Fee": ["Fee", "Frais"],
        "Currency": ["Currency", "Devise"],
        "State": ["State", "État"],
        "Balance": ["Balance", "Solde"],
    }
    # Fields loaded from environment variables
    app_env: AppEnvEnum = Field(
        default=AppEnvEnum.DEV
    )  # Field necesary for pytest in Docker
    root_dir: str = Field(
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    )  # Root directory of the project
    sql_url: str
    blob_url: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @property
    def log_level(self) -> str:
        """Return the log level depending on the environment."""
        if self.app_env == AppEnvEnum.PROD:
            return "INFO"
        else:
            return "DEBUG"


settings = Settings()  # type: ignore


if __name__ == "__main__":
    print("Configuration:")
    print(f"Environment: {settings.app_env.value}")
    print(f"Root Dir: {settings.root_dir}")
    print(f"Log Level: {settings.log_level}")
    print(f"SQL URL: {settings.sql_url}")
    print(f"Blob URL: {settings.blob_url}")
