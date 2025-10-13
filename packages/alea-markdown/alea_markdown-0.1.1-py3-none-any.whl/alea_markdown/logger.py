"""
Logging module for alea-markdown-converter.

This module provides a centralized logging configuration with the ability
to create both a global application logger as well as specific loggers for
individual modules or classes.

Usage:
    # Get the root package logger
    from alea_markdown.logger import get_logger
    logger = get_logger()
    logger.info("Using root package logger")

    # Get a module-specific logger
    from alea_markdown.logger import get_logger
    logger = get_logger(__name__)
    logger.debug("Using module-specific logger")

    # Get a class-specific logger
    from alea_markdown.logger import get_logger
    class MyClass:
        def __init__(self):
            self.logger = get_logger(self.__class__.__name__)
"""

import logging
import os
import sys
from typing import Optional, Union


# Default logging format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment variable to control log level
LOG_LEVEL_ENV_VAR = "ALEA_MARKDOWN_LOG_LEVEL"

# Default log level if not specified in environment
DEFAULT_LOG_LEVEL = "WARNING"

# Root logger name for the package
ROOT_LOGGER_NAME = "alea_markdown"


def get_log_level() -> int:
    """
    Get the logging level from environment variable or use default.

    Returns:
        int: The logging level as defined in the logging module
    """
    level_name = os.environ.get(LOG_LEVEL_ENV_VAR, DEFAULT_LOG_LEVEL).upper()
    try:
        return getattr(logging, level_name)
    except AttributeError:
        # If an invalid level is specified, fall back to default
        return getattr(logging, DEFAULT_LOG_LEVEL)


def configure_logger(logger: logging.Logger, log_format: Optional[str] = None) -> None:
    """
    Configure a logger with handlers and formatting.

    Args:
        logger: The logger to configure
        log_format: Optional custom log format
    """
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Set the log level
    logger.setLevel(get_log_level())

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(get_log_level())

    # Create formatter
    formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Don't propagate to the root logger
    # This prevents duplicate log messages
    logger.propagate = False


def get_logger(
    name: Optional[Union[str, object]] = None, log_format: Optional[str] = None
) -> logging.Logger:
    """
    Get or create a logger for the specified name.

    Args:
        name: The name for the logger. If None, returns the root package logger.
              If an object is passed, its class name is used.
        log_format: Optional custom log format string

    Returns:
        logging.Logger: A configured logger instance
    """
    # Handle different types of name input
    if name is None:
        logger_name = ROOT_LOGGER_NAME
    elif isinstance(name, str):
        # If it's already a full module name in the package, use it directly
        if name.startswith(ROOT_LOGGER_NAME):
            logger_name = name
        # If it's a short name (like a class name or module name without package prefix)
        elif "." not in name:
            logger_name = f"{ROOT_LOGGER_NAME}.{name}"
        # If it's a module name like "alea_markdown.some_module"
        else:
            logger_name = name
    else:
        # If it's an object, use its class name
        logger_name = f"{ROOT_LOGGER_NAME}.{name.__class__.__name__}"

    # Get or create the logger
    logger = logging.getLogger(logger_name)

    # If this is a new logger or it hasn't been configured yet,
    # set up handlers and formatter
    if not logger.handlers:
        configure_logger(logger, log_format)

    return logger


# Initialize the root package logger
root_logger = get_logger()


# Convenience methods to avoid importing logging module in other files
def set_level(level: Union[int, str]) -> None:
    """
    Set the logging level for the root package logger.

    Args:
        level: The logging level (can be a string like 'DEBUG' or a logging constant)
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    root_logger.setLevel(level)

    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(level)


def set_format(log_format: str) -> None:
    """
    Set the log format for all handlers on the root logger.

    Args:
        log_format: The format string to use
    """
    formatter = logging.Formatter(log_format)
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
