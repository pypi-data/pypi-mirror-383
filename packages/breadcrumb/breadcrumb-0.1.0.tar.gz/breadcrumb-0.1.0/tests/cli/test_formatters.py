"""
Tests for CLI formatters.

Validates JSON and table formatting for different data types.
"""

import pytest
import json
from datetime import datetime

from breadcrumb.cli.formatters import (
    format_json,
    format_table,
    format_error,
    format_success_message,
)


class TestJSONFormatter:
    """Test JSON formatting."""

    def test_format_simple_dict(self):
        """Test formatting a simple dict."""
        data = {"key": "value", "count": 42}
        result = format_json(data)

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["count"] == 42

    def test_format_list_of_dicts(self):
        """Test formatting a list of dicts."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        result = format_json(data)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "Alice"

    def test_format_datetime(self):
        """Test formatting datetime objects."""
        now = datetime(2025, 1, 10, 15, 30, 45)
        data = {"timestamp": now}
        result = format_json(data)

        parsed = json.loads(result)
        assert "2025-01-10" in parsed["timestamp"]

    def test_format_custom_indent(self):
        """Test custom indentation."""
        data = {"key": "value"}
        result = format_json(data, indent=4)

        # Should have 4-space indentation
        assert "    " in result

    def test_format_nested_structures(self):
        """Test nested dicts and lists."""
        data = {
            "user": {
                "name": "Alice",
                "tags": ["admin", "user"]
            }
        }
        result = format_json(data)

        parsed = json.loads(result)
        assert parsed["user"]["name"] == "Alice"
        assert len(parsed["user"]["tags"]) == 2


class TestTableFormatter:
    """Test table formatting."""

    def test_format_empty_list(self):
        """Test formatting empty list."""
        result = format_table([])
        assert "No results" in result

    def test_format_list_of_dicts(self):
        """Test formatting list of dicts as table."""
        data = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ]
        result = format_table(data)

        # Should contain column headers
        assert "id" in result
        assert "name" in result
        assert "age" in result

        # Should contain data
        assert "Alice" in result
        assert "Bob" in result

        # Should have separator
        assert "-+-" in result or "---" in result

        # Should have total count
        assert "Total: 2 rows" in result

    def test_format_single_dict(self):
        """Test formatting single dict as key-value pairs."""
        data = {"name": "Alice", "age": 30}
        result = format_table(data)

        # Should contain key-value pairs
        assert "name" in result.lower()
        assert "Alice" in result
        assert "age" in result.lower()
        assert "30" in result

    def test_format_with_title(self):
        """Test formatting with title."""
        data = {"key": "value"}
        result = format_table(data, title="Test Results")

        assert "Test Results" in result
        assert "=" in result  # Title separator

    def test_format_simple_value(self):
        """Test formatting simple value."""
        result = format_table("simple string")
        assert "simple string" in result

    def test_format_nested_dict_in_table(self):
        """Test formatting dict with nested structures."""
        data = {
            "name": "Alice",
            "metadata": {"role": "admin", "level": 5}
        }
        result = format_table(data)

        # Nested dict should be formatted as JSON
        assert "name" in result.lower()
        assert "Alice" in result
        assert "metadata" in result.lower()

    def test_format_empty_dict(self):
        """Test formatting empty dict."""
        result = format_table({})
        assert "No data" in result


class TestErrorFormatter:
    """Test error formatting."""

    def test_format_error_json(self):
        """Test formatting error as JSON."""
        result = format_error(
            error_type="ValueError",
            message="Invalid input",
            suggestion="Check your parameters",
            format="json"
        )

        parsed = json.loads(result)
        assert parsed["error"] == "ValueError"
        assert parsed["message"] == "Invalid input"
        assert parsed["suggestion"] == "Check your parameters"

    def test_format_error_table(self):
        """Test formatting error as table."""
        result = format_error(
            error_type="ValueError",
            message="Invalid input",
            suggestion="Check your parameters",
            format="table"
        )

        assert "ERROR: ValueError" in result
        assert "Invalid input" in result
        assert "Check your parameters" in result

    def test_format_error_without_suggestion(self):
        """Test formatting error without suggestion."""
        result = format_error(
            error_type="RuntimeError",
            message="Something went wrong",
            format="json"
        )

        parsed = json.loads(result)
        assert parsed["error"] == "RuntimeError"
        assert parsed["message"] == "Something went wrong"
        assert "suggestion" not in parsed


class TestSuccessFormatter:
    """Test success message formatting."""

    def test_format_success_json(self):
        """Test formatting success message as JSON."""
        result = format_success_message("Operation completed", format="json")

        parsed = json.loads(result)
        assert parsed["status"] == "success"
        assert parsed["message"] == "Operation completed"

    def test_format_success_table(self):
        """Test formatting success message as table."""
        result = format_success_message("Operation completed", format="table")

        assert "SUCCESS:" in result
        assert "Operation completed" in result


class TestTableFormattingEdgeCases:
    """Test edge cases in table formatting."""

    def test_truncate_long_values(self):
        """Test that very long values are truncated."""
        data = [
            {"id": 1, "value": "x" * 1000}
        ]
        result = format_table(data)

        # Value should be truncated with ...
        assert "..." in result

    def test_handle_none_values(self):
        """Test handling None values in table."""
        data = [
            {"id": 1, "value": None}
        ]
        result = format_table(data)

        assert "None" in result or "1" in result

    def test_handle_missing_keys(self):
        """Test handling missing keys in rows."""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2}  # Missing 'name' key
        ]
        result = format_table(data)

        # Should handle gracefully without crashing
        assert "Alice" in result
        assert "2" in result
