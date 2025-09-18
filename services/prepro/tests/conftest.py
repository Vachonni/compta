import os
import pytest


@pytest.fixture(autouse=True)
def env_vars(monkeypatch: pytest.MonkeyPatch):
    """
    Ensure required environment variables exist for settings during tests.
    These are read by prepro.config.settings.Settings on import.
    """
    monkeypatch.setenv(
        "SQL_URL",
        os.getenv("SQL_URL", "postgresql+psycopg2://user:pass@localhost:5432/db"),
    )
    monkeypatch.setenv("BLOB_URL", os.getenv("BLOB_URL", "http://localhost:8000"))
    # Allow individual tests to override APP_ENV explicitly; default to dev
    monkeypatch.setenv("APP_ENV", os.getenv("APP_ENV", "dev"))
    yield
