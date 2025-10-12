"""
Secret Redaction Engine for Breadcrumb AI Tracer

This module provides automatic detection and redaction of sensitive information
from traced variable values before storage. It prevents accidental logging of
passwords, API keys, tokens, credit cards, SSNs, and other secrets.

Key Features:
- Pattern-based redaction for common secret types
- Key-based redaction (detects sensitive keys in dictionaries)
- Value-based redaction (detects patterns in string values)
- Recursive processing of nested structures
- Configurable custom patterns
- Preserves data structure and types
- Performance optimized (< 1ms per event)

Usage:
    from breadcrumb.capture.secret_redactor import redact_secrets

    # Basic usage
    data = {"user": "alice", "password": "secret123", "email": "alice@example.com"}
    redacted = redact_secrets(data)
    # Result: {"user": "alice", "password": "[REDACTED]", "email": "alice@example.com"}

    # Custom patterns
    data = {"custom_token": "abc123"}
    redacted = redact_secrets(data, patterns=['custom_token'])
    # Result: {"custom_token": "[REDACTED]"}

    # Nested structures
    data = {
        "user": {
            "name": "alice",
            "credentials": {
                "password": "secret123",
                "api_key": "sk-1234567890"
            }
        }
    }
    redacted = redact_secrets(data)
    # All password and api_key values will be "[REDACTED]"
"""

import re
from typing import Any, Dict, List, Optional, Set


# Default patterns for sensitive keys (case-insensitive)
DEFAULT_KEY_PATTERNS = [
    # Passwords
    'password',
    'passwd',
    'pwd',
    'pass',
    'secret',
    'password_hash',
    'password_digest',

    # API Keys and Tokens
    'api_key',
    'apikey',
    'api-key',
    'token',
    'auth_token',
    'auth-token',
    'access_token',
    'access-token',
    'refresh_token',
    'refresh-token',
    'secret_key',
    'secret-key',
    'private_key',
    'private-key',
    'bearer',
    'authorization',
    'auth',

    # Authentication
    'credentials',
    'credential',
    'client_secret',
    'client-secret',
    'session_key',
    'session-key',
    'session_token',
    'session-token',

    # Security
    'security_token',
    'security-token',
    'csrf_token',
    'csrf-token',
    'xsrf_token',
    'xsrf-token',

    # Cloud provider specific
    'aws_secret',
    'aws_secret_access_key',
    'azure_secret',
    'gcp_secret',
]

# Regular expressions for value-based detection
# These patterns detect secrets in string values regardless of key name

# Credit card: 16 digits with optional dashes/spaces
CREDIT_CARD_PATTERN = re.compile(
    r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
)

# SSN: XXX-XX-XXXX format
SSN_PATTERN = re.compile(
    r'\b\d{3}-\d{2}-\d{4}\b'
)

# JWT: Starts with "eyJ" (base64 encoded JSON header)
# Format: header.payload.signature
JWT_PATTERN = re.compile(
    r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b'
)

# Common API key patterns
# AWS keys: starts with AKIA
AWS_KEY_PATTERN = re.compile(
    r'\bAKIA[A-Z0-9]{16}\b'
)

# GitHub tokens: starts with ghp_, gho_, ghu_, ghs_, ghr_
GITHUB_TOKEN_PATTERN = re.compile(
    r'\bgh[pousr]_[A-Za-z0-9]{36,}\b'
)

# Generic API key pattern: long alphanumeric strings that look like keys
# At least 20 characters, mix of letters and numbers
GENERIC_API_KEY_PATTERN = re.compile(
    r'\b[A-Za-z0-9_-]{32,}\b'
)

# Redaction marker
REDACTED = "[REDACTED]"


class SecretRedactor:
    """
    Secret redaction engine for sensitive data detection and removal.

    This class provides configurable redaction of sensitive information from
    data structures before they are stored or logged.
    """

    def __init__(
        self,
        key_patterns: Optional[List[str]] = None,
        custom_patterns: Optional[List[str]] = None,
        redact_credit_cards: bool = True,
        redact_ssns: bool = True,
        redact_jwts: bool = True,
        redact_api_keys: bool = True,
    ):
        """
        Initialize secret redactor.

        Args:
            key_patterns: List of key patterns to redact (case-insensitive).
                         If None, uses DEFAULT_KEY_PATTERNS.
            custom_patterns: Additional custom key patterns to redact.
            redact_credit_cards: Whether to detect and redact credit card numbers.
            redact_ssns: Whether to detect and redact SSNs.
            redact_jwts: Whether to detect and redact JWT tokens.
            redact_api_keys: Whether to detect and redact API keys.
        """
        # Build key pattern set (case-insensitive)
        if key_patterns is None:
            self.key_patterns = set(p.lower() for p in DEFAULT_KEY_PATTERNS)
        else:
            self.key_patterns = set(p.lower() for p in key_patterns)

        # Add custom patterns
        if custom_patterns:
            for pattern in custom_patterns:
                self.key_patterns.add(pattern.lower())

        # Value-based redaction flags
        self.redact_credit_cards = redact_credit_cards
        self.redact_ssns = redact_ssns
        self.redact_jwts = redact_jwts
        self.redact_api_keys = redact_api_keys

        # Cache for processed patterns (for wildcard matching)
        self._pattern_cache: Dict[str, bool] = {}

    def _should_redact_key(self, key: str) -> bool:
        """
        Check if a key should be redacted based on patterns.

        Supports exact matches and wildcard patterns (e.g., 'secret_*').

        Args:
            key: The key name to check (dictionary key or object attribute)

        Returns:
            True if the key should be redacted, False otherwise
        """
        key_lower = key.lower()

        # Check cache first
        if key_lower in self._pattern_cache:
            return self._pattern_cache[key_lower]

        # Check for exact match
        if key_lower in self.key_patterns:
            self._pattern_cache[key_lower] = True
            return True

        # Check for wildcard patterns
        for pattern in self.key_patterns:
            if '*' in pattern:
                # Convert glob pattern to regex
                regex_pattern = pattern.replace('*', '.*')
                if re.match(f'^{regex_pattern}$', key_lower):
                    self._pattern_cache[key_lower] = True
                    return True
            elif key_lower.endswith(pattern) or key_lower.startswith(pattern):
                # Partial match for common cases like 'user_password' or 'password_hash'
                # Only if the pattern is at the start or end
                self._pattern_cache[key_lower] = True
                return True

        self._pattern_cache[key_lower] = False
        return False

    def _should_redact_value(self, value: str) -> bool:
        """
        Check if a string value should be redacted based on patterns.

        This detects sensitive data in values regardless of the key name.

        Args:
            value: The string value to check

        Returns:
            True if the value should be redacted, False otherwise
        """
        if not isinstance(value, str):
            return False

        # Skip very short strings (unlikely to be secrets)
        if len(value) < 8:
            return False

        # Check credit cards
        if self.redact_credit_cards and CREDIT_CARD_PATTERN.search(value):
            return True

        # Check SSNs
        if self.redact_ssns and SSN_PATTERN.search(value):
            return True

        # Check JWTs
        if self.redact_jwts and JWT_PATTERN.search(value):
            return True

        # Check API keys
        if self.redact_api_keys:
            if AWS_KEY_PATTERN.search(value):
                return True
            if GITHUB_TOKEN_PATTERN.search(value):
                return True
            # Generic API key detection (be conservative)
            # Only if it looks like a random token (high entropy)
            if len(value) >= 32 and GENERIC_API_KEY_PATTERN.match(value):
                # Additional heuristic: should have both letters and numbers
                has_letters = any(c.isalpha() for c in value)
                has_numbers = any(c.isdigit() for c in value)
                if has_letters and has_numbers:
                    return True

        return False

    def redact(self, data: Any, key_name: Optional[str] = None) -> Any:
        """
        Redact sensitive information from data recursively.

        This method handles dictionaries, lists, and primitive types.
        It preserves the data structure and only redacts values.

        Args:
            data: The data to redact (any type)
            key_name: Optional key name for context (used for dict values)

        Returns:
            Redacted copy of the data with the same structure
        """
        # Handle None
        if data is None:
            return None

        # Handle primitive types that should never be redacted
        if isinstance(data, (bool, int, float)):
            return data

        # Handle strings
        if isinstance(data, str):
            # If this string is associated with a sensitive key, redact it
            if key_name and self._should_redact_key(key_name):
                return REDACTED

            # Check if the value itself looks like a secret
            if self._should_redact_value(data):
                return REDACTED

            return data

        # Handle dictionaries recursively
        if isinstance(data, dict):
            redacted_dict = {}
            for key, value in data.items():
                # Redact the value if the key matches a pattern
                redacted_dict[key] = self.redact(value, key_name=str(key))
            return redacted_dict

        # Handle lists recursively
        if isinstance(data, (list, tuple)):
            redacted_list = [self.redact(item) for item in data]
            # Preserve tuple type
            if isinstance(data, tuple):
                return tuple(redacted_list)
            return redacted_list

        # Handle sets
        if isinstance(data, set):
            return {self.redact(item) for item in data}

        # For other types (objects, functions, etc.), convert to safe repr
        # This shouldn't happen in normal event data, but handle gracefully
        try:
            # Try to get a string representation
            repr_str = repr(data)
            # Don't redact object representations, but truncate if too long
            if len(repr_str) > 200:
                return repr_str[:200] + "...[TRUNCATED]"
            return repr_str
        except Exception:
            return f"<{type(data).__name__}>"


# Global default redactor instance
_default_redactor = SecretRedactor()


def redact_secrets(
    data: Any,
    patterns: Optional[List[str]] = None,
) -> Any:
    """
    Redact sensitive information from data using default or custom patterns.

    This is a convenience function that uses a global redactor instance.
    For more control, create your own SecretRedactor instance.

    Args:
        data: The data to redact (dict, list, or any other type)
        patterns: Optional list of additional custom key patterns to redact

    Returns:
        Redacted copy of the data with the same structure

    Example:
        >>> data = {"user": "alice", "password": "secret123"}
        >>> redact_secrets(data)
        {"user": "alice", "password": "[REDACTED]"}

        >>> data = {"custom_token": "abc123"}
        >>> redact_secrets(data, patterns=['custom_token'])
        {"custom_token": "[REDACTED]"}
    """
    if patterns:
        # Create a custom redactor with additional patterns
        redactor = SecretRedactor(custom_patterns=patterns)
        return redactor.redact(data)
    else:
        # Use the global default redactor
        return _default_redactor.redact(data)


def configure_redactor(
    key_patterns: Optional[List[str]] = None,
    custom_patterns: Optional[List[str]] = None,
    redact_credit_cards: bool = True,
    redact_ssns: bool = True,
    redact_jwts: bool = True,
    redact_api_keys: bool = True,
) -> None:
    """
    Configure the global default redactor.

    This allows you to customize the redaction behavior globally
    without creating new redactor instances.

    Args:
        key_patterns: Replace default key patterns with custom ones
        custom_patterns: Add additional custom patterns to defaults
        redact_credit_cards: Whether to detect and redact credit card numbers
        redact_ssns: Whether to detect and redact SSNs
        redact_jwts: Whether to detect and redact JWT tokens
        redact_api_keys: Whether to detect and redact API keys

    Example:
        >>> configure_redactor(custom_patterns=['my_secret_*'])
        >>> data = {"my_secret_key": "abc123"}
        >>> redact_secrets(data)
        {"my_secret_key": "[REDACTED]"}
    """
    global _default_redactor
    _default_redactor = SecretRedactor(
        key_patterns=key_patterns,
        custom_patterns=custom_patterns,
        redact_credit_cards=redact_credit_cards,
        redact_ssns=redact_ssns,
        redact_jwts=redact_jwts,
        redact_api_keys=redact_api_keys,
    )
