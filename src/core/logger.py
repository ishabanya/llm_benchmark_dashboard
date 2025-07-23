"""Logging configuration for the LLM benchmark framework."""

import logging
import os
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "llm_bench",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """Set up logger with appropriate handlers and formatting."""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all messages
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_evaluation_logger() -> logging.Logger:
    """Get logger specifically for evaluation runs."""
    log_file = os.getenv("LOG_FILE", "llm_bench.log")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    return setup_logger(
        name="llm_bench.evaluation",
        level=log_level,
        log_file=log_file,
        console_output=True
    )