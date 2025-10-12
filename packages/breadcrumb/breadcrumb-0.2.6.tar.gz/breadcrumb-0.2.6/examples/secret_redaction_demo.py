"""
Secret Redaction Demo - Breadcrumb AI Tracer

This script demonstrates the secret redaction engine that automatically
detects and redacts sensitive information from traced variable values.

Features demonstrated:
1. Password redaction
2. API key and token redaction
3. Credit card detection
4. SSN detection
5. JWT token detection
6. Custom pattern configuration
7. Nested structure handling
8. No false positives
"""

from breadcrumb.capture.secret_redactor import redact_secrets, SecretRedactor
import json


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_example(description: str, original: dict, redacted: dict):
    """Print an example with original and redacted data."""
    print(f"\n{description}")
    print("-" * 70)
    print("Original:")
    print(json.dumps(original, indent=2))
    print("\nRedacted:")
    print(json.dumps(redacted, indent=2))


def demo_basic_patterns():
    """Demonstrate basic password and API key patterns."""
    print_section("Demo 1: Basic Password and API Key Redaction")

    # Password redaction
    data1 = {"user": "alice", "password": "secret123", "email": "alice@example.com"}
    redacted1 = redact_secrets(data1)
    print_example("Password redaction", data1, redacted1)

    # API key redaction
    data2 = {"service": "openai", "api_key": "sk-1234567890abcdef", "model": "gpt-4"}
    redacted2 = redact_secrets(data2)
    print_example("API key redaction", data2, redacted2)

    # Multiple sensitive keys
    data3 = {
        "username": "bob",
        "password": "mypassword",
        "token": "bearer-xyz123",
        "email": "bob@example.com"
    }
    redacted3 = redact_secrets(data3)
    print_example("Multiple sensitive keys", data3, redacted3)


def demo_value_based_detection():
    """Demonstrate value-based pattern detection."""
    print_section("Demo 2: Value-Based Detection (Credit Cards, SSNs, JWTs)")

    # Credit card detection
    data1 = {
        "user": "alice",
        "payment_info": "Card: 4532 1488 0343 6467"
    }
    redacted1 = redact_secrets(data1)
    print_example("Credit card detection", data1, redacted1)

    # SSN detection
    data2 = {
        "name": "John Doe",
        "ssn": "123-45-6789",
        "phone": "555-123-4567"  # Not SSN format
    }
    redacted2 = redact_secrets(data2)
    print_example("SSN detection (phone NOT redacted)", data2, redacted2)

    # JWT token detection
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123"
    data3 = {
        "user": "alice",
        "jwt_token": jwt,
        "session_id": "abc123"
    }
    redacted3 = redact_secrets(data3)
    print_example("JWT token detection", data3, redacted3)

    # AWS key detection
    data4 = {
        "service": "aws",
        "access_key": "AKIAIOSFODNN7EXAMPLE",
        "region": "us-east-1"
    }
    redacted4 = redact_secrets(data4)
    print_example("AWS access key detection", data4, redacted4)


def demo_nested_structures():
    """Demonstrate redaction in nested structures."""
    print_section("Demo 3: Nested Structure Handling")

    # Nested dictionary
    data1 = {
        "user": {
            "name": "alice",
            "credentials": {
                "password": "secret123",
                "api_key": "sk-abc123"
            },
            "metadata": {
                "created": "2023-01-01",
                "email": "alice@example.com"
            }
        }
    }
    redacted1 = redact_secrets(data1)
    print_example("Nested dictionary", data1, redacted1)

    # List of users with passwords
    data2 = {
        "users": [
            {"name": "alice", "password": "secret1", "role": "admin"},
            {"name": "bob", "password": "secret2", "role": "user"}
        ]
    }
    redacted2 = redact_secrets(data2)
    print_example("List of dictionaries", data2, redacted2)


def demo_custom_patterns():
    """Demonstrate custom pattern configuration."""
    print_section("Demo 4: Custom Pattern Configuration")

    # Custom patterns with wildcard
    data1 = {
        "my_secret_key": "value1",
        "my_secret_token": "value2",
        "user": "alice"
    }
    redacted1 = redact_secrets(data1, patterns=["my_secret_*"])
    print_example("Wildcard pattern (my_secret_*)", data1, redacted1)

    # Custom SecretRedactor instance
    redactor = SecretRedactor(custom_patterns=["internal_token", "session_*"])
    data2 = {
        "internal_token": "xyz123",
        "session_id": "abc456",
        "session_user": "alice",
        "public_id": "789"
    }
    redacted2 = redactor.redact(data2)
    print_example("Custom SecretRedactor instance", data2, redacted2)


def demo_no_false_positives():
    """Demonstrate that legitimate data is not redacted."""
    print_section("Demo 5: No False Positives")

    data = {
        "user": "alice",
        "email": "alice@example.com",
        "url": "https://example.com/api",
        "phone": "555-123-4567",  # Not SSN format
        "date": "2023-01-01",
        "user_id": "12345",
        "transaction_id": "tx-67890",
        "description": "This is a description with the word password in it"
    }
    redacted = redact_secrets(data)
    print_example("Legitimate data (NOT redacted)", data, redacted)


def demo_performance():
    """Demonstrate performance of redaction."""
    print_section("Demo 6: Performance")

    import time

    # Simple event
    event = {"user": "alice", "password": "secret123", "email": "alice@example.com"}

    iterations = 10000
    start = time.perf_counter()
    for _ in range(iterations):
        redact_secrets(event)
    end = time.perf_counter()

    avg_time = (end - start) / iterations
    print(f"\nSimple event redaction:")
    print(f"  Iterations: {iterations:,}")
    print(f"  Total time: {(end - start)*1000:.2f} ms")
    print(f"  Average: {avg_time*1000:.4f} ms/event")
    print(f"  Status: {'PASS' if avg_time < 0.001 else 'FAIL'} (< 1ms requirement)")

    # Complex nested event
    complex_event = {
        "user": {
            "name": "alice",
            "credentials": {
                "password": "secret123",
                "api_key": "sk-1234567890"
            }
        },
        "metadata": {
            "tags": ["admin", "user"],
            "created": "2023-01-01"
        }
    }

    iterations = 1000
    start = time.perf_counter()
    for _ in range(iterations):
        redact_secrets(complex_event)
    end = time.perf_counter()

    avg_time = (end - start) / iterations
    print(f"\nComplex nested event redaction:")
    print(f"  Iterations: {iterations:,}")
    print(f"  Total time: {(end - start)*1000:.2f} ms")
    print(f"  Average: {avg_time*1000:.4f} ms/event")
    print(f"  Status: {'PASS' if avg_time < 0.001 else 'FAIL'} (< 1ms requirement)")


def demo_real_world_example():
    """Demonstrate a real-world API request/response scenario."""
    print_section("Demo 7: Real-World API Request/Response")

    # Simulated API request
    api_request = {
        "method": "POST",
        "url": "https://api.example.com/auth/login",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0In0.abc"
        },
        "body": {
            "username": "alice@example.com",
            "password": "mypassword123",
            "remember_me": True
        }
    }
    redacted_request = redact_secrets(api_request)
    print_example("API Request (with sensitive data)", api_request, redacted_request)

    # Simulated database query
    db_query = {
        "query": "SELECT * FROM users WHERE email = ?",
        "params": ["alice@example.com"],
        "connection": {
            "host": "db.example.com",
            "port": 5432,
            "username": "db_user",
            "password": "db_secret_password",
            "database": "myapp"
        }
    }
    redacted_query = redact_secrets(db_query)
    print_example("Database Query (with credentials)", db_query, redacted_query)


def main():
    """Run all demonstration scenarios."""
    print("\n" + "=" * 70)
    print("  BREADCRUMB AI TRACER - SECRET REDACTION ENGINE DEMO")
    print("=" * 70)
    print("\nThis demo shows how the secret redaction engine automatically")
    print("detects and redacts sensitive information from trace data.")

    demo_basic_patterns()
    demo_value_based_detection()
    demo_nested_structures()
    demo_custom_patterns()
    demo_no_false_positives()
    demo_performance()
    demo_real_world_example()

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Passwords, API keys, tokens automatically redacted")
    print("  2. Credit cards, SSNs, JWTs detected in values")
    print("  3. Nested structures handled recursively")
    print("  4. Custom patterns supported")
    print("  5. No false positives on legitimate data")
    print("  6. Performance < 1ms per event")
    print("\n")


if __name__ == "__main__":
    main()
