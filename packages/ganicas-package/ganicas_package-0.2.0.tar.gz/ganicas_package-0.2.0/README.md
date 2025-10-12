# Ganicas Utils

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Code Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](https://github.com/ganicas/ganicas_utils)

**Ganicas Utils** is an internal Python package providing structured logging utilities and middleware for Flask and FastAPI applications. Built on top of [structlog](https://www.structlog.org/), it enables production-ready, context-aware logging with minimal configuration.

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Structured Logging](#-structured-logging)
  - [Basic Configuration](#basic-configuration)
  - [Production Configuration](#production-configuration)
- [Middleware](#-middleware)
  - [Flask Middleware](#flask-middleware)
  - [FastAPI Middleware](#fastapi-middleware)
  - [Request Logging Middleware](#request-logging-middleware)
- [Why Structured Logging?](#-why-structured-logging)
- [Development](#-development)
- [License](#-license)

---

## ✨ Features

- **Structured Logging**: JSON-formatted logs for easy parsing by log aggregation tools (ELK, Datadog, Grafana Loki)
- **Context Management**: Automatic request context binding (request_id, IP, user_agent, etc.)
- **Flask & FastAPI Support**: Ready-to-use middleware for both frameworks
- **Advanced Request Logging**: Comprehensive ASGI middleware with:
  - Automatic request/response logging
  - Sensitive header sanitization
  - Slow request detection
  - Sampling for high-traffic endpoints
  - Exception tracking with full context
  - Distributed tracing support (traceparent header)
- **Production Ready**: Battle-tested with 99% code coverage

---

## 📦 Installation

```bash
pip install ganicas-package
```

Or with Poetry:

```bash
poetry add ganicas-package
```

---

## 🚀 Quick Start

### Basic Configuration

Replace `logger = logging.getLogger(__name__)` with `logger = structlog.get_logger(__name__)`:

```python
from ganicas_utils.logging import LoggingConfigurator
from ganicas_utils.config import Config
import structlog

config = Config()

LoggingConfigurator(
    service_name=config.APP_NAME,
    log_level='INFO',
    setup_logging_dict=True
).configure_structlog(
    formatter='plain_console',
    formatter_std_lib='plain_console'
)

logger = structlog.get_logger(__name__)
logger.info("Application started", version="1.0.0", environment="production")
```

![basic example](images/plain_console_logger.png)

---

## 📊 Structured Logging

### Production Configuration

For production environments, use JSON formatting for machine-readable logs:

```python
from ganicas_utils.logging import LoggingConfigurator
from ganicas_utils.config import Config
import structlog

config = Config()

LoggingConfigurator(
    service_name=config.APP_NAME,
    log_level='INFO',
    setup_logging_dict=True
).configure_structlog(
    formatter='json_formatter',
    formatter_std_lib='json_formatter'
)

logger = structlog.get_logger(__name__)
logger.info("User login", user_id=12345, ip_address="192.168.1.1")
logger.warning("High memory usage", memory_percent=85.5, threshold=80)
logger.error("Database connection failed", db_host="localhost", error_code="CONN_REFUSED")

try:
    result = 1 / 0
except ZeroDivisionError:
    logger.exception("Division by zero error", operation="calculate_ratio")
```

![logger with different keys](images/json_logger.png)


---

## 🔧 Middleware

### Flask Middleware

The `FlaskRequestContextMiddleware` automatically adds request context to all logs:

```python
import uuid
from flask import Flask
from ganicas_utils.logging import LoggingConfigurator
from ganicas_utils.logging.middlewares import FlaskRequestContextMiddleware
from ganicas_utils.config import Config
import structlog

config = Config()

LoggingConfigurator(
    service_name=config.APP_NAME,
    log_level="INFO",
    setup_logging_dict=True,
).configure_structlog(formatter='json_formatter', formatter_std_lib='json_formatter')

logger = structlog.get_logger(__name__)

app = Flask(__name__)
app.wsgi_app = FlaskRequestContextMiddleware(app.wsgi_app)

@app.route("/")
def home():
    logger.info("Processing request")  # Automatically includes request_id, method, path
    return "Hello, World!"

if __name__ == "__main__":
    app.run()
```

![logger with context flask](images/flask_logger_with_context.png)

**Automatic context injection:**
- `request_id` - Unique identifier for each request
- `request_method` - HTTP method (GET, POST, etc.)
- `request_path` - Request URL path

---

### FastAPI Middleware

#### Basic Context Middleware

For simple request context binding, use `FastAPIRequestContextMiddleware`:

```python
from fastapi import FastAPI
from ganicas_utils.logging import LoggingConfigurator
from ganicas_utils.logging.middlewares import FastAPIRequestContextMiddleware
from ganicas_utils.config import Config
import structlog

config = Config()

LoggingConfigurator(
    service_name=config.APP_NAME,
    log_level="INFO",
    setup_logging_dict=True,
).configure_structlog(formatter='json_formatter', formatter_std_lib='json_formatter')

logger = structlog.get_logger(__name__)
app = FastAPI()
app.add_middleware(FastAPIRequestContextMiddleware)

@app.get("/")
async def root():
    logger.info("Processing request")  # Automatically includes request context
    return {"message": "Hello World"}
```

![logger with context fastapi](images/fastapi_logger_with_context.png)

---

### Request Logging Middleware

For production-grade request/response logging with advanced features, use `RequestLoggingMiddleware`:

```python
from fastapi import FastAPI
from ganicas_utils.logging import LoggingConfigurator
from ganicas_utils.logging.middlewares import RequestLoggingMiddleware
import structlog

LoggingConfigurator(
    service_name="my-api",
    log_level="INFO",
    setup_logging_dict=True,
).configure_structlog(formatter='json_formatter', formatter_std_lib='json_formatter')

app = FastAPI()

# Add comprehensive request logging
app.add_middleware(
    RequestLoggingMiddleware,
    slow_request_threshold_ms=1000,      # Warn on requests > 1s
    propagate_request_id=True,           # Add request_id to response headers
    skip_paths={"/healthz", "/metrics"}, # Don't log health checks
    sample_2xx_rate=0.1,                 # Sample 10% of successful requests
)

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "name": "John Doe"}
```

#### Features

**Automatic Logging:**
- `request.start` - Logs when request begins
- `request.end` - Logs when request completes (with status, duration, size)
- `request.exception` - Logs unhandled exceptions with full traceback

**Logged Information:**
- Request: method, path, query params, client IP, user agent, content type/length
- Response: status code, size, content type, duration
- Headers: Sanitized request/response headers (for 4xx/5xx errors)
- Performance: Request duration, slow request detection

**Security:**
- Automatic sanitization of sensitive headers (`Authorization`, `Cookie`, `X-API-Key`)
- Authorization header preserves scheme: `Bearer ***` instead of exposing tokens
- No request/response body logging (only sizes)

**Performance Optimization:**
- Skip logging for health checks and metrics endpoints
- Sample successful requests to reduce log volume
- Skip OPTIONS requests
- Configurable path prefixes to skip

**Distributed Tracing:**
- Supports W3C `traceparent` header
- Falls back to `x-request-id` or `x-amzn-trace-id`
- Propagates request_id to response headers

#### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `logger` | `structlog.BoundLoggerBase` | `structlog.get_logger("http")` | Custom logger instance |
| `slow_request_threshold_ms` | `int` | `None` | Threshold in ms to flag slow requests |
| `propagate_request_id` | `bool` | `True` | Add `x-request-id` to response headers |
| `skip_paths` | `set[str]` | `{"/healthz", "/metrics"}` | Exact paths to skip logging |
| `skip_prefixes` | `tuple[str, ...]` | `("/metrics",)` | Path prefixes to skip logging |
| `sample_2xx_rate` | `float` | `None` | Sample rate for 2xx/3xx responses (0.0-1.0) |

#### Example Logs

**Successful Request:**
```json
{
  "event": "request.end",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "GET",
  "path": "/api/users/123",
  "status_code": 200,
  "duration_ms": 45,
  "response_size": 256,
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "level": "info"
}
```

**Slow Request Warning:**
```json
{
  "event": "request.end",
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "method": "POST",
  "path": "/api/process",
  "status_code": 200,
  "duration_ms": 1523,
  "slow_request": true,
  "slow_threshold_ms": 1000,
  "level": "warning"
}
```

**Error with Sanitized Headers:**
```json
{
  "event": "request.end",
  "request_id": "550e8400-e29b-41d4-a716-446655440002",
  "method": "POST",
  "path": "/api/login",
  "status_code": 401,
  "duration_ms": 12,
  "request_headers": {
    "authorization": "Bearer ***",
    "content-type": "application/json"
  },
  "level": "warning"
}
```

---

## 🎯 Why Structured Logging?

**Traditional logging challenges:**
- Plain text logs are hard to parse programmatically
- Difficult to filter and search in log aggregation tools
- Missing context makes debugging distributed systems challenging

**Structured logging benefits:**
- **Machine-readable**: JSON format for easy parsing by ELK, Datadog, Grafana Loki
- **Rich context**: Automatic correlation with request_id, user_id, transaction_id
- **Better filtering**: Query logs by any field (status_code, duration, user_id, etc.)
- **Observability**: Enhanced monitoring and alerting capabilities
- **Debugging**: Trace requests across microservices with distributed tracing support

**This package uses [structlog](https://www.structlog.org/)** - a powerful library that enhances Python's standard logging with better context management and flexible log formatting.


---

## 🛠️ Development

### Prerequisites

Install [Poetry](https://python-poetry.org/docs/#installation) for dependency management:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Setup

```bash
# Install dependencies
poetry install --with dev

# Run tests with coverage
poetry run pytest -v --cov=ganicas_utils

# Run tests with detailed output
poetry run pytest -rs --cov=ganicas_utils -s

# Run pre-commit hooks
poetry run pre-commit run --all-files
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_request_logging_middleware.py

# Run with coverage report
poetry run pytest --cov=ganicas_utils --cov-report=html
```

### Code Quality

This project uses:
- **pytest** for testing (99% coverage)
- **ruff** for linting and formatting
- **pre-commit** for automated checks

---

## 📄 License

Proprietary - Internal use only for Ganicas projects.

---

## 🤝 Contributing

This is an internal package. For questions or contributions, please contact the Ganicas development team.

---

## 📚 Additional Resources

- [structlog Documentation](https://www.structlog.org/en/stable/)
- [FastAPI Middleware Guide](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Flask Middleware Guide](https://flask.palletsprojects.com/en/latest/api/#flask.Flask.wsgi_app)

---

**Made with ❤️ by Ganicas Team**
