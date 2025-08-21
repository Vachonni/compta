"""
Unit tests for prepro.config.settings.

These tests verify environment variable handling, enum validation, and settings loading.
"""

from importlib import reload
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

import prepro.config.settings as config_mod
from prepro.config.settings import AppEnvEnum


def test_env_defaults_to_dev(monkeypatch: MonkeyPatch) -> None:
    """Should default to dev environment if APP_ENV is not set."""
    monkeypatch.delenv("APP_ENV", raising=False)
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.DEV


def test_env_variables_are_loaded(monkeypatch: MonkeyPatch) -> None:
    """Should load settings from environment variables correctly."""
    monkeypatch.setenv("APP_ENV", "dev")
    reload(config_mod)
    settings = config_mod.settings
    assert settings.app_env == AppEnvEnum.DEV
    assert settings.log_level == "DEBUG"


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
    with pytest.raises(ValueError):
        reload(config_mod)
        _ = config_mod.settings
