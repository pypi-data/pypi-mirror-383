"""
Example 1: Simple Function Tracing

This is a "hello world" example demonstrating basic Breadcrumb usage.
Learn how to trace simple function calls and query the results.
"""

import sys
sys.path.insert(0, '../../src')

import breadcrumb

# Initialize Breadcrumb tracing
breadcrumb.init()


def add(a, b):
    """Add two numbers."""
    return a + b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}!"


def calculate_total(price, quantity, tax_rate=0.1):
    """Calculate total price with tax."""
    subtotal = multiply(price, quantity)
    tax = multiply(subtotal, tax_rate)
    total = add(subtotal, tax)
    return total


def main():
    print("=" * 60)
    print("Breadcrumb Example 1: Simple Function Tracing")
    print("=" * 60)
    print()

    # Execute some simple functions
    print("1. Testing add function:")
    result = add(5, 3)
    print(f"   add(5, 3) = {result}")
    print()

    print("2. Testing multiply function:")
    result = multiply(7, 6)
    print(f"   multiply(7, 6) = {result}")
    print()

    print("3. Testing greet function:")
    message = greet("Alice")
    print(f"   greet('Alice') = '{message}'")
    print()

    print("4. Testing complex calculation:")
    total = calculate_total(price=100, quantity=2, tax_rate=0.15)
    print(f"   calculate_total(100, 2, 0.15) = ${total:.2f}")
    print()

    print("=" * 60)
    print("Execution complete! Traces captured.")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("  1. Run: breadcrumb list")
    print("  2. Run: breadcrumb query \"SELECT * FROM events WHERE function_name='add'\"")
    print("  3. See README.md for more query examples")
    print()


if __name__ == "__main__":
    main()
