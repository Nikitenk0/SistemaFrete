import logging
import os

from logging.handlers import RotatingFileHandler
from pathlib import Path


LOGGER_NAME = "sistemafrete"

_LOG_FILENAME = "sistemafrete.log"
_MAX_LOG_SIZE = 2 * 1024 * 1024
_BACKUP_COUNT = 5


def _get_log_directory() -> Path:

    configured_directory = os.getenv(
        "SISTEMAFRETE_LOG_DIR"
    )

    if configured_directory:

        return Path(
            configured_directory
        ).expanduser()

    if os.name == "nt":

        local_app_data = os.getenv(
            "LOCALAPPDATA"
        )

        if local_app_data:

            return (
                Path(local_app_data)
                / "SistemaFrete"
                / "logs"
            )

    return (
        Path.home()
        / ".sistemafrete"
        / "logs"
    )


def configure_logging() -> None:

    log_directory = _get_log_directory()

    log_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    log_path = (
        log_directory
        / _LOG_FILENAME
    )

    logger = logging.getLogger(
        LOGGER_NAME
    )

    logger.setLevel(
        logging.INFO
    )

    logger.propagate = False

    if logger.handlers:
        return

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=_MAX_LOG_SIZE,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8"
    )

    file_handler.setLevel(
        logging.INFO
    )

    file_handler.setFormatter(
        logging.Formatter(
            (
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(message)s"
            )
        )
    )

    logger.addHandler(
        file_handler
    )