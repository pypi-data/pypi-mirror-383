"""
sys.settrace fallback backend for Python 3.10-3.11.

This module implements tracing using the legacy sys.settrace API for Python versions
that don't support PEP 669 (sys.monitoring). It provides the same interface as the
PEP 669 backend but with significantly higher overhead.

Performance Warning:
    sys.settrace has ~2000%+ overhead compared to ~5% for PEP 669.
    Upgrade to Python 3.12+ for production use.
"""

import sys
import threading
import warnings
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timezone
import traceback


@dataclass
class TraceEvent:
    """Represents a single trace event."""
    event_type: str  # "call", "return", "line", "exception"
    timestamp: datetime
    thread_id: int
    function_name: str
    module: str
    filename: str
    line_number: int
    locals: Dict[str, Any] = field(default_factory=dict)
    return_value: Any = None
    exception: Optional[Dict[str, Any]] = None


class ThreadLocalContext:
    """Thread-local storage for trace context."""

    def __init__(self):
        self._local = threading.local()

    @property
    def trace_id(self) -> Optional[str]:
        """Get the current trace ID for this thread."""
        return getattr(self._local, 'trace_id', None)

    @trace_id.setter
    def trace_id(self, value: str):
        """Set the trace ID for this thread."""
        self._local.trace_id = value

    @property
    def events(self) -> List[TraceEvent]:
        """Get the event list for this thread."""
        if not hasattr(self._local, 'events'):
            self._local.events = []
        return self._local.events

    def clear(self):
        """Clear thread-local context."""
        if hasattr(self._local, 'trace_id'):
            del self._local.trace_id
        if hasattr(self._local, 'events'):
            del self._local.events


class SettraceBackend:
    """
    Tracing backend using sys.settrace for Python 3.10-3.11.

    This backend provides the same interface as the PEP 669 backend but uses
    the legacy sys.settrace API, which has significantly higher overhead.

    Thread Safety:
        Each thread maintains its own trace context using threading.local().
        Note that sys.settrace is set per-thread in Python.

    Limitations:
        - ~2000%+ overhead vs ~5% for PEP 669
        - Each thread needs to call sys.settrace separately
        - Less efficient for high-frequency tracing
    """

    def __init__(
        self,
        callback: Optional[Callable[[TraceEvent], None]] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        capture_locals: bool = True,
        capture_lines: bool = False,
    ):
        """
        Initialize the settrace backend.

        Args:
            callback: Function to call for each trace event
            include_patterns: List of module patterns to include (glob style)
            exclude_patterns: List of module patterns to exclude (glob style)
            capture_locals: Whether to capture local variables (performance impact)
            capture_lines: Whether to capture line-level execution (high overhead)
        """
        self.callback = callback
        self.include_patterns = include_patterns or ['*']
        self.exclude_patterns = exclude_patterns or [
            'threading',
            'queue',
            '_thread',
            'contextlib',
            'importlib',
            'sys',
            'os',
            'posixpath',
            'genericpath',
        ]
        self.capture_locals = capture_locals
        self.capture_lines = capture_lines
        self._context = ThreadLocalContext()
        self._enabled = False
        self._warned = False

    def _should_trace(self, frame) -> bool:
        """
        Determine if a frame should be traced based on include/exclude patterns.

        Args:
            frame: The frame object to check

        Returns:
            True if the frame should be traced, False otherwise
        """
        module = frame.f_globals.get('__name__', '')
        filename = frame.f_code.co_filename

        # Exclude this module itself
        if 'breadcrumb' in module and 'settrace_backend' in filename:
            return False

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if self._match_pattern(module, pattern):
                return False

        # Check include patterns
        for pattern in self.include_patterns:
            if self._match_pattern(module, pattern):
                return True

        return False

    def _match_pattern(self, text: str, pattern: str) -> bool:
        """
        Simple glob-style pattern matching.

        Args:
            text: The text to match
            pattern: The pattern to match against

        Returns:
            True if the text matches the pattern
        """
        if pattern == '*':
            return True
        if pattern.endswith('.*'):
            prefix = pattern[:-2]
            return text.startswith(prefix)
        return text == pattern

    def _trace_function(self, frame, event: str, arg):
        """
        The actual trace function called by sys.settrace.

        Args:
            frame: The current frame
            event: The event type ('call', 'return', 'line', 'exception')
            arg: Additional event argument

        Returns:
            The trace function to use for this frame (self for continued tracing)
        """
        # Check if we should trace this frame
        if not self._should_trace(frame):
            return None

        # Skip line events if not enabled
        if event == 'line' and not self.capture_lines:
            return self._trace_function

        try:
            # Create trace event
            trace_event = self._create_event(frame, event, arg)

            # Store event in thread-local context
            self._context.events.append(trace_event)

            # Call callback if provided
            if self.callback:
                self.callback(trace_event)

        except Exception as e:
            # Don't let tracing errors crash the application
            sys.stderr.write(f"Breadcrumb tracing error: {e}\n")

        return self._trace_function

    def _create_event(self, frame, event: str, arg) -> TraceEvent:
        """
        Create a TraceEvent from a frame and event type.

        Args:
            frame: The current frame
            event: The event type
            arg: Additional event argument

        Returns:
            A TraceEvent object
        """
        code = frame.f_code

        # Capture local variables if enabled
        local_vars = {}
        if self.capture_locals and event in ('call', 'return'):
            try:
                # Safely capture locals, handling non-serializable objects
                local_vars = {
                    k: self._safe_repr(v)
                    for k, v in frame.f_locals.items()
                    if not k.startswith('_')
                }
            except Exception as e:
                local_vars = {'_error': f'Failed to capture locals: {e}'}

        # Handle exception events
        exception_data = None
        if event == 'exception' and arg:
            exc_type, exc_value, exc_traceback = arg
            exception_data = {
                'type': exc_type.__name__ if exc_type else 'Unknown',
                'message': str(exc_value),
                'traceback': traceback.format_tb(exc_traceback) if exc_traceback else []
            }

        # Create the event
        return TraceEvent(
            event_type=event,
            timestamp=datetime.now(timezone.utc) if sys.version_info >= (3, 11) else datetime.utcnow(),
            thread_id=threading.get_ident(),
            function_name=code.co_name,
            module=frame.f_globals.get('__name__', '<unknown>'),
            filename=code.co_filename,
            line_number=frame.f_lineno,
            locals=local_vars,
            return_value=self._safe_repr(arg) if event == 'return' else None,
            exception=exception_data,
        )

    def _safe_repr(self, obj: Any, max_length: int = 1000) -> Any:
        """
        Safely convert an object to a string representation.

        Args:
            obj: The object to convert
            max_length: Maximum length of the representation

        Returns:
            A string representation or the object itself if simple type
        """
        # Handle simple types directly
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj

        # Handle collections
        if isinstance(obj, (list, tuple)):
            try:
                return [self._safe_repr(item, max_length) for item in obj[:10]]
            except:
                return f"<{type(obj).__name__}>"

        if isinstance(obj, dict):
            try:
                return {
                    k: self._safe_repr(v, max_length)
                    for k, v in list(obj.items())[:10]
                }
            except:
                return f"<{type(obj).__name__}>"

        # For other objects, use repr
        try:
            repr_str = repr(obj)
            if len(repr_str) > max_length:
                repr_str = repr_str[:max_length] + '...[TRUNCATED]'
            return repr_str
        except:
            return f"<{type(obj).__name__}>"

    def start(self):
        """
        Start tracing in the current thread.

        Warning:
            This will print a performance warning on first use.
            sys.settrace has ~2000%+ overhead vs ~5% for PEP 669.
        """
        if not self._warned:
            self._print_overhead_warning()
            self._warned = True

        self._enabled = True
        sys.settrace(self._trace_function)

    def stop(self):
        """Stop tracing in the current thread."""
        self._enabled = False
        sys.settrace(None)

    def get_events(self) -> List[TraceEvent]:
        """
        Get all trace events for the current thread.

        Returns:
            List of TraceEvent objects
        """
        return self._context.events.copy()

    def clear_events(self):
        """Clear all trace events for the current thread."""
        self._context.clear()

    def _print_overhead_warning(self):
        """Print a warning about sys.settrace overhead."""
        warning_msg = """
╔════════════════════════════════════════════════════════════════════════════╗
║ WARNING: Using sys.settrace fallback backend                              ║
║                                                                            ║
║ Performance Impact: ~2000%+ overhead vs ~5% for PEP 669                  ║
║                                                                            ║
║ You are running Python {version} which doesn't support PEP 669.          ║
║ For production use, upgrade to Python 3.12+ for significantly better     ║
║ performance.                                                               ║
║                                                                            ║
║ Recommendations:                                                           ║
║   - Development: This backend is acceptable for debugging                 ║
║   - Production: Upgrade to Python 3.12+ or disable tracing               ║
║   - CI/CD: Consider selective instrumentation to reduce overhead         ║
╚════════════════════════════════════════════════════════════════════════════╝
""".format(version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

        print(warning_msg, file=sys.stderr)


def is_supported() -> bool:
    """
    Check if sys.settrace backend is supported.

    Returns:
        True if Python version is 3.10 or 3.11, False otherwise
    """
    version_info = sys.version_info
    return version_info.major == 3 and version_info.minor in (10, 11)


def create_backend(**kwargs) -> SettraceBackend:
    """
    Create a settrace backend instance.

    Args:
        **kwargs: Arguments to pass to SettraceBackend constructor

    Returns:
        A SettraceBackend instance

    Raises:
        RuntimeError: If Python version doesn't support sys.settrace (< 3.10)
    """
    if sys.version_info < (3, 10):
        raise RuntimeError(
            f"Python {sys.version_info.major}.{sys.version_info.minor} is not supported. "
            "Breadcrumb requires Python 3.10 or higher."
        )

    return SettraceBackend(**kwargs)
