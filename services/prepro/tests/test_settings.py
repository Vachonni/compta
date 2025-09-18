"""
Unit tests for prepro.config.settings.

These tests verify environment variable handling, enum validation, and settings loading.
"""

from importlib import reload

import pytest
from _pytest.monkeypatch import MonkeyPatch

import prepro.config.settings as config_mod
from prepro.config.schemas import AppEnvEnum
from pydantic import ValidationError


def test_env_defaults_to_dev(monkeypatch: MonkeyPatch) -> None:
    """Should default to dev environment if APP_ENV is not set."""
    monkeypatch.delenv("APP_ENV", raising=False)
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.DEV


def test_env_variables_are_loaded(monkeypatch: MonkeyPatch) -> None:
    """Should load settings from environment variables correctly."""
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("SQL_URL", "postgresql://user:pass@localhost:5432/testdb")
    monkeypatch.setenv("BLOB_URL", "https://storage.example.com/container")
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.DEV
    assert settings.log_level == "DEBUG"
    assert settings.sql_url == "postgresql://user:pass@localhost:5432/testdb"
    assert settings.blob_url == "https://storage.example.com/container"


def test_app_env_enum_variants(monkeypatch: MonkeyPatch) -> None:
    """Should correctly parse and validate all AppEnvEnum variants."""

    monkeypatch.setenv("APP_ENV", "staging")
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.STAGING
    assert settings.log_level == "DEBUG"

    monkeypatch.setenv("APP_ENV", "prod")
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.PROD
    assert settings.log_level == "INFO"


@pytest.mark.parametrize("invalid_env", ["foo", "", "DEV "])
def test_invalid_app_env_raises(monkeypatch: MonkeyPatch, invalid_env: str) -> None:
    """Should raise ValueError for invalid APP_ENV values."""
    monkeypatch.setenv("APP_ENV", invalid_env)
    with pytest.raises(ValidationError):
        reload(config_mod)
        _ = config_mod.settings


def test_different_url_formats(monkeypatch: MonkeyPatch) -> None:
    """Should accept different valid URL formats for sql_url and blob_url."""
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("SQL_URL", "sqlite:///path/to/database.db")
    monkeypatch.setenv("BLOB_URL", "file:///local/storage/path")
    reload(config_mod)
    settings = config_mod.settings
    assert settings.sql_url == "sqlite:///path/to/database.db"
    assert settings.blob_url == "file:///local/storage/path"


def test_default_urls_from_conftest() -> None:
    """Should use default URLs from conftest.py when no explicit env vars are set."""
    reload(config_mod)
    settings = config_mod.settings
    # These default values come from the conftest.py env_vars fixture
    assert settings.sql_url == "postgresql+psycopg2://user:pass@localhost:5432/db"
    assert settings.blob_url == "http://localhost:8000"
    assert settings.app_env == AppEnvEnum.DEV


def test_missing_env_var_detection() -> None:
    """Demonstrates that missing required environment variables are properly detected.

    This test shows that if SQL_URL or BLOB_URL are missing from both:
    1. Environment variables
    2. The .env file

    Then pydantic will raise a ValidationError with clear error messages.
    """
    import os
    from prepro.config.settings import Settings

    # Save current state
    original_sql = os.environ.get("SQL_URL")
    original_blob = os.environ.get("BLOB_URL")
    env_file = "/Users/nicholasvachon/Code/Repos/compta/services/prepro/.env"
    temp_file = env_file + ".backup"

    try:
        # Remove from environment
        if "SQL_URL" in os.environ:
            del os.environ["SQL_URL"]
        if "BLOB_URL" in os.environ:
            del os.environ["BLOB_URL"]

        # Hide .env file temporarily
        if os.path.exists(env_file):
            os.rename(env_file, temp_file)

        # This should raise ValidationError - we use try/except to avoid linter complaints
        try:
            # pylint: disable=missing-kwoa
            Settings()  # type: ignore[call-arg]
            # If we get here, the test failed
            pytest.fail("Expected ValidationError was not raised")
        except ValidationError as exc:
            error_message = str(exc)
            print(f"\nValidation error when missing env vars:\n{error_message}")

            # Verify both fields are mentioned in the error
            assert "sql_url" in error_message.lower()
            assert "blob_url" in error_message.lower()
            assert (
                "field required" in error_message.lower()
                or "missing" in error_message.lower()
            )

    finally:
        # Restore everything
        if os.path.exists(temp_file):
            os.rename(temp_file, env_file)
        if original_sql:
            os.environ["SQL_URL"] = original_sql
        if original_blob:
            os.environ["BLOB_URL"] = original_blob
