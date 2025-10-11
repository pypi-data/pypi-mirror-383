# ReptiDex Structured Logging Library

Shared Python logging library for all ReptiDex microservices, providing:

- **Structured JSON logging** with consistent field formats
- **PII filtering** for automatic redaction of sensitive data
- **Correlation ID tracking** across service boundaries
- **Error fingerprinting** for grouping similar errors
- **FastAPI decorators** for automatic endpoint logging
- **Context management** for request/user tracking

## Installation

```bash
# Basic installation
pip install -e /path/to/backend/shared/repti-logging

# With FastAPI support
pip install -e "/path/to/backend/shared/repti-logging[fastapi]"

# Development installation
pip install -e "/path/to/backend/shared/repti-logging[fastapi,dev]"
```

## Quick Start

### Basic Setup

```python
from repti_logging import setup_logging, get_logger

# Initialize logging (call once at application startup)
setup_logging(
    service_name="repti-core",
    log_level="INFO",
    enable_pii_filtering=True,
)

# Get a logger
logger = get_logger(__name__)

logger.info("Application started", extra={"version": "1.0.0"})
```

### FastAPI Integration

```python
from fastapi import FastAPI
from repti_logging import setup_logging
from repti_logging.middleware import RequestLoggingMiddleware

app = FastAPI()

# Setup logging
setup_logging(service_name="repti-core")

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)
```

### Using Decorators

```python
from repti_logging.decorators import log_endpoint, log_errors

@log_endpoint(log_args=True, log_result=False)
async def my_endpoint(user_id: str):
    """This endpoint will automatically log entry/exit."""
    return {"user_id": user_id}

@log_errors(log_traceback=True)
async def risky_operation():
    """Errors will be automatically logged with full context."""
    raise ValueError("Something went wrong")
```

## Standard Log Fields

All logs include these standard fields:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp with microseconds |
| `level` | string | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `service` | string | Service name (e.g., "repti-core") |
| `logger` | string | Python logger name (e.g., "app.services.auth") |
| `message` | string | Log message |
| `request_id` | string | Correlation ID for request tracking |
| `user_id` | string | Authenticated user ID (if available) |
| `session_id` | string | Session ID (if available) |
| `endpoint` | string | API endpoint path |
| `method` | string | HTTP method |
| `status_code` | int | HTTP status code |
| `duration_ms` | float | Request duration in milliseconds |
| `error_type` | string | Exception class name |
| `error_fingerprint` | string | Hash for grouping similar errors |
| `stack_trace` | string | Full exception traceback |

## PII Filtering

The library automatically redacts:

- Passwords
- API keys and tokens (Bearer tokens, API keys)
- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers

```python
logger.info("User login", extra={
    "email": "user@example.com",  # Will be redacted to "***@***.com"
    "password": "secret123",       # Will be redacted to "***REDACTED***"
})
```

## Error Fingerprinting

Errors are automatically fingerprinted for grouping:

```python
try:
    result = 1 / 0
except Exception as e:
    logger.error("Division error", exc_info=True)
    # Includes error_fingerprint: "ZeroDivisionError:division_by_zero:line_42"
```

## Context Management

Track request context across async boundaries:

```python
from repti_logging import LogContext

async def process_request(request_id: str, user_id: str):
    with LogContext(request_id=request_id, user_id=user_id):
        # All logs within this context include request_id and user_id
        logger.info("Processing request")
        await some_async_operation()
        logger.info("Request completed")
```

## Development

```bash
# Install development dependencies (includes pre-commit hooks)
make install

# Or manually
pip install -e ".[fastapi,dev]"
pre-commit install

# Run tests
make test

# Run pre-commit hooks
make pre-commit

# Format code
make format

# Run all CI checks locally
make ci
```

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit to ensure code quality:
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- bandit (security)
- Various safety checks

See [PRECOMMIT_SUMMARY.md](PRECOMMIT_SUMMARY.md) for details.

## License

MIT License - Copyright (c) 2025 ReptiDex
