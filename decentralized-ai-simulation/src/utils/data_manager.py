"""
Data Management Utilities for Decentralized AI Simulation

This module provides comprehensive data management capabilities including
JSON/YAML storage, database file management, blacklist organization, and
data validation with integrity checks.
"""

import json
import yaml
import sqlite3
import hashlib
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from dataclasses import dataclass, asdict
import logging
import time
from contextlib import contextmanager
import threading
import os

try:
    from src.utils.logging_setup import get_logger
except ImportError:
    try:
        from utils.logging_setup import get_logger
    except ImportError:
        import logging
        get_logger = lambda name: logging.getLogger(name)

try:
    from src.utils.exceptions import (
        FileOperationError,
        ValidationError,
        ConfigurationError,
        SecurityError
    )
except ImportError:
    from exceptions import (
        FileOperationError,
        ValidationError,
        ConfigurationError,
        SecurityError
    )

logger = get_logger(__name__)


@dataclass
class DataValidationRule:
    """Data validation rule definition."""
    field: str
    rule_type: str  # 'required', 'type', 'range', 'pattern', 'custom'
    value: Any = None
    message: str = ""


@dataclass
class BlacklistEntry:
    """Blacklist entry structure."""
    entity_id: str
    reason: str
    timestamp: float
    severity: str = 'medium'  # low, medium, high, critical
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DataManager:
    """
    Comprehensive data management utilities for the decentralized AI simulation.

    This class provides:
    - JSON/YAML data storage and retrieval
    - Database file management with connection pooling
    - Blacklist data organization and management
    - Data validation and integrity checks
    - Backup and recovery capabilities
    """

    def __init__(self, base_data_path: Optional[str] = None):
        """
        Initialize DataManager.

        Args:
            base_data_path: Base path for data files
        """
        self.base_data_path = Path(base_data_path) if base_data_path else Path("data")
        self.base_data_path.mkdir(parents=True, exist_ok=True)

        # Database connections cache
        self._db_connections: Dict[str, sqlite3.Connection] = {}
        self._db_locks: Dict[str, threading.Lock] = {}

        # Data directories
        self.databases_path = self.base_data_path / "databases"
        self.blacklists_path = self.base_data_path / "blacklists"
        self.documents_path = self.base_data_path / "documents"

        # Create directory structure
        for path in [self.databases_path, self.blacklists_path, self.documents_path]:
            path.mkdir(parents=True, exist_ok=True)

        logger.info(f"DataManager initialized with base path: {self.base_data_path}")

    def store_json_data(self, data: Any, file_path: Union[str, Path], indent: int = 2) -> bool:
        """
        Store data as JSON with validation and backup.

        Args:
            data: Data to store (must be JSON serializable)
            file_path: Path to store the file
            indent: JSON indentation

        Returns:
            bool: True if storage was successful

        Raises:
            FileOperationError: If storage fails
            ValidationError: If data is not JSON serializable
        """
        file_path = Path(file_path)

        try:
            # Validate data is JSON serializable
            json.dumps(data)  # Test serialization

            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Create backup if file exists
            if file_path.exists():
                backup_path = file_path.with_suffix('.backup')
                if backup_path.exists():
                    backup_path.unlink()
                file_path.rename(backup_path)

            # Write new data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)

            # Validate written data
            with open(file_path, 'r', encoding='utf-8') as f:
                written_data = json.load(f)

            # Calculate and store checksum for integrity
            checksum = self._calculate_data_checksum(written_data)
            checksum_file = file_path.with_suffix('.checksum')
            with open(checksum_file, 'w', encoding='utf-8') as f:
                f.write(checksum)

            logger.info(f"Successfully stored JSON data to {file_path}")
            return True

        except json.JSONDecodeError as e:
            raise ValidationError(f"Data is not valid JSON: {e}")
        except Exception as e:
            # Restore backup if available
            backup_path = file_path.with_suffix('.backup')
            if backup_path.exists():
                try:
                    backup_path.rename(file_path)
                except Exception:
                    pass  # Ignore restore errors

            raise FileOperationError(f"Failed to store JSON data to {file_path}: {e}")

    def load_json_data(self, file_path: Union[str, Path], default: Any = None) -> Any:
        """
        Load JSON data with integrity validation.

        Args:
            file_path: Path to load data from
            default: Default value if file doesn't exist or is invalid

        Returns:
            Loaded data or default value

        Raises:
            FileOperationError: If loading fails
            ValidationError: If data integrity check fails
        """
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                logger.warning(f"JSON file does not exist: {file_path}")
                return default

            # Load data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate integrity if checksum exists
            checksum_file = file_path.with_suffix('.checksum')
            if checksum_file.exists():
                expected_checksum = checksum_file.read_text(encoding='utf-8').strip()
                actual_checksum = self._calculate_data_checksum(data)

                if expected_checksum != actual_checksum:
                    raise ValidationError(
                        f"Data integrity check failed for {file_path}. "
                        f"Expected checksum: {expected_checksum}, got: {actual_checksum}"
                    )

            logger.debug(f"Successfully loaded JSON data from {file_path}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {file_path}: {e}")
            if default is not None:
                logger.info(f"Returning default value for {file_path}")
                return default
            raise ValidationError(f"Invalid JSON format in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to load JSON data from {file_path}: {e}")
            if default is not None:
                logger.info(f"Returning default value for {file_path}")
                return default
            raise FileOperationError(f"Failed to load JSON data from {file_path}: {e}")

    def store_yaml_data(self, data: Any, file_path: Union[str, Path]) -> bool:
        """
        Store data as YAML with validation.

        Args:
            data: Data to store (must be YAML serializable)
            file_path: Path to store the file

        Returns:
            bool: True if storage was successful

        Raises:
            FileOperationError: If storage fails
            ValidationError: If data is not YAML serializable
        """
        file_path = Path(file_path)

        try:
            # Validate data is YAML serializable
            yaml.dump(data)  # Test serialization

            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write data
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"Successfully stored YAML data to {file_path}")
            return True

        except yaml.YAMLError as e:
            raise ValidationError(f"Data is not valid YAML: {e}")
        except Exception as e:
            raise FileOperationError(f"Failed to store YAML data to {file_path}: {e}")

    def load_yaml_data(self, file_path: Union[str, Path], default: Any = None) -> Any:
        """
        Load YAML data with error handling.

        Args:
            file_path: Path to load data from
            default: Default value if file doesn't exist or is invalid

        Returns:
            Loaded data or default value
        """
        file_path = Path(file_path)

        try:
            if not file_path.exists():
                logger.warning(f"YAML file does not exist: {file_path}")
                return default

            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            logger.debug(f"Successfully loaded YAML data from {file_path}")
            return data

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML format in {file_path}: {e}")
            if default is not None:
                logger.info(f"Returning default value for {file_path}")
                return default
            raise ValidationError(f"Invalid YAML format in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to load YAML data from {file_path}: {e}")
            if default is not None:
                logger.info(f"Returning default value for {file_path}")
                return default
            raise FileOperationError(f"Failed to load YAML data from {file_path}: {e}")

    def validate_data(self, data: Any, rules: List[DataValidationRule]) -> List[str]:
        """
        Validate data against a set of rules.

        Args:
            data: Data to validate
            rules: List of validation rules

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        def get_nested_value(data_dict: Dict[str, Any], field_path: str) -> Any:
            """Get nested value from dictionary."""
            keys = field_path.split('.')
            value = data_dict
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value

        def set_nested_value(data_dict: Dict[str, Any], field_path: str, new_value: Any) -> Dict[str, Any]:
            """Set nested value in dictionary."""
            keys = field_path.split('.')
            result = data_dict.copy()

            current = result
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            current[keys[-1]] = new_value
            return result

        for rule in rules:
            try:
                # Get field value
                if isinstance(data, dict):
                    field_value = get_nested_value(data, rule.field)
                else:
                    # For non-dict data, only validate if field is empty string
                    field_value = data if rule.field == '' else None

                # Apply validation rule
                if rule.rule_type == 'required':
                    if field_value is None or field_value == '':
                        errors.append(rule.message or f"Field '{rule.field}' is required")

                elif rule.rule_type == 'type':
                    if field_value is not None:
                        expected_type = rule.value
                        if not isinstance(field_value, expected_type):
                            errors.append(
                                rule.message or
                                f"Field '{rule.field}' must be of type {expected_type.__name__}, got {type(field_value).__name__}"
                            )

                elif rule.rule_type == 'range':
                    if field_value is not None:
                        min_val, max_val = rule.value
                        if not (min_val <= field_value <= max_val):
                            errors.append(
                                rule.message or
                                f"Field '{rule.field}' must be between {min_val} and {max_val}, got {field_value}"
                            )

                elif rule.rule_type == 'pattern':
                    if field_value is not None and isinstance(field_value, str):
                        import re
                        if not re.match(rule.value, field_value):
                            errors.append(
                                rule.message or
                                f"Field '{rule.field}' does not match required pattern '{rule.value}'"
                            )

                elif rule.rule_type == 'custom':
                    if not rule.value(field_value):
                        errors.append(rule.message or f"Custom validation failed for field '{rule.field}'")

            except Exception as e:
                errors.append(f"Validation error for field '{rule.field}': {e}")

        logger.debug(f"Data validation completed with {len(errors)} errors")
        return errors

    def create_database(self, db_name: str, schema: Dict[str, Any]) -> bool:
        """
        Create a new SQLite database with specified schema.

        Args:
            db_name: Name of the database
            schema: Schema definition with table definitions

        Returns:
            bool: True if database was created successfully

        Raises:
            FileOperationError: If database creation fails
        """
        db_path = self.databases_path / f"{db_name}.db"

        try:
            with self._get_db_connection(db_path) as conn:
                cursor = conn.cursor()

                for table_name, table_def in schema.items():
                    if table_def.get('type') == 'table':
                        columns = table_def.get('columns', [])
                        indexes = table_def.get('indexes', [])

                        # Create table
                        column_defs = []
                        for col_name, col_def in columns.items():
                            col_type = col_def.get('type', 'TEXT')
                            constraints = col_def.get('constraints', [])
                            column_defs.append(f"{col_name} {col_type} {' '.join(constraints)}")

                        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
                        cursor.execute(create_table_sql)

                        # Create indexes
                        for index_def in indexes:
                            index_name = index_def.get('name', f"idx_{table_name}_{'_'.join(index_def['columns'])}")
                            index_columns = ', '.join(index_def['columns'])
                            unique = 'UNIQUE' if index_def.get('unique', False) else ''

                            create_index_sql = f"CREATE {unique} INDEX IF NOT EXISTS {index_name} ON {table_name} ({index_columns})"
                            cursor.execute(create_index_sql)

                conn.commit()
                logger.info(f"Successfully created database {db_name} with schema")
                return True

        except Exception as e:
            raise FileOperationError(f"Failed to create database {db_name}: {e}")

    def query_database(self, db_name: str, query: str, parameters: Tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a query on a database and return results as dictionaries.

        Args:
            db_name: Name of the database
            query: SQL query to execute
            parameters: Query parameters

        Returns:
            List of result dictionaries
        """
        db_path = self.databases_path / f"{db_name}.db"

        try:
            with self._get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)

                # Get column names
                columns = [description[0] for description in cursor.description]

                # Convert results to dictionaries
                results = []
                for row in cursor.fetchall():
                    result_dict = dict(zip(columns, row))
                    results.append(result_dict)

                return results

        except Exception as e:
            logger.error(f"Database query failed for {db_name}: {e}")
            raise FileOperationError(f"Database query failed: {e}")

    def add_blacklist_entry(self, entry: BlacklistEntry) -> bool:
        """
        Add an entry to the blacklist.

        Args:
            entry: BlacklistEntry to add

        Returns:
            bool: True if entry was added successfully
        """
        try:
            # Store in JSON file organized by date
            date_str = time.strftime('%Y-%m-%d', time.localtime(entry.timestamp))
            blacklist_file = self.blacklists_path / f"blacklist_{date_str}.json"

            # Load existing entries for the day
            existing_entries = []
            if blacklist_file.exists():
                try:
                    with open(blacklist_file, 'r', encoding='utf-8') as f:
                        existing_entries = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load existing blacklist file {blacklist_file}: {e}")

            # Check for duplicates
            for existing_entry in existing_entries:
                if existing_entry.get('entity_id') == entry.entity_id:
                    logger.info(f"Blacklist entry for {entry.entity_id} already exists")
                    return True

            # Add new entry
            entry_dict = asdict(entry)
            existing_entries.append(entry_dict)

            # Sort by timestamp (newest first)
            existing_entries.sort(key=lambda x: x['timestamp'], reverse=True)

            # Save updated blacklist
            success = self.store_json_data(existing_entries, blacklist_file)
            if success:
                logger.info(f"Added blacklist entry for entity {entry.entity_id}")
            return success

        except Exception as e:
            logger.error(f"Failed to add blacklist entry: {e}")
            raise FileOperationError(f"Failed to add blacklist entry: {e}")

    def get_blacklist_entries(
        self,
        entity_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[BlacklistEntry]:
        """
        Retrieve blacklist entries with optional filtering.

        Args:
            entity_id: Filter by specific entity ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            severity: Filter by severity level

        Returns:
            List of matching BlacklistEntry objects
        """
        try:
            all_entries = []

            # Determine which files to check
            if start_date and end_date:
                # Load specific date range
                start = time.strptime(start_date, '%Y-%m-%d')
                end = time.strptime(end_date, '%Y-%m-%d')

                current = start
                while current <= end:
                    date_str = time.strftime('%Y-%m-%d', current)
                    blacklist_file = self.blacklists_path / f"blacklist_{date_str}.json"

                    if blacklist_file.exists():
                        entries = self.load_json_data(blacklist_file, default=[])
                        all_entries.extend(entries)

                    current = time.localtime(time.mktime(current) + 86400)  # Next day
            else:
                # Load all blacklist files
                for blacklist_file in self.blacklists_path.glob("blacklist_*.json"):
                    entries = self.load_json_data(blacklist_file, default=[])
                    all_entries.extend(entries)

            # Convert to BlacklistEntry objects
            blacklist_entries = []
            for entry_dict in all_entries:
                try:
                    entry = BlacklistEntry(**entry_dict)
                    blacklist_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Failed to parse blacklist entry: {e}")

            # Apply filters
            filtered_entries = blacklist_entries

            if entity_id:
                filtered_entries = [e for e in filtered_entries if e.entity_id == entity_id]

            if severity:
                filtered_entries = [e for e in filtered_entries if e.severity == severity]

            logger.info(f"Retrieved {len(filtered_entries)} blacklist entries")
            return filtered_entries

        except Exception as e:
            logger.error(f"Failed to retrieve blacklist entries: {e}")
            raise FileOperationError(f"Failed to retrieve blacklist entries: {e}")

    def backup_data(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of all data files.

        Args:
            backup_path: Custom backup path (optional)

        Returns:
            Path to the created backup

        Raises:
            FileOperationError: If backup creation fails
        """
        try:
            if backup_path:
                backup_dir = Path(backup_path)
            else:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                backup_dir = self.base_data_path / f"backup_{timestamp}"

            backup_dir.mkdir(parents=True, exist_ok=True)

            # Copy all data directories
            import shutil

            for source_dir in [self.databases_path, self.blacklists_path, self.documents_path]:
                if source_dir.exists():
                    dest_dir = backup_dir / source_dir.name
                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)
                    shutil.copytree(source_dir, dest_dir)

            # Create backup metadata
            metadata = {
                'timestamp': time.time(),
                'backup_type': 'full',
                'source_path': str(self.base_data_path),
                'directories': ['databases', 'blacklists', 'documents']
            }

            metadata_file = backup_dir / "backup_metadata.json"
            self.store_json_data(metadata, metadata_file)

            logger.info(f"Created data backup at {backup_dir}")
            return str(backup_dir)

        except Exception as e:
            raise FileOperationError(f"Failed to create data backup: {e}")

    def _get_db_connection(self, db_path: Union[str, Path]) -> sqlite3.Connection:
        """Get or create database connection with thread safety."""
        db_path = str(db_path)

        if db_path not in self._db_locks:
            self._db_locks[db_path] = threading.Lock()

        with self._db_locks[db_path]:
            if db_path not in self._db_connections:
                try:
                    conn = sqlite3.connect(db_path, check_same_thread=False)
                    conn.row_factory = sqlite3.Row  # Enable dict-like access
                    self._db_connections[db_path] = conn
                    logger.debug(f"Created new database connection for {db_path}")
                except Exception as e:
                    raise FileOperationError(f"Failed to connect to database {db_path}: {e}")

            return self._db_connections[db_path]

    def _calculate_data_checksum(self, data: Any) -> str:
        """Calculate checksum for data integrity validation."""
        try:
            # Convert data to JSON string for consistent hashing
            data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            return hashlib.md5(data_str.encode('utf-8')).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate data checksum: {e}")
            return ""

    @contextmanager
    def database_transaction(self, db_name: str):
        """
        Context manager for database transactions.

        Usage:
            with data_manager.database_transaction('my_db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO table VALUES (?)", (value,))
                # Transaction is automatically committed on success
        """
        db_path = self.databases_path / f"{db_name}.db"

        try:
            conn = self._get_db_connection(db_path)
            conn.execute("BEGIN")

            try:
                yield conn
                conn.commit()
                logger.debug(f"Database transaction committed for {db_name}")
            except Exception:
                conn.rollback()
                logger.debug(f"Database transaction rolled back for {db_name}")
                raise

        except Exception as e:
            raise FileOperationError(f"Database transaction failed for {db_name}: {e}")

    def cleanup_old_backups(self, max_age_days: int = 30) -> int:
        """
        Clean up old backup files.

        Args:
            max_age_days: Maximum age of backups to keep in days

        Returns:
            Number of backups removed
        """
        try:
            removed_count = 0
            cutoff_time = time.time() - (max_age_days * 24 * 3600)

            # Find backup directories
            backup_pattern = "backup_*"
            for item in self.base_data_path.iterdir():
                if item.is_dir() and item.name.startswith("backup_"):
                    try:
                        # Extract timestamp from directory name
                        timestamp_str = item.name.replace("backup_", "")
                        backup_time = time.mktime(time.strptime(timestamp_str, '%Y%m%d_%H%M%S'))

                        if backup_time < cutoff_time:
                            import shutil
                            shutil.rmtree(item)
                            removed_count += 1
                            logger.info(f"Removed old backup: {item.name}")

                    except (ValueError, OSError) as e:
                        logger.warning(f"Failed to process backup directory {item.name}: {e}")

            logger.info(f"Cleaned up {removed_count} old backups")
            return removed_count

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            raise FileOperationError(f"Failed to cleanup old backups: {e}")

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all managed data.

        Returns:
            Summary dictionary with data statistics
        """
        try:
            summary = {
                'base_path': str(self.base_data_path),
                'directories': {},
                'total_size': 0,
                'file_counts': {}
            }

            # Analyze each data directory
            for dir_name, dir_path in [
                ('databases', self.databases_path),
                ('blacklists', self.blacklists_path),
                ('documents', self.documents_path)
            ]:
                if dir_path.exists():
                    files = list(dir_path.glob('*'))
                    total_size = sum(f.stat().st_size for f in files if f.is_file())

                    summary['directories'][dir_name] = {
                        'file_count': len(files),
                        'total_size': total_size,
                        'files': [f.name for f in files[:10]]  # First 10 files
                    }
                    summary['total_size'] += total_size
                    summary['file_counts'][dir_name] = len(files)

            # Get blacklist statistics
            try:
                all_entries = self.get_blacklist_entries()
                summary['blacklist_stats'] = {
                    'total_entries': len(all_entries),
                    'severity_breakdown': {}
                }

                for entry in all_entries:
                    severity = entry.severity
                    summary['blacklist_stats']['severity_breakdown'][severity] = \
                        summary['blacklist_stats']['severity_breakdown'].get(severity, 0) + 1

            except Exception as e:
                logger.warning(f"Failed to get blacklist statistics: {e}")
                summary['blacklist_stats'] = {'error': str(e)}

            return summary

        except Exception as e:
            logger.error(f"Failed to generate data summary: {e}")
            return {'error': str(e)}