"""Logging configuration for the bot."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

import colorlog

from app.core.config import config

def setup_logger(name: str = "veka") -> logging.Logger:
    """Setup and configure logger with color support."""
    logger = colorlog.getLogger(name)
    
    if logger.handlers:  # Return if logger is already configured
        return logger
    
    # Set log level from config
    logger.setLevel(getattr(logging, config.logging.log_level.upper()))
    
    # Create console handler with color formatting
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )
    
    # Create file handler
    log_file = Path(config.logging.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config.logging.max_file_size,
        backupCount=config.logging.backup_count
    )
    file_handler.setFormatter(logging.Formatter(config.logging.log_format))
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger() 