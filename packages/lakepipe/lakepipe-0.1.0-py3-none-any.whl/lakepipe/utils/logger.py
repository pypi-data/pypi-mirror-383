"""Logging utilities for LakePipe."""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

# Global console for rich output
console = Console()


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    rich_output: bool = True
) -> None:
    """Setup logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        rich_output: Use rich formatting for console output
    """
    # Remove existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # Console handler
    if rich_output:
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        console_format = "%(message)s"
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    console_handler.setFormatter(logging.Formatter(console_format))
    root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
