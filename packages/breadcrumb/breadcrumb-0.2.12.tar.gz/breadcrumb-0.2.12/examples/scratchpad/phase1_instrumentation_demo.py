# -*- coding: utf-8 -*-
"""
Phase 1: Instrumentation Demo

Demonstrates the PEP 669 and settrace backends collecting execution traces.
Note: Phase 1 (instrumentation) and Phase 2 (storage) are not yet integrated.

This example shows the instrumentation layer capturing events in memory.

Usage:
    python -X utf8 examples/phase1_instrumentation_demo.py
"""

import sys
sys.path.insert(0, 'src')

from breadcrumb.instrumentation.pep669_backend import PEP669Backend, is_pep669_available
from breadcrumb.instrumentation.settrace_backend import SettraceBackend


def fibonacci(n):
    """Recursive fibonacci - generates lots of traces!"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def example_function(x, y):
    """A simple function to trace."""
    result = x + y
    if result > 10:
        raise ValueError("Result too large!")
    return result


def main():
    print("=" * 70)
    print("PHASE 1: INSTRUMENTATION DEMO")
    print("=" * 70)
    print()

    # Step 1: Choose backend based on Python version
    if is_pep669_available():
        print("[1] Using PEP 669 Backend (Python 3.12+)")
        print("    - Lowest overhead")
        print("    - sys.monitoring API")
        backend = PEP669Backend(
            capture_args=True,
            capture_returns=True,
            capture_exceptions=True,
            include_patterns=['__main__']  # Only trace this script
        )
    else:
        print("[1] Using sys.settrace Backend (Python 3.10-3.11)")
        print("    - Compatible fallback")
        print("    - sys.settrace API")
        backend = SettraceBackend(
            capture_args=True,
            capture_returns=True,
            capture_exceptions=True,
            include_patterns=['__main__']
        )
    print()

    # Step 2: Start instrumentation
    print("[2] Starting instrumentation...")
    backend.start()
    print("    Status: TRACING ACTIVE")
    print()

    # Step 3: Execute some code to trace
    print("[3] Executing traced code...")
    print()

    print("    >> fibonacci(5)")
    result = fibonacci(5)
    print(f"    << Result: {result}")
    print()

    print("    >> example_function(3, 4)")
    result2 = example_function(3, 4)
    print(f"    << Result: {result2}")
    print()

    print("    >> example_function(6, 7) - will raise exception")
    try:
        example_function(6, 7)
    except ValueError as e:
        print(f"    << Caught: {e}")
    print()

    # Step 4: Stop instrumentation
    print("[4] Stopping instrumentation...")
    backend.stop()
    print("    Status: TRACING STOPPED")
    print()

    # Step 5: Retrieve events
    print("[5] Retrieving captured events...")
    events = backend.get_events()
    print(f"    Total events captured: {len(events)}")
    print()

    # Step 6: Analyze events
    print("[6] Event Analysis:")
    print("    " + "-" * 66)

    event_types = {}
    for event in events:
        event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

    for event_type, count in sorted(event_types.items()):
        print(f"    {event_type:15s}: {count:3d} events")

    print("    " + "-" * 66)
    print()

    # Step 7: Show sample events
    print("[7] Sample Events (first 10):")
    print()

    for i, event in enumerate(events[:10]):
        print(f"    Event {i+1}:")
        print(f"      Type:     {event.event_type}")
        print(f"      Function: {event.function_name}")
        print(f"      Module:   {event.module_name}")
        print(f"      Line:     {event.line_number}")

        if event.event_type == 'call' and event.args:
            print(f"      Args:     {event.args}")
        elif event.event_type == 'return' and event.return_value is not None:
            print(f"      Return:   {event.return_value}")
        elif event.event_type == 'exception':
            print(f"      Exception: {event.exception_type}: {event.exception_message}")

        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"  SUCCESS: Captured {len(events)} execution events")
    print(f"  Backend: {'PEP 669' if is_pep669_available() else 'sys.settrace'}")
    print()
    print("  What's Working:")
    print("    [x] Function call/return tracking")
    print("    [x] Argument capture")
    print("    [x] Return value capture")
    print("    [x] Exception tracking")
    print("    [x] Line-level execution tracking")
    print()
    print("  What's Not Yet Integrated:")
    print("    [ ] Persistent storage (Phase 2 is complete but not integrated)")
    print("    [ ] MCP Server (Phase 3 - not started)")
    print("    [ ] CLI Interface (Phase 4 - not started)")
    print()
    print("  Next Steps:")
    print("    - Phase 6: Integrate instrumentation with storage layer")
    print("    - Phase 3-4: Build MCP Server and CLI")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
