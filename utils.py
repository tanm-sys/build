"""
Common utilities module to eliminate code duplication and improve organization.
Provides shared functionality across the application.
"""

import os
import sys
from typing import Any, Dict, List, Optional, Type, Union
from functools import wraps
import time
import logging

# Import with fallback to handle duplicate files
try:
    from decentralized_ai_simulation.src.utils.logging_setup import get_logger
except ImportError:
    try:
        from logging_setup import get_logger
    except ImportError:
        # Final fallback to basic logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


def safe_import(module_name: str, fallback_module_name: str = None) -> Any:
    """Safely import a module with fallback options.

    Args:
        module_name: Primary module name to import
        fallback_module_name: Fallback module name if primary fails

    Returns:
        Imported module or None if all imports fail
    """
    modules_to_try = [module_name]
    if fallback_module_name:
        modules_to_try.append(fallback_module_name)

    for module in modules_to_try:
        try:
            return __import__(module, fromlist=[''])
        except ImportError:
            logger.debug(f"Failed to import {module}")
            continue

    logger.warning(f"Failed to import any of: {modules_to_try}")
    return None


def validate_input(value: Any, param_name: str, expected_type: Type,
                  min_val: Any = None, max_val: Any = None,
                  allow_none: bool = False) -> None:
    """Comprehensive input validation utility.

    Args:
        value: Value to validate
        param_name: Name of the parameter for error messages
        expected_type: Expected type of the value
        min_val: Minimum allowed value (for numeric types)
        max_val: Maximum allowed value (for numeric types)
        allow_none: Whether None values are allowed

    Raises:
        ValueError: If validation fails
        TypeError: If type validation fails
    """
    # None validation
    if value is None and not allow_none:
        raise ValueError(f"{param_name} cannot be None")
    elif value is None and allow_none:
        return

    # Type validation
    if not isinstance(value, expected_type):
        raise TypeError(f"{param_name} must be {expected_type.__name__}, got {type(value).__name__}")

    # Range validation for numeric types
    if expected_type in (int, float):
        if min_val is not None and value < min_val:
            raise ValueError(f"{param_name} must be >= {min_val}, got {value}")
        if max_val is not None and value > max_val:
            raise ValueError(f"{param_name} must be <= {max_val}, got {value}")
    elif expected_type == str:
        if not value.strip():  # Empty or whitespace-only strings
            raise ValueError(f"{param_name} cannot be empty or whitespace-only")


def performance_timer(func_name: str = None):
    """Decorator to measure and log function execution time.

    Args:
        func_name: Optional name for the function (defaults to function's __name__)

    Returns:
        Decorated function with timing
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or func.__name__

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                if execution_time > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation: {name} took {execution_time:.2f}s")
                else:
                    logger.debug(f"Operation {name} completed in {execution_time:.4f}s")

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Operation {name} failed after {execution_time:.4f}s: {e}")
                raise

        return wrapper
    return decorator


def batch_process(items: List[Any], processor_func, batch_size: int = 100,
                 continue_on_error: bool = True) -> List[Any]:
    """Process items in batches with error handling.

    Args:
        items: List of items to process
        processor_func: Function to process each item
        batch_size: Size of each processing batch
        continue_on_error: Whether to continue processing if individual items fail

    Returns:
        List of successfully processed results
    """
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        for item in batch:
            try:
                result = processor_func(item)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing item {i}: {e}")
                if not continue_on_error:
                    raise

    return results


def get_config_with_fallback(key: str, default: Any = None, config_source: str = None) -> Any:
    """Get configuration value with multiple fallback sources.

    Args:
        key: Configuration key to retrieve
        default: Default value if key not found
        config_source: Specific config source to use

    Returns:
        Configuration value or default
    """
    try:
        # Try to import and use config_loader
        config_loader = safe_import('config_loader')
        if config_loader:
            return config_loader.get_config(key, default)
    except Exception as e:
        logger.debug(f"Config loader not available: {e}")

    # Fallback to environment variables
    env_key = key.upper().replace('.', '_')
    env_value = os.environ.get(env_key)
    if env_value is not None:
        return env_value

    return default


def create_directory_if_not_exists(dir_path: str) -> bool:
    """Create directory if it doesn't exist with proper error handling.

    Args:
        dir_path: Path of directory to create

    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {dir_path}: {e}")
        return False


class ResourceManager:
    """Context manager for resource cleanup and management."""

    def __init__(self):
        self.resources = []
        self.cleanup_functions = []

    def add_resource(self, resource: Any, cleanup_func: callable = None) -> None:
        """Add a resource to be managed.

        Args:
            resource: Resource to manage
            cleanup_func: Optional cleanup function for the resource
        """
        self.resources.append(resource)
        if cleanup_func:
            self.cleanup_functions.append((resource, cleanup_func))

    def cleanup(self) -> None:
        """Clean up all managed resources."""
        for resource, cleanup_func in self.cleanup_functions:
            try:
                if cleanup_func:
                    cleanup_func(resource)
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
                elif hasattr(resource, 'close'):
                    resource.close()
            except Exception as e:
                logger.error(f"Error cleaning up resource: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


def format_bytes(bytes_value: int) -> str:
    """Format bytes value into human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., '1.5 MB', '256 KB')
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values.

    Args:
        old_value: Original value
        new_value: New value

    Returns:
        Percentage change (positive for increase, negative for decrease)
    """
    if old_value == 0:
        return 0.0 if new_value == 0 else float('inf')
    return ((new_value - old_value) / old_value) * 100.0