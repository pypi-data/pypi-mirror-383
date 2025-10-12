"""
Demonstration of selective instrumentation with PEP 669 backend.

This example shows how to use include/exclude patterns to selectively
trace only specific modules or packages in your application.
"""

import sys

# Check Python version
if sys.version_info < (3, 12):
    print("This example requires Python 3.12+ for PEP 669 support")
    sys.exit(1)

from breadcrumb.instrumentation.pep669_backend import PEP669Backend


# Simulate a myapp package structure
class MyAppModule:
    """Simulates myapp module"""

    @staticmethod
    def main_function(x, y):
        """Main application function"""
        return x + y

    @staticmethod
    def helper_function(data):
        """Helper function"""
        return data * 2


class MyAppVendor:
    """Simulates myapp.vendor module (should be excluded)"""

    @staticmethod
    def vendor_function(value):
        """Vendor library function"""
        return value + 100


class MyAppTests:
    """Simulates myapp.tests module (should be excluded)"""

    @staticmethod
    def test_function():
        """Test function"""
        return "test result"


def demo_basic_selective_instrumentation():
    """Demo 1: Include only specific patterns"""
    print("\n" + "="*70)
    print("Demo 1: Basic Selective Instrumentation")
    print("Pattern: include=['__main__']")
    print("="*70)

    backend = PEP669Backend(
        include_patterns=['__main__'],
        exclude_patterns=[]  # Clear default excludes for demo
    )

    backend.start()

    # This should be traced (in __main__)
    result1 = MyAppModule.main_function(10, 20)
    result2 = MyAppModule.helper_function(5)

    backend.stop()

    events = backend.get_events()
    call_events = [e for e in events if e.event_type == 'call']

    print(f"\nCaptured {len(call_events)} call events:")
    for event in call_events:
        print(f"  - {event.function_name}() in {event.module_name}")

    print(f"\nResults: main_function={result1}, helper_function={result2}")


def demo_exclude_patterns():
    """Demo 2: Exclude specific patterns"""
    print("\n" + "="*70)
    print("Demo 2: Exclude Patterns")
    print("Pattern: include=['*'], exclude=['__main__']")
    print("="*70)

    backend = PEP669Backend(
        include_patterns=['*'],
        exclude_patterns=['__main__']
    )

    backend.start()

    # These should NOT be traced (excluded)
    result1 = MyAppModule.main_function(10, 20)
    result2 = MyAppModule.helper_function(5)

    backend.stop()

    events = backend.get_events()
    call_events = [e for e in events if e.event_type == 'call']

    print(f"\nCaptured {len(call_events)} call events (should be 0 for our functions):")
    for event in call_events[:5]:  # Show first 5
        print(f"  - {event.function_name}() in {event.module_name}")

    print(f"\nResults: main_function={result1}, helper_function={result2}")


def demo_wildcard_patterns():
    """Demo 3: Wildcard patterns with submodules"""
    print("\n" + "="*70)
    print("Demo 3: Wildcard Patterns")
    print("Pattern: include=['myapp.*'], exclude=['myapp.vendor.*', 'myapp.tests.*']")
    print("="*70)

    # For this demo, we'll show the pattern matching logic
    backend = PEP669Backend(
        include_patterns=['myapp.*'],
        exclude_patterns=['myapp.vendor.*', 'myapp.tests.*']
    )

    test_modules = [
        'myapp',
        'myapp.core',
        'myapp.core.handlers',
        'myapp.vendor',
        'myapp.vendor.lib',
        'myapp.tests',
        'myapp.tests.unit',
        'other.module',
    ]

    print("\nPattern matching results:")
    for module in test_modules:
        # Simulate frame and code objects
        class MockCode:
            co_filename = f"{module}.py"
            co_name = "test"
            co_flags = 0
            co_firstlineno = 1

        class MockFrame:
            f_globals = {'__name__': module}
            f_lineno = 1

        should_trace = backend._should_trace(MockCode(), MockFrame())
        status = "TRACED" if should_trace else "EXCLUDED"
        print(f"  {module:30s} -> {status}")


def demo_default_excludes():
    """Demo 4: Default excludes for standard library"""
    print("\n" + "="*70)
    print("Demo 4: Default Excludes")
    print("Default excludes filter out standard library modules")
    print("="*70)

    backend = PEP669Backend()  # Use default patterns

    print("\nDefault exclude patterns:")
    for pattern in backend.exclude_patterns:
        print(f"  - {pattern}")

    print("\nDefault include patterns:")
    for pattern in backend.include_patterns:
        print(f"  - {pattern}")


def demo_performance_comparison():
    """Demo 5: Performance with and without filtering"""
    print("\n" + "="*70)
    print("Demo 5: Performance Impact")
    print("Comparing event counts with different filtering strategies")
    print("="*70)

    import time

    def work_function():
        """Function that does some work"""
        result = 0
        for i in range(100):
            result += i
        return result

    # Test 1: No filtering (trace everything)
    backend1 = PEP669Backend(
        include_patterns=['*'],
        exclude_patterns=[]
    )
    backend1.start()
    start1 = time.time()
    for _ in range(10):
        work_function()
    elapsed1 = time.time() - start1
    backend1.stop()
    events1 = len(backend1.get_events())

    # Test 2: With filtering (exclude this module)
    backend2 = PEP669Backend(
        include_patterns=['nonexistent.*'],
        exclude_patterns=['__main__']
    )
    backend2.start()
    start2 = time.time()
    for _ in range(10):
        work_function()
    elapsed2 = time.time() - start2
    backend2.stop()
    events2 = len(backend2.get_events())

    print(f"\nWithout filtering:")
    print(f"  Events captured: {events1}")
    print(f"  Time: {elapsed1*1000:.2f}ms")

    print(f"\nWith filtering (excluded):")
    print(f"  Events captured: {events2}")
    print(f"  Time: {elapsed2*1000:.2f}ms")

    if events1 > 0:
        reduction = (1 - events2/events1) * 100
        print(f"\nEvent reduction: {reduction:.1f}%")


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("BREADCRUMB SELECTIVE INSTRUMENTATION DEMO")
    print("PEP 669 Backend - Include/Exclude Pattern Filtering")
    print("="*70)

    try:
        demo_basic_selective_instrumentation()
        demo_exclude_patterns()
        demo_wildcard_patterns()
        demo_default_excludes()
        demo_performance_comparison()

        print("\n" + "="*70)
        print("All demos completed successfully!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
