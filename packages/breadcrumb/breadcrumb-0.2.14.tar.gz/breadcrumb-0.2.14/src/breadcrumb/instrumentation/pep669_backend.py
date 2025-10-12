"""
PEP 669 Instrumentation Backend for Breadcrumb AI Tracer

This module implements execution tracing using sys.monitoring (PEP 669)
introduced in Python 3.12+. It provides low-overhead instrumentation for
capturing function calls, line execution, and exceptions.

Architecture:
- Uses sys.monitoring events (CALL, RETURN, LINE, EXCEPTION)
- Thread-safe state management with threading.local()
- Async-aware for async/await functions
- Captures metadata, arguments, return values, and exceptions
- Selective instrumentation with include patterns (include-only workflow)

Usage:
    from breadcrumb.instrumentation.pep669_backend import PEP669Backend

    # Trace only __main__ (default)
    backend = PEP669Backend()
    backend.start()

    # Selective instrumentation - include specific modules
    backend = PEP669Backend(
        include_patterns=['__main__', 'myapp.*', 'flock.orchestrator.*']
    )
    backend.start()
    # ... your code here ...
    backend.stop()
    events = backend.get_events()
"""

import sys
import threading
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from datetime import datetime
import inspect
import os
import site

from breadcrumb.instrumentation.call_tracker import CallTracker


# Python version check
PYTHON_VERSION = sys.version_info
PEP669_AVAILABLE = PYTHON_VERSION >= (3, 12)


@dataclass
class TraceEvent:
    """Represents a single trace event captured during execution."""

    event_type: str  # 'call', 'return', 'line', 'exception', 'call_site'
    timestamp: datetime
    thread_id: int

    # Function/code context
    function_name: Optional[str] = None
    module_name: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None

    # Function call/return data
    args: Optional[Dict[str, Any]] = None
    kwargs: Optional[Dict[str, Any]] = None
    return_value: Any = None

    # Line execution data
    local_vars: Optional[Dict[str, Any]] = None

    # Exception data
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    exception_traceback: Optional[str] = None

    # Async context
    is_async: bool = False

    # Call site data (for gap detection)
    called_from_function: Optional[str] = None
    called_from_module: Optional[str] = None

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ThreadLocalState:
    """Thread-local state for trace event collection."""

    def __init__(self):
        self.events: List[TraceEvent] = []
        self.call_stack: List[Dict[str, Any]] = []
        self.enabled: bool = True


class PEP669Backend:
    """
    PEP 669 instrumentation backend using sys.monitoring.

    This backend provides low-overhead execution tracing by registering
    callbacks for sys.monitoring events introduced in Python 3.12.

    Features:
    - Function call/return tracking with argument capture
    - Line-level execution tracking
    - Exception tracking with stack traces
    - Thread-safe event collection
    - Async/await function support
    - Selective instrumentation with include patterns (include-only workflow)
    - Instrumentation-time filtering for optimal performance

    Example:
        # Basic usage - trace only __main__
        backend = PEP669Backend()
        backend.start()

        def add(a, b):
            return a + b

        result = add(2, 3)
        backend.stop()

        events = backend.get_events()
        # Events will include call, line, and return events for add()

        # Selective instrumentation - include specific modules
        backend = PEP669Backend(
            include_patterns=['__main__', 'myapp.*', 'flock.orchestrator.*']
        )
        backend.start()
        # Only specified modules will be traced
    """

    # Tool ID for sys.monitoring (must be between 0-5 for third-party tools)
    TOOL_ID = 0

    def __init__(
        self,
        capture_args: bool = True,
        capture_returns: bool = True,
        capture_lines: bool = False,  # Very noisy, disabled by default
        capture_locals: bool = False,  # Expensive, disabled by default
        capture_exceptions: bool = True,
        capture_call_sites: bool = True,  # For gap detection
        max_events_per_thread: int = 10000,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        event_callback: Optional[Callable[[TraceEvent], None]] = None,
        # Smart auto-filtering to prevent event queue overflow
        auto_filter_enabled: bool = True,
        auto_filter_threshold: int = 100,
        auto_filter_window: float = 10.0,
        auto_filter_reset_interval: float = 60.0,
        max_repr_length: int = 2000,
    ):
        """
        Initialize PEP 669 backend.

        Args:
            capture_args: Whether to capture function arguments
            capture_returns: Whether to capture return values
            capture_lines: Whether to capture line-level execution (very noisy, disabled by default)
            capture_locals: Whether to capture local variables on line events
            capture_exceptions: Whether to capture exception details
            capture_call_sites: Whether to capture ALL function calls for gap detection (default: True)
            max_events_per_thread: Maximum events to store per thread (prevents memory issues)
            include_patterns: List of module patterns to include (glob style, e.g., ['__main__', 'myapp.*'])
            exclude_patterns: List of module patterns to exclude (glob style, e.g., ['wrapt.*'])
            event_callback: Optional callback function to call for each event (for integration with storage)
            auto_filter_enabled: Enable smart auto-filtering to prevent event overflow (default: True)
            auto_filter_threshold: Max calls per function in window before filtering (default: 100)
            auto_filter_window: Time window for counting calls in seconds (default: 10.0)
            auto_filter_reset_interval: How often to reset filters to re-sample in seconds (default: 60.0)
        """
        if not PEP669_AVAILABLE:
            raise RuntimeError(
                f"PEP 669 (sys.monitoring) requires Python 3.12+. "
                f"Current version: {PYTHON_VERSION.major}.{PYTHON_VERSION.minor}"
            )

        self.capture_args = capture_args
        self.capture_returns = capture_returns
        self.capture_lines = capture_lines
        self.capture_locals = capture_locals
        self.capture_exceptions = capture_exceptions
        self.capture_call_sites = capture_call_sites
        self.max_events_per_thread = max_events_per_thread
        self.event_callback = event_callback
        self.max_repr_length = max_repr_length if max_repr_length and max_repr_length > 0 else 2000

        # Smart auto-filtering
        self.auto_filter_enabled = auto_filter_enabled
        self.call_tracker = None
        if auto_filter_enabled:
            self.call_tracker = CallTracker(
                threshold=auto_filter_threshold,
                window_seconds=auto_filter_window,
                reset_interval=auto_filter_reset_interval,
            )

        # Pattern filtering for selective instrumentation (include-only)
        self.include_patterns = list(include_patterns) if include_patterns is not None else ['__main__']
        self.exclude_patterns = list(exclude_patterns) if exclude_patterns is not None else []

        # Thread-local storage for events
        self._thread_local = threading.local()

        # Global state
        self._active = False
        self._lock = threading.Lock()

    def _get_thread_state(self) -> ThreadLocalState:
        """Get or create thread-local state."""
        if not hasattr(self._thread_local, 'state'):
            self._thread_local.state = ThreadLocalState()
        return self._thread_local.state

    def _match_pattern(self, text: str, pattern: str) -> bool:
        """
        Simple glob-style pattern matching.

        Supports:
        - '*' matches everything
        - 'module.*' matches module and all submodules
        - 'module' matches exact module name

        Args:
            text: The text to match (e.g., module name)
            pattern: The pattern to match against

        Returns:
            True if the text matches the pattern
        """
        if pattern == '*':
            return True
        if pattern.endswith('.*'):
            # Match module and all submodules
            prefix = pattern[:-2]
            return text == prefix or text.startswith(prefix + '.')
        # Exact match
        return text == pattern

    def _should_trace_module(self, module_name: str) -> bool:
        """
        Check if a module name matches include patterns.

        Args:
            module_name: The module name to check

        Returns:
            True if the module should be traced
        """
        # Always exclude breadcrumb internal modules
        if 'breadcrumb' in module_name:
            return False

        # Check include patterns
        # Respect explicit exclude patterns first
        for exclude_pattern in self.exclude_patterns:
            if self._match_pattern(module_name, exclude_pattern):
                return False

        for pattern in self.include_patterns:
            if self._match_pattern(module_name, pattern):
                return True

        return False

    def _should_trace(self, code: Any, frame: Any) -> bool:
        """
        Determine if a code object should be traced based on include patterns.

        This is called at instrumentation time to filter events before capture,
        providing better performance than post-capture filtering.

        Args:
            code: The code object
            frame: The frame object (may be None)

        Returns:
            True if the code should be traced, False otherwise
        """
        # Get file path
        file_path = code.co_filename

        # Always exclude breadcrumb internal modules (but not user code in directories containing 'breadcrumb')
        # Check if it's actually IN the breadcrumb package by looking for /breadcrumb/ or \breadcrumb\ in path
        if '/breadcrumb/' in file_path or '\\breadcrumb\\' in file_path:
            # Additional check: make sure it's the actual breadcrumb package, not just a directory name
            # Look for /breadcrumb/instrumentation/, /breadcrumb/storage/, /breadcrumb/config.py, etc.
            if any(x in file_path for x in ['/breadcrumb/instrumentation/', '/breadcrumb/storage/',
                                             '/breadcrumb/integration.py', '/breadcrumb/config.py',
                                             '\\breadcrumb\\instrumentation\\', '\\breadcrumb\\storage\\',
                                             '\\breadcrumb\\integration.py', '\\breadcrumb\\config.py']):
                return False

        # Exclude Python internal special files (but allow user code like <string>)
        if file_path.startswith('<frozen') or file_path.startswith('<__'):
            return False

        # Get module name from file path inference (not frame globals!)
        # This is critical - we need the CALLED function's module, not the caller's
        module_name = self._infer_module_from_file(file_path)

        if not module_name:
            # If we can't determine module from file path, it's likely a user script
            # Use frame globals as fallback (will give us caller's context, but better than nothing)
            if frame and hasattr(frame, 'f_globals'):
                module_name = frame.f_globals.get('__name__', None)

            if not module_name:
                # Still can't determine - default to not tracing
                # (Better to miss some traces than to incorrectly trace stdlib/internals)
                return False

        # Use the module check helper
        return self._should_trace_module(module_name)

    def _add_event(self, event: TraceEvent) -> None:
        """Add event to thread-local storage with size limit."""
        state = self._get_thread_state()

        if not state.enabled:
            return

        # If callback is configured, call it instead of storing locally
        if self.event_callback is not None:
            try:
                self.event_callback(event)
            except Exception:
                # Don't crash instrumentation if callback fails
                pass
            # Still store event locally for get_events() compatibility
            # but don't enforce size limit to avoid dropping events

        # Enforce max events limit to prevent memory issues (only if no callback)
        if self.event_callback is None and len(state.events) >= self.max_events_per_thread:
            # Drop oldest events (FIFO)
            state.events.pop(0)

        state.events.append(event)

    def _extract_function_metadata(self, code: Any, frame: Any) -> Dict[str, Any]:
        """Extract metadata from code object and frame."""
        function_name = code.co_name

        # For class methods/constructors, try to get the qualified name
        if frame and function_name in ('__init__', '__new__', '__call__'):
            # Try to get the class name from 'self' or 'cls'
            if 'self' in frame.f_locals:
                cls = frame.f_locals['self'].__class__
                function_name = f"{cls.__name__}.{code.co_name}"
            elif 'cls' in frame.f_locals:
                cls = frame.f_locals['cls']
                if isinstance(cls, type):
                    function_name = f"{cls.__name__}.{code.co_name}"

        # Infer module name from code object's file path, not frame globals
        # This is critical for gap detection - we need the CALLED function's module,
        # not the caller's module
        module_name = self._infer_module_from_file(code.co_filename)

        metadata = {
            'function_name': function_name,
            'file_path': code.co_filename,
            'line_number': frame.f_lineno if frame else code.co_firstlineno,
            'module_name': module_name,
        }

        # Detect async functions
        if code.co_flags & inspect.CO_COROUTINE:
            metadata['is_async'] = True
        elif code.co_flags & inspect.CO_ASYNC_GENERATOR:
            metadata['is_async'] = True
        else:
            metadata['is_async'] = False

        return metadata

    def _infer_module_from_file(self, file_path: str) -> Optional[str]:
        """
        Infer module name from file path.

        For Python files, we try to determine the module name from the file path.
        This is used for gap detection to correctly identify which module a function belongs to.

        Args:
            file_path: File path from code object

        Returns:
            Inferred module name, or None if cannot determine
        """
        # Handle special cases
        if file_path == '<stdin>':
            return '__main__'
        if file_path.startswith('<'):
            return None  # Other special files

        # For regular files, try to infer from path
        # Common patterns:
        # - /path/to/script.py -> user script (could be __main__ but we can't tell from path alone)
        # - /usr/lib/python3.12/json/__init__.py -> json (stdlib)
        # - /path/to/site-packages/package/module.py -> package.module (3rd party)

        # Normalize path separators
        normalized_path = file_path.replace('\\', '/')

        # If it's in site-packages or dist-packages, extract package path
        if 'site-packages/' in normalized_path or 'dist-packages/' in normalized_path:
            # Get everything after site-packages/
            if 'site-packages/' in normalized_path:
                parts = normalized_path.split('site-packages/')[-1]
            else:
                parts = normalized_path.split('dist-packages/')[-1]

            # Convert path to module name
            parts = parts.replace('/', '.')
            if parts.endswith('.py'):
                parts = parts[:-3]
            if parts.endswith('.__init__'):
                parts = parts[:-9]
            return parts

        # Check if it's a standard library module
        # Standard library is typically in /usr/lib/pythonX.Y/ or similar
        if '/lib/python' in normalized_path or '/lib64/python' in normalized_path:
            # Extract the module path after pythonX.Y/
            import re
            match = re.search(r'/lib(?:64)?/python[\d.]+/(.+)', normalized_path)
            if match:
                module_path = match.group(1)
                # Convert to module name
                module_path = module_path.replace('/', '.')
                if module_path.endswith('.py'):
                    module_path = module_path[:-3]
                if module_path.endswith('.__init__'):
                    module_path = module_path[:-9]
                return module_path

        # For user scripts: try to use sys.modules to get the actual module
        # This is more reliable than path heuristics
        try:
            import sys

            # First, check __main__ specifically (most common case for user scripts)
            if '__main__' in sys.modules:
                main_module = sys.modules['__main__']
                if hasattr(main_module, '__file__') and main_module.__file__:
                    try:
                        if os.path.samefile(main_module.__file__, file_path):
                            return '__main__'
                    except (OSError, ValueError):
                        pass

            # Then try to find the module in sys.modules by matching file paths
            for module_name, module in sys.modules.items():
                if hasattr(module, '__file__') and module.__file__:
                    try:
                        # Use os.path.samefile for robust path comparison
                        # This handles symlinks, relative vs absolute, etc.
                        if os.path.samefile(module.__file__, file_path):
                            return module_name
                    except (OSError, ValueError):
                        # Files don't exist or can't be compared
                        # Fall back to string comparison
                        module_file = module.__file__.replace('\\', '/')
                        # Handle .pyc files
                        if module_file.endswith('.pyc'):
                            module_file = module_file[:-1]  # Remove 'c' to get .py

                        if module_file == normalized_path:
                            return module_name
        except Exception:
            pass  # If anything goes wrong, fall through to default

        # Default: if we can't determine, return None
        # This is better than guessing wrong
        return None

    def _capture_arguments(self, code: Any, frame: Any) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Capture function arguments from frame."""
        if not self.capture_args or not frame:
            return {}, {}

        try:
            # Get argument names from code object
            arg_count = code.co_argcount
            arg_names = code.co_varnames[:arg_count]

            # Extract positional arguments
            args = {}
            for name in arg_names:
                if name in frame.f_locals:
                    args[name] = self._safe_repr(frame.f_locals[name])

            # Extract keyword arguments (if any)
            kwargs = {}
            kwonly_arg_count = code.co_kwonlyargcount
            if kwonly_arg_count > 0:
                kwonly_names = code.co_varnames[arg_count:arg_count + kwonly_arg_count]
                for name in kwonly_names:
                    if name in frame.f_locals:
                        kwargs[name] = self._safe_repr(frame.f_locals[name])

            var_index = arg_count + kwonly_arg_count

            if code.co_flags & inspect.CO_VARARGS:
                vararg_name = code.co_varnames[var_index]
                vararg_value = frame.f_locals.get(vararg_name)
                if vararg_value:
                    args[vararg_name] = [
                        self._safe_repr(item) for item in vararg_value
                    ]
                var_index += 1

            if code.co_flags & inspect.CO_VARKEYWORDS:
                varkw_name = code.co_varnames[var_index]
                varkw_value = frame.f_locals.get(varkw_name)
                if isinstance(varkw_value, dict):
                    for key, value in varkw_value.items():
                        kwargs[key] = self._safe_repr(value)

            return args, kwargs
        except Exception:
            # Fail gracefully if we can't capture arguments
            return {}, {}

    def _safe_repr(self, value: Any) -> Any:
        """
        Safe representation of values with truncation.

        Handles circular references and large objects gracefully.
        """
        max_length = self.max_repr_length
        try:
            # For simple types, return as-is
            if isinstance(value, (int, float, bool, type(None))):
                return value

            # For strings, truncate if too long
            if isinstance(value, str):
                if len(value) > max_length:
                    return value[:max_length] + "..."
                return value

            # For other types, use repr with truncation
            repr_str = repr(value)
            if len(repr_str) > max_length:
                return repr_str[:max_length] + "..."
            return repr_str
        except Exception:
            return "<unable to represent>"

    # sys.monitoring callback handlers

    def _on_call(self, code: Any, instruction_offset: int) -> Any:
        """Handle PY_START event - function call."""
        frame = sys._getframe(1)  # Get caller frame

        # Extract metadata for this function
        metadata = self._extract_function_metadata(code, frame)

        # Get caller information for gap detection
        caller_function = None
        caller_module = None
        if frame and frame.f_back:
            caller_frame = frame.f_back
            caller_code = caller_frame.f_code
            caller_function = caller_code.co_name
            caller_module = caller_frame.f_globals.get('__name__', '__unknown__')

        # Check if we should trace this code object (instrumentation-time filtering)
        should_trace = self._should_trace(code, frame)

        if not should_trace and self.capture_call_sites:
            # Capture lightweight call_site event for gap detection
            # Only if the caller IS being traced (otherwise no point)
            if caller_module and self._should_trace_module(caller_module):
                call_site_event = TraceEvent(
                    event_type='call_site',
                    timestamp=datetime.now(),
                    thread_id=threading.get_ident(),
                    function_name=metadata['function_name'],
                    module_name=metadata['module_name'],
                    file_path=metadata['file_path'],
                    line_number=metadata['line_number'],
                    called_from_function=caller_function,
                    called_from_module=caller_module,
                )
                self._add_event(call_site_event)

            # Don't capture full event for filtered modules
            return None

        # Smart auto-filtering: Check if this function should be filtered due to high frequency
        if self.call_tracker is not None:
            module_name = metadata['module_name'] or '__unknown__'
            function_name = metadata['function_name']
            if self.call_tracker.should_filter(module_name, function_name):
                # Function is being auto-filtered - drop this event
                return None

        args, kwargs = self._capture_arguments(code, frame)

        event = TraceEvent(
            event_type='call',
            timestamp=datetime.now(),
            thread_id=threading.get_ident(),
            function_name=metadata['function_name'],
            module_name=metadata['module_name'],
            file_path=metadata['file_path'],
            line_number=metadata['line_number'],
            args=args,
            kwargs=kwargs,
            is_async=metadata['is_async'],
        )

        self._add_event(event)

        # Push to call stack for matching with returns
        state = self._get_thread_state()
        state.call_stack.append({
            'function_name': metadata['function_name'],
            'timestamp': event.timestamp,
        })

        # Return DISABLE is not needed - just continue monitoring
        return None

    def _on_return(self, code: Any, instruction_offset: int, retval: Any) -> Any:
        """Handle PY_RETURN event - function return."""
        frame = sys._getframe(1)

        # Check if we should trace this code object (instrumentation-time filtering)
        if not self._should_trace(code, frame):
            # Don't capture event for filtered modules
            return None

        metadata = self._extract_function_metadata(code, frame)

        event = TraceEvent(
            event_type='return',
            timestamp=datetime.now(),
            thread_id=threading.get_ident(),
            function_name=metadata['function_name'],
            module_name=metadata['module_name'],
            file_path=metadata['file_path'],
            line_number=metadata['line_number'],
            return_value=self._safe_repr(retval) if self.capture_returns else None,
            is_async=metadata['is_async'],
        )

        self._add_event(event)

        # Pop from call stack
        state = self._get_thread_state()
        if state.call_stack:
            state.call_stack.pop()

        return None

    def _on_line(self, code: Any, line_number: int) -> Any:
        """Handle LINE event - line execution."""
        frame = sys._getframe(1)

        # Check if we should trace this code object (instrumentation-time filtering)
        if not self._should_trace(code, frame):
            # Don't capture event for filtered modules
            return None

        metadata = self._extract_function_metadata(code, frame)

        # Optionally capture local variables (expensive)
        local_vars = None
        if self.capture_locals and frame:
            try:
                local_vars = {
                    k: self._safe_repr(v)
                    for k, v in frame.f_locals.items()
                    if not k.startswith('__')
                }
            except Exception:
                pass

        event = TraceEvent(
            event_type='line',
            timestamp=datetime.now(),
            thread_id=threading.get_ident(),
            function_name=metadata['function_name'],
            module_name=metadata['module_name'],
            file_path=metadata['file_path'],
            line_number=line_number,
            local_vars=local_vars,
            is_async=metadata['is_async'],
        )

        self._add_event(event)

        return None

    def _on_exception(self, code: Any, instruction_offset: int, exception: BaseException) -> Any:
        """Handle RAISE event - exception raised."""
        if not self.capture_exceptions:
            return None

        frame = sys._getframe(1)

        # Check if we should trace this code object (instrumentation-time filtering)
        if not self._should_trace(code, frame):
            # Don't capture event for filtered modules
            return None

        metadata = self._extract_function_metadata(code, frame)

        # Capture exception details
        exc_type = type(exception).__name__
        exc_message = str(exception)
        exc_traceback = None

        try:
            exc_traceback = ''.join(traceback.format_exception(
                type(exception), exception, exception.__traceback__
            ))
        except Exception:
            exc_traceback = "<unable to format traceback>"

        event = TraceEvent(
            event_type='exception',
            timestamp=datetime.now(),
            thread_id=threading.get_ident(),
            function_name=metadata['function_name'],
            module_name=metadata['module_name'],
            file_path=metadata['file_path'],
            line_number=metadata['line_number'],
            exception_type=exc_type,
            exception_message=exc_message,
            exception_traceback=exc_traceback,
            is_async=metadata['is_async'],
        )

        self._add_event(event)

        return None

    def start(self) -> None:
        """Start tracing with PEP 669 sys.monitoring."""
        with self._lock:
            if self._active:
                raise RuntimeError("Backend is already active")

            # Try to free the tool ID first if it's already in use
            try:
                sys.monitoring.free_tool_id(self.TOOL_ID)
            except ValueError:
                pass  # Tool ID wasn't in use

            # Register callbacks for monitoring events
            sys.monitoring.use_tool_id(self.TOOL_ID, "breadcrumb")

            # Register event callbacks
            # Note: CALL event is for all function calls (not PY_CALL)
            sys.monitoring.register_callback(
                self.TOOL_ID,
                sys.monitoring.events.PY_START,
                self._on_call
            )

            sys.monitoring.register_callback(
                self.TOOL_ID,
                sys.monitoring.events.PY_RETURN,
                self._on_return
            )

            # Only register LINE events if capture_lines is enabled
            if self.capture_lines:
                sys.monitoring.register_callback(
                    self.TOOL_ID,
                    sys.monitoring.events.LINE,
                    self._on_line
                )

            sys.monitoring.register_callback(
                self.TOOL_ID,
                sys.monitoring.events.RAISE,
                self._on_exception
            )

            # Set event states to enable monitoring
            events_to_monitor = (
                sys.monitoring.events.PY_START |
                sys.monitoring.events.PY_RETURN |
                sys.monitoring.events.RAISE
            )
            if self.capture_lines:
                events_to_monitor |= sys.monitoring.events.LINE

            sys.monitoring.set_events(self.TOOL_ID, events_to_monitor)

            # CRITICAL: Restart events to apply monitoring to already-loaded code
            # Without this, only NEW code loaded after start() will be monitored
            sys.monitoring.restart_events()

            self._active = True

    def stop(self) -> None:
        """Stop tracing and unregister callbacks."""
        with self._lock:
            if not self._active:
                return

            try:
                # Disable all events
                sys.monitoring.set_events(self.TOOL_ID, 0)

                # Unregister callbacks
                sys.monitoring.register_callback(
                    self.TOOL_ID,
                    sys.monitoring.events.PY_START,
                    None
                )
                sys.monitoring.register_callback(
                    self.TOOL_ID,
                    sys.monitoring.events.PY_RETURN,
                    None
                )
                sys.monitoring.register_callback(
                    self.TOOL_ID,
                    sys.monitoring.events.LINE,
                    None
                )
                sys.monitoring.register_callback(
                    self.TOOL_ID,
                    sys.monitoring.events.RAISE,
                    None
                )

                # Free tool ID
                sys.monitoring.free_tool_id(self.TOOL_ID)
            except Exception:
                # Fail gracefully if cleanup fails
                pass

            self._active = False

    def get_events(self, thread_id: Optional[int] = None) -> List[TraceEvent]:
        """
        Get captured trace events.

        Args:
            thread_id: Optional thread ID to filter events. If None, returns
                      events from current thread.

        Returns:
            List of TraceEvent objects
        """
        if thread_id is None or thread_id == threading.get_ident():
            state = self._get_thread_state()
            return list(state.events)
        else:
            # Can't access other thread's local storage
            raise ValueError("Cannot access events from other threads")

    def clear_events(self) -> None:
        """Clear all events from current thread."""
        state = self._get_thread_state()
        state.events.clear()
        state.call_stack.clear()

    def is_active(self) -> bool:
        """Check if backend is currently active."""
        return self._active

    def get_truncation_summary(self) -> Dict[str, Any]:
        """
        Get summary of auto-filtered functions (smart truncation).

        Returns:
            Dictionary with truncation statistics, or empty dict if auto-filter disabled
        """
        if self.call_tracker is None:
            return {
                "auto_filter_enabled": False,
                "truncated_functions": 0,
                "total_dropped_events": 0,
            }

        summary = self.call_tracker.get_truncation_summary()
        summary["auto_filter_enabled"] = True
        return summary

    def get_active_filters(self) -> Set[Tuple[str, str]]:
        """
        Get currently auto-filtered functions.

        Returns:
            Set of (module_name, function_name) tuples currently being filtered
        """
        if self.call_tracker is None:
            return set()
        return self.call_tracker.get_active_filters()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False


# Convenience function for version checking
def is_pep669_available() -> bool:
    """Check if PEP 669 (sys.monitoring) is available."""
    return PEP669_AVAILABLE
