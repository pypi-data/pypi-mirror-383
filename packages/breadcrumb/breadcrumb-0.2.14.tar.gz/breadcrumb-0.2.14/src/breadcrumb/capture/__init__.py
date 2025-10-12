"""
Breadcrumb Capture Module

This module provides utilities for capturing and processing trace data,
including secret redaction for security.
"""

from breadcrumb.capture.secret_redactor import (
    redact_secrets,
    SecretRedactor,
    configure_redactor,
    REDACTED,
)

__all__ = [
    "redact_secrets",
    "SecretRedactor",
    "configure_redactor",
    "REDACTED",
]
