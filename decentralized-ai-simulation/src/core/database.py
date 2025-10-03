import sqlite3
import json
from typing import List, Dict, Any, Optional, Generator, ContextManager
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from logging_setup import get_logger
from config_loader import get_config
import time
from functools import lru_cache

logger = get_logger(__name__)


@dataclass
class DatabaseConfig:
    """Configuration settings for database connections."""
    path: str = 'ledger.db'
    timeout: int = 30
    check_same_thread: bool = False
    journal_mode: str = 'WAL'
    synchronous_mode: str = 'NORMAL'
    cache_size: int = 10000
    max_connections: int = 10


@dataclass
class ConnectionPool:
    """Enhanced connection pool with better resource management."""
    config: DatabaseConfig
    _connections: Dict[int, sqlite3.Connection] = None
    _lock: threading.Lock = None

    def __post_init__(self) -> None:
        """Initialize the connection pool."""
        if self._connections is None:
            self._connections = {}
        if self._lock is None:
            self._lock = threading.Lock()

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with enhanced configuration."""
        thread_id = threading.get_ident()

        with self._lock:
            if thread_id not in self._connections:
                if len(self._connections) >= self.config.max_connections:
                    # Remove oldest connection if pool is full
                    oldest_thread = min(self._connections.keys())
                    self._close_connection(oldest_thread)

                # Create new connection with optimized settings
                connection = sqlite3.connect(
                    self.config.path,
                    timeout=self.config.timeout,
                    check_same_thread=self.config.check_same_thread
                )

                # Apply performance optimizations
                connection.execute(f'PRAGMA journal_mode={self.config.journal_mode}')
                connection.execute(f'PRAGMA synchronous={self.config.synchronous_mode}')
                connection.execute(f'PRAGMA cache_size={self.config.cache_size}')
                connection.execute('PRAGMA foreign_keys=ON')
                connection.execute('PRAGMA temp_store=memory')

                self._connections[thread_id] = connection
                logger.debug(f"Created new database connection for thread {thread_id}")

        return self._connections[thread_id]

    def _close_connection(self, thread_id: int) -> None:
        """Close connection for specific thread."""
        if thread_id in self._connections:
            try:
                self._connections[thread_id].close()
            except Exception as e:
                logger.warning(f"Error closing connection for thread {thread_id}: {e}")
            finally:
                del self._connections[thread_id]

    def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            for thread_id in list(self._connections.keys()):
                self._close_connection(thread_id)
            logger.info("Closed all database connections")


# Global connection pool instance
_connection_pool: Optional[ConnectionPool] = None


def get_connection_pool() -> ConnectionPool:
    """Get or create global connection pool."""
    global _connection_pool
    if _connection_pool is None:
        config = DatabaseConfig(
            path=get_config('database.path', 'ledger.db'),
            timeout=get_config('database.timeout', 30),
            check_same_thread=get_config('database.check_same_thread', False)
        )
        _connection_pool = ConnectionPool(config)
    return _connection_pool


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with automatic cleanup."""
    pool = get_connection_pool()
    connection = None
    try:
        connection = pool.get_connection()
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        # Connection is managed by pool, no need to close here
        pass


def close_all_connections() -> None:
    """Close all database connections."""
    pool = get_connection_pool()
    pool.close_all_connections()


class DatabaseLedger:
    """
    SQLite-based ledger for storing immutable records of agent states and anomalies.

    Provides thread-safe operations for append, read, and query new entries.
    Uses enhanced connection pooling and context managers for better resource management.
    """

    def __init__(self, db_file: Optional[str] = None) -> None:
        """
        Initialize the ledger with SQLite database and enhanced configuration.

        Args:
            db_file: Path to the SQLite database file. If None, uses config.
        """
        self.db_file: str = db_file or get_config('database.path', 'ledger.db')
        self.lock: threading.Lock = threading.Lock()
        self._connection_pool = get_connection_pool()
        self._cache_ttl: int = 300  # 5 minutes cache TTL
        self._last_cache_update: float = 0

        logger.info(f"Initializing enhanced database ledger at {self.db_file}")
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema with enhanced configuration."""
        with self.lock:
            try:
                with get_db_connection() as conn:
                    # Create ledger table with improved schema
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS ledger (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp REAL NOT NULL,
                            node_id TEXT NOT NULL,
                            features TEXT NOT NULL,
                            confidence REAL NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(timestamp, node_id)
                        )
                    """)

                    # Create indexes for better query performance
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_ledger_timestamp
                        ON ledger(timestamp)
                    """)
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_ledger_node_id
                        ON ledger(node_id)
                    """)
                    conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_ledger_confidence
                        ON ledger(confidence)
                    """)

                    conn.commit()
                    logger.info("Enhanced database schema initialized successfully")

            except sqlite3.Error as e:
                logger.error(f"Failed to initialize database: {e}")
                raise

    def append_entry(self, entry: Dict[str, Any]) -> int:
        """
        Append a new entry to the ledger with enhanced validation and error handling.

        Args:
            entry: The entry to append. Must contain keys 'timestamp', 'node_id',
                   'features', and 'confidence'.

        Returns:
            The ID of the newly inserted entry.

        Raises:
            ValueError: If required keys are missing or data is invalid.
        """
        self._validate_entry(entry)

        with self.lock:
            try:
                with get_db_connection() as conn:
                    cursor = conn.execute(
                        """
                        INSERT OR REPLACE INTO ledger (timestamp, node_id, features, confidence)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            entry['timestamp'],
                            entry['node_id'],
                            json.dumps(entry['features'], separators=(',', ':')),
                            entry['confidence']
                        )
                    )
                    conn.commit()
                    entry_id = cursor.lastrowid

                    logger.debug(f"Appended entry with ID {entry_id}")
                    self._invalidate_cache()

                    return entry_id

            except sqlite3.IntegrityError as e:
                logger.error(f"Duplicate entry or constraint violation: {e}")
                raise ValueError(f"Entry violates database constraints: {e}")
            except sqlite3.Error as e:
                logger.error(f"Failed to append entry: {e}")
                # Retry logic for transient errors
                if self._is_transient_error(e):
                    logger.warning("Transient database error, retrying...")
                    time.sleep(0.1)
                    return self.append_entry(entry)
                raise

    def _validate_entry(self, entry: Dict[str, Any]) -> None:
        """Validate entry data before insertion."""
        required_keys = {'timestamp', 'node_id', 'features', 'confidence'}

        if not isinstance(entry, dict):
            raise ValueError("Entry must be a dictionary")

        if not all(key in entry for key in required_keys):
            missing_keys = required_keys - set(entry.keys())
            raise ValueError(f"Entry missing required keys: {missing_keys}")

        # Validate data types and ranges
        if not isinstance(entry['timestamp'], (int, float)):
            raise ValueError("Timestamp must be a number")

        if not isinstance(entry['node_id'], str) or not entry['node_id'].strip():
            raise ValueError("Node ID must be a non-empty string")

        if not isinstance(entry['features'], (list, dict)):
            raise ValueError("Features must be a list or dictionary")

        if not isinstance(entry['confidence'], (int, float)):
            raise ValueError("Confidence must be a number")
        if not 0 <= entry['confidence'] <= 1:
            raise ValueError("Confidence must be between 0 and 1")

    def _is_transient_error(self, error: sqlite3.Error) -> bool:
        """Check if error is transient and worth retrying."""
        error_msg = str(error).lower()
        return any(term in error_msg for term in ['locked', 'busy', 'timeout'])

    def read_ledger(self) -> List[Dict[str, Any]]:
        """
        Read all entries from the ledger with enhanced caching and performance.

        Returns:
            List of all ledger entries sorted by ID.
        """
        # Use cached result if still valid
        if self._is_cache_valid():
            logger.debug("Returning cached ledger entries")
            return self._cached_ledger

        with self.lock:
            try:
                with get_db_connection() as conn:
                    # Use optimized query with indexes
                    cursor = conn.execute("""
                        SELECT id, timestamp, node_id, features, confidence
                        FROM ledger
                        ORDER BY id ASC
                    """)

                    rows = cursor.fetchall()
                    entries = []

                    for row in rows:
                        try:
                            entry = {
                                'id': int(row[0]),
                                'timestamp': float(row[1]),
                                'node_id': str(row[2]),
                                'features': json.loads(row[3]),
                                'confidence': float(row[4])
                            }
                            entries.append(entry)
                        except (json.JSONDecodeError, ValueError, TypeError) as e:
                            logger.warning(f"Skipping invalid entry {row[0]}: {e}")
                            continue

                    logger.debug(f"Read {len(entries)} valid entries from ledger")

                    # Update cache with timestamp
                    self._cached_ledger = entries
                    self._last_cache_update = time.time()

                    return entries

            except sqlite3.Error as e:
                logger.error(f"Failed to read ledger: {e}")
                raise

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid based on TTL."""
        return (
            hasattr(self, '_cached_ledger') and
            (time.time() - self._last_cache_update) < self._cache_ttl
        )

    def get_new_entries(self, last_seen_id: int) -> List[Dict[str, Any]]:
        """
        Get entries newer than the last seen ID with enhanced performance and validation.

        Args:
            last_seen_id: The last seen entry ID.

        Returns:
            List of new entries with IDs greater than last_seen_id.
        """
        if not isinstance(last_seen_id, int) or last_seen_id < 0:
            raise ValueError("last_seen_id must be a non-negative integer")

        with self.lock:
            try:
                with get_db_connection() as conn:
                    # Use parameterized query for security and performance
                    cursor = conn.execute(
                        """
                        SELECT id, timestamp, node_id, features, confidence
                        FROM ledger
                        WHERE id > ?
                        ORDER BY id ASC
                        """,
                        (last_seen_id,)
                    )

                    rows = cursor.fetchall()
                    entries = []

                    for row in rows:
                        try:
                            entry = {
                                'id': int(row[0]),
                                'timestamp': float(row[1]),
                                'node_id': str(row[2]),
                                'features': json.loads(row[3]),
                                'confidence': float(row[4])
                            }
                            entries.append(entry)
                        except (json.JSONDecodeError, ValueError, TypeError) as e:
                            logger.warning(f"Skipping invalid new entry {row[0]}: {e}")
                            continue

                    logger.debug(f"Retrieved {len(entries)} new entries since ID {last_seen_id}")
                    return entries

            except sqlite3.Error as e:
                logger.error(f"Failed to get new entries: {e}")
                raise

    def _invalidate_cache(self) -> None:
        """Invalidate cached data after write operations."""
        self._last_cache_update = 0
        if hasattr(self, '_cached_ledger'):
            self._cached_ledger = None
        if hasattr(self, '_entry_cache'):
            self._entry_cache.clear()

    def get_entry_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific entry by its ID with enhanced caching and validation.

        Args:
            entry_id: The entry ID to retrieve.

        Returns:
            The entry if found, None otherwise.
        """
        if not isinstance(entry_id, int) or entry_id <= 0:
            raise ValueError("entry_id must be a positive integer")

        # Check cache first
        cache_key = f"entry_{entry_id}"
        if hasattr(self, '_entry_cache') and cache_key in self._entry_cache:
            logger.debug(f"Returning cached entry {entry_id}")
            return self._entry_cache[cache_key]

        with self.lock:
            try:
                with get_db_connection() as conn:
                    cursor = conn.execute(
                        """
                        SELECT id, timestamp, node_id, features, confidence
                        FROM ledger
                        WHERE id = ?
                        """,
                        (entry_id,)
                    )
                    row = cursor.fetchone()

                    if row:
                        try:
                            entry = {
                                'id': int(row[0]),
                                'timestamp': float(row[1]),
                                'node_id': str(row[2]),
                                'features': json.loads(row[3]),
                                'confidence': float(row[4])
                            }

                            logger.debug(f"Retrieved entry with ID {entry_id}")

                            # Cache the entry
                            if not hasattr(self, '_entry_cache'):
                                self._entry_cache = {}
                            self._entry_cache[cache_key] = entry

                            return entry

                        except (json.JSONDecodeError, ValueError, TypeError) as e:
                            logger.warning(f"Invalid entry data for ID {entry_id}: {e}")
                            return None

                    logger.debug(f"Entry with ID {entry_id} not found")
                    return None

            except sqlite3.Error as e:
                logger.error(f"Failed to get entry by ID {entry_id}: {e}")
                raise

    @lru_cache(maxsize=32)
    def get_entries_by_node(self, node_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get entries for a specific node with optional limit and caching.

        Args:
            node_id: The node ID to filter by.
            limit: Maximum number of entries to return.

        Returns:
            List of entries for the specified node.
        """
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError("node_id must be a non-empty string")

        # Create cache key
        cache_key = f"{node_id}_{limit}"
        if cache_key in self._entry_cache:
            logger.debug(f"Returning cached entries for node {node_id}")
            return self._entry_cache[cache_key]

        with self.lock:
            try:
                with get_db_connection() as conn:
                    query = """
                        SELECT id, timestamp, node_id, features, confidence
                        FROM ledger
                        WHERE node_id = ?
                        ORDER BY timestamp DESC
                    """
                    params = (node_id,)

                    if limit is not None:
                        if not isinstance(limit, int) or limit <= 0:
                            raise ValueError("limit must be a positive integer")
                        query += " LIMIT ?"
                        params = (node_id, limit)

                    cursor = conn.execute(query, params)
                    rows = cursor.fetchall()
                    entries = []

                    for row in rows:
                        try:
                            entry = {
                                'id': int(row[0]),
                                'timestamp': float(row[1]),
                                'node_id': str(row[2]),
                                'features': json.loads(row[3]),
                                'confidence': float(row[4])
                            }
                            entries.append(entry)
                        except (json.JSONDecodeError, ValueError, TypeError) as e:
                            logger.warning(f"Skipping invalid entry {row[0]}: {e}")
                            continue

                    # Cache the result
                    self._entry_cache[cache_key] = entries
                    logger.debug(f"Retrieved and cached {len(entries)} entries for node {node_id}")
                    return entries

            except sqlite3.Error as e:
                logger.error(f"Failed to get entries for node {node_id}: {e}")
                raise

    def cleanup_old_entries(self, max_age_seconds: int) -> int:
        """
        Clean up old entries based on age.

        Args:
            max_age_seconds: Maximum age in seconds for entries to keep.

        Returns:
            Number of entries deleted.
        """
        if not isinstance(max_age_seconds, int) or max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be a positive integer")

        with self.lock:
            try:
                with get_db_connection() as conn:
                    cursor = conn.execute(
                        "DELETE FROM ledger WHERE timestamp < ?",
                        (time.time() - max_age_seconds,)
                    )
                    deleted_count = cursor.rowcount
                    conn.commit()

                    logger.info(f"Cleaned up {deleted_count} old entries")
                    self._invalidate_cache()

                    return deleted_count

            except sqlite3.Error as e:
                logger.error(f"Failed to cleanup old entries: {e}")
                raise