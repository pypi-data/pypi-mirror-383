"""
logger.py - Centralized logging configuration for the PropIntel FastAPI backend.

This module:
1. Creates and configures a RotatingFileHandler for persistent log storage.
2. Directs logs to both console (StreamHandler) and file (app.log).
3. Supports configurable log level via environment variable (LOG_LEVEL).
4. Suppresses noisy third-party loggers like uvicorn and watchfiles.
5. Provides a helper function `get_logger` for consistent logger creation.

Log rotation:
- Each log file can grow up to 5 MB (maxBytes=5_000_000).
- Keeps 5 backup files (app.log.1, app.log.2, ...).

Usage:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Your log message")
"""

import logging
from logging.handlers import RotatingFileHandler
import os

# --- Log directory and file setup ---
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

# --- Logging level configuration ---
# Can be overridden via environment variable: LOG_LEVEL=DEBUG / INFO / WARNING / ERROR
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


# --- Base logger configuration ---
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        # File handler with rotation
        RotatingFileHandler(LOG_FILE_PATH, maxBytes=5_000_000, backupCount=5),
        # Console output
        logging.StreamHandler()
    ]
)

# --- Suppress noisy third-party loggers ---
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("watchfiles").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with the given name.
    Use this to ensure consistent logging across the project.

    Args:
        name (str): Typically __name__, so logs show the module name.

    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)
