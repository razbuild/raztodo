import logging
import os


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
        logger.propagate = False

    level_name = os.getenv("LOG_LEVEL", "ERROR").upper()
    level = getattr(logging, level_name, logging.ERROR)
    logger.setLevel(level)

    return logger
