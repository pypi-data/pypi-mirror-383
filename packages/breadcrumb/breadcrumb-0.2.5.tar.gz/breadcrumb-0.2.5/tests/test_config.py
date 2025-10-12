"""
Unit tests for breadcrumb configuration system.

Tests configuration resolution from Python API, environment variables, and defaults.
"""

import os
import pytest
from unittest.mock import patch

import breadcrumb
from breadcrumb.config import (
    BreadcrumbConfig,
    init,
    get_config,
    reset_config,
    _parse_bool_env,
    _parse_float_env,
    _load_from_env,
    ENV_ENABLED,
    ENV_DB_PATH,
    ENV_SAMPLE_RATE,
    DEFAULT_ENABLED,
    DEFAULT_DB_PATH,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_BACKEND,
)


@pytest.fixture(autouse=True)
def reset_config_before_each_test():
    """Reset config before each test."""
    reset_config()
    yield
    reset_config()


@pytest.fixture
def clean_env(monkeypatch):
    """Remove all Breadcrumb environment variables."""
    monkeypatch.delenv(ENV_ENABLED, raising=False)
    monkeypatch.delenv(ENV_DB_PATH, raising=False)
    monkeypatch.delenv(ENV_SAMPLE_RATE, raising=False)


class TestBreadcrumbConfig:
    """Test BreadcrumbConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = BreadcrumbConfig()

        assert config.enabled == DEFAULT_ENABLED
        assert config.include == ["**/*.py"]
        assert config.exclude == []
        assert config.sample_rate == DEFAULT_SAMPLE_RATE
        assert config.db_path == DEFAULT_DB_PATH
        assert config.backend == DEFAULT_BACKEND

    def test_custom_config(self):
        """Test custom configuration values."""
        config = BreadcrumbConfig(
            enabled=False,
            include=["src/**/*.py"],
            exclude=["tests/**"],
            sample_rate=0.5,
            db_path="/tmp/traces.db",
            backend="memory",
        )

        assert config.enabled is False
        assert config.include == ["src/**/*.py"]
        assert config.exclude == ["tests/**"]
        assert config.sample_rate == 0.5
        assert config.db_path == "/tmp/traces.db"
        assert config.backend == "memory"

    def test_sample_rate_validation(self):
        """Test sample_rate must be between 0.0 and 1.0."""
        # Valid values
        BreadcrumbConfig(sample_rate=0.0)
        BreadcrumbConfig(sample_rate=0.5)
        BreadcrumbConfig(sample_rate=1.0)

        # Invalid values
        with pytest.raises(ValueError, match="sample_rate must be between 0.0 and 1.0"):
            BreadcrumbConfig(sample_rate=-0.1)

        with pytest.raises(ValueError, match="sample_rate must be between 0.0 and 1.0"):
            BreadcrumbConfig(sample_rate=1.1)

    def test_backend_validation(self):
        """Test backend must be 'sqlite', 'memory', or 'pep669'."""
        # Valid values
        BreadcrumbConfig(backend="sqlite")
        BreadcrumbConfig(backend="memory")
        BreadcrumbConfig(backend="pep669")

        # Invalid value
        with pytest.raises(ValueError, match="backend must be 'sqlite', 'memory', or 'pep669'"):
            BreadcrumbConfig(backend="invalid")

    def test_include_type_validation(self):
        """Test include must be a list."""
        with pytest.raises(TypeError, match="include must be a list"):
            BreadcrumbConfig(include="not a list")

    def test_exclude_type_validation(self):
        """Test exclude must be a list."""
        with pytest.raises(TypeError, match="exclude must be a list"):
            BreadcrumbConfig(exclude="not a list")

    def test_summary_enabled(self):
        """Test summary for enabled configuration."""
        config = BreadcrumbConfig(
            enabled=True,
            backend="sqlite",
            db_path="/tmp/test.db",
            sample_rate=0.75,
            include=["a", "b"],
            exclude=["c"],
        )

        summary = config.summary()
        assert "enabled" in summary
        assert "backend=sqlite" in summary
        assert "db=/tmp/test.db" in summary
        assert "sample_rate=0.75" in summary
        assert "include=2" in summary
        assert "exclude=1" in summary

    def test_summary_disabled(self):
        """Test summary for disabled configuration."""
        config = BreadcrumbConfig(enabled=False)

        summary = config.summary()
        assert "disabled" in summary

    def test_summary_memory_backend(self):
        """Test summary for memory backend (no db path)."""
        config = BreadcrumbConfig(backend="memory")

        summary = config.summary()
        assert "backend=memory" in summary
        # Should not include db path for memory backend
        assert "db=" not in summary


class TestEnvironmentParsing:
    """Test environment variable parsing."""

    def test_parse_bool_env_true_values(self):
        """Test parsing boolean true values."""
        true_values = ["1", "true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"]
        for value in true_values:
            assert _parse_bool_env(value) is True

    def test_parse_bool_env_false_values(self):
        """Test parsing boolean false values."""
        false_values = ["0", "false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF"]
        for value in false_values:
            assert _parse_bool_env(value) is False

    def test_parse_bool_env_invalid_values(self):
        """Test parsing invalid boolean values."""
        with pytest.raises(ValueError, match="Invalid boolean value"):
            _parse_bool_env("invalid")

    def test_parse_float_env_valid_values(self):
        """Test parsing valid float values."""
        assert _parse_float_env("0.0") == 0.0
        assert _parse_float_env("0.5") == 0.5
        assert _parse_float_env("1.0") == 1.0
        assert _parse_float_env("0.123") == 0.123

    def test_parse_float_env_invalid_values(self):
        """Test parsing invalid float values."""
        with pytest.raises(ValueError, match="Invalid float value"):
            _parse_float_env("not a number")


class TestLoadFromEnv:
    """Test loading configuration from environment variables."""

    def test_load_from_env_empty(self, clean_env):
        """Test loading from environment with no variables set."""
        config = _load_from_env()
        assert config == {}

    def test_load_from_env_enabled(self, monkeypatch):
        """Test loading BREADCRUMB_ENABLED."""
        monkeypatch.setenv(ENV_ENABLED, "false")
        config = _load_from_env()
        assert config["enabled"] is False

    def test_load_from_env_db_path(self, monkeypatch):
        """Test loading BREADCRUMB_DB_PATH."""
        monkeypatch.setenv(ENV_DB_PATH, "/custom/path.db")
        config = _load_from_env()
        assert config["db_path"] == "/custom/path.db"

    def test_load_from_env_sample_rate(self, monkeypatch):
        """Test loading BREADCRUMB_SAMPLE_RATE."""
        monkeypatch.setenv(ENV_SAMPLE_RATE, "0.25")
        config = _load_from_env()
        assert config["sample_rate"] == 0.25

    def test_load_from_env_all_variables(self, monkeypatch):
        """Test loading all environment variables."""
        monkeypatch.setenv(ENV_ENABLED, "true")
        monkeypatch.setenv(ENV_DB_PATH, "/test/db.sqlite")
        monkeypatch.setenv(ENV_SAMPLE_RATE, "0.8")

        config = _load_from_env()
        assert config["enabled"] is True
        assert config["db_path"] == "/test/db.sqlite"
        assert config["sample_rate"] == 0.8


class TestInitFunction:
    """Test init() function."""

    def test_init_defaults(self, clean_env):
        """Test init with default values."""
        config = init(silent=True)

        assert config.enabled == DEFAULT_ENABLED
        assert config.include == ["**/*.py"]
        assert config.exclude == []
        assert config.sample_rate == DEFAULT_SAMPLE_RATE
        assert config.db_path == DEFAULT_DB_PATH
        assert config.backend == DEFAULT_BACKEND

    def test_init_with_python_api(self, clean_env):
        """Test init with Python API parameters."""
        config = init(
            enabled=False,
            include=["src/**/*.py"],
            exclude=["tests/**"],
            sample_rate=0.5,
            db_path="/tmp/test.db",
            backend="memory",
            silent=True,
        )

        assert config.enabled is False
        assert config.include == ["src/**/*.py"]
        assert config.exclude == ["tests/**"]
        assert config.sample_rate == 0.5
        assert config.db_path == "/tmp/test.db"
        assert config.backend == "memory"

    def test_init_with_env_vars(self, monkeypatch):
        """Test init with environment variables."""
        monkeypatch.setenv(ENV_ENABLED, "false")
        monkeypatch.setenv(ENV_DB_PATH, "/env/path.db")
        monkeypatch.setenv(ENV_SAMPLE_RATE, "0.3")

        config = init(silent=True)

        assert config.enabled is False
        assert config.db_path == "/env/path.db"
        assert config.sample_rate == 0.3

    def test_init_precedence_python_over_env(self, monkeypatch):
        """Test Python API takes precedence over environment variables."""
        # Set environment variables
        monkeypatch.setenv(ENV_ENABLED, "false")
        monkeypatch.setenv(ENV_DB_PATH, "/env/path.db")
        monkeypatch.setenv(ENV_SAMPLE_RATE, "0.5")

        # Python API should override
        config = init(
            enabled=True,
            db_path="/python/path.db",
            sample_rate=0.1,
            silent=True,
        )

        assert config.enabled is True
        assert config.db_path == "/python/path.db"
        assert config.sample_rate == 0.1

    def test_init_precedence_partial_override(self, monkeypatch):
        """Test partial override - some from env, some from Python API."""
        monkeypatch.setenv(ENV_ENABLED, "false")
        monkeypatch.setenv(ENV_SAMPLE_RATE, "0.7")

        # Only override sample_rate, enabled should come from env
        config = init(sample_rate=0.2, silent=True)

        assert config.enabled is False  # from env
        assert config.sample_rate == 0.2  # from Python API

    def test_init_prints_summary(self, clean_env, capsys):
        """Test init prints summary message."""
        config = init()  # silent=False by default

        captured = capsys.readouterr()
        assert "Breadcrumb enabled" in captured.out

    def test_init_silent_mode(self, clean_env, capsys):
        """Test init with silent=True suppresses output."""
        config = init(silent=True)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_init_sets_global_config(self, clean_env):
        """Test init sets global config."""
        assert get_config() is None

        config = init(silent=True)

        assert get_config() is not None
        assert get_config() is config

    def test_init_validation_errors(self, clean_env):
        """Test init raises errors for invalid configuration."""
        with pytest.raises(ValueError, match="sample_rate must be between 0.0 and 1.0"):
            init(sample_rate=2.0, silent=True)

        with pytest.raises(ValueError, match="backend must be 'sqlite', 'memory', or 'pep669'"):
            init(backend="invalid", silent=True)


class TestGetConfig:
    """Test get_config() function."""

    def test_get_config_before_init(self):
        """Test get_config returns None before init."""
        assert get_config() is None

    def test_get_config_after_init(self, clean_env):
        """Test get_config returns config after init."""
        config = init(silent=True)
        assert get_config() is config


class TestResetConfig:
    """Test reset_config() function."""

    def test_reset_config(self, clean_env):
        """Test reset_config clears global config."""
        init(silent=True)
        assert get_config() is not None

        reset_config()
        assert get_config() is None


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""

    def test_validation_code_from_plan(self, monkeypatch):
        """Test the validation code from PLAN.md."""
        # Set environment variable
        monkeypatch.setenv(ENV_SAMPLE_RATE, "0.5")

        # Python API should override
        config = init(sample_rate=0.1, silent=True)

        # Verify sample_rate = 0.1 (Python API wins)
        assert config.sample_rate == 0.1

    def test_typical_usage_minimal(self, clean_env):
        """Test typical usage with minimal configuration."""
        config = init(silent=True)

        assert config.enabled is True
        assert config.sample_rate == 1.0

    def test_typical_usage_custom_paths(self, clean_env):
        """Test typical usage with custom include/exclude."""
        config = init(
            include=["src/**/*.py", "lib/**/*.py"],
            exclude=["tests/**", "**/*_test.py"],
            silent=True,
        )

        assert len(config.include) == 2
        assert len(config.exclude) == 2

    def test_typical_usage_sampling(self, clean_env):
        """Test typical usage with sampling for production."""
        config = init(
            sample_rate=0.1,  # 10% sampling
            db_path="/var/log/breadcrumb/traces.db",
            silent=True,
        )

        assert config.sample_rate == 0.1
        assert config.db_path == "/var/log/breadcrumb/traces.db"

    def test_typical_usage_memory_backend(self, clean_env):
        """Test typical usage with memory backend for testing."""
        config = init(
            backend="memory",
            silent=True,
        )

        assert config.backend == "memory"

    def test_disabled_via_env(self, monkeypatch):
        """Test disabling tracing via environment variable."""
        monkeypatch.setenv(ENV_ENABLED, "false")

        config = init(silent=True)

        assert config.enabled is False

    def test_multiple_init_calls(self, clean_env):
        """Test calling init multiple times updates config."""
        config1 = init(sample_rate=0.5, silent=True)
        assert config1.sample_rate == 0.5

        config2 = init(sample_rate=0.8, silent=True)
        assert config2.sample_rate == 0.8

        # Global config should be updated
        assert get_config().sample_rate == 0.8


class TestBreadcrumbPublicAPI:
    """Test public API exports."""

    def test_public_api_exports(self):
        """Test that public API is correctly exported."""
        assert hasattr(breadcrumb, "init")
        assert hasattr(breadcrumb, "get_config")
        assert hasattr(breadcrumb, "reset_config")
        assert hasattr(breadcrumb, "BreadcrumbConfig")

    def test_import_from_breadcrumb(self, clean_env):
        """Test importing and using breadcrumb.init()."""
        import breadcrumb

        config = breadcrumb.init(sample_rate=0.6, silent=True)
        assert config.sample_rate == 0.6

        retrieved_config = breadcrumb.get_config()
        assert retrieved_config.sample_rate == 0.6

        breadcrumb.reset_config()
        assert breadcrumb.get_config() is None
