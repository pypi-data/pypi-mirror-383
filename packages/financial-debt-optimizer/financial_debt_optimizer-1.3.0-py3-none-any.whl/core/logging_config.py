"""Logging configuration for the Financial Debt Optimizer."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO", log_file: Optional[str] = None, console_output: bool = True
) -> logging.Logger:
    """Set up logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        console_output: Whether to output logs to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("financial_debt_optimizer")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # Always debug level for file
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (will be prefixed with main app name)

    Returns:
        Logger instance
    """
    if name:
        full_name = f"financial_debt_optimizer.{name}"
    else:
        full_name = "financial_debt_optimizer"

    return logging.getLogger(full_name)
