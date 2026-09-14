"""Structured JSON logs (tech:4774-4784, tech:5841, plan:2579-2588)."""

import json
import logging
import sys
from datetime import UTC, datetime

LOGGER_NAME = "app"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
        }
        fields = getattr(record, "fields", None)
        if fields:
            payload.update(fields)
        else:
            payload["message"] = record.getMessage()
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    logger = logging.getLogger(LOGGER_NAME)
    if any(isinstance(h.formatter, JsonFormatter) for h in logger.handlers):
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{LOGGER_NAME}.{name}")
