import contextlib
import logging
import os
import platform
import shutil
import sys
import uuid
from pathlib import Path

from frogml.core.inner.build_config.build_config_v1 import BuildConfigV1
from frogml.core.inner.build_logic.constants.host_resource import HOST_FROGML_HIDDEN_FOLDER

from frogml_cli import __version__ as frogml_cli_version
from frogml_cli.inner.tools.logger import setup_frogml_logger
from frogml_cli.inner.tools.logger.logger import (
    BUILD_LOCAL_FILE_HANDLER_NAME,
    BUILD_LOCAL_LOGGER_NAME,
    CONSOLE_HANDLER_NAME,
    REMOTE_CONSOLE_HANDLER_NAME,
    REMOTE_LOGGER_NAME,
    VERBOSITY_LEVEL_MAPPING,
    get_frogml_logger,
    non_frogml_logger_enabled,
    set_file_handler_log_file,
    set_handler_verbosity,
)

BUILDS_LOGS = HOST_FROGML_HIDDEN_FOLDER / "logs" / "build"
BUILD_LOG_NAME = "build.log"
MAX_LOGS_NUMBER = 15
DEBUG_LEVEL = 2


@contextlib.contextmanager
def get_build_logger(config: BuildConfigV1, json_logs: bool):
    log_path = BUILDS_LOGS / config.build_properties.model_id / str(uuid.uuid4())[:4]
    log_path.mkdir(parents=True, exist_ok=True)
    try:
        (log_path / "build_config.yml").write_text(config.to_yaml())
        log_system_information(log_path)

        log_file = log_path / BUILD_LOG_NAME
        setup_frogml_logger()
        yield setup_logger(
            log_file=log_file, verbosity_level=config.verbose, json_logs=json_logs
        ), log_path
    finally:
        # Cleanup - Save only x last zips
        logs_zip_sorted_by_data = sorted(
            BUILDS_LOGS.rglob("**/*"), key=os.path.getmtime
        )[:-MAX_LOGS_NUMBER]
        path: Path
        for path in logs_zip_sorted_by_data:
            if path.is_file():
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)


def setup_logger(
    log_file: Path, verbosity_level: int, json_logs: bool
) -> logging.Logger:
    # Init logger
    fallback_logger_name = (
        BUILD_LOCAL_LOGGER_NAME if not json_logs else REMOTE_LOGGER_NAME
    )
    logger = get_frogml_logger(fallback_logger_name=fallback_logger_name)

    if not non_frogml_logger_enabled():
        if logger.name == BUILD_LOCAL_LOGGER_NAME:
            set_file_handler_log_file(logger, BUILD_LOCAL_FILE_HANDLER_NAME, log_file)
            set_handler_verbosity(
                logger, CONSOLE_HANDLER_NAME, VERBOSITY_LEVEL_MAPPING[verbosity_level]
            )
        elif logger.name == REMOTE_LOGGER_NAME and json_logs:
            set_handler_verbosity(
                logger,
                REMOTE_CONSOLE_HANDLER_NAME,
                VERBOSITY_LEVEL_MAPPING[DEBUG_LEVEL],
            )

    return logger


def log_system_information(destination: Path):
    (destination / "python_version").write_text(sys.version)
    (destination / "frogml_cli_version").write_text(frogml_cli_version)
    (destination / "os_detail").write_text(platform.platform())
