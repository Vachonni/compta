"""
Unit tests for database_pkg.config module.

These tests verify environment variable handling, enum validation, and settings loading.
"""

from importlib import reload
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

import database_pkg.config as config_mod
from database_pkg.config import AppEnvEnum


def test_env_defaults_to_dev(monkeypatch: MonkeyPatch) -> None:
    """Should default to DEV environment if APP_ENV is not set."""
    monkeypatch.delenv("APP_ENV", raising=False)
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.LOCAL


def test_env_variables_are_loaded(monkeypatch: MonkeyPatch) -> None:
    """Should load settings from environment variables correctly."""
    monkeypatch.setenv("APP_ENV", "dev")
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.SERVICE_NAME == "database"
    assert settings.app_env == AppEnvEnum.DEV
    assert settings.log_level == "DEBUG"
    assert settings.databases_dir == settings.DATABASES_DIR_DOCKER
    assert settings.db_path == Path(settings.databases_dir) / "compta"
    assert settings.sqlite_dev_path == settings.db_path / "SQL" / "dev.db"
    assert settings.table_name == "transactions"
    assert (
        settings.excel_path
        == Path(settings.databases_dir)
        / "compta"
        / "Blob"
        / "Legacy"
        / "REVOLUT AVRIL 2025.xlsx"
    )


def test_app_env_enum_variants(monkeypatch: MonkeyPatch) -> None:
    """Should correctly parse and validate all AppEnvEnum variants."""
    monkeypatch.setenv("APP_ENV", "local")
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.LOCAL
    assert settings.sqlite_dev_path.name == "dev.db"
    assert "Users" in settings.sqlite_dev_path.parts

    monkeypatch.setenv("APP_ENV", "staging")
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.STAGING
    assert settings.sqlite_dev_path.name == "dev.db"
    assert "app" in settings.sqlite_dev_path.parts

    monkeypatch.setenv("APP_ENV", "prod")
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.PROD
    assert settings.sqlite_dev_path.name == "prod.db"
    assert "app" in settings.sqlite_dev_path.parts


@pytest.mark.parametrize("invalid_env", ["foo", "", "DEV "])
def test_invalid_app_env_raises(monkeypatch: MonkeyPatch, invalid_env: str) -> None:
    """Should raise ValueError for invalid APP_ENV values."""
    monkeypatch.setenv("APP_ENV", invalid_env)
    with pytest.raises(ValueError):
        reload(config_mod)
        _ = config_mod.database_settings
