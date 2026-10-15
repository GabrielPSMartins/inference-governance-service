import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.context import get_request_id

APP_LOGGER_NAME = "app"


class RequestIdFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        payload.update(getattr(record, "fields", {}))

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    logger = logging.getLogger(APP_LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    if any(isinstance(h.formatter, JsonFormatter) for h in logger.handlers):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    logger.addHandler(handler)


def log_event(
    logger: logging.Logger,
    level: int,
    event: str,
    *,
    exc_info: bool = False,
    **fields: Any,
) -> None:

    logger.log(level, event, exc_info=exc_info, extra={"fields": fields})
