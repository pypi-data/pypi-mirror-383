"""
PII and sensitive data filtering for log records.
"""

import logging
import re
from typing import Any, Dict, List, Pattern


class PIIFilter(logging.Filter):
    """
    Logging filter that redacts personally identifiable information (PII)
    and sensitive data from log records.

    Automatically redacts:
    - Email addresses
    - Phone numbers
    - Credit card numbers
    - Social Security Numbers
    - Passwords and API keys
    - Bearer tokens
    - AWS keys
    """

    # Regex patterns for PII detection
    EMAIL_PATTERN: Pattern = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    )

    PHONE_PATTERN: Pattern = re.compile(
        r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b"
    )

    CREDIT_CARD_PATTERN: Pattern = re.compile(
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b"
    )

    SSN_PATTERN: Pattern = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

    # Bearer token pattern (Authorization: Bearer xxx)
    BEARER_TOKEN_PATTERN: Pattern = re.compile(
        r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE
    )

    # API key patterns
    API_KEY_PATTERN: Pattern = re.compile(
        r"(api[_-]?key|apikey|api[_-]?secret|secret[_-]?key)[\s:=]+['\"]?[A-Za-z0-9\-._~+/]+['\"]?",
        re.IGNORECASE,
    )

    # AWS Access Key patterns
    AWS_ACCESS_KEY_PATTERN: Pattern = re.compile(r"AKIA[0-9A-Z]{16}")
    AWS_SECRET_KEY_PATTERN: Pattern = re.compile(
        r"(?i)aws_secret_access_key.*?['\"]([^'\"]+)['\"]"
    )

    # Password patterns in JSON or query params
    PASSWORD_PATTERN: Pattern = re.compile(
        r"(?i)(password|passwd|pwd)[\s:=]+['\"]?([^'\"&\s]+)['\"]?",
        re.IGNORECASE,
    )

    # Sensitive field names that should always be redacted
    SENSITIVE_FIELDS: List[str] = [
        "password",
        "passwd",
        "pwd",
        "secret",
        "api_key",
        "apikey",
        "api_secret",
        "access_token",
        "refresh_token",
        "auth_token",
        "authorization",
        "credit_card",
        "card_number",
        "cvv",
        "ssn",
        "social_security",
        "aws_secret_access_key",
        "private_key",
    ]

    def __init__(self, name: str = ""):
        """Initialize the PII filter."""
        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter the log record to redact PII.

        Args:
            record: The log record to filter

        Returns:
            True (always allows the record to be logged)
        """
        # Redact message
        if hasattr(record, "msg"):
            if isinstance(record.msg, str):
                record.msg = self.redact_pii(record.msg)

        # Redact arguments
        if hasattr(record, "args") and record.args:
            if isinstance(record.args, dict):
                record.args = self.redact_dict(record.args)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    self.redact_pii(arg) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        return True

    def redact_pii(self, text: str) -> str:
        """
        Redact PII from a text string.

        Args:
            text: Text that may contain PII

        Returns:
            Text with PII redacted
        """
        # Redact emails
        text = self.EMAIL_PATTERN.sub(self._redact_email, text)

        # Redact phone numbers
        text = self.PHONE_PATTERN.sub("***-***-****", text)

        # Redact credit cards
        text = self.CREDIT_CARD_PATTERN.sub("****-****-****-****", text)

        # Redact SSNs
        text = self.SSN_PATTERN.sub("***-**-****", text)

        # Redact bearer tokens
        text = self.BEARER_TOKEN_PATTERN.sub("Bearer ***REDACTED***", text)

        # Redact API keys
        text = self.API_KEY_PATTERN.sub(r"\1=***REDACTED***", text)

        # Redact AWS keys
        text = self.AWS_ACCESS_KEY_PATTERN.sub("AKIA***REDACTED***", text)
        text = self.AWS_SECRET_KEY_PATTERN.sub(
            r"aws_secret_access_key=***REDACTED***", text
        )

        # Redact passwords
        text = self.PASSWORD_PATTERN.sub(r"\1=***REDACTED***", text)

        return text

    def redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively redact sensitive fields from a dictionary.

        Args:
            data: Dictionary that may contain sensitive data

        Returns:
            Dictionary with sensitive fields redacted
        """
        if not isinstance(data, dict):
            return data

        redacted = {}
        for key, value in data.items():
            key_lower = key.lower()

            # Check if this is a sensitive field
            if any(sensitive in key_lower for sensitive in self.SENSITIVE_FIELDS):
                redacted[key] = "***REDACTED***"
            elif isinstance(value, dict):
                redacted[key] = self.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [
                    self.redact_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            elif isinstance(value, str):
                redacted[key] = self.redact_pii(value)
            else:
                redacted[key] = value

        return redacted

    @staticmethod
    def _redact_email(match: re.Match) -> str:
        """
        Partially redact an email address.

        Args:
            match: Regex match object for email

        Returns:
            Partially redacted email (e.g., "u***@e***.com")
        """
        email = match.group(0)
        parts = email.split("@")
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]

            # Keep first char of username, redact rest
            redacted_username = username[0] + "***" if len(username) > 1 else "***"

            # Keep first char of domain, redact rest before TLD
            domain_parts = domain.split(".")
            if len(domain_parts) >= 2:
                domain_name = domain_parts[0]
                tld = ".".join(domain_parts[1:])
                redacted_domain = (
                    domain_name[0] + "***" if len(domain_name) > 1 else "***"
                )
                return f"{redacted_username}@{redacted_domain}.{tld}"

        return "***@***.***"


def create_pii_filter() -> PIIFilter:
    """
    Create a PIIFilter instance.

    Returns:
        Configured PIIFilter
    """
    return PIIFilter()
