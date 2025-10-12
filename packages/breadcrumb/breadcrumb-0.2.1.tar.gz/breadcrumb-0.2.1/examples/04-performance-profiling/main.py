"""
Example 4: Performance Profiling

This example demonstrates how to use Breadcrumb to identify performance
bottlenecks, analyze slow functions, and guide optimization.
"""

import sys
sys.path.insert(0, '../../src')

import time
import random
import breadcrumb

# Initialize Breadcrumb tracing
breadcrumb.init()


def fast_function(n):
    """A fast function that completes quickly."""
    return n * 2


def slow_function(n):
    """
    A slow function with an intentional delay.
    BOTTLENECK: This sleep simulates slow I/O or computation.
    """
    time.sleep(0.1)  # 100ms delay
    return n * n


def very_slow_function(n):
    """
    A very slow function with a longer delay.
    BOTTLENECK: This sleep simulates very slow operations.
    """
    time.sleep(0.5)  # 500ms delay
    return n ** 3


def inefficient_loop(items):
    """
    Inefficient implementation using nested loops.
    BOTTLENECK: O(n²) complexity when O(n) would work.
    """
    result = []
    for i in range(len(items)):
        # Inefficient: Searches entire list for each item
        for j in range(len(items)):
            if items[j]["id"] == i:
                result.append(items[j])
                break
    return result


def efficient_loop(items):
    """
    Efficient implementation using dictionary lookup.
    OPTIMIZED: O(n) complexity.
    """
    # Build a lookup dictionary
    lookup = {item["id"]: item for item in items}

    # Fast O(1) lookups
    result = [lookup[i] for i in range(len(items)) if i in lookup]
    return result


def wasteful_string_concat(strings):
    """
    Inefficient string concatenation.
    BOTTLENECK: String concatenation is O(n²) in Python.
    """
    result = ""
    for s in strings:
        result += s  # Creates a new string each time!
    return result


def efficient_string_concat(strings):
    """
    Efficient string concatenation.
    OPTIMIZED: Using join() is O(n).
    """
    return "".join(strings)


def redundant_computation(n):
    """
    Function that recomputes the same value repeatedly.
    BOTTLENECK: Doesn't cache expensive computation.
    """
    total = 0
    for i in range(n):
        # Recomputes slow_function(10) every iteration!
        total += slow_function(10)
    return total


def cached_computation(n):
    """
    Function that caches expensive computation.
    OPTIMIZED: Computes once, reuses result.
    """
    cached_value = slow_function(10)  # Compute once
    total = 0
    for i in range(n):
        total += cached_value  # Reuse cached value
    return total


def process_data(data):
    """
    Process data through multiple steps.
    Demonstrates cascading performance issues.
    """
    # Step 1: Filter (fast)
    filtered = [x for x in data if x > 0]

    # Step 2: Transform (slow - has bottleneck!)
    transformed = [slow_function(x) for x in filtered]

    # Step 3: Aggregate (fast)
    total = sum(transformed)

    return total


def optimized_process_data(data):
    """
    Optimized data processing.
    Removes unnecessary slow operations.
    """
    # Step 1: Filter (fast)
    filtered = [x for x in data if x > 0]

    # Step 2: Transform (optimized - use fast function!)
    transformed = [fast_function(x) for x in filtered]

    # Step 3: Aggregate (fast)
    total = sum(transformed)

    return total


def example_1_identify_bottleneck():
    """Example 1: Identify the slowest function."""
    print("\n" + "=" * 60)
    print("Example 1: Identify Performance Bottleneck")
    print("=" * 60)
    print("Running multiple functions with different speeds...")
    print()

    # Call functions with varying performance
    for i in range(5):
        fast_function(i)

    for i in range(3):
        slow_function(i)

    very_slow_function(1)

    print("Functions executed:")
    print("  - fast_function: 5 calls")
    print("  - slow_function: 3 calls")
    print("  - very_slow_function: 1 call")
    print()
    print("Query to find bottleneck:")
    print("  breadcrumb performance --sort duration")
    print()
    print("Expected result:")
    print("  very_slow_function should be slowest (~500ms)")
    print("  slow_function should be second (~100ms each)")
    print("  fast_function should be fastest (~0ms)")


def example_2_algorithm_optimization():
    """Example 2: Compare inefficient vs efficient algorithms."""
    print("\n" + "=" * 60)
    print("Example 2: Algorithm Optimization")
    print("=" * 60)
    print("Comparing O(n²) vs O(n) implementations...")
    print()

    # Create test data
    items = [{"id": i, "value": f"item_{i}"} for i in range(100)]

    # Inefficient version (O(n²))
    print("Running inefficient_loop (O(n²))...")
    start = time.time()
    result1 = inefficient_loop(items)
    elapsed1 = time.time() - start
    print(f"  Completed in {elapsed1*1000:.1f}ms")

    # Efficient version (O(n))
    print("Running efficient_loop (O(n))...")
    start = time.time()
    result2 = efficient_loop(items)
    elapsed2 = time.time() - start
    print(f"  Completed in {elapsed2*1000:.1f}ms")

    if elapsed1 > 0:
        improvement = (elapsed1 - elapsed2) / elapsed1 * 100
    else:
        improvement = 0
    print(f"  Improvement: {improvement:.1f}% faster")
    print()
    print("Query to compare:")
    print("  breadcrumb query \"SELECT function_name, AVG(duration_ms) FROM events WHERE function_name LIKE '%loop' GROUP BY function_name\"")


def example_3_string_operations():
    """Example 3: Optimize string operations."""
    print("\n" + "=" * 60)
    print("Example 3: String Operation Optimization")
    print("=" * 60)
    print("Comparing string concatenation methods...")
    print()

    # Create test strings
    strings = [f"string_{i}_" for i in range(1000)]

    # Wasteful version
    print("Running wasteful_string_concat...")
    start = time.time()
    result1 = wasteful_string_concat(strings)
    elapsed1 = time.time() - start
    print(f"  Completed in {elapsed1*1000:.1f}ms")

    # Efficient version
    print("Running efficient_string_concat...")
    start = time.time()
    result2 = efficient_string_concat(strings)
    elapsed2 = time.time() - start
    print(f"  Completed in {elapsed2*1000:.1f}ms")

    if elapsed1 > 0:
        improvement = (elapsed1 - elapsed2) / elapsed1 * 100
    else:
        improvement = 0
    print(f"  Improvement: {improvement:.1f}% faster")


def example_4_redundant_computation():
    """Example 4: Eliminate redundant computation."""
    print("\n" + "=" * 60)
    print("Example 4: Eliminate Redundant Computation")
    print("=" * 60)
    print("Comparing redundant vs cached computation...")
    print()

    # Redundant version
    print("Running redundant_computation (computes same value 10 times)...")
    start = time.time()
    result1 = redundant_computation(10)
    elapsed1 = time.time() - start
    print(f"  Completed in {elapsed1*1000:.1f}ms")

    # Cached version
    print("Running cached_computation (computes once, reuses)...")
    start = time.time()
    result2 = cached_computation(10)
    elapsed2 = time.time() - start
    print(f"  Completed in {elapsed2*1000:.1f}ms")

    if elapsed1 > 0:
        improvement = (elapsed1 - elapsed2) / elapsed1 * 100
    else:
        improvement = 0
    print(f"  Improvement: {improvement:.1f}% faster")
    print()
    print("Trace insight:")
    print("  - redundant_computation calls slow_function 10 times")
    print("  - cached_computation calls slow_function only 1 time")


def example_5_end_to_end_optimization():
    """Example 5: End-to-end pipeline optimization."""
    print("\n" + "=" * 60)
    print("Example 5: End-to-End Pipeline Optimization")
    print("=" * 60)
    print("Optimizing a complete data processing pipeline...")
    print()

    # Test data
    data = list(range(-50, 51))  # -50 to 50

    # Original version
    print("Running original process_data (with bottleneck)...")
    start = time.time()
    result1 = process_data(data)
    elapsed1 = time.time() - start
    print(f"  Completed in {elapsed1*1000:.1f}ms")

    # Optimized version
    print("Running optimized_process_data (bottleneck removed)...")
    start = time.time()
    result2 = optimized_process_data(data)
    elapsed2 = time.time() - start
    print(f"  Completed in {elapsed2*1000:.1f}ms")

    if elapsed1 > 0:
        improvement = (elapsed1 - elapsed2) / elapsed1 * 100
    else:
        improvement = 0
    print(f"  Improvement: {improvement:.1f}% faster")
    print()
    print("Analysis workflow:")
    print("  1. Run: breadcrumb performance process_data")
    print("  2. See that slow_function calls are the bottleneck")
    print("  3. Replace with fast_function")
    print("  4. Verify improvement with new trace")


def main():
    """Run all performance profiling examples."""
    print("=" * 60)
    print("Breadcrumb Example 4: Performance Profiling")
    print("=" * 60)
    print()
    print("This example demonstrates performance optimization")
    print("using Breadcrumb to identify and fix bottlenecks.")
    print()

    # Run all examples
    example_1_identify_bottleneck()
    example_2_algorithm_optimization()
    example_3_string_operations()
    example_4_redundant_computation()
    example_5_end_to_end_optimization()

    print("\n" + "=" * 60)
    print("Examples complete! Performance data captured.")
    print("=" * 60)
    print()
    print("Profiling Workflow:")
    print("  1. Run: breadcrumb performance --sort duration")
    print("  2. Identify slowest functions")
    print("  3. Run: breadcrumb get <trace-id> for detailed timing")
    print("  4. Optimize the bottleneck")
    print("  5. Re-run and compare performance")
    print()
    print("See README.md for detailed optimization strategies")
    print()


if __name__ == "__main__":
    main()
