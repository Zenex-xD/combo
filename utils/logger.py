# language: Python 3.11 — utils/logger.py
import logging
import sys

from config import LOG_LEVEL


def setup_logger(name: str = "bot") -> logging.Logger:
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    log.addHandler(handler)
    log.propagate = False
    return log


log = setup_logger()
