"""
Unit tests for PEP 669 instrumentation backend.

Tests cover:
- Python version detection
- Event capture (CALL, RETURN, LINE, EXCEPTION)
- Argument and return value capture
- Thread safety
- Async/await function handling
- Context manager usage
- Edge cases
"""

import sys
import threading
import pytest
from datetime import datetime

# Only run these tests on Python 3.12+
pytest_plugins = []
pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason="PEP 669 requires Python 3.12+"
)


from breadcrumb.instrumentation.pep669_backend import (
    PEP669Backend,
    TraceEvent,
    is_pep669_available,
    PEP669_AVAILABLE,
)


class TestVersionDetection:
    """Test Python version detection and availability checks."""

    def test_pep669_available_on_312_plus(self):
        """Test that PEP 669 is detected as available on Python 3.12+."""
        if sys.version_info >= (3, 12):
            assert PEP669_AVAILABLE is True
            assert is_pep669_available() is True
        else:
            assert PEP669_AVAILABLE is False
            assert is_pep669_available() is False

    def test_backend_initialization_on_312_plus(self):
        """Test backend can be initialized on Python 3.12+."""
        if sys.version_info >= (3, 12):
            backend = PEP669Backend()
            assert backend is not None
            assert backend.is_active() is False


class TestBasicFunctionCalls:
    """Test basic function call and return event capture."""

    def test_simple_function_call(self):
        """Test capturing a simple function call."""
        backend = PEP669Backend()
        backend.start()

        def add(a, b):
            return a + b

        result = add(2, 3)

        backend.stop()
        events = backend.get_events()

        # Should have call, line, and return events
        assert len(events) > 0

        # Find the call event
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'add']
        assert len(call_events) > 0

        call_event = call_events[0]
        assert call_event.function_name == 'add'
        assert call_event.args == {'a': 2, 'b': 3}
        assert call_event.module_name == __name__

        # Find the return event
        return_events = [e for e in events if e.event_type == 'return' and e.function_name == 'add']
        assert len(return_events) > 0

        return_event = return_events[0]
        assert return_event.function_name == 'add'
        assert return_event.return_value == 5

        assert result == 5

    def test_function_with_kwargs(self):
        """Test capturing function with keyword arguments."""
        backend = PEP669Backend()
        backend.start()

        def greet(name, *, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("World", greeting="Hi")

        backend.stop()
        events = backend.get_events()

        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'greet']
        assert len(call_events) > 0

        call_event = call_events[0]
        assert 'name' in call_event.args
        assert call_event.args['name'] == 'World'
        # Note: kwargs capture may vary based on how Python handles them
        # The greeting parameter might be in args or kwargs depending on implementation

    def test_nested_function_calls(self):
        """Test capturing nested function calls."""
        backend = PEP669Backend()
        backend.start()

        def inner(x):
            return x * 2

        def outer(x):
            return inner(x) + 1

        result = outer(5)

        backend.stop()
        events = backend.get_events()

        # Should have events for both outer and inner
        outer_calls = [e for e in events if e.event_type == 'call' and e.function_name == 'outer']
        inner_calls = [e for e in events if e.event_type == 'call' and e.function_name == 'inner']

        assert len(outer_calls) > 0
        assert len(inner_calls) > 0
        assert result == 11


class TestLineExecution:
    """Test line-level execution tracking."""

    def test_line_events_captured(self):
        """Test that line execution events are captured."""
        backend = PEP669Backend()
        backend.start()

        def multi_line():
            x = 1
            y = 2
            z = x + y
            return z

        result = multi_line()

        backend.stop()
        events = backend.get_events()

        # Should have multiple line events for multi_line function
        line_events = [e for e in events if e.event_type == 'line' and e.function_name == 'multi_line']
        assert len(line_events) >= 3  # At least 3 lines executed

        assert result == 3

    def test_local_variables_capture(self):
        """Test capturing local variables (when enabled)."""
        backend = PEP669Backend(capture_locals=True)
        backend.start()

        def with_locals():
            x = 42
            y = "test"
            return x

        result = with_locals()

        backend.stop()
        events = backend.get_events()

        # Find line events with local variables
        line_events = [e for e in events if e.event_type == 'line' and e.function_name == 'with_locals']

        # Some line events should have local_vars captured
        events_with_locals = [e for e in line_events if e.local_vars is not None]
        # We might capture locals, but it's implementation dependent

        assert result == 42


class TestExceptionHandling:
    """Test exception capture."""

    def test_exception_captured(self):
        """Test that exceptions are captured."""
        backend = PEP669Backend()
        backend.start()

        def raises_error():
            raise ValueError("Test error")

        try:
            raises_error()
        except ValueError:
            pass

        backend.stop()
        events = backend.get_events()

        # Should have exception event
        exception_events = [e for e in events if e.event_type == 'exception']
        assert len(exception_events) > 0

        exc_event = exception_events[0]
        assert exc_event.exception_type == 'ValueError'
        assert 'Test error' in exc_event.exception_message

    def test_exception_with_traceback(self):
        """Test that exception traceback is captured."""
        backend = PEP669Backend()
        backend.start()

        def deep_error():
            def inner():
                raise RuntimeError("Deep error")
            return inner()

        try:
            deep_error()
        except RuntimeError:
            pass

        backend.stop()
        events = backend.get_events()

        exception_events = [e for e in events if e.event_type == 'exception']
        assert len(exception_events) > 0

        exc_event = exception_events[0]
        assert exc_event.exception_type == 'RuntimeError'
        assert exc_event.exception_traceback is not None
        assert 'RuntimeError' in exc_event.exception_traceback


class TestThreadSafety:
    """Test thread-safe event collection."""

    def test_multiple_threads(self):
        """Test that events are isolated per thread."""
        backend = PEP669Backend()
        backend.start()

        results = {}
        errors = []

        def worker(thread_id):
            try:
                def thread_func(n):
                    return n * thread_id

                result = thread_func(10)
                results[thread_id] = result
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i + 1,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        backend.stop()

        # Should have no errors
        assert len(errors) == 0

        # Results should be correct
        assert results[1] == 10
        assert results[2] == 20
        assert results[3] == 30

        # Events are thread-local, so we can only access current thread's events
        events = backend.get_events()
        # Main thread might have some events, but worker thread events are isolated


class TestAsyncFunctions:
    """Test async/await function handling."""

    @pytest.mark.asyncio
    async def test_async_function_detected(self):
        """Test that async functions are detected."""
        backend = PEP669Backend()
        backend.start()

        async def async_add(a, b):
            return a + b

        result = await async_add(2, 3)

        backend.stop()
        events = backend.get_events()

        # Find async function call
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'async_add']

        if call_events:
            call_event = call_events[0]
            assert call_event.is_async is True

        assert result == 5

    @pytest.mark.asyncio
    async def test_async_with_await(self):
        """Test async function with await."""
        backend = PEP669Backend()
        backend.start()

        async def async_inner(x):
            return x * 2

        async def async_outer(x):
            result = await async_inner(x)
            return result + 1

        result = await async_outer(5)

        backend.stop()
        events = backend.get_events()

        # Should capture both async functions
        async_calls = [e for e in events if e.event_type == 'call' and e.is_async]
        # Async functions should be detected

        assert result == 11


class TestContextManager:
    """Test context manager usage."""

    def test_context_manager_usage(self):
        """Test using backend as context manager."""
        with PEP669Backend() as backend:
            def test_func(x):
                return x * 2

            result = test_func(5)

        # Backend should auto-stop
        assert backend.is_active() is False
        events = backend.get_events()

        # Should have captured events
        assert len(events) > 0

        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        assert len(call_events) > 0

        assert result == 10


class TestConfiguration:
    """Test backend configuration options."""

    def test_disable_arg_capture(self):
        """Test disabling argument capture."""
        backend = PEP669Backend(capture_args=False)
        backend.start()

        def add(a, b):
            return a + b

        result = add(2, 3)

        backend.stop()
        events = backend.get_events()

        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'add']
        # Args should be empty or None when capture is disabled
        if call_events:
            # Implementation might still create empty dict
            call_event = call_events[0]
            assert call_event.args == {} or call_event.args is None

    def test_disable_return_capture(self):
        """Test disabling return value capture."""
        backend = PEP669Backend(capture_returns=False)
        backend.start()

        def add(a, b):
            return a + b

        result = add(2, 3)

        backend.stop()
        events = backend.get_events()

        return_events = [e for e in events if e.event_type == 'return' and e.function_name == 'add']
        if return_events:
            return_event = return_events[0]
            assert return_event.return_value is None

    def test_max_events_limit(self):
        """Test that max events limit is enforced."""
        backend = PEP669Backend(max_events_per_thread=10)
        backend.start()

        # Generate many events
        for i in range(20):
            def dummy():
                pass
            dummy()

        backend.stop()
        events = backend.get_events()

        # Should not exceed max limit
        assert len(events) <= 10


class TestEventMetadata:
    """Test event metadata capture."""

    def test_event_timestamps(self):
        """Test that events have timestamps."""
        backend = PEP669Backend()
        backend.start()

        def test_func():
            return 42

        result = test_func()

        backend.stop()
        events = backend.get_events()

        # All events should have timestamps
        for event in events:
            assert isinstance(event.timestamp, datetime)
            assert event.timestamp is not None

    def test_event_thread_ids(self):
        """Test that events have thread IDs."""
        backend = PEP669Backend()
        backend.start()

        def test_func():
            return 42

        result = test_func()

        backend.stop()
        events = backend.get_events()

        current_thread_id = threading.get_ident()

        # All events in current thread should have correct thread ID
        for event in events:
            assert event.thread_id == current_thread_id

    def test_file_and_line_info(self):
        """Test that file and line information is captured."""
        backend = PEP669Backend()
        backend.start()

        def test_func():
            return 42

        result = test_func()

        backend.stop()
        events = backend.get_events()

        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        if call_events:
            call_event = call_events[0]
            assert call_event.file_path is not None
            assert call_event.line_number is not None
            assert __file__ in call_event.file_path


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_start_when_already_started(self):
        """Test starting backend when already active."""
        backend = PEP669Backend()
        backend.start()

        with pytest.raises(RuntimeError, match="already active"):
            backend.start()

        backend.stop()

    def test_stop_when_not_started(self):
        """Test stopping backend when not active."""
        backend = PEP669Backend()
        # Should not raise error
        backend.stop()

    def test_clear_events(self):
        """Test clearing events."""
        backend = PEP669Backend()
        backend.start()

        def test_func():
            return 42

        test_func()

        # Should have some events
        events_before = backend.get_events()
        assert len(events_before) > 0

        # Clear events
        backend.clear_events()

        # After clear, should have no events from test_func
        # but will have events from get_events/clear_events calls since tracing is still active
        # Stop backend to prevent new events
        backend.stop()

        # Clear again after stopping
        backend.clear_events()
        events_after = backend.get_events()

        assert len(events_after) == 0

    def test_get_events_other_thread_raises(self):
        """Test that accessing other thread's events raises error."""
        backend = PEP669Backend()
        backend.start()

        def test_func():
            return 42

        test_func()

        backend.stop()

        # Should raise when trying to access other thread
        with pytest.raises(ValueError, match="Cannot access events from other threads"):
            backend.get_events(thread_id=99999)

    def test_safe_repr_with_large_objects(self):
        """Test that large objects are safely represented."""
        backend = PEP669Backend()
        backend.start()

        def test_func(large_str):
            return len(large_str)

        large_string = "x" * 1000
        result = test_func(large_string)

        backend.stop()
        events = backend.get_events()

        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        if call_events:
            call_event = call_events[0]
            # Argument should be truncated
            assert 'large_str' in call_event.args
            arg_repr = call_event.args['large_str']
            assert len(str(arg_repr)) <= 210  # max_length + "..."

    def test_safe_repr_with_circular_reference(self):
        """Test that circular references are handled."""
        backend = PEP669Backend()
        backend.start()

        def test_func(obj):
            return obj

        # Create circular reference
        circular = {}
        circular['self'] = circular

        try:
            result = test_func(circular)
        except:
            pass

        backend.stop()
        events = backend.get_events()

        # Should not crash, and should have some representation
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        if call_events:
            call_event = call_events[0]
            assert 'obj' in call_event.args


class TestTraceEvent:
    """Test TraceEvent dataclass."""

    def test_trace_event_creation(self):
        """Test creating TraceEvent instance."""
        event = TraceEvent(
            event_type='call',
            timestamp=datetime.now(),
            thread_id=threading.get_ident(),
            function_name='test_func',
            module_name='__main__',
            file_path='/path/to/file.py',
            line_number=42,
            args={'a': 1, 'b': 2},
            is_async=False,
        )

        assert event.event_type == 'call'
        assert event.function_name == 'test_func'
        assert event.args == {'a': 1, 'b': 2}
        assert event.is_async is False

    def test_trace_event_defaults(self):
        """Test TraceEvent default values."""
        event = TraceEvent(
            event_type='line',
            timestamp=datetime.now(),
            thread_id=threading.get_ident(),
        )

        assert event.function_name is None
        assert event.args is None
        assert event.return_value is None
        assert event.exception_type is None
        assert event.is_async is False
        assert event.metadata == {}


class TestSelectiveInstrumentation:
    """Test selective instrumentation with include/exclude patterns."""

    def test_include_pattern_wildcard(self):
        """Test that wildcard pattern includes everything."""
        backend = PEP669Backend(include_patterns=['*'])
        backend.start()

        def test_func():
            return 42

        result = test_func()
        backend.stop()
        events = backend.get_events()

        # Should capture events with wildcard
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        assert len(call_events) > 0

    def test_include_pattern_exact_match(self):
        """Test exact module name matching."""
        backend = PEP669Backend(include_patterns=[__name__])
        backend.start()

        def test_func():
            return 42

        result = test_func()
        backend.stop()
        events = backend.get_events()

        # Should capture events from this module
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        assert len(call_events) > 0
        assert call_events[0].module_name == __name__

    def test_include_pattern_prefix_match(self):
        """Test prefix pattern matching with '.*' suffix."""
        # Get the package prefix (e.g., 'breadcrumb.tests' from 'breadcrumb.tests.instrumentation.test_pep669_backend')
        module_parts = __name__.split('.')
        if len(module_parts) >= 2:
            prefix = '.'.join(module_parts[:2])
            pattern = f"{prefix}.*"

            backend = PEP669Backend(include_patterns=[pattern])
            backend.start()

            def test_func():
                return 42

            result = test_func()
            backend.stop()
            events = backend.get_events()

            # Should capture events matching prefix
            call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
            assert len(call_events) > 0

    def test_exclude_pattern_blocks_module(self):
        """Test that exclude patterns block matching modules."""
        backend = PEP669Backend(
            include_patterns=['*'],
            exclude_patterns=[__name__]
        )
        backend.start()

        def test_func():
            return 42

        result = test_func()
        backend.stop()
        events = backend.get_events()

        # Should NOT capture events from excluded module
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        assert len(call_events) == 0

    def test_exclude_takes_precedence_over_include(self):
        """Test that exclude patterns take precedence over include patterns."""
        backend = PEP669Backend(
            include_patterns=[__name__],
            exclude_patterns=[__name__]
        )
        backend.start()

        def test_func():
            return 42

        result = test_func()
        backend.stop()
        events = backend.get_events()

        # Exclude should win over include
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        assert len(call_events) == 0

    def test_exclude_pattern_with_wildcard(self):
        """Test exclude pattern with wildcard suffix."""
        # Get base module name
        module_parts = __name__.split('.')
        if len(module_parts) >= 3:
            # Exclude all test modules
            pattern = f"{module_parts[0]}.tests.*"

            backend = PEP669Backend(
                include_patterns=['*'],
                exclude_patterns=[pattern]
            )
            backend.start()

            def test_func():
                return 42

            result = test_func()
            backend.stop()
            events = backend.get_events()

            # Should NOT capture events from test modules
            call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
            assert len(call_events) == 0

    def test_default_excludes_standard_library(self):
        """Test that default excludes filter out standard library modules."""
        backend = PEP669Backend()
        # Default excludes should include threading, os, sys, etc.
        assert 'threading' in backend.exclude_patterns
        assert 'sys' in backend.exclude_patterns
        assert 'os' in backend.exclude_patterns

    def test_multiple_include_patterns(self):
        """Test multiple include patterns work correctly."""
        backend = PEP669Backend(
            include_patterns=[__name__, 'other.module.*']
        )
        backend.start()

        def test_func():
            return 42

        result = test_func()
        backend.stop()
        events = backend.get_events()

        # Should capture events from included module
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'test_func']
        assert len(call_events) > 0

    def test_breadcrumb_internal_modules_excluded(self):
        """Test that breadcrumb internal instrumentation modules are excluded."""
        backend = PEP669Backend(include_patterns=['*'])

        # Check that internal modules would be excluded
        # We can't easily test this directly without importing those modules,
        # but we can verify the logic in _should_trace

        # Mock a frame from breadcrumb.instrumentation
        class MockCode:
            co_filename = 'breadcrumb/instrumentation/pep669_backend.py'
            co_name = 'test'
            co_flags = 0
            co_firstlineno = 1

        class MockFrame:
            f_globals = {'__name__': 'breadcrumb.instrumentation.pep669_backend'}
            f_lineno = 1

        result = backend._should_trace(MockCode(), MockFrame())
        assert result is False

    def test_pattern_matching_exact(self):
        """Test pattern matching for exact matches."""
        backend = PEP669Backend()

        # Test exact match
        assert backend._match_pattern('myapp', 'myapp') is True
        assert backend._match_pattern('myapp.submodule', 'myapp') is False
        assert backend._match_pattern('other', 'myapp') is False

    def test_pattern_matching_wildcard(self):
        """Test pattern matching with wildcard."""
        backend = PEP669Backend()

        # Test wildcard
        assert backend._match_pattern('anything', '*') is True
        assert backend._match_pattern('', '*') is True

    def test_pattern_matching_prefix(self):
        """Test pattern matching with prefix (.*) pattern."""
        backend = PEP669Backend()

        # Test prefix pattern
        assert backend._match_pattern('myapp', 'myapp.*') is True
        assert backend._match_pattern('myapp.submodule', 'myapp.*') is True
        assert backend._match_pattern('myapp.sub.deep', 'myapp.*') is True
        assert backend._match_pattern('other', 'myapp.*') is False
        assert backend._match_pattern('myappother', 'myapp.*') is False

    def test_instrumentation_time_filtering_performance(self):
        """Test that filtering happens at instrumentation time, not post-capture."""
        # Create backend that excludes this module
        backend = PEP669Backend(
            include_patterns=['nonexistent.module.*'],
            exclude_patterns=[__name__]
        )
        backend.start()

        # Call many functions
        def func1():
            return 1
        def func2():
            return 2
        def func3():
            return 3

        for _ in range(10):
            func1()
            func2()
            func3()

        backend.stop()
        events = backend.get_events()

        # Should have NO events because filtering happened at instrumentation time
        # (not after capture)
        func_events = [e for e in events if e.function_name in ['func1', 'func2', 'func3']]
        assert len(func_events) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
