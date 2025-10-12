"""
Unit tests for sys.settrace fallback backend.

These tests verify that the settrace backend correctly captures:
- Function calls with arguments
- Function returns with return values
- Line-level execution (when enabled)
- Exceptions with stack traces
- Thread-safe operation
"""

import sys
import pytest
import threading
import time
from datetime import datetime, timezone
from breadcrumb.instrumentation.settrace_backend import (
    SettraceBackend,
    TraceEvent,
    ThreadLocalContext,
    is_supported,
    create_backend,
)


class TestThreadLocalContext:
    """Tests for ThreadLocalContext class."""

    def test_trace_id_isolation_between_threads(self):
        """Test that trace IDs are isolated between threads."""
        context = ThreadLocalContext()
        results = {}

        def worker(thread_id: int):
            context.trace_id = f"trace-{thread_id}"
            time.sleep(0.01)  # Let other threads run
            results[thread_id] = context.trace_id

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each thread should have its own trace ID
        assert len(results) == 5
        for i in range(5):
            assert results[i] == f"trace-{i}"

    def test_events_isolation_between_threads(self):
        """Test that event lists are isolated between threads."""
        context = ThreadLocalContext()
        results = {}

        def worker(thread_id: int):
            event = TraceEvent(
                event_type="call",
                timestamp=datetime.now(timezone.utc) if sys.version_info >= (3, 11) else datetime.utcnow(),
                thread_id=thread_id,
                function_name=f"func_{thread_id}",
                module="test",
                filename="test.py",
                line_number=1,
            )
            context.events.append(event)
            time.sleep(0.01)
            results[thread_id] = len(context.events)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each thread should have exactly 1 event
        for i in range(5):
            assert results[i] == 1

    def test_clear_context(self):
        """Test clearing thread-local context."""
        context = ThreadLocalContext()
        context.trace_id = "test-trace"
        context.events.append(
            TraceEvent(
                event_type="call",
                timestamp=datetime.now(timezone.utc) if sys.version_info >= (3, 11) else datetime.utcnow(),
                thread_id=1,
                function_name="test",
                module="test",
                filename="test.py",
                line_number=1,
            )
        )

        context.clear()

        assert context.trace_id is None
        assert len(context.events) == 0


class TestSettraceBackend:
    """Tests for SettraceBackend class."""

    def test_initialization_with_defaults(self):
        """Test backend initialization with default parameters."""
        backend = SettraceBackend()

        assert backend.callback is None
        assert backend.include_patterns == ['*']
        assert len(backend.exclude_patterns) > 0
        assert backend.capture_locals is True
        assert backend.capture_lines is False
        assert backend._enabled is False

    def test_initialization_with_custom_parameters(self):
        """Test backend initialization with custom parameters."""

        def callback(event):
            pass

        backend = SettraceBackend(
            callback=callback,
            include_patterns=['myapp.*'],
            exclude_patterns=['myapp.vendor.*'],
            capture_locals=False,
            capture_lines=True,
        )

        assert backend.callback == callback
        assert backend.include_patterns == ['myapp.*']
        assert 'myapp.vendor.*' in backend.exclude_patterns
        assert backend.capture_locals is False
        assert backend.capture_lines is True

    def test_pattern_matching_wildcard(self):
        """Test pattern matching with wildcard."""
        backend = SettraceBackend(include_patterns=['*'])

        assert backend._match_pattern('any.module', '*') is True
        assert backend._match_pattern('', '*') is True

    def test_pattern_matching_prefix(self):
        """Test pattern matching with prefix pattern."""
        backend = SettraceBackend()

        assert backend._match_pattern('myapp.core', 'myapp.*') is True
        assert backend._match_pattern('myapp.utils.helpers', 'myapp.*') is True
        assert backend._match_pattern('otherapp.core', 'myapp.*') is False

    def test_pattern_matching_exact(self):
        """Test pattern matching with exact match."""
        backend = SettraceBackend()

        assert backend._match_pattern('myapp', 'myapp') is True
        assert backend._match_pattern('myapp.core', 'myapp') is False

    def test_trace_function_call_event(self):
        """Test capturing function call events."""
        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        def test_function(a, b):
            return a + b

        result = test_function(2, 3)
        backend.stop()

        events = backend.get_events()
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_function']

        assert len(call_events) > 0
        call_event = call_events[0]
        assert call_event.function_name == 'test_function'
        assert 'a' in call_event.locals or 'b' in call_event.locals  # locals captured

    def test_trace_function_return_event(self):
        """Test capturing function return events."""
        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        def test_function(a, b):
            return a + b

        result = test_function(2, 3)
        backend.stop()

        events = backend.get_events()
        return_events = [e for e in events if e.event_type == 'return' and e.function_name == 'test_function']

        assert len(return_events) > 0
        return_event = return_events[0]
        assert return_event.function_name == 'test_function'
        assert return_event.return_value == 5

    def test_trace_exception_event(self):
        """Test capturing exception events."""
        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        def test_function():
            raise ValueError("Test error")

        try:
            test_function()
        except ValueError:
            pass

        backend.stop()

        events = backend.get_events()
        exception_events = [e for e in events if e.event_type == 'exception' and e.function_name == 'test_function']

        assert len(exception_events) > 0
        exc_event = exception_events[0]
        assert exc_event.exception is not None
        assert exc_event.exception['type'] == 'ValueError'
        assert 'Test error' in exc_event.exception['message']

    def test_trace_line_events_when_enabled(self):
        """Test capturing line events when enabled."""
        backend = SettraceBackend(
            include_patterns=['*'],
            capture_lines=True
        )
        backend.start()

        def test_function():
            x = 1
            y = 2
            return x + y

        result = test_function()
        backend.stop()

        events = backend.get_events()
        line_events = [e for e in events if e.event_type == 'line' and e.function_name == 'test_function']

        # Should have multiple line events
        assert len(line_events) > 0

    def test_trace_line_events_when_disabled(self):
        """Test that line events are not captured when disabled."""
        backend = SettraceBackend(
            include_patterns=['*'],
            capture_lines=False
        )
        backend.start()

        def test_function():
            x = 1
            y = 2
            return x + y

        result = test_function()
        backend.stop()

        events = backend.get_events()
        line_events = [e for e in events if e.event_type == 'line']

        # Should have no line events
        assert len(line_events) == 0

    def test_exclude_patterns_prevent_tracing(self):
        """Test that exclude patterns prevent tracing."""
        backend = SettraceBackend(
            include_patterns=['*'],
            exclude_patterns=['test_module.*']
        )

        # Create a mock frame with test_module
        class MockCode:
            co_name = 'test_func'
            co_filename = 'test.py'

        class MockFrame:
            f_code = MockCode()
            f_globals = {'__name__': 'test_module.submodule'}

        should_trace = backend._should_trace(MockFrame())
        assert should_trace is False

    def test_include_patterns_enable_tracing(self):
        """Test that include patterns enable tracing."""
        backend = SettraceBackend(
            include_patterns=['myapp.*'],
            exclude_patterns=['threading']
        )

        class MockCode:
            co_name = 'test_func'
            co_filename = 'test.py'

        class MockFrame:
            f_code = MockCode()
            f_globals = {'__name__': 'myapp.core'}

        should_trace = backend._should_trace(MockFrame())
        assert should_trace is True

    def test_callback_invoked_on_events(self):
        """Test that callback is invoked for each event."""
        captured_events = []

        def callback(event: TraceEvent):
            captured_events.append(event)

        backend = SettraceBackend(
            callback=callback,
            include_patterns=['*']
        )
        backend.start()

        def test_function():
            return 42

        result = test_function()
        backend.stop()

        # Callback should have been called
        test_events = [e for e in captured_events if e.function_name == 'test_function']
        assert len(test_events) > 0
        assert any(e.event_type == 'call' for e in test_events)

    def test_clear_events(self):
        """Test clearing events."""
        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        def test_function():
            return 42

        test_function()
        backend.stop()

        events = [e for e in backend.get_events() if e.function_name == 'test_function']
        assert len(events) > 0

        backend.clear_events()
        assert len(backend.get_events()) == 0

    def test_safe_repr_simple_types(self):
        """Test safe repr for simple types."""
        backend = SettraceBackend()

        assert backend._safe_repr(None) is None
        assert backend._safe_repr(True) is True
        assert backend._safe_repr(42) == 42
        assert backend._safe_repr(3.14) == 3.14
        assert backend._safe_repr("hello") == "hello"

    def test_safe_repr_collections(self):
        """Test safe repr for collections."""
        backend = SettraceBackend()

        # List
        result = backend._safe_repr([1, 2, 3])
        assert result == [1, 2, 3]

        # Dict
        result = backend._safe_repr({'a': 1, 'b': 2})
        assert result == {'a': 1, 'b': 2}

        # Tuple
        result = backend._safe_repr((1, 2, 3))
        assert isinstance(result, list)

    def test_safe_repr_truncation(self):
        """Test safe repr truncates long strings."""
        backend = SettraceBackend()

        long_string = 'x' * 2000
        result = backend._safe_repr(long_string, max_length=100)

        # For simple strings, they're returned as-is if they're simple types
        # For complex objects, repr is used and truncated
        assert isinstance(result, str)
        # Since 'x' * 2000 is a simple string, it returns the full string
        # Let's test with a complex object instead
        class LongRepr:
            def __repr__(self):
                return 'x' * 2000

        obj = LongRepr()
        result = backend._safe_repr(obj, max_length=100)
        assert isinstance(result, str)
        assert len(result) <= 120  # 100 + '[TRUNCATED]'
        assert '[TRUNCATED]' in result

    def test_safe_repr_complex_objects(self):
        """Test safe repr for complex objects."""
        backend = SettraceBackend()

        class CustomObject:
            def __repr__(self):
                return "<CustomObject>"

        obj = CustomObject()
        result = backend._safe_repr(obj)
        assert result == "<CustomObject>"

    def test_thread_safety(self):
        """Test that tracing is thread-safe."""
        backend = SettraceBackend(include_patterns=['*'])
        results = {}

        def worker(thread_id: int):
            backend.start()

            def test_function(x):
                return x * 2

            result = test_function(thread_id)

            events = backend.get_events()
            backend.stop()

            test_events = [e for e in events if e.function_name == 'test_function' and e.event_type == 'call']
            results[thread_id] = len(test_events)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each thread should have captured events independently
        for i in range(3):
            assert results[i] > 0

    def test_capture_locals_disabled(self):
        """Test that locals are not captured when disabled."""
        backend = SettraceBackend(
            include_patterns=['*'],
            capture_locals=False
        )
        backend.start()

        def test_function(a, b):
            c = a + b
            return c

        test_function(2, 3)
        backend.stop()

        events = backend.get_events()
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_function']

        # Locals should be empty or minimal
        for event in call_events:
            assert len(event.locals) == 0

    def test_timestamp_accuracy(self):
        """Test that timestamps are captured accurately."""
        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        before = datetime.now(timezone.utc) if sys.version_info >= (3, 11) else datetime.utcnow()

        def test_function():
            return 42

        test_function()
        backend.stop()

        after = datetime.now(timezone.utc) if sys.version_info >= (3, 11) else datetime.utcnow()

        events = backend.get_events()
        test_events = [e for e in events if e.function_name == 'test_function']
        for event in test_events:
            assert before <= event.timestamp <= after

    def test_thread_id_captured(self):
        """Test that thread ID is captured correctly."""
        backend = SettraceBackend(include_patterns=['*'])
        result_container = []

        def worker():
            backend.start()

            def test_function():
                return 42

            test_function()
            events = backend.get_events()
            backend.stop()

            # Filter to only test_function events
            test_events = [e for e in events if e.function_name == 'test_function']

            # All events should have the same thread ID
            thread_ids = {e.thread_id for e in test_events}
            result_container.append({
                'thread_ids': thread_ids,
                'current_thread': threading.get_ident(),
                'event_count': len(test_events)
            })

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        # Check results from thread
        assert len(result_container) == 1
        result = result_container[0]
        assert result['event_count'] > 0
        assert len(result['thread_ids']) == 1
        assert list(result['thread_ids'])[0] == result['current_thread']


class TestModuleFunctions:
    """Tests for module-level utility functions."""

    def test_is_supported_python_312(self):
        """Test is_supported returns False for Python 3.12+."""
        # This test runs on Python 3.12+, so should return False
        if sys.version_info >= (3, 12):
            assert is_supported() is False
        elif sys.version_info.major == 3 and sys.version_info.minor in (10, 11):
            assert is_supported() is True

    def test_create_backend_success(self):
        """Test creating backend succeeds on supported versions."""
        backend = create_backend()
        assert isinstance(backend, SettraceBackend)

    def test_create_backend_with_parameters(self):
        """Test creating backend with custom parameters."""
        backend = create_backend(
            include_patterns=['myapp.*'],
            capture_lines=True
        )
        assert backend.include_patterns == ['myapp.*']
        assert backend.capture_lines is True


class TestOverheadWarning:
    """Tests for overhead warning functionality."""

    def test_warning_printed_on_first_start(self, capsys):
        """Test that overhead warning is printed on first start."""
        backend = SettraceBackend(include_patterns=['*'])

        # Warning should not be printed yet
        backend._warned = False

        backend.start()

        captured = capsys.readouterr()
        assert 'WARNING' in captured.err
        assert '2000%+' in captured.err
        assert 'PEP 669' in captured.err

        backend.stop()

    def test_warning_printed_only_once(self, capsys):
        """Test that overhead warning is printed only once."""
        backend = SettraceBackend(include_patterns=['*'])
        backend._warned = False

        backend.start()
        backend.stop()

        # Clear captured output
        capsys.readouterr()

        backend.start()
        backend.stop()

        # Should not print warning again
        captured = capsys.readouterr()
        assert 'WARNING' not in captured.err


class TestIntegration:
    """Integration tests for realistic scenarios."""

    def test_trace_recursive_function(self):
        """Test tracing a recursive function."""
        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)

        result = factorial(5)
        backend.stop()

        events = backend.get_events()
        call_events = [
            e for e in events
            if e.event_type == 'call' and e.function_name == 'factorial'
        ]

        # Should have 5 call events (one for each recursion)
        assert len(call_events) == 5
        assert result == 120

    def test_trace_nested_function_calls(self):
        """Test tracing nested function calls."""
        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        def outer(x):
            def inner(y):
                return y * 2

            return inner(x) + 1

        result = outer(5)
        backend.stop()

        events = backend.get_events()
        call_events = [e for e in events if e.event_type == 'call']

        # Should have calls to both outer and inner
        function_names = {e.function_name for e in call_events}
        assert 'outer' in function_names
        assert 'inner' in function_names
        assert result == 11

    def test_trace_async_function(self):
        """Test tracing async functions (basic support)."""
        import asyncio

        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        async def async_function(x):
            await asyncio.sleep(0.001)
            return x * 2

        result = asyncio.run(async_function(5))
        backend.stop()

        events = backend.get_events()
        call_events = [
            e for e in events
            if e.function_name == 'async_function'
        ]

        # Should have captured the async function call
        assert len(call_events) > 0
        assert result == 10

    def test_trace_with_multiple_exceptions(self):
        """Test tracing functions that raise multiple exceptions."""
        backend = SettraceBackend(include_patterns=['*'])
        backend.start()

        def test_function(should_raise):
            if should_raise == 'value':
                raise ValueError("Value error")
            elif should_raise == 'type':
                raise TypeError("Type error")
            return "success"

        results = []
        for error_type in ['value', 'type', None]:
            try:
                results.append(test_function(error_type))
            except Exception:
                pass

        backend.stop()

        events = backend.get_events()
        exception_events = [e for e in events if e.event_type == 'exception' and e.function_name == 'test_function']

        # Should have captured both exceptions
        assert len(exception_events) >= 2
        exception_types = {e.exception['type'] for e in exception_events}
        assert 'ValueError' in exception_types
        assert 'TypeError' in exception_types
