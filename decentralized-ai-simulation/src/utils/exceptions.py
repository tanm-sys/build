"""
Custom Exception Classes for File Management Utilities

This module defines comprehensive exception hierarchy for file management operations,
providing detailed error context and facilitating proper error handling strategies.
"""

from typing import Optional, Dict, Any
import logging

try:
    from src.utils.logging_setup import get_logger
except ImportError:
    try:
        from utils.logging_setup import get_logger
    except ImportError:
        import logging
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class FileManagementError(Exception):
    """
    Base exception class for all file management operations.

    This is the root exception for the file management system, providing
    common functionality for error context and logging.
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize FileManagementError with detailed context.

        Args:
            message: Human-readable error message
            file_path: Path related to the error (if applicable)
            operation: Operation that failed (e.g., 'read', 'write', 'move')
            context: Additional context information
            cause: Original exception that caused this error
        """
        super().__init__(message)

        self.message = message
        self.file_path = file_path
        self.operation = operation
        self.context = context or {}
        self.cause = cause
        self.timestamp = None  # Will be set by logging system

        # Log the error with full context
        self._log_error()

    def _log_error(self) -> None:
        """Log the error with appropriate level and context."""
        log_data = {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'file_path': self.file_path,
            'operation': self.operation,
            'context': self.context
        }

        if self.cause:
            log_data['cause'] = str(self.cause)
            log_data['cause_type'] = self.cause.__class__.__name__

        # Log as error for serious issues, warning for recoverable ones
        if isinstance(self, (ValidationError, ConfigurationError)):
            logger.warning(f"File management issue: {log_data}")
        else:
            logger.error(f"File management error: {log_data}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'file_path': self.file_path,
            'operation': self.operation,
            'context': self.context,
            'cause': str(self.cause) if self.cause else None,
            'timestamp': self.timestamp
        }

    def __str__(self) -> str:
        """Enhanced string representation with context."""
        parts = [self.message]

        if self.file_path:
            parts.append(f"File: {self.file_path}")
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.cause:
            parts.append(f"Cause: {self.cause}")

        return " | ".join(parts)


class FileOperationError(FileManagementError):
    """
    Exception raised for file operation failures.

    This includes read, write, copy, move, and delete operations.
    """
    pass


class DirectoryError(FileManagementError):
    """
    Exception raised for directory-related errors.

    This includes directory creation, permission, and traversal errors.
    """
    pass


class ValidationError(FileManagementError):
    """
    Exception raised for file/data validation failures.

    This includes format validation, integrity checks, and schema validation.
    """
    pass


class ConfigurationError(FileManagementError):
    """
    Exception raised for configuration-related errors.

    This includes missing config files, invalid formats, and schema violations.
    """
    pass


class MigrationError(FileManagementError):
    """
    Exception raised for migration operation failures.

    This includes file reorganization, import updates, and rollback failures.
    """

    def __init__(
        self,
        message: str,
        migration_step: Optional[str] = None,
        rollback_attempted: bool = False,
        **kwargs
    ):
        """
        Initialize MigrationError with migration-specific context.

        Args:
            message: Error message
            migration_step: Current step in migration process
            rollback_attempted: Whether rollback was attempted
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.migration_step = migration_step
        self.rollback_attempted = rollback_attempted

        if migration_step:
            self.context['migration_step'] = migration_step
        self.context['rollback_attempted'] = rollback_attempted


class RetryableError(FileManagementError):
    """
    Exception raised for errors that may succeed on retry.

    This includes network timeouts, temporary locks, and resource conflicts.
    """

    def __init__(
        self,
        message: str,
        retry_count: int = 0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs
    ):
        """
        Initialize RetryableError with retry information.

        Args:
            message: Error message
            retry_count: Number of retries already attempted
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.context.update({
            'retry_count': retry_count,
            'max_retries': max_retries,
            'retry_delay': retry_delay
        })

    def should_retry(self) -> bool:
        """Check if operation should be retried."""
        return self.retry_count < self.max_retries

    def get_next_retry_delay(self) -> float:
        """Get delay before next retry attempt."""
        return self.retry_delay * (2 ** self.retry_count)  # Exponential backoff


class SecurityError(FileManagementError):
    """
    Exception raised for security-related file operation errors.

    This includes permission violations, suspicious file access, and security policy violations.
    """

    def __init__(
        self,
        message: str,
        security_violation: Optional[str] = None,
        risk_level: str = 'medium',
        **kwargs
    ):
        """
        Initialize SecurityError with security context.

        Args:
            message: Error message
            security_violation: Type of security violation
            risk_level: Risk level (low, medium, high, critical)
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.security_violation = security_violation
        self.risk_level = risk_level

        self.context.update({
            'security_violation': security_violation,
            'risk_level': risk_level
        })


class ResourceError(FileManagementError):
    """
    Exception raised for resource-related errors.

    This includes disk space, memory, and handle limit errors.
    """

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        available: Optional[int] = None,
        required: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize ResourceError with resource context.

        Args:
            message: Error message
            resource_type: Type of resource (disk, memory, handles)
            available: Available resource amount
            required: Required resource amount
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.available = available
        self.required = required

        self.context.update({
            'resource_type': resource_type,
            'available': available,
            'required': required
        })


# Utility functions for error handling

def handle_file_operation_error(error: Exception, operation: str, file_path: str) -> FileManagementError:
    """
    Convert generic exceptions to appropriate FileManagementError types.

    Args:
        error: Original exception
        operation: Operation that was being performed
        file_path: File path related to the operation

    Returns:
        Appropriate FileManagementError subclass
    """
    error_message = f"Failed {operation} operation on {file_path}: {str(error)}"

    # Map common exceptions to appropriate types
    if isinstance(error, PermissionError):
        return SecurityError(
            error_message,
            security_violation='permission_denied',
            file_path=file_path,
            operation=operation,
            cause=error
        )
    elif isinstance(error, FileNotFoundError):
        return FileOperationError(
            error_message,
            file_path=file_path,
            operation=operation,
            cause=error
        )
    elif isinstance(error, IsADirectoryError):
        return ValidationError(
            error_message,
            file_path=file_path,
            operation=operation,
            cause=error
        )
    elif isinstance(error, OSError):
        # Check for specific OS error codes
        if error.errno in (28,):  # No space left on device
            return ResourceError(
                error_message,
                resource_type='disk_space',
                file_path=file_path,
                operation=operation,
                cause=error
            )
        else:
            return FileOperationError(
                error_message,
                file_path=file_path,
                operation=operation,
                cause=error
            )
    else:
        return FileOperationError(
            error_message,
            file_path=file_path,
            operation=operation,
            cause=error
        )


def create_error_context(
    operation: str,
    file_path: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create standardized error context dictionary.

    Args:
        operation: Operation being performed
        file_path: File path related to operation
        **kwargs: Additional context information

    Returns:
        Dictionary containing error context
    """
    import traceback
    import os
    from datetime import datetime

    context = {
        'operation': operation,
        'timestamp': datetime.utcnow().isoformat(),
        'process_id': os.getpid(),
        'thread_id': getattr(__import__('threading').current_thread(), 'ident', None),
        'traceback': traceback.format_stack()[-3:-1],  # Last few stack frames
        **kwargs
    }

    if file_path:
        context['file_path'] = file_path
        # Add file system context
        try:
            path_obj = __import__('pathlib').Path(file_path)
            if path_obj.exists():
                stat = path_obj.stat()
                context.update({
                    'file_size': stat.st_size,
                    'file_modified': stat.st_mtime,
                    'file_permissions': oct(stat.st_mode)
                })
        except Exception:
            pass  # Ignore file system info errors

    return context