import json
import logging
import logging.handlers
import sys
import uuid
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .config import settings

# Context variable for correlation ID
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdFilter(logging.Filter):
    """Filter to add correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get() or "no-correlation-id"
        return True


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with JSON output."""

    def format(self, record: logging.LogRecord) -> str:
        # Create structured log entry
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "no-correlation-id"),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "correlation_id",
            ):
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_ctx.set(correlation_id)


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return correlation_id_ctx.get()


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def log_request(
    method: str, url: str, headers: Dict[str, Any], body: Any = None
) -> None:
    """Log incoming request details."""
    logger = logging.getLogger("app.request")

    # Filter sensitive headers
    safe_headers = {
        k: v
        for k, v in headers.items()
        if k.lower() not in ["authorization", "cookie", "x-api-key"]
    }

    log_data = {
        "event": "request_received",
        "method": method,
        "url": url,
        "headers": safe_headers,
        "user_agent": headers.get("user-agent", "unknown"),
        "remote_addr": headers.get(
            "x-forwarded-for", headers.get("remote-addr", "unknown")
        ),
    }

    # Add body for non-GET requests (but filter sensitive data)
    if method != "GET" and body is not None:
        if isinstance(body, dict):
            safe_body = {
                k: v
                for k, v in body.items()
                if k.lower() not in ["password", "token", "secret"]
            }
            log_data["body"] = safe_body
        else:
            log_data["body_size"] = len(str(body))

    logger.info("Incoming request", extra=log_data)


def log_response(
    status_code: int, response_time: float, response_size: int = 0
) -> None:
    """Log outgoing response details."""
    logger = logging.getLogger("app.response")

    log_data = {
        "event": "response_sent",
        "status_code": status_code,
        "response_time_ms": round(response_time * 1000, 2),
        "response_size_bytes": response_size,
        "status_category": "success"
        if 200 <= status_code < 300
        else "redirect"
        if 300 <= status_code < 400
        else "client_error"
        if 400 <= status_code < 500
        else "server_error",
    }

    # Choose log level based on status code
    if status_code >= 500:
        logger.error("Response sent", extra=log_data)
    elif status_code >= 400:
        logger.warning("Response sent", extra=log_data)
    else:
        logger.info("Response sent", extra=log_data)


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with context."""
    logger = logging.getLogger("app.error")

    log_data = {
        "event": "error_occurred",
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
    }

    logger.error("Error occurred", extra=log_data, exc_info=True)


def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """Log security-related events."""
    logger = logging.getLogger("app.security")

    log_data = {"event": "security_event", "event_type": event_type, "details": details}

    logger.warning("Security event", extra=log_data)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_rotation: bool = True,
    structured_logging: bool = False,
) -> None:
    """Setup centralized logging configuration."""

    # Use log level from settings if not provided
    if log_level is None:
        log_level = settings.log_level

    # Configure log level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Set default log file
    if log_file is None:
        log_file = str(log_dir / "clinical_sample_service.log")

    # Create correlation ID filter
    correlation_filter = CorrelationIdFilter()

    # Create formatters
    if structured_logging:
        formatter: logging.Formatter = StructuredFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        detailed_formatter: logging.Formatter = StructuredFormatter(
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        detailed_formatter = logging.Formatter(
            fmt=(
                "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - "
                "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(correlation_filter)
    root_logger.addHandler(console_handler)

    # File handler with rotation
    file_handler: Union[logging.handlers.RotatingFileHandler, logging.FileHandler]
    if enable_rotation:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
    else:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")

    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    file_handler.addFilter(correlation_filter)
    root_logger.addHandler(file_handler)

    # Setup structured logging file handler for production
    if structured_logging:
        structured_file = str(log_dir / "structured_logs.json")
        structured_handler = logging.handlers.RotatingFileHandler(
            structured_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        structured_handler.setLevel(numeric_level)
        structured_handler.setFormatter(
            StructuredFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        )
        structured_handler.addFilter(correlation_filter)
        root_logger.addHandler(structured_handler)

    # Configure specific loggers
    configure_specific_loggers(numeric_level)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured - Level: {log_level}, File: {log_file}, Structured: {structured_logging}"
    )


def configure_specific_loggers(level: int) -> None:
    """Configure specific loggers for different components."""

    # SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    if settings.debug:
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger.setLevel(logging.WARNING)

    # Uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(level)

    # FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(level)

    # Application logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Get logger for specific module."""
    return logging.getLogger(name)


# Setup logging on module import
try:
    setup_logging()
except Exception as e:
    # Fallback to basic logging if setup fails
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to setup logging: {e}")
    logger.info("Using fallback logging configuration")
