import sys
from types import SimpleNamespace

import pytest

import breadcrumb.config as config_module
from breadcrumb.config import (
    BreadcrumbConfig,
    DEFAULT_EXCLUDE,
    init,
    reset_config,
    shutdown,
)


class DummyIntegration:
    def __init__(self, backend, max_value_size):
        self.backend = backend
        self.max_value_size = max_value_size

    def start(self):
        pass

    def stop(self, timeout: float = 5.0):
        pass


class DummyBackend:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._active = False

    def start(self):
        self._active = True

    def stop(self):
        self._active = False

    def is_active(self):
        return self._active

    def get_events(self):
        return []


@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    """Ensure each test gets a clean config state."""
    monkeypatch.setattr(config_module, "_config", None)
    monkeypatch.setattr(config_module, "_backend_instance", None)
    monkeypatch.setattr(config_module, "_integration_instance", None)
    yield
    shutdown()
    reset_config()
    monkeypatch.setattr(config_module, "_config", None)
    monkeypatch.setattr(config_module, "_backend_instance", None)
    monkeypatch.setattr(config_module, "_integration_instance", None)


def test_breadcrumb_config_defaults():
    config = BreadcrumbConfig()
    assert config.enabled is True
    assert config.include == ["__main__"]
    assert config.exclude == DEFAULT_EXCLUDE
    assert config.sample_rate == 1.0
    assert config.max_repr_length == 2000
    summary = config.summary()
    assert "max_repr_length=2000" in summary
    assert "include=1 patterns" in summary
    assert f"exclude={len(DEFAULT_EXCLUDE)} patterns" in summary


def test_breadcrumb_config_validation():
    with pytest.raises(ValueError):
        BreadcrumbConfig(sample_rate=1.5)
    with pytest.raises(ValueError):
        BreadcrumbConfig(max_repr_length=0)
    with pytest.raises(TypeError):
        BreadcrumbConfig(include="not-a-list")
    with pytest.raises(TypeError):
        BreadcrumbConfig(exclude="not-a-list")


def test_breadcrumb_config_to_dict_includes_new_field():
    config = BreadcrumbConfig(max_repr_length=4000)
    config_dict = config.to_dict()
    assert config_dict["max_repr_length"] == 4000
    assert config_dict["exclude"] == DEFAULT_EXCLUDE


def test_init_propagates_max_repr(monkeypatch, tmp_path):
    captured = {}

    def fake_load_config_file():
        return {"db_path": str(tmp_path / "traces.duckdb")}

    monkeypatch.setattr(config_module, "_load_config_file", fake_load_config_file)
    monkeypatch.setattr(config_module, "_load_from_env", lambda: {})

    class BackendStub(DummyBackend):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            captured["backend_kwargs"] = kwargs

    fake_module = SimpleNamespace(PEP669Backend=BackendStub)
    monkeypatch.setitem(sys.modules, "breadcrumb.instrumentation.pep669_backend", fake_module)

    def fake_start_integration(backend, writer=None, db_path=None, max_value_size=None):
        captured["max_value_size"] = max_value_size
        return DummyIntegration(backend, max_value_size)

    fake_integration = SimpleNamespace(start_integration=fake_start_integration)
    monkeypatch.setitem(sys.modules, "breadcrumb.integration", fake_integration)

    config = init(max_repr_length=5000, silent=True)

    assert config.max_repr_length == 5000
    assert captured["backend_kwargs"]["max_repr_length"] == 5000
    assert captured["backend_kwargs"]["exclude_patterns"] == DEFAULT_EXCLUDE
    # Max value size should be at least 4x for nested structures, but never smaller than 1024
    assert captured["max_value_size"] == max(5000 * 4, 1024)


def test_init_uses_defaults_when_not_specified(monkeypatch):
    monkeypatch.setattr(config_module, "_load_config_file", lambda: {})
    monkeypatch.setattr(config_module, "_load_from_env", lambda: {})
    fake_module = SimpleNamespace(PEP669Backend=DummyBackend)
    monkeypatch.setitem(sys.modules, "breadcrumb.instrumentation.pep669_backend", fake_module)
    fake_integration = SimpleNamespace(
        start_integration=lambda backend, writer=None, db_path=None, max_value_size=None: DummyIntegration(backend, max_value_size)
    )
    monkeypatch.setitem(sys.modules, "breadcrumb.integration", fake_integration)

    config = init(silent=True)
    assert config.max_repr_length == 2000
    assert config.exclude == DEFAULT_EXCLUDE


def test_shutdown_handles_missing_backend(monkeypatch):
    # No backend started -> shutdown should be a no-op
    shutdown()
