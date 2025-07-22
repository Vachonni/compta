"""File with settings common to all services of this application."""

from pathlib import Path

from pydantic_settings import BaseSettings


class SharedSettings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parents[4]

    ENVIRONMENT: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


shared_settings = SharedSettings()  # type: ignore


if __name__ == "__main__":
    print("Configuration paths:")
    print(f"Base dir: {shared_settings.BASE_DIR}")
    print(f"Environment: {shared_settings.ENVIRONMENT}")
