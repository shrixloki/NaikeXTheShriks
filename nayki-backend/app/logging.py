import logging
import sys
from contextvars import ContextVar

import structlog
from structlog.types import EventDict, WrappedLogger

# ContextVar to store request ID across async tasks
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def add_request_id(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Structlog processor to inject request_id from context variables."""
    req_id = request_id_var.get()
    if req_id:
        event_dict["request_id"] = req_id
    return event_dict


def redact_coordinates(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Structlog processor to automatically redact raw exact coordinates.

    This ensures that raw latitude, longitude, and exact geometry are never
    leaked to logs.
    """
    coordinate_keys = {
        "lat",
        "lng",
        "latitude",
        "longitude",
        "coords",
        "coordinates",
        "location",
        "geo",
    }

    # Redact matching keys
    for key in list(event_dict.keys()):
        if any(coord_key in key.lower() for coord_key in coordinate_keys):
            event_dict[key] = "[REDACTED_COORD]"

    return event_dict


def configure_logging(log_level: str = "INFO", app_env: str = "local") -> None:
    """Configure structured logging using structlog."""
    # Configure standard logging to redirect to stdout
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(log_level.upper()),
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_request_id,
        redact_coordinates,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if app_env == "local":
        # Human-friendly colorized output for local dev
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Structured JSON for production logging dashboards
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level.upper())
        ),
        cache_logger_on_first_use=True,
    )


# Get standard structured logger
logger = structlog.get_logger()
