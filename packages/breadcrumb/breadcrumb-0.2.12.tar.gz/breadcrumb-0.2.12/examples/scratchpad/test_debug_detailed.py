"""Detailed debug of module inference during tracing."""

import sys
import os

# Monkey-patch _infer_module_from_file to add logging
from breadcrumb.instrumentation import pep669_backend

original_infer = pep669_backend.PEP669Backend._infer_module_from_file

def debug_infer(self, file_path):
    result = original_infer(self, file_path)
    # Only log for our test functions, not breadcrumb internals
    if 'test_debug_detailed.py' in file_path:
        print(f"  [DEBUG] _infer_module_from_file('{file_path}') -> {result}", file=sys.stderr)
    return result

pep669_backend.PEP669Backend._infer_module_from_file = debug_infer

# Now run normal breadcrumb
import breadcrumb

print("=== Initializing breadcrumb with tracing ===", file=sys.stderr)
breadcrumb.init(silent=True)

def test_function():
    return "hello"

print("\n=== Calling test_function() ===", file=sys.stderr)
result = test_function()
print(f"Result: {result}")

print("\n=== Shutting down ===", file=sys.stderr)
breadcrumb.shutdown()
print("Done!", file=sys.stderr)
