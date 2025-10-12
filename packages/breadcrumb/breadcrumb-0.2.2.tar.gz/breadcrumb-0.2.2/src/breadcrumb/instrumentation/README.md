# Breadcrumb Instrumentation Backends

This directory contains the tracing backend implementations for Breadcrumb.

## Available Backends

### 1. sys.settrace Backend (Python 3.10-3.11)

**File**: `settrace_backend.py`

A fallback tracing backend using Python's legacy `sys.settrace` API. This backend is designed for Python 3.10 and 3.11, which don't support the newer PEP 669 monitoring API.

**Features**:
- Captures CALL, RETURN, LINE, and EXCEPTION events
- Thread-safe using `threading.local()` for per-thread state
- Configurable include/exclude patterns for selective instrumentation
- Optional local variable capture
- Optional line-level execution tracing
- Performance overhead warning (2000%+ vs 5% for PEP 669)

**Usage**:

```python
from breadcrumb.instrumentation.settrace_backend import SettraceBackend

# Create backend with custom configuration
backend = SettraceBackend(
    callback=lambda event: print(f"{event.event_type}: {event.function_name}"),
    include_patterns=['myapp.*'],
    exclude_patterns=['myapp.vendor.*'],
    capture_locals=True,
    capture_lines=False  # Disable for better performance
)

# Start tracing
backend.start()

# Your code here
def my_function(x, y):
    return x + y

result = my_function(2, 3)

# Stop tracing
backend.stop()

# Get captured events
events = backend.get_events()
for event in events:
    print(f"{event.event_type}: {event.function_name} at line {event.line_number}")

# Clear events
backend.clear_events()
```

**Event Types**:

- `call`: Function call event with arguments and local variables
- `return`: Function return event with return value
- `line`: Line execution event (only if `capture_lines=True`)
- `exception`: Exception event with type, message, and stack trace

**Performance Considerations**:

The `sys.settrace` backend has significantly higher overhead than PEP 669:

- **PEP 669 (Python 3.12+)**: ~5% overhead
- **sys.settrace (Python 3.10-3.11)**: ~2000%+ overhead

For production use, we strongly recommend upgrading to Python 3.12+ and using the PEP 669 backend.

**Recommendations**:

1. **Development**: This backend is acceptable for debugging and development
2. **Production**: Upgrade to Python 3.12+ or disable tracing
3. **CI/CD**: Use selective instrumentation to reduce overhead
4. **Performance-critical code**: Disable line tracing (`capture_lines=False`)
5. **Large applications**: Use exclude patterns to filter out third-party code

**Thread Safety**:

The backend uses `threading.local()` to maintain separate trace contexts for each thread. This means:

- Each thread maintains its own event list
- Each thread must call `backend.start()` to enable tracing
- Events are isolated between threads

**API Reference**:

**`SettraceBackend`** class:

Constructor parameters:
- `callback: Optional[Callable[[TraceEvent], None]]` - Function called for each event
- `include_patterns: Optional[List[str]]` - Module patterns to include (glob style)
- `exclude_patterns: Optional[List[str]]` - Module patterns to exclude (glob style)
- `capture_locals: bool = True` - Whether to capture local variables
- `capture_lines: bool = False` - Whether to capture line-level execution

Methods:
- `start()` - Start tracing in the current thread
- `stop()` - Stop tracing in the current thread
- `get_events() -> List[TraceEvent]` - Get all captured events for current thread
- `clear_events()` - Clear all events for current thread

**`TraceEvent`** dataclass:

Fields:
- `event_type: str` - Event type ("call", "return", "line", "exception")
- `timestamp: datetime` - Event timestamp (UTC)
- `thread_id: int` - Thread ID where event occurred
- `function_name: str` - Name of the function
- `module: str` - Module name
- `filename: str` - Source file path
- `line_number: int` - Line number in source file
- `locals: Dict[str, Any]` - Local variables (if captured)
- `return_value: Any` - Return value (for "return" events)
- `exception: Optional[Dict[str, Any]]` - Exception info (for "exception" events)

**Module Functions**:

- `is_supported() -> bool` - Check if Python version is 3.10 or 3.11
- `create_backend(**kwargs) -> SettraceBackend` - Create backend instance

## Future Backends

### 2. PEP 669 Backend (Python 3.12+) - Coming Soon

A high-performance tracing backend using Python 3.12's new `sys.monitoring` API (PEP 669). This backend will offer:

- ~5% overhead (vs 2000%+ for sys.settrace)
- Better performance for production use
- Same interface as settrace backend for drop-in replacement

### 3. Other Potential Backends

- **C Extension Backend**: Ultra-low overhead using C-level hooks
- **Sampling Backend**: Statistical profiling with minimal overhead
- **Remote Backend**: Distributed tracing with remote storage

## Testing

Run tests for the settrace backend:

```bash
pytest tests/instrumentation/test_settrace_backend.py -v
```

## Examples

See `examples/settrace_demo.py` for a complete demonstration of the settrace backend.

## Contributing

When implementing a new backend:

1. Match the interface defined in `settrace_backend.py`
2. Implement all four event types: CALL, RETURN, LINE, EXCEPTION
3. Ensure thread safety using `threading.local()`
4. Add comprehensive unit tests
5. Document performance characteristics
6. Include usage examples
