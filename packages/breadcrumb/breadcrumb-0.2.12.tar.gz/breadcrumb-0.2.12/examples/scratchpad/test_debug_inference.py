"""Debug script to understand module inference."""

import sys
import os

# Before importing breadcrumb, let's check __main__
print(f"__main__.__file__ at script start: {__file__}")
print(f"sys.modules['__main__'].__file__: {sys.modules['__main__'].__file__ if hasattr(sys.modules['__main__'], '__file__') else 'NOT SET'}")

import breadcrumb

# Manually test the inference
from breadcrumb.instrumentation.pep669_backend import PEP669Backend
backend = PEP669Backend(include_patterns=['__main__'])

# Test inference for this script's path
this_file = os.path.abspath(__file__)
result = backend._infer_module_from_file(this_file)
print(f"\n_infer_module_from_file('{this_file}'):")
print(f"  Result: {result}")

# Test _should_trace_module
if result:
    should_trace = backend._should_trace_module(result)
    print(f"  _should_trace_module('{result}'): {should_trace}")

# Now let's init breadcrumb and trace a simple function
print("\n\n=== Starting breadcrumb tracing ===")
breadcrumb.init()

def test_function():
    return "hello"

result = test_function()
print(f"test_function() = {result}")

breadcrumb.shutdown()
print("\n=== Breadcrumb shutdown ===")
