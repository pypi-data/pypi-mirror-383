# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys
import time
from enum import Enum
from logging import config

from pythonjsonlogger import jsonlogger

_LOGGING_CONFIGURED = False
"""
Ensure that our logging is only configured once.
"""


def _get_log_format() -> str:
    # Use ISO 8601 timestamps.
    # Note: it requires separate millisecond section, since ``strftime`` format doesn't support milliseconds.
    # That %(msecs)d structure is defined in logging.Formatter.
    fmt = "%(asctime)s.%(msecs)03dZ [%(process)d] - %(levelname)s - %(name)s - %(message)s"

    return fmt


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if level := log_record.get("level"):
            log_record["level"] = level.upper()
        else:
            log_record["level"] = record.levelname


class UTCFormatter(logging.Formatter):
    """
    Formatter that uses ISO 8601 timestamps, with UTC timezone.

    This matches format that AWS Lambda is using and it's also default for CloudWatch Logs agent.
    Sample log line: ``2021-03-03T02:03:45,110Z - INFO - nemo_safe_synthesizer.legacy.gretel_core - TEST``

    See: https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime
    """

    def __init__(self, fmt: str):
        super().__init__(
            fmt=fmt,
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

        # change timezone used for timestamps to UTC
        self.converter = time.gmtime


def _get_default_logging_level() -> int:
    if os.getenv("GRETEL_DEBUG_LOGGING") == "yes":
        return logging.DEBUG

    return logging.INFO


STANDARD_LOG_FORMAT = "%(asctime)s %(process)s %(level)s %(name)s %(message)s"


class LoggingFormat(Enum):
    JSON = "json"
    PLAIN = "plain"

    @staticmethod
    def from_str(input: str) -> "LoggingFormat":
        if input == "json":
            return LoggingFormat.JSON
        if input == "plain" or not input:
            return LoggingFormat.PLAIN
        print(
            f"Unrecognized logging format: '{input}', using default plain",
            file=sys.stderr,
        )
        return LoggingFormat.PLAIN


class StandardHandler(logging.StreamHandler):
    def __init__(self) -> None:
        logging.StreamHandler.__init__(self, stream=sys.stdout)
        logging_format = LoggingFormat.from_str(os.getenv("LOGGING_FORMAT"))
        if logging_format == LoggingFormat.JSON:
            self.formatter = CustomJsonFormatter(STANDARD_LOG_FORMAT)
        else:
            self.formatter = UTCFormatter(_get_log_format())
        self.level = _get_default_logging_level()

        self.addFilter(DiscardSensitiveMessages())


class DiscardSensitiveMessages(logging.Filter):
    """
    Discards messages marked as sensitive via the `sensitive` flag.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return not getattr(record, "sensitive", False)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "()": StandardHandler,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": _get_default_logging_level(),
    },
}


def configure_logging():
    """
    Configures ``logging`` handlers.

    Default configuration includes:

    - formatter (sample log record ``2021-03-03T02:03:45,110Z - INFO - nemo_safe_synthesizer.utils - TEST``)
    - handler writing to standard output
    """

    config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger with the given name and common configuration.
    """

    global _LOGGING_CONFIGURED

    if not _LOGGING_CONFIGURED or name == "__main__":
        configure_logging()

        _LOGGING_CONFIGURED = True

    return logging.getLogger(name)


class ProgressCallback:
    """ProgressCallback is a callback that tracks or accepts some value indicating a processes progress."""

    def update_inc(self, inc: int):
        """
        update_inc calls the callback with an incremental progress value.

        Args:
            inc: Number processed since last call
        """
        ...

    def update_total(self, total: int):
        """
        update_total calls the callback with a cumulative progress value.

        Args:
            total: Total number processed so far.
        """
        ...

    def flush(self): ...


class DoNothingProgressCallback(ProgressCallback):
    """DoNothingProgressCallback is a ProgressCallback that does nothing."""

    def __init__(self):
        return

    def update_inc(self, inc: int):
        return

    def update_total(self, total: int):
        return

    def flush(self):
        return


class ProgressCallbackFactory:
    """ProgressCallbackFactory produces a ProgressCallback from given kwargs."""

    def get(self, prefix: str) -> ProgressCallback:
        """
        get returns a new instance of a ProgressCallback.

        Args:
            prefix: String to prefix logged progress.
        """
        ...


class DoNothingProgressCallbackFactory(ProgressCallbackFactory):
    """DoNothingProgressCallbackFactory is a ProgressCallbackFactory that only returns DoNothingProgressCallback."""

    def __init__(self):
        return

    def get(self, prefix: str) -> ProgressCallback:
        return DoNothingProgressCallback()


_PROGRESS_CALLBACK_FACTORY: ProgressCallbackFactory = DoNothingProgressCallbackFactory()


def configure_progress_callback_factory(
    progress_callback_factory: ProgressCallbackFactory,
):
    global _PROGRESS_CALLBACK_FACTORY
    _PROGRESS_CALLBACK_FACTORY = progress_callback_factory


def get_progress_callback(prefix: str) -> ProgressCallback:
    global _PROGRESS_CALLBACK_FACTORY
    return _PROGRESS_CALLBACK_FACTORY.get(prefix=prefix)
