"""Structured JSON logging and secret redaction for CampusGPT (WP11).

Provides:
- ContextVar-based request correlation ID tracking.
- Redaction filter masking passwords, OTPs, tokens, cookies, and secret values.
- JSON formatter rendering machine-readable, structured logs.
- Safe logging configuration using standard Python logging.
"""

from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import re
from typing import Any

# ContextVar storing current request's correlation ID
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# Redaction patterns for sensitive keys and values
SENSITIVE_KEY_PATTERN = re.compile(
    r"(password|passwd|secret|token|refresh_token|access_token|authorization|bearer|"
    r"otp|code|oauth_binding_nonce|client_secret|cookie)",
    re.IGNORECASE,
)

# Regex matching bearer tokens, JWT-like strings, and OTP-like numeric sequences in text
SENSITIVE_VALUE_PATTERN = re.compile(
    r"(Bearer\s+)[A-Za-z0-9\-_\.]+|"
    r"(eyJ[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,})|"
    r"('otp':\s*'[0-9]+'|\"otp\":\s*\"[0-9]+\")",
    re.IGNORECASE,
)


def get_current_request_id() -> str | None:
    """Retrieve the current request's correlation ID, if set."""
    return request_id_var.get()


def set_current_request_id(req_id: str | None) -> None:
    """Set the current request's correlation ID in context."""
    request_id_var.set(req_id)


def redact_sensitive_value(val: Any) -> Any:
    """Recursively redacts sensitive keys and values in dictionaries, lists, or strings."""
    if isinstance(val, dict):
        clean_dict = {}
        for k, v in val.items():
            if SENSITIVE_KEY_PATTERN.search(str(k)):
                clean_dict[k] = "[REDACTED]"
            else:
                clean_dict[k] = redact_sensitive_value(v)
        return clean_dict
    elif isinstance(val, (list, tuple)):
        return [redact_sensitive_value(item) for item in val]
    elif isinstance(val, str):
        # Mask any JWT or Bearer pattern detected in free text
        return SENSITIVE_VALUE_PATTERN.sub(r"\1[REDACTED]", val)
    return val


class RedactionFilter(logging.Filter):
    """Logging filter that redacts secrets from log record arguments."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.args:
            if isinstance(record.args, dict):
                record.args = redact_sensitive_value(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(redact_sensitive_value(a) for a in record.args)
            elif isinstance(record.args, list):
                record.args = [redact_sensitive_value(a) for a in record.args]
        return True


class JSONLogFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects with correlation IDs and redaction."""

    def format(self, record: logging.LogRecord) -> str:
        try:
            raw_msg = record.getMessage()
        except Exception:
            raw_msg = str(record.msg)

        # Redact any sensitive value or key=value patterns in the rendered message
        clean_msg = SENSITIVE_VALUE_PATTERN.sub(r"\1[REDACTED]", raw_msg)
        clean_msg = re.sub(
            r"((?:password|passwd|otp|token|code|secret)=)([^&\s]+)",
            r"\1[REDACTED]",
            clean_msg,
            flags=re.IGNORECASE,
        )

        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": clean_msg,
            "request_id": get_current_request_id(),
        }

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            log_entry["exception"] = SENSITIVE_VALUE_PATTERN.sub(r"\1[REDACTED]", record.exc_text)

        # Include custom extra fields if provided
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "message",
            }:
                log_entry[key] = redact_sensitive_value(value)

        return json.dumps(log_entry, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configures root and application loggers with JSON formatting and redaction."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to prevent duplicate lines
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONLogFormatter())
    handler.addFilter(RedactionFilter())
    root_logger.addHandler(handler)
