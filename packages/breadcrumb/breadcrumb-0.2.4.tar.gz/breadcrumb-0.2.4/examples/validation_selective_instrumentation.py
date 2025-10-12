"""
Validation script for Task 1.3: Selective Instrumentation

This script validates the acceptance criteria from PLAN.md:
- Supports glob patterns: include=['myapp.*'], exclude=['myapp.vendor.*']
- Filters at instrumentation time (not post-capture) for performance
- Default excludes: standard library, site-packages (configurable)
- Unit tests verify filtering logic
"""

import sys

if sys.version_info < (3, 12):
    print("SKIP: PEP 669 requires Python 3.12+")
    sys.exit(0)

from breadcrumb.instrumentation.pep669_backend import PEP669Backend


def test_glob_patterns():
    """Test glob pattern support"""
    print("\n[TEST 1] Glob Pattern Support")
    print("-" * 50)

    backend = PEP669Backend(
        include_patterns=['myapp.*'],
        exclude_patterns=['myapp.vendor.*']
    )

    # Mock test modules
    class MockCode:
        def __init__(self, module_name):
            self.co_filename = f"{module_name}.py"
            self.co_name = "test"
            self.co_flags = 0
            self.co_firstlineno = 1

    class MockFrame:
        def __init__(self, module_name):
            self.f_globals = {'__name__': module_name}
            self.f_lineno = 1

    test_cases = [
        ('myapp', True),
        ('myapp.core', True),
        ('myapp.core.handlers', True),
        ('myapp.vendor', False),
        ('myapp.vendor.lib', False),
        ('other.module', False),
    ]

    all_passed = True
    for module, expected in test_cases:
        result = backend._should_trace(MockCode(module), MockFrame(module))
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"  {module:25s} -> traced={str(result):5s} (expected={str(expected):5s}) [{status}]")

    print(f"\nResult: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


def test_instrumentation_time_filtering():
    """Test that filtering happens at instrumentation time"""
    print("\n[TEST 2] Instrumentation-Time Filtering")
    print("-" * 50)

    # Create backend that excludes current module
    backend = PEP669Backend(
        include_patterns=['nonexistent.*'],
        exclude_patterns=['__main__']
    )

    backend.start()

    # Call functions that should be filtered out
    def test_func1():
        return 1

    def test_func2():
        return 2

    # Execute many times
    for _ in range(100):
        test_func1()
        test_func2()

    backend.stop()
    events = backend.get_events()

    # Check that NO events were captured (filtered at instrumentation time)
    test_events = [e for e in events if e.function_name in ['test_func1', 'test_func2']]

    print(f"  Functions called: 200 times")
    print(f"  Events captured: {len(test_events)}")
    print(f"  Expected: 0 (filtered at instrumentation time)")

    passed = len(test_events) == 0
    print(f"\nResult: {'PASS' if passed else 'FAIL'}")
    return passed


def test_default_excludes():
    """Test default excludes for standard library"""
    print("\n[TEST 3] Default Excludes")
    print("-" * 50)

    backend = PEP669Backend()  # Use defaults

    # Check that standard library modules are in default excludes
    expected_excludes = ['threading', 'sys', 'os']
    all_present = all(exclude in backend.exclude_patterns for exclude in expected_excludes)

    print(f"  Default exclude patterns: {len(backend.exclude_patterns)}")
    print(f"  Expected excludes present: {expected_excludes}")
    print(f"  All present: {all_present}")

    print(f"\n  Default excludes:")
    for pattern in backend.exclude_patterns[:10]:
        print(f"    - {pattern}")

    print(f"\nResult: {'PASS' if all_present else 'FAIL'}")
    return all_present


def test_exclude_precedence():
    """Test that exclude patterns take precedence over include"""
    print("\n[TEST 4] Exclude Precedence")
    print("-" * 50)

    backend = PEP669Backend(
        include_patterns=['myapp.*'],
        exclude_patterns=['myapp.tests.*']
    )

    class MockCode:
        co_filename = "myapp/tests/test.py"
        co_name = "test"
        co_flags = 0
        co_firstlineno = 1

    class MockFrame:
        f_globals = {'__name__': 'myapp.tests.unit'}
        f_lineno = 1

    # myapp.tests.unit matches include pattern myapp.* but also matches exclude pattern myapp.tests.*
    # Exclude should win
    result = backend._should_trace(MockCode(), MockFrame())

    print(f"  Module: myapp.tests.unit")
    print(f"  Matches include 'myapp.*': Yes")
    print(f"  Matches exclude 'myapp.tests.*': Yes")
    print(f"  Should trace: {result}")
    print(f"  Expected: False (exclude wins)")

    passed = result is False
    print(f"\nResult: {'PASS' if passed else 'FAIL'}")
    return passed


def test_pattern_matching():
    """Test pattern matching logic"""
    print("\n[TEST 5] Pattern Matching Logic")
    print("-" * 50)

    backend = PEP669Backend()

    test_cases = [
        # (text, pattern, expected)
        ('myapp', 'myapp', True),
        ('myapp.sub', 'myapp', False),
        ('myapp', 'myapp.*', True),
        ('myapp.sub', 'myapp.*', True),
        ('myapp.sub.deep', 'myapp.*', True),
        ('other', 'myapp.*', False),
        ('myappother', 'myapp.*', False),
        ('anything', '*', True),
    ]

    all_passed = True
    for text, pattern, expected in test_cases:
        result = backend._match_pattern(text, pattern)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"  _match_pattern('{text}', '{pattern}') = {str(result):5s} (expected {str(expected):5s}) [{status}]")

    print(f"\nResult: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


def main():
    """Run all validation tests"""
    print("=" * 70)
    print("VALIDATION: Task 1.3 - Selective Instrumentation")
    print("PEP 669 Backend - Include/Exclude Pattern Filtering")
    print("=" * 70)

    results = []

    try:
        results.append(("Glob Patterns", test_glob_patterns()))
        results.append(("Instrumentation-Time Filtering", test_instrumentation_time_filtering()))
        results.append(("Default Excludes", test_default_excludes()))
        results.append(("Exclude Precedence", test_exclude_precedence()))
        results.append(("Pattern Matching", test_pattern_matching()))

    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name:40s} [{status}]")

    all_passed = all(passed for _, passed in results)
    print("\n" + "=" * 70)
    if all_passed:
        print("ALL TESTS PASSED")
        print("Task 1.3 acceptance criteria validated successfully!")
    else:
        print("SOME TESTS FAILED")
        print("Please review the failures above.")
    print("=" * 70 + "\n")

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
