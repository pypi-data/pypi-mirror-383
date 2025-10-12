"""Debug include patterns during execution."""

import sys

# Monkey-patch _should_trace_module to add logging
from breadcrumb.instrumentation import pep669_backend

original_should_trace_module = pep669_backend.PEP669Backend._should_trace_module

def debug_should_trace_module(self, module_name):
    result = original_should_trace_module(self, module_name)
    if module_name == '__main__':
        print(f"  [DEBUG] _should_trace_module('{module_name}'):", file=sys.stderr)
        print(f"    include_patterns = {self.include_patterns}", file=sys.stderr)
        print(f"    result = {result}", file=sys.stderr)
    return result

pep669_backend.PEP669Backend._should_trace_module = debug_should_trace_module

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
