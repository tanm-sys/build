"""
File Management Utilities for Decentralized AI Simulation

This module provides robust file management capabilities with comprehensive error handling,
atomic operations, and rollback mechanisms for safe file operations.
"""

import os
import shutil
import json
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from contextlib import contextmanager
import logging

try:
    from src.utils.logging_setup import get_logger
except ImportError:
    try:
        from utils.logging_setup import get_logger
    except ImportError:
        import logging
        get_logger = lambda name: logging.getLogger(name)

# Import error classes (defined below)
try:
    from .exceptions import (
        FileManagementError,
        FileOperationError,
        DirectoryError,
        ValidationError,
        ConfigurationError,
        MigrationError
    )
except ImportError:
    from exceptions import (
        FileManagementError,
        FileOperationError,
        DirectoryError,
        ValidationError,
        ConfigurationError,
        MigrationError
    )

logger = get_logger(__name__)


class FileManager:
    """
    Comprehensive file management utilities with atomic operations and rollback capabilities.

    This class provides safe file I/O operations, directory management, file validation,
    and migration support with comprehensive error handling and logging.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize FileManager with optional base path.

        Args:
            base_path: Base directory path for all operations. If None, uses current working directory.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.base_path = self.base_path.resolve()
        self._backup_suffix = '.backup'
        self._temp_suffix = '.tmp'

        logger.info(f"FileManager initialized with base path: {self.base_path}")

    def safe_write_file(
        self,
        file_path: Union[str, Path],
        content: Union[str, bytes],
        backup: bool = True,
        encoding: str = 'utf-8',
        mode: str = 'w'
    ) -> bool:
        """
        Safely write content to a file with atomic operations and optional backup.

        Args:
            file_path: Path to the file to write
            content: Content to write (string or bytes)
            backup: Whether to create a backup of the existing file
            encoding: Text encoding for string content
            mode: File mode for writing

        Returns:
            bool: True if write was successful

        Raises:
            FileOperationError: If write operation fails
        """
        file_path = Path(file_path)

        # Ensure parent directory exists
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise DirectoryError(f"Failed to create parent directory for {file_path}: {e}")

        # Create backup if file exists and backup is requested
        backup_path = None
        if backup and file_path.exists():
            try:
                backup_path = file_path.with_suffix(file_path.suffix + self._backup_suffix)
                if backup_path.exists():
                    backup_path.unlink()  # Remove old backup
                shutil.copy2(file_path, backup_path)
                logger.debug(f"Created backup: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup for {file_path}: {e}")

        # Write to temporary file first (atomic operation)
        temp_path = file_path.with_suffix(file_path.suffix + self._temp_suffix)
        write_successful = False

        try:
            # Write to temporary file
            if isinstance(content, str):
                with open(temp_path, mode, encoding=encoding) as f:
                    f.write(content)
            else:
                with open(temp_path, 'wb') as f:
                    f.write(content)

            # Validate the written content
            if not self._validate_file_integrity(temp_path, content):
                raise FileOperationError(f"Content validation failed for {temp_path}")

            # Atomic move from temp to final location
            temp_path.replace(file_path)
            write_successful = True

            logger.info(f"Successfully wrote file: {file_path}")
            return True

        except Exception as e:
            # Clean up temporary file
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors

            # Restore from backup if available
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, file_path)
                    logger.info(f"Restored from backup: {file_path}")
                except Exception as restore_error:
                    logger.error(f"Failed to restore backup for {file_path}: {restore_error}")

            raise FileOperationError(f"Failed to write file {file_path}: {e}")

        finally:
            # Clean up backup file only if write was successful
            if backup_path and backup_path.exists() and write_successful:
                try:
                    backup_path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors

    def safe_read_file(
        self,
        file_path: Union[str, Path],
        encoding: str = 'utf-8',
        default: Optional[Union[str, bytes]] = None
    ) -> Optional[Union[str, bytes]]:
        """
        Safely read content from a file with error handling.

        Args:
            file_path: Path to the file to read
            encoding: Text encoding for text files
            default: Default content to return if file doesn't exist or can't be read

        Returns:
            File content as string/bytes or default value if file can't be read
        """
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return default

            if file_path.is_dir():
                raise FileOperationError(f"Path is a directory, not a file: {file_path}")

            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                raise FileOperationError(f"File is not readable: {file_path}")

            # Read file based on type
            if file_path.suffix.lower() in ['.json', '.yaml', '.yml']:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    # Validate JSON/YAML syntax
                    if file_path.suffix.lower() == '.json':
                        json.loads(content)  # Validate JSON
                    return content
            else:
                # Binary read for other files
                with open(file_path, 'rb') as f:
                    return f.read()

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {file_path}: {e}")
            raise ValidationError(f"Invalid JSON format in {file_path}: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {file_path}: {e}")
            raise FileOperationError(f"Encoding error reading {file_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            if default is not None:
                logger.info(f"Returning default content for {file_path}")
                return default
            raise FileOperationError(f"Failed to read file {file_path}: {e}")

    def create_directory_structure(self, structure: Dict[str, Any]) -> bool:
        """
        Create directory structure with proper permissions.

        Args:
            structure: Dictionary representing directory structure

        Returns:
            bool: True if structure was created successfully

        Raises:
            DirectoryError: If directory creation fails
        """
        def create_dirs(data: Dict[str, Any], base_path: Path) -> None:
            for key, value in data.items():
                current_path = base_path / key

                if isinstance(value, dict):
                    # Create directory and recurse
                    try:
                        current_path.mkdir(parents=True, exist_ok=True)
                        logger.debug(f"Created directory: {current_path}")
                        create_dirs(value, current_path)
                    except Exception as e:
                        raise DirectoryError(f"Failed to create directory {current_path}: {e}")
                else:
                    # Create file
                    try:
                        if isinstance(value, str):
                            self.safe_write_file(current_path, value)
                        elif isinstance(value, bytes):
                            self.safe_write_file(current_path, value, mode='wb')
                        else:
                            # Create empty file
                            current_path.touch()
                        logger.debug(f"Created file: {current_path}")
                    except Exception as e:
                        raise FileOperationError(f"Failed to create file {current_path}: {e}")

        try:
            create_dirs(structure, self.base_path)
            logger.info(f"Successfully created directory structure under {self.base_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create directory structure: {e}")
            raise

    def move_files_safely(self, file_mappings: List[Tuple[str, str]]) -> bool:
        """
        Move multiple files with rollback capabilities.

        Args:
            file_mappings: List of (source, destination) path tuples

        Returns:
            bool: True if all moves were successful

        Raises:
            FileOperationError: If any move operation fails
        """
        # Validate all source files exist
        for src, dst in file_mappings:
            src_path = Path(src)
            if not src_path.exists():
                raise FileOperationError(f"Source file does not exist: {src_path}")

        # Create backups and perform moves
        backups = []
        moved_files = []

        try:
            for src, dst in file_mappings:
                src_path = Path(src)
                dst_path = Path(dst)

                # Create backup of destination if it exists
                if dst_path.exists():
                    backup_path = dst_path.with_suffix(dst_path.suffix + self._backup_suffix)
                    if backup_path.exists():
                        backup_path.unlink()
                    shutil.copy2(dst_path, backup_path)
                    backups.append((dst_path, backup_path))

                # Ensure destination directory exists
                dst_path.parent.mkdir(parents=True, exist_ok=True)

                # Move file
                shutil.move(str(src_path), str(dst_path))
                moved_files.append((src_path, dst_path))

                logger.debug(f"Moved file: {src_path} -> {dst_path}")

            logger.info(f"Successfully moved {len(file_mappings)} files")
            return True

        except Exception as e:
            # Rollback all operations
            logger.error(f"Move operation failed, rolling back: {e}")

            # Restore moved files
            for src_path, dst_path in reversed(moved_files):
                try:
                    if dst_path.exists():
                        dst_path.unlink()
                    if src_path.exists():
                        shutil.move(str(dst_path), str(src_path))
                except Exception as rollback_error:
                    logger.error(f"Failed to rollback move {src_path} -> {dst_path}: {rollback_error}")

            # Restore backups
            for dst_path, backup_path in reversed(backups):
                try:
                    if backup_path.exists():
                        shutil.move(str(backup_path), str(dst_path))
                except Exception as restore_error:
                    logger.error(f"Failed to restore backup {backup_path} -> {dst_path}: {restore_error}")

            raise FileOperationError(f"Failed to move files: {e}")

    def validate_file_structure(self, expected_structure: Dict[str, Any]) -> List[str]:
        """
        Validate that the current file structure matches expected structure.

        Args:
            expected_structure: Expected directory/file structure

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        def validate_structure(expected: Dict[str, Any], current_path: Path) -> None:
            for name, expected_item in expected.items():
                item_path = current_path / name

                if isinstance(expected_item, dict):
                    # Expected directory
                    if not item_path.exists():
                        errors.append(f"Missing expected directory: {item_path}")
                    elif not item_path.is_dir():
                        errors.append(f"Expected directory but found file: {item_path}")
                    else:
                        validate_structure(expected_item, item_path)
                else:
                    # Expected file
                    if not item_path.exists():
                        errors.append(f"Missing expected file: {item_path}")
                    elif item_path.is_dir():
                        errors.append(f"Expected file but found directory: {item_path}")

        try:
            validate_structure(expected_structure, self.base_path)
            logger.info(f"File structure validation completed with {len(errors)} errors")
            return errors
        except Exception as e:
            logger.error(f"Error during structure validation: {e}")
            errors.append(f"Validation error: {e}")
            return errors

    def _validate_file_integrity(self, file_path: Path, expected_content: Union[str, bytes]) -> bool:
        """
        Validate that file content matches expected content.

        Args:
            file_path: Path to file to validate
            expected_content: Expected content

        Returns:
            bool: True if content matches
        """
        try:
            if isinstance(expected_content, str):
                with open(file_path, 'r', encoding='utf-8') as f:
                    actual_content = f.read()
            else:
                with open(file_path, 'rb') as f:
                    actual_content = f.read()

            return actual_content == expected_content
        except Exception as e:
            logger.error(f"Failed to validate file integrity for {file_path}: {e}")
            return False

    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get comprehensive information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing file information
        """
        file_path = Path(file_path)

        try:
            stat = file_path.stat()

            info = {
                'path': str(file_path),
                'name': file_path.name,
                'size': stat.st_size,
                'modified_time': stat.st_mtime,
                'accessed_time': stat.st_atime,
                'created_time': stat.st_ctime,
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir(),
                'exists': file_path.exists(),
                'extension': file_path.suffix,
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK),
                'executable': os.access(file_path, os.X_OK)
            }

            # Calculate checksum for files
            if file_path.is_file():
                try:
                    if file_path.suffix.lower() in ['.json', '.yaml', '.yml', '.txt']:
                        # Text file checksum
                        content = self.safe_read_file(file_path, default='')
                        if content:
                            info['checksum'] = hashlib.md5(content.encode('utf-8')).hexdigest()
                    else:
                        # Binary file checksum
                        with open(file_path, 'rb') as f:
                            info['checksum'] = hashlib.md5(f.read()).hexdigest()
                except Exception as e:
                    logger.warning(f"Failed to calculate checksum for {file_path}: {e}")

            return info

        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {
                'path': str(file_path),
                'error': str(e),
                'exists': False
            }

    @contextmanager
    def atomic_write_context(self, file_path: Union[str, Path]):
        """
        Context manager for atomic write operations.

        Usage:
            with file_manager.atomic_write_context('file.txt') as temp_file:
                temp_file.write('content')
                # File is atomically moved when context exits
        """
        file_path = Path(file_path)
        temp_path = file_path.with_suffix(file_path.suffix + self._temp_suffix)

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Open temporary file for writing
            with open(temp_path, 'w', encoding='utf-8') as f:
                yield f

            # Validate and move to final location
            if not temp_path.exists():
                raise FileOperationError("Temporary file was not created")

            temp_path.replace(file_path)
            logger.debug(f"Atomic write completed: {file_path}")

        except Exception as e:
            # Clean up temporary file
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            raise FileOperationError(f"Atomic write failed for {file_path}: {e}")

        finally:
            # Ensure cleanup
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass