import pytest

from breadcrumb.instrumentation.pep669_backend import PEP669Backend


@pytest.mark.skipif(PEP669Backend is None, reason="PEP 669 backend unavailable")
def test_backend_captures_events():
    backend = PEP669Backend(include_patterns=[__name__], capture_lines=True)
    backend.start()

    def sample_function(x, y):
        return x + y

    sample_function(2, 3)

    backend.stop()
    events = backend.get_events()

    assert any(e.event_type == "call" and e.function_name == "sample_function" for e in events)
    assert any(e.event_type == "return" and e.function_name == "sample_function" for e in events)
    assert any(e.event_type == "line" for e in events)


@pytest.mark.skipif(PEP669Backend is None, reason="PEP 669 backend unavailable")
def test_max_repr_length_truncates_return_value():
    backend = PEP669Backend(include_patterns=[__name__], max_repr_length=50)
    backend.start()

    def make_payload():
        return "X" * 200

    make_payload()

    backend.stop()
    events = backend.get_events()
    returns = [e for e in events if e.event_type == "return" and e.function_name == "make_payload"]
    assert returns
    payload = returns[0].return_value
    assert isinstance(payload, str)
    assert len(payload) <= 53  # 50 chars + ellipsis
    assert payload.endswith("...")


@pytest.mark.skipif(PEP669Backend is None, reason="PEP 669 backend unavailable")
def test_max_repr_length_preserves_short_values():
    backend = PEP669Backend(include_patterns=[__name__], max_repr_length=2000)
    backend.start()

    def short_value():
        return "short string"

    short_value()

    backend.stop()
    events = backend.get_events()
    returns = [e for e in events if e.event_type == "return" and e.function_name == "short_value"]
    assert returns
    assert returns[0].return_value == "short string"


@pytest.mark.skipif(PEP669Backend is None, reason="PEP 669 backend unavailable")
def test_constructor_kwargs_captured():
    backend = PEP669Backend(include_patterns=[__name__])
    backend.start()

    class Demo:
        def __init__(self, **data):
            self.data = data

    Demo(color="red", size=42)

    backend.stop()

    events = backend.get_events()
    init_calls = [e for e in events if e.event_type == "call" and e.function_name.endswith("__init__")]
    assert init_calls
    kwargs = init_calls[0].kwargs or {}
    assert kwargs.get("color") == "red"
    assert kwargs.get("size") == 42
