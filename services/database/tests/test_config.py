"""
Unit tests for database_pkg.config module.

These tests verify environment variable handling, enum validation, and settings loading.
"""

import pytest
from importlib import reload
from database_pkg.config import AppEnvEnum
import database_pkg.config as config_mod


def test_env_defaults_to_dev(monkeypatch, tmp_path):
    """Should default to DEV environment if APP_ENV is not set."""
    monkeypatch.delenv("APP_ENV", raising=False)
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.DEV


def test_env_variables_are_loaded(monkeypatch, tmp_path):
    """Should load settings from environment variables correctly."""
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("DATABASES_DIR", str(tmp_path))
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.DEV
    assert settings.databases_dir == str(tmp_path)
    assert settings.db_path == tmp_path / "compta"
    assert settings.sqlite_dev_path == tmp_path / "compta" / "SQL" / "dev.db"
    assert settings.table_name == "transactions"
    assert (
        settings.excel_path
        == tmp_path / "compta" / "Blob" / "Legacy" / "REVOLUT AVRIL 2025.xlsx"
    )


def test_app_env_enum_variants(monkeypatch):
    """Should correctly parse and validate all AppEnvEnum variants."""
    monkeypatch.setenv("APP_ENV", "dev")
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.DEV
    assert settings.sqlite_dev_path.name == "dev.db"
    assert settings.sqlite_dev_path.name == f"{settings.app_env.value}.db"
    assert "Users" in settings.sqlite_dev_path.parts

    monkeypatch.setenv("APP_ENV", "prod")
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.PROD
    assert settings.sqlite_dev_path.name == "prod.db"
    assert "app" in settings.sqlite_dev_path.parts

    monkeypatch.setenv("APP_ENV", "staging")
    reload(config_mod)
    settings = config_mod.database_settings
    assert settings.app_env == AppEnvEnum.STAGING
    assert settings.sqlite_dev_path.name == "staging.db"
    assert "app" in settings.sqlite_dev_path.parts


@pytest.mark.parametrize("invalid_env", ["foo", "", "DEV "])
def test_invalid_app_env_raises(monkeypatch, invalid_env):
    """Should raise ValueError for invalid APP_ENV values."""
    monkeypatch.setenv("APP_ENV", invalid_env)
    monkeypatch.setenv("DATABASES_DIR", "/tmp")
    with pytest.raises(ValueError):
        reload(config_mod)
        _ = config_mod.database_settings
