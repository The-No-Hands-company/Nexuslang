"""
Logging utilities for NLPL.
Provides structured logging with levels, formatting, and file output.
"""

import logging
import sys
from typing import Optional
from ...runtime.runtime import Runtime


# Global logger instance
_logger = None
_handlers = []


def _get_logger():
    """Get or create the global logger."""
    global _logger
    if _logger is None:
        _logger = logging.getLogger('nlpl')
        _logger.setLevel(logging.DEBUG)
        # Add console handler by default
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
        _handlers.append(console_handler)
    return _logger


def log_debug(message: str) -> None:
    """Log debug message."""
    _get_logger().debug(message)


def log_info(message: str) -> None:
    """Log info message."""
    _get_logger().info(message)


def log_warning(message: str) -> None:
    """Log warning message."""
    _get_logger().warning(message)


def log_error(message: str) -> None:
    """Log error message."""
    _get_logger().error(message)


def log_critical(message: str) -> None:
    """Log critical message."""
    _get_logger().critical(message)


def set_log_level(level: str) -> None:
    """
    Set logging level.
    Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    log_level = level_map.get(level.upper(), logging.INFO)
    _get_logger().setLevel(log_level)


def add_file_handler(filepath: str, level: str = 'DEBUG') -> bool:
    """Add file handler to logger."""
    try:
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        log_level = level_map.get(level.upper(), logging.DEBUG)
        
        file_handler = logging.FileHandler(filepath)
        file_handler.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        _get_logger().addHandler(file_handler)
        _handlers.append(file_handler)
        return True
    except Exception as e:
        print(f"Failed to add file handler: {e}")
        return False


def remove_all_handlers() -> None:
    """Remove all logging handlers."""
    logger = _get_logger()
    for handler in _handlers[:]:
        logger.removeHandler(handler)
        handler.close()
        _handlers.remove(handler)


def set_log_format(format_string: str) -> None:
    """
    Set log format for all handlers.
    Format variables: %(asctime)s, %(name)s, %(levelname)s, %(message)s, %(filename)s, %(lineno)d
    """
    formatter = logging.Formatter(format_string)
    for handler in _handlers:
        handler.setFormatter(formatter)


def log_exception(message: str = "Exception occurred") -> None:
    """Log exception with traceback."""
    _get_logger().exception(message)


def register_logging_functions(runtime: Runtime) -> None:
    """Register logging functions with the runtime."""
    
    # Log levels
    runtime.register_function("log_debug", log_debug)
    runtime.register_function("log_info", log_info)
    runtime.register_function("log_warning", log_warning)
    runtime.register_function("log_error", log_error)
    runtime.register_function("log_critical", log_critical)
    
    # Configuration
    runtime.register_function("set_log_level", set_log_level)
    runtime.register_function("add_file_handler", add_file_handler)
    runtime.register_function("remove_all_handlers", remove_all_handlers)
    runtime.register_function("set_log_format", set_log_format)
    runtime.register_function("log_exception", log_exception)
    
    # Aliases
    runtime.register_function("debug", log_debug)
    runtime.register_function("info", log_info)
    runtime.register_function("warning", log_warning)
    runtime.register_function("error", log_error)
    runtime.register_function("critical", log_critical)
