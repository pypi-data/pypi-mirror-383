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
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO, Union

from pythonjsonlogger import jsonlogger


@dataclass
class LoggerConfig:
    name: str
    level: str


@dataclass
class OutputConfig:
    destination: Union[TextIO, Path]
    structured: bool


@dataclass
class LoggingConfig:
    logger_configs: list[LoggerConfig]
    output_configs: list[OutputConfig]
    root_level: str = "INFO"
    to_silence: list[str] = field(default_factory=lambda: _DEFAULT_NOISY_LOGGERS)

    @classmethod
    def default(cls):
        return LoggingConfig(
            logger_configs=[LoggerConfig(name="nemo_data_designer", level="INFO")],
            output_configs=[OutputConfig(destination=sys.stderr, structured=False)],
        )

    @classmethod
    def debug(cls):
        return LoggingConfig(
            logger_configs=[LoggerConfig(name="nemo_data_designer", level="DEBUG")],
            output_configs=[OutputConfig(destination=sys.stderr, structured=False)],
        )


def configure_logging(config: LoggingConfig) -> None:
    root_logger = logging.getLogger()

    # Remove all handlers
    root_logger.handlers.clear()

    # Create and attach handler(s)
    handlers = [_create_handler(output_config) for output_config in config.output_configs]
    for handler in handlers:
        root_logger.addHandler(handler)

    # Set levels
    root_logger.setLevel(config.root_level)
    for logger_config in config.logger_configs:
        logger = logging.getLogger(logger_config.name)
        logger.setLevel(logger_config.level)

    # Adjust noisy loggers
    for name in config.to_silence:
        quiet_noisy_logger(name)


def quiet_noisy_logger(name: str) -> None:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.WARNING)


def _create_handler(output_config: OutputConfig) -> logging.Handler:
    if isinstance(output_config.destination, Path):
        handler = logging.FileHandler(str(output_config.destination))
    else:
        handler = logging.StreamHandler()

    if output_config.structured:
        formatter = _make_json_formatter()
    else:
        formatter = _make_stream_formatter()

    handler.setFormatter(formatter)
    return handler


def _make_json_formatter() -> logging.Formatter:
    log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    return jsonlogger.JsonFormatter(log_format)


def _make_stream_formatter() -> logging.Formatter:
    log_format = "[%(asctime)s] [%(levelname)s] %(message)s"
    time_format = "%H:%M:%S"
    return logging.Formatter(log_format, time_format)


_DEFAULT_NOISY_LOGGERS = ["httpx", "matplotlib"]
