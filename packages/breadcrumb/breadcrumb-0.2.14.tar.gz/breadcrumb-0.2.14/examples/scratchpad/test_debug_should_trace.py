"""Debug _should_trace return value."""

import sys

# Monkey-patch _should_trace to add logging
from breadcrumb.instrumentation import pep669_backend

original_should_trace = pep669_backend.PEP669Backend._should_trace

def debug_should_trace(self, code, frame):
    result = original_should_trace(self, code, frame)
    if 'test_debug_should_trace.py' in code.co_filename:
        print(f"  [DEBUG] _should_trace():", file=sys.stderr)
        print(f"    file: {code.co_filename}", file=sys.stderr)
        print(f"    function: {code.co_name}", file=sys.stderr)
        print(f"    result: {result}", file=sys.stderr)
    return result

pep669_backend.PEP669Backend._should_trace = debug_should_trace

# Now run normal breadcrumb
import breadcrumb

print("=== Initializing breadcrumb ===", file=sys.stderr)
breadcrumb.init(silent=True)

def test_function():
    return "hello"

print("\n=== Calling test_function() ===", file=sys.stderr)
result = test_function()
print(f"Result: {result}")

print("\n=== Shutting down ===", file=sys.stderr)
breadcrumb.shutdown()
