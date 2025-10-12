"""
Demo script showing the sys.settrace backend in action.

This script demonstrates the basic usage of the settrace backend for tracing
Python execution. Note that this backend has significantly higher overhead
than the PEP 669 backend (2000%+ vs 5%).

Run with: python examples/settrace_demo.py
"""

import sys
sys.path.insert(0, 'src')

from breadcrumb.instrumentation.settrace_backend import SettraceBackend


def fibonacci(n: int) -> int:
    """Calculate fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def divide(a: int, b: int) -> float:
    """Divide two numbers (may raise exception)."""
    return a / b


def process_data(items: list) -> dict:
    """Process a list of items."""
    result = {}
    for i, item in enumerate(items):
        result[f"item_{i}"] = item * 2
    return result


def main():
    """Run demo functions with tracing enabled."""
    print("=" * 80)
    print("Breadcrumb sys.settrace Backend Demo")
    print("=" * 80)
    print()

    # Create backend with callback to print events
    def print_event(event):
        if event.function_name in ('fibonacci', 'divide', 'process_data'):
            print(f"[{event.event_type:10s}] {event.function_name:20s} "
                  f"at {event.filename}:{event.line_number}")
            if event.event_type == 'return' and event.return_value is not None:
                print(f"             -> returned: {event.return_value}")
            if event.exception:
                print(f"             -> exception: {event.exception['type']}: {event.exception['message']}")

    backend = SettraceBackend(
        callback=print_event,
        include_patterns=['*'],
        capture_locals=True,
        capture_lines=False  # Disable line events for less noise
    )

    print("\n1. Testing Fibonacci (recursive calls):")
    print("-" * 80)
    backend.start()
    result = fibonacci(5)
    backend.stop()
    print(f"\nResult: fibonacci(5) = {result}")
    print(f"Events captured: {len(backend.get_events())}")

    print("\n\n2. Testing Division (normal execution):")
    print("-" * 80)
    backend.clear_events()
    backend.start()
    result = divide(10, 2)
    backend.stop()
    print(f"\nResult: divide(10, 2) = {result}")
    print(f"Events captured: {len(backend.get_events())}")

    print("\n\n3. Testing Division with Exception:")
    print("-" * 80)
    backend.clear_events()
    backend.start()
    try:
        result = divide(10, 0)
    except ZeroDivisionError as e:
        print(f"\nCaught exception: {e}")
    backend.stop()
    print(f"Events captured: {len(backend.get_events())}")

    print("\n\n4. Testing Data Processing:")
    print("-" * 80)
    backend.clear_events()
    backend.start()
    result = process_data([1, 2, 3, 4, 5])
    backend.stop()
    print(f"\nResult: {result}")
    print(f"Events captured: {len(backend.get_events())}")

    print("\n\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)

    # Show summary of all events
    all_events = backend.get_events()
    print(f"\nTotal events in final trace: {len(all_events)}")

    # Count by event type
    event_counts = {}
    for event in all_events:
        event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

    print("\nEvent breakdown:")
    for event_type, count in sorted(event_counts.items()):
        print(f"  {event_type:15s}: {count}")


if __name__ == '__main__':
    main()
