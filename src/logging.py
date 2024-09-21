from __future__ import annotations  # to postpone the evaluation of annotations

import gzip
import json
import logging
import pathlib
import shutil
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from typing import TYPE_CHECKING, Any, Literal, Self

from src.setting import settings

from . import __name__, __version__

if TYPE_CHECKING:
    from logging import LogRecord


TIMEZONE = time.strftime("%Z")
ISO_DATE_FORMAT_STRING = "[{asctime}.{msecs:>03.0f}" + TIMEZONE + "]"
DEFAULT_DATETIME_FORMAT = r"%Y-%m-%dT%H:%M:%S"


def get_logging_foramtters_dict() -> dict:
    return {
        "verbose": {
            "format": (
                ISO_DATE_FORMAT_STRING
                + " - [{levelname}]"
                + " - [{name}:{funcName}#L{lineno}]"
                + " - [{processName}#{process}]"
                + " - [{threadName}#{thread}]"
                + " - {message}"
            ),
            "datefmt": DEFAULT_DATETIME_FORMAT,
            "style": "{",
        },
        "simple": {
            "format": ISO_DATE_FORMAT_STRING + " - [{levelname}]" + " - {message}",
            "datefmt": DEFAULT_DATETIME_FORMAT,
            "style": "{",
        },
        "json": {
            "()": "src.logging.JSONFormatter",
            "datefmt": DEFAULT_DATETIME_FORMAT,
        },
    }


def get_logging_filters_dict() -> dict:
    return {}


def get_logging_handlers_dict(log_level: str, log_file: str) -> dict:
    return {
        "console": {
            "level": log_level,
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stderr,
        },
        "json_console": {
            "level": log_level,
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": sys.stderr,
        },
        "file": {
            "level": log_level,
            "class": "src.logging.CompressedTimedRotatingFileHandler",
            "formatter": "verbose",
            "filename": log_file,
            "when": "midnight",
            "interval": 1,
            "backupCount": 3,
            "encoding": "UTF-8-SIG",
        },
        "json_file": {
            "level": log_level,
            "class": "src.logging.CompressedTimedRotatingFileHandler",
            "formatter": "json",
            "filename": log_file,
            "when": "midnight",
            "interval": 1,
            "backupCount": 3,
            "encoding": "UTF-8-SIG",
        },
    }


def get_logging_dict(log_filename: str = "app.log") -> dict[str, Any]:
    """Returns the configured logging dictionary."""

    handler_log_directory = pathlib.Path(settings.BASE_DIR).joinpath(
        rf"logs/{__name__}/v{__version__}"
    )
    handler_log_directory.mkdir(mode=0o755, exist_ok=True, parents=True)
    handler_log_file = handler_log_directory.joinpath(log_filename).resolve().as_posix()
    handler_log_level = "DEBUG" if settings.ENVIRONMENT == "development" else "INFO"

    logger_log_level = "INFO" if settings.ENVIRONMENT == "development" else "WARNING"
    logger_handlers = (
        ["console"]
        if settings.ENVIRONMENT == "development"
        else ["json_console", "json_file"]
    )

    return {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": get_logging_foramtters_dict(),
        "filters": get_logging_filters_dict(),
        "handlers": {
            handler_name: handler
            for handler_name, handler in get_logging_handlers_dict(
                log_level=handler_log_level, log_file=handler_log_file
            ).items()
            if handler_name in set(logger_handlers)
        },
        "root": {
            "level": logger_log_level,
            "handlers": logger_handlers,
        },
        "loggers": {
            "src": {
                "level": "INFO",
                "handlers": logger_handlers,
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": logger_handlers,
                "propagate": False,
            },
        },
    }


class JSONFormatter(logging.Formatter):
    def __init__(self: Self, datefmt: str = r"%Y-%m-%dT%H:%M:%S") -> None:
        super().__init__()
        self.datefmt = datefmt

    def usesTime(self: Self) -> Literal[True]:
        """Check if the format uses the creation time of the record."""

        return True

    def format(self: Self, record: LogRecord) -> str:
        """Format the specified record as text."""

        super().format(record)  # format log record.
        return json.dumps(vars(record), skipkeys=True, default=str, sort_keys=True)


class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    A handler that logs to a file, rotates the log at specified intervals, and
    compresses the rotated logs using gzip.

    References
    ----------
    [1] https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
    """

    @staticmethod
    def _namer(name: str) -> str:
        return name + ".gz"

    @staticmethod
    def _rotator(source: str, dest: str) -> None:
        with pathlib.Path(source).open("rb") as fin, gzip.open(dest, "wb") as fout:
            shutil.copyfileobj(fin, fout)

        pathlib.Path(source).unlink()

    namer = _namer
    rotator = _rotator
