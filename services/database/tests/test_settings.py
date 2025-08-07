"""
Unit tests for database_pkg.config.settings module.

These tests verify environment variable handling, enum validation, settings loading,
and property methods for path resolution.
"""

from importlib import reload
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

import database_pkg.config.settings as settings_mod
from database_pkg.config.schemas import AppEnvEnum


def test_env_defaults_to_local(monkeypatch: MonkeyPatch) -> None:
    """Should default to LOCAL environment if APP_ENV is not set."""
    monkeypatch.delenv("APP_ENV", raising=False)
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.app_env == AppEnvEnum.LOCAL


def test_env_variables_are_loaded(monkeypatch: MonkeyPatch) -> None:
    """Should load settings from environment variables correctly."""
    monkeypatch.setenv("APP_ENV", "dev")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.SERVICE_NAME == "database"
    assert settings.app_env == AppEnvEnum.DEV
    assert settings.log_level == "DEBUG"
    assert settings.databases_dir == settings.DATABASES_DIR_DOCKER
    assert settings.db_path == Path(settings.databases_dir) / "compta"
    assert settings.sqlite_path == settings.db_path / "SQL" / "dev.db"
    assert settings.excel_path == settings.blob_path / "Legacy" / "REVOLUT AVRIL 2025.xlsx"


def test_app_env_enum_variants(monkeypatch: MonkeyPatch) -> None:
    """Should correctly parse and validate all AppEnvEnum variants."""
    monkeypatch.setenv("APP_ENV", "local")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.app_env == AppEnvEnum.LOCAL
    assert settings.sqlite_path.name == "dev.db"
    assert "Users" in str(settings.sqlite_path)

    monkeypatch.setenv("APP_ENV", "staging")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.app_env == AppEnvEnum.STAGING
    assert settings.sqlite_path.name == "dev.db"
    assert "app" in str(settings.sqlite_path)

    monkeypatch.setenv("APP_ENV", "prod")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.app_env == AppEnvEnum.PROD
    assert settings.sqlite_path.name == "prod.db"
    assert "app" in str(settings.sqlite_path)


@pytest.mark.parametrize("invalid_env", ["foo", "", "DEV "])
def test_invalid_app_env_raises(monkeypatch: MonkeyPatch, invalid_env: str) -> None:
    """Should raise ValueError for invalid APP_ENV values."""
    monkeypatch.setenv("APP_ENV", invalid_env)
    with pytest.raises(ValueError):
        reload(settings_mod)
        _ = settings_mod.database_settings


def test_databases_dir_property(monkeypatch: MonkeyPatch) -> None:
    """Should return correct databases directory based on environment."""
    # Test LOCAL environment
    monkeypatch.setenv("APP_ENV", "local")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.databases_dir == settings.DATABASES_DIR_LOCAL
    assert "/Users/nicholas/Databases" in settings.databases_dir

    # Test non-LOCAL environment (DEV)
    monkeypatch.setenv("APP_ENV", "dev")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.databases_dir == settings.DATABASES_DIR_DOCKER
    assert "/app/DatabasesMount" in settings.databases_dir


def test_log_level_property(monkeypatch: MonkeyPatch) -> None:
    """Should return correct log level based on environment."""
    # Test PROD environment
    monkeypatch.setenv("APP_ENV", "prod")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.log_level == "INFO"

    # Test non-PROD environment (DEV)
    monkeypatch.setenv("APP_ENV", "dev")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.log_level == "DEBUG"

    # Test LOCAL environment
    monkeypatch.setenv("APP_ENV", "local")
    reload(settings_mod)
    settings = settings_mod.database_settings
    assert settings.log_level == "DEBUG"


def test_db_path_property(monkeypatch: MonkeyPatch) -> None:
    """Should return correct database path based on databases directory."""
    monkeypatch.setenv("APP_ENV", "local")
    reload(settings_mod)
    settings = settings_mod.database_settings
    expected_path = Path(settings.databases_dir) / "compta"
    assert settings.db_path == expected_path
    assert settings.db_path.name == "compta"


def test_blob_path_property(monkeypatch: MonkeyPatch) -> None:
    """Should return correct blob path based on environment."""
    # Test PROD environment
    monkeypatch.setenv("APP_ENV", "prod")
    reload(settings_mod)
    settings = settings_mod.database_settings
    expected_path = settings.db_path / "blob" / "prod"
    assert settings.blob_path == expected_path
    assert "prod" in str(settings.blob_path)

    # Test non-PROD environment (DEV)
    monkeypatch.setenv("APP_ENV", "dev")
    reload(settings_mod)
    settings = settings_mod.database_settings
    expected_path = settings.db_path / "blob" / "dev"
    assert settings.blob_path == expected_path
    assert "dev" in str(settings.blob_path)


def test_sqlite_path_property(monkeypatch: MonkeyPatch) -> None:
    """Should return correct SQLite path based on environment."""
    # Test PROD environment
    monkeypatch.setenv("APP_ENV", "prod")
    reload(settings_mod)
    settings = settings_mod.database_settings
    expected_path = settings.db_path / "SQL" / "prod.db"
    assert settings.sqlite_path == expected_path
    assert settings.sqlite_path.name == "prod.db"

    # Test non-PROD environment (DEV)
    monkeypatch.setenv("APP_ENV", "dev")
    reload(settings_mod)
    settings = settings_mod.database_settings
    expected_path = settings.db_path / "SQL" / "dev.db"
    assert settings.sqlite_path == expected_path
    assert settings.sqlite_path.name == "dev.db"


def test_excel_path_property(monkeypatch: MonkeyPatch) -> None:
    """Should return correct Excel path based on blob path."""
    monkeypatch.setenv("APP_ENV", "dev")
    reload(settings_mod)
    settings = settings_mod.database_settings
    expected_path = settings.blob_path / "Legacy" / "REVOLUT AVRIL 2025.xlsx"
    assert settings.excel_path == expected_path
    assert settings.excel_path.name == "REVOLUT AVRIL 2025.xlsx"
    assert "Legacy" in str(settings.excel_path)


def test_property_paths_consistency(monkeypatch: MonkeyPatch) -> None:
    """Should ensure all property paths are consistent with each other."""
    monkeypatch.setenv("APP_ENV", "staging")
    reload(settings_mod)
    settings = settings_mod.database_settings
    
    # Verify path hierarchy consistency
    assert settings.db_path == Path(settings.databases_dir) / "compta"
    assert settings.blob_path.parent.parent == settings.db_path
    assert settings.sqlite_path.parent.parent == settings.db_path
    assert settings.excel_path.parent.parent == settings.blob_path
