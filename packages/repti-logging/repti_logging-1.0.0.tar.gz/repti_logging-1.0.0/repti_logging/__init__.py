"""
ReptiDex Structured Logging Library

Provides structured JSON logging with PII filtering, error fingerprinting,
and context tracking for all ReptiDex microservices.
"""

__version__ = "1.0.0"

# Context management
from repti_logging.context import LogContext, get_current_context

# Decorators
from repti_logging.decorators import log_endpoint, log_errors, log_performance

# Filters
from repti_logging.filters import PIIFilter, create_pii_filter

# Formatter
from repti_logging.formatter import (
    EnhancedJsonFormatter,
    create_formatter,
    generate_error_fingerprint,
)

# Core logging setup
from repti_logging.setup import configure_sqlalchemy_logging, get_logger, setup_logging

# Try to import FastAPI middleware (optional)
try:
    from repti_logging.middleware import RequestLoggingMiddleware

    __all_middleware__ = ["RequestLoggingMiddleware"]
except ImportError:
    __all_middleware__ = []

__all__ = [
    # Version
    "__version__",
    # Core setup
    "setup_logging",
    "get_logger",
    "configure_sqlalchemy_logging",
    # Context
    "LogContext",
    "get_current_context",
    # Decorators
    "log_endpoint",
    "log_errors",
    "log_performance",
    # Filters
    "PIIFilter",
    "create_pii_filter",
    # Formatter
    "EnhancedJsonFormatter",
    "create_formatter",
    "generate_error_fingerprint",
] + __all_middleware__
