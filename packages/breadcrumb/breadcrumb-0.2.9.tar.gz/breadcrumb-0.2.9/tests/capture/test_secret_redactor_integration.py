"""
Integration tests for secret redaction with TraceEvent.

This test suite demonstrates how the secret redactor integrates with
the instrumentation backend's TraceEvent objects.
"""

import pytest
from datetime import datetime
from dataclasses import asdict
from breadcrumb.capture.secret_redactor import redact_secrets
from breadcrumb.instrumentation.pep669_backend import TraceEvent


class TestTraceEventIntegration:
    """Test secret redaction integration with TraceEvent objects."""

    def test_redact_trace_event_with_password(self):
        """Test redacting a TraceEvent containing password in args."""
        event = TraceEvent(
            event_type="call",
            timestamp=datetime.now(),
            thread_id=12345,
            function_name="authenticate",
            module_name="myapp.auth",
            file_path="/app/auth.py",
            line_number=42,
            args={"username": "alice", "password": "secret123"},
            kwargs={},
        )

        # Convert to dict for redaction
        event_dict = asdict(event)
        redacted = redact_secrets(event_dict)

        assert redacted["args"]["username"] == "alice"
        assert redacted["args"]["password"] == "[REDACTED]"

    def test_redact_trace_event_with_api_key(self):
        """Test redacting a TraceEvent containing API key."""
        event = TraceEvent(
            event_type="call",
            timestamp=datetime.now(),
            thread_id=12345,
            function_name="call_api",
            module_name="myapp.api",
            file_path="/app/api.py",
            line_number=100,
            args={"url": "https://api.example.com"},
            kwargs={"api_key": "sk-1234567890abcdef", "timeout": 30},
        )

        event_dict = asdict(event)
        redacted = redact_secrets(event_dict)

        assert redacted["args"]["url"] == "https://api.example.com"
        assert redacted["kwargs"]["api_key"] == "[REDACTED]"
        assert redacted["kwargs"]["timeout"] == 30

    def test_redact_trace_event_with_local_vars(self):
        """Test redacting a TraceEvent with sensitive local variables."""
        event = TraceEvent(
            event_type="line",
            timestamp=datetime.now(),
            thread_id=12345,
            function_name="process_payment",
            module_name="myapp.payment",
            file_path="/app/payment.py",
            line_number=50,
            local_vars={
                "amount": 100.50,
                "currency": "USD",
                "card_number": "4532 1488 0343 6467",
                "user_id": "12345"
            },
        )

        event_dict = asdict(event)
        redacted = redact_secrets(event_dict)

        assert redacted["local_vars"]["amount"] == 100.50
        assert redacted["local_vars"]["currency"] == "USD"
        assert redacted["local_vars"]["card_number"] == "[REDACTED]"
        assert redacted["local_vars"]["user_id"] == "12345"

    def test_redact_trace_event_with_jwt_in_return_value(self):
        """Test redacting a TraceEvent with JWT in return value."""
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123"
        event = TraceEvent(
            event_type="return",
            timestamp=datetime.now(),
            thread_id=12345,
            function_name="generate_token",
            module_name="myapp.auth",
            file_path="/app/auth.py",
            line_number=75,
            return_value={"token": jwt, "expires_in": 3600},
        )

        event_dict = asdict(event)
        redacted = redact_secrets(event_dict)

        assert redacted["return_value"]["token"] == "[REDACTED]"
        assert redacted["return_value"]["expires_in"] == 3600

    def test_redact_trace_event_metadata(self):
        """Test redacting TraceEvent with sensitive metadata."""
        event = TraceEvent(
            event_type="call",
            timestamp=datetime.now(),
            thread_id=12345,
            function_name="connect_db",
            module_name="myapp.db",
            file_path="/app/db.py",
            line_number=20,
            metadata={
                "host": "db.example.com",
                "port": 5432,
                "username": "db_user",
                "password": "db_secret",
                "database": "myapp"
            },
        )

        event_dict = asdict(event)
        redacted = redact_secrets(event_dict)

        assert redacted["metadata"]["host"] == "db.example.com"
        assert redacted["metadata"]["port"] == 5432
        assert redacted["metadata"]["username"] == "db_user"
        assert redacted["metadata"]["password"] == "[REDACTED]"
        assert redacted["metadata"]["database"] == "myapp"

    def test_redact_multiple_events(self):
        """Test redacting a batch of TraceEvents."""
        events = [
            TraceEvent(
                event_type="call",
                timestamp=datetime.now(),
                thread_id=12345,
                function_name="login",
                args={"username": "alice", "password": "secret1"},
            ),
            TraceEvent(
                event_type="call",
                timestamp=datetime.now(),
                thread_id=12345,
                function_name="fetch_user",
                args={"user_id": "123"},
            ),
            TraceEvent(
                event_type="return",
                timestamp=datetime.now(),
                thread_id=12345,
                function_name="login",
                return_value={"token": "abc123xyz", "success": True},
            ),
        ]

        events_dict = [asdict(event) for event in events]
        redacted_events = [redact_secrets(event) for event in events_dict]

        # First event - password redacted
        assert redacted_events[0]["args"]["password"] == "[REDACTED]"
        assert redacted_events[0]["args"]["username"] == "alice"

        # Second event - no sensitive data
        assert redacted_events[1]["args"]["user_id"] == "123"

        # Third event - token redacted (key-based)
        assert redacted_events[2]["return_value"]["token"] == "[REDACTED]"
        assert redacted_events[2]["return_value"]["success"] is True

    def test_redact_preserves_event_structure(self):
        """Test that redaction preserves TraceEvent structure."""
        event = TraceEvent(
            event_type="call",
            timestamp=datetime.now(),
            thread_id=12345,
            function_name="test_func",
            module_name="myapp.test",
            file_path="/app/test.py",
            line_number=10,
            args={"password": "secret"},
            kwargs={},
            return_value=None,
            local_vars=None,
            exception_type=None,
            exception_message=None,
            exception_traceback=None,
            is_async=False,
            metadata={},
        )

        event_dict = asdict(event)
        redacted = redact_secrets(event_dict)

        # Verify all fields are preserved
        assert set(redacted.keys()) == set(event_dict.keys())
        assert redacted["event_type"] == "call"
        assert redacted["function_name"] == "test_func"
        assert redacted["args"]["password"] == "[REDACTED]"


class TestBatchRedaction:
    """Test batch redaction for performance."""

    def test_batch_redaction_performance(self):
        """Test redacting multiple events meets performance requirements."""
        import time

        # Create 100 events with various sensitive data
        events = []
        for i in range(100):
            event = TraceEvent(
                event_type="call",
                timestamp=datetime.now(),
                thread_id=12345,
                function_name=f"func_{i}",
                args={
                    "user": f"user{i}",
                    "password": f"secret{i}",
                    "email": f"user{i}@example.com"
                },
            )
            events.append(asdict(event))

        # Redact all events
        start = time.perf_counter()
        redacted_events = [redact_secrets(event) for event in events]
        end = time.perf_counter()

        # Verify performance
        avg_time = (end - start) / len(events)
        assert avg_time < 0.001, f"Average time {avg_time*1000:.3f}ms exceeds 1ms"

        # Verify redaction worked
        for i, redacted in enumerate(redacted_events):
            assert redacted["args"]["password"] == "[REDACTED]"
            assert redacted["args"]["user"] == f"user{i}"
            assert redacted["args"]["email"] == f"user{i}@example.com"
