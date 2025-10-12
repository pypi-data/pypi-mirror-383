"""
Example 3: Exception Debugging

This example demonstrates how to use Breadcrumb to debug exceptions.
It includes intentional bugs and shows how to trace back to find root causes.
"""

import sys
sys.path.insert(0, '../../src')

import breadcrumb

# Initialize Breadcrumb tracing
breadcrumb.init()


class User:
    """Simple user class for demonstration."""

    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email

    def get_domain(self):
        """Extract domain from email."""
        # BUG: Doesn't handle missing email!
        return self.email.split('@')[1]


def load_user_data(user_id):
    """
    Load user from a fake database.
    BUG: Returns None for invalid IDs.
    """
    database = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@company.org"},
        3: {"name": "Charlie", "email": None},  # BUG: Missing email!
    }

    user_data = database.get(user_id)
    if user_data:
        return User(user_id, user_data["name"], user_data["email"])
    return None


def calculate_discount(price, discount_percent):
    """
    Calculate discounted price.
    BUG: Doesn't validate inputs!
    """
    if discount_percent > 100:
        raise ValueError("Discount cannot exceed 100%")

    # BUG: Division by zero if discount_percent is 0
    multiplier = 100 / (100 - discount_percent)
    return price / multiplier


def process_order(user_id, items):
    """
    Process a user's order.
    BUG: Doesn't check if user exists!
    """
    user = load_user_data(user_id)

    # BUG: This will fail if user is None
    print(f"Processing order for {user.name}...")

    total = 0
    for item in items:
        # BUG: Doesn't handle missing 'price' key
        total += item["price"] * item.get("quantity", 1)

    # BUG: Doesn't handle invalid discount
    discount = calculate_discount(total, items[0].get("discount", 0))

    print(f"Total: ${total:.2f}, After discount: ${discount:.2f}")
    return discount


def send_email(user_id, subject, body):
    """
    Send an email to a user.
    BUG: Doesn't handle users without email!
    """
    user = load_user_data(user_id)

    # BUG: This will fail if email is None
    domain = user.get_domain()

    print(f"Sending email to {user.name} at {user.email} (domain: {domain})")
    return True


def divide_numbers(a, b):
    """
    Divide two numbers.
    Classic division by zero bug.
    """
    return a / b  # BUG: No check for b == 0


def access_nested_data(data, path):
    """
    Access nested dictionary data.
    BUG: Doesn't handle missing keys!
    """
    result = data
    for key in path:
        result = result[key]  # BUG: KeyError if key doesn't exist
    return result


def example_1_none_access():
    """Demonstrate NoneType attribute access error."""
    print("\n" + "=" * 60)
    print("Example 1: NoneType Attribute Access")
    print("=" * 60)
    print("Problem: Trying to process order for non-existent user")
    print()

    try:
        # User ID 999 doesn't exist, returns None
        order = process_order(
            user_id=999,
            items=[{"name": "Widget", "price": 10.0, "quantity": 2}]
        )
        print(f"Order processed: ${order:.2f}")
    except AttributeError as e:
        print(f"ERROR: {e}")
        print()
        print("How to debug with Breadcrumb:")
        print("  1. Run: breadcrumb exceptions --since 1m")
        print("  2. Find the exception trace")
        print("  3. Look at the arguments passed to process_order()")
        print("  4. See that load_user_data() returned None")
        print("  5. Root cause: User 999 doesn't exist in database")


def example_2_division_by_zero():
    """Demonstrate division by zero error."""
    print("\n" + "=" * 60)
    print("Example 2: Division By Zero")
    print("=" * 60)
    print("Problem: Calculating discount with invalid percentage")
    print()

    try:
        price = calculate_discount(100, 100)  # 100% discount causes division by zero
        print(f"Discounted price: ${price:.2f}")
    except ZeroDivisionError as e:
        print(f"ERROR: {e}")
        print()
        print("How to debug with Breadcrumb:")
        print("  1. Run: breadcrumb exceptions")
        print("  2. See calculate_discount() was called with (100, 100)")
        print("  3. Trace shows: 100 - 100 = 0 in denominator")
        print("  4. Root cause: Discount of 100% not handled correctly")


def example_3_key_error():
    """Demonstrate KeyError in nested data access."""
    print("\n" + "=" * 60)
    print("Example 3: Missing Key in Nested Data")
    print("=" * 60)
    print("Problem: Accessing non-existent nested key")
    print()

    try:
        data = {
            "user": {
                "name": "Alice",
                "profile": {
                    "age": 30
                }
            }
        }
        # Trying to access a key that doesn't exist
        result = access_nested_data(data, ["user", "profile", "address", "city"])
        print(f"City: {result}")
    except KeyError as e:
        print(f"ERROR: Missing key {e}")
        print()
        print("How to debug with Breadcrumb:")
        print("  1. Run: breadcrumb get <trace-id>")
        print("  2. See access_nested_data() arguments: path=['user', 'profile', 'address', 'city']")
        print("  3. See data structure doesn't have 'address' key")
        print("  4. Root cause: Trying to access data['user']['profile']['address'] which doesn't exist")


def example_4_none_email():
    """Demonstrate error with None email field."""
    print("\n" + "=" * 60)
    print("Example 4: None Value in Required Field")
    print("=" * 60)
    print("Problem: User has None email, can't send message")
    print()

    try:
        # User 3 has email=None
        send_email(user_id=3, subject="Welcome", body="Hello!")
    except AttributeError as e:
        print(f"ERROR: {e}")
        print()
        print("How to debug with Breadcrumb:")
        print("  1. Run: breadcrumb exceptions --details")
        print("  2. See send_email() called with user_id=3")
        print("  3. Trace load_user_data(3) which returned User with email=None")
        print("  4. See get_domain() tried to call .split() on None")
        print("  5. Root cause: Database has None email for user 3")


def example_5_successful_case():
    """Demonstrate a successful case for comparison."""
    print("\n" + "=" * 60)
    print("Example 5: Successful Execution (for comparison)")
    print("=" * 60)
    print("Processing valid order...")
    print()

    try:
        order = process_order(
            user_id=1,
            items=[
                {"name": "Widget", "price": 10.0, "quantity": 2, "discount": 10}
            ]
        )
        print(f"Order processed successfully: ${order:.2f}")
        print()
        print("Compare with failures:")
        print("  1. Run: breadcrumb list")
        print("  2. See both successful and failed traces")
        print("  3. Compare arguments and execution paths")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    """Run all exception examples."""
    print("=" * 60)
    print("Breadcrumb Example 3: Exception Debugging")
    print("=" * 60)
    print()
    print("This example intentionally triggers errors to demonstrate")
    print("how Breadcrumb helps you debug exceptions.")
    print()

    # Run each example (each will fail)
    example_1_none_access()
    example_2_division_by_zero()
    example_3_key_error()
    example_4_none_email()
    example_5_successful_case()

    print("\n" + "=" * 60)
    print("Examples complete! All exceptions captured in traces.")
    print("=" * 60)
    print()
    print("Debugging Workflow:")
    print("  1. Run: breadcrumb exceptions")
    print("  2. Find the exception you want to debug")
    print("  3. Run: breadcrumb get <trace-id> to see full execution")
    print("  4. Examine function arguments and return values")
    print("  5. Trace backwards to find root cause")
    print()
    print("See README.md for detailed debugging examples")
    print()


if __name__ == "__main__":
    main()
