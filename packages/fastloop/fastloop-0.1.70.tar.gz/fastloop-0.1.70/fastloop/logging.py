import json
import logging
import sys
from typing import Any, ClassVar

_logger = None


class LoggerRedirectHandler(logging.Handler):
    def __init__(self, target_logger: logging.Logger) -> None:
        super().__init__()
        self.target_logger = target_logger

    def emit(self, record: logging.LogRecord) -> None:
        for handler in self.target_logger.handlers:
            handler.emit(record)


class PrettyFormatter(logging.Formatter):
    """Pretty formatter with colors and structured field display"""

    COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
        "BOLD": "\033[1m",  # Bold
        "BLUE": "\033[34m",  # Blue
    }

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)

        extra_fields = self._extract_extra_fields(record)
        if extra_fields:
            field_str = " | ".join(
                [
                    f"{self.COLORS['BLUE']}{k}{self.COLORS['RESET']}={v}"
                    for k, v in extra_fields.items()
                ]
            )
            formatted += f" {self.COLORS['BOLD']}|{self.COLORS['RESET']} {field_str}"

        location = f"{record.filename}:{record.lineno}"
        formatted += f" {self.COLORS['BOLD']}|{self.COLORS['RESET']} {self.COLORS['BLUE']}location{self.COLORS['RESET']}={location}"

        return formatted

    def _extract_extra_fields(self, record: logging.LogRecord) -> dict[str, Any]:
        """Extract extra fields from the log record"""
        # Fields to exclude from structured logging
        exclude_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "getMessage",
            "exc_info",
            "exc_text",
            "stack_info",
            # Uvicorn internal fields
            "color_message",
            "taskName",
            "asctime",
            "message",
        }

        extra_fields: dict[str, Any] = {}
        for key, value in record.__dict__.items():
            if key not in exclude_fields:
                extra_fields[key] = value
        return extra_fields


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.levelno >= logging.ERROR:
            log_entry["location"] = f"{record.filename}:{record.lineno}"

        # Add extra fields (filtered)
        exclude_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "getMessage",
            "exc_info",
            "exc_text",
            "stack_info",
            # Uvicorn internal fields
            "color_message",
            "taskName",
            "asctime",
            "message",
        }

        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in exclude_fields:
                extra_fields[key] = value

        if extra_fields:
            log_entry["fields"] = extra_fields  # type: ignore

        return json.dumps(log_entry)


def setup_logger(
    name: str = "fastloop", level: int = logging.INFO, pretty_print: bool = True
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        if pretty_print:
            formatter = PrettyFormatter(
                "[%(asctime)s: %(levelname)s/%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            formatter = JSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Redirect uvicorn and fastapi logs
        redirect_handler = LoggerRedirectHandler(logger)
        for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
            specific_logger = logging.getLogger(logger_name)
            specific_logger.handlers = [redirect_handler]
            specific_logger.setLevel(level)
            specific_logger.propagate = False

        root_logger = logging.getLogger()
        root_logger.handlers = [redirect_handler]
        root_logger.setLevel(level)
        root_logger.propagate = False

    return logger


def configure_logging(pretty_print: bool = True) -> None:
    """Configure the global logging format for all handlers."""

    root_logger = logging.getLogger()
    if pretty_print:
        formatter = PrettyFormatter(
            "[%(asctime)s: %(levelname)s/%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = JSONFormatter()
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)

    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        specific_logger = logging.getLogger(logger_name)
        for handler in specific_logger.handlers:
            handler.setFormatter(formatter)
