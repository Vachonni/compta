"""Settings for project prepro"""


import os
from prepro.config.schemas import AppEnvEnum

from pydantic import Field
from pydantic_settings import BaseSettings

env_file: str = f".env.{os.getenv('APP_ENV', 'dev')}"





class Settings(BaseSettings):
    """Settings for the database service."""

    # Fixed fields
    FIXED_VAR: str = "fixed_var"
    # Fields loaded from environment variables
    app_env: AppEnvEnum = Field(
        default=AppEnvEnum.DEV
    )  # Field necesary for pytest in Docker

    model_config = {
        "env_file": env_file,
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
    print(f"Log Level: {settings.log_level}")
