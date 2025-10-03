import sqlite3
import json
from typing import List, Dict, Any, Optional
import threading
from src.utils.logging_setup import get_logger
from src.config.config_loader import get_config
import time

logger = get_logger(__name__)

# Connection pool using threading.local for thread-safe connections
_thread_local = threading.local()

def get_db_connection(db_file: str) -> sqlite3.Connection:
    """Get or create a SQLite connection for the current thread."""
    if not hasattr(_thread_local, 'connection'):
        # Configure SQLite for better performance
        _thread_local.connection = sqlite3.connect(
            db_file,
            timeout=get_config('database.timeout', 30),
            check_same_thread=get_config('database.check_same_thread', False)
        )
        # Enable performance optimizations
        _thread_local.connection.execute('PRAGMA journal_mode=WAL')
        _thread_local.connection.execute('PRAGMA synchronous=NORMAL')
        _thread_local.connection.execute('PRAGMA cache_size=10000')
    return _thread_local.connection

def close_db_connection() -> None:
    """Close the database connection for the current thread."""
    if hasattr(_thread_local, 'connection'):
        _thread_local.connection.close()
        delattr(_thread_local, 'connection')


class DatabaseLedger:
    """
    SQLite-based ledger for storing immutable records of agent states and anomalies.
    
    Provides thread-safe operations for append, read, and query new entries.
    Replaces JSON file with SQLite for better concurrency and immutability.
    Uses connection pooling and efficient queries for performance.
    """

    def __init__(self, db_file: Optional[str] = None) -> None:
        """
        Initialize the ledger with SQLite database.

        Args:
            db_file: Path to the SQLite database file. If None, uses config.
        """
        self.db_file: str = db_file or get_config('database.path', 'ledger.db')
        self.lock: threading.Lock = threading.Lock()
        logger.info(f"Initializing database ledger at {self.db_file}")
        self._init_db()

    def _init_db(self) -> None:
        """
        Initialize the database schema if it doesn't exist.
        Creates the ledger table with appropriate columns.
        """
        with self.lock:  # Ensure thread-safe initialization
            try:
                conn = get_db_connection(self.db_file)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ledger (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        node_id TEXT NOT NULL,
                       features TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                logger.info("Database schema initialized successfully")
            except sqlite3.Error as e:
                logger.error(f"Failed to initialize database: {e}")
                raise

    def append_entry(self, entry: Dict[str, Any]) -> int:
        """
        Append a new entry to the ledger and return the assigned ID.

        Args:
            entry: The entry to append. Must contain keys 'timestamp', 'node_id',
                   'features', and 'confidence'.

        Returns:
            The ID of the newly inserted entry.

        Raises:
            ValueError: If required keys are missing from the entry.
        """
        required_keys = {'timestamp', 'node_id', 'features', 'confidence'}
        if not all(key in entry for key in required_keys):
            raise ValueError(f"Entry must contain keys: {required_keys}")

        with self.lock:
            try:
                conn = get_db_connection(self.db_file)
                cursor = conn.execute(
                    """
                    INSERT INTO ledger (timestamp, node_id, features, confidence)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        entry['timestamp'],
                        entry['node_id'],
                        json.dumps(entry['features']),
                        entry['confidence']
                    )
                )
                conn.commit()
                entry_id = cursor.lastrowid
                logger.debug(f"Appended entry with ID {entry_id}")
                # Invalidate cache after write
                self._invalidate_cache()
                return entry_id
            except sqlite3.Error as e:
                logger.error(f"Failed to append entry: {e}")
                # Retry logic for transient errors
                if 'locked' in str(e).lower():
                    logger.warning("Database locked, retrying...")
                    time.sleep(0.1)
                    return self.append_entry(entry)
                raise

    def read_ledger(self) -> List[Dict[str, Any]]:
        """
        Read all entries from the ledger in chronological order.

        Returns:
            List of all ledger entries sorted by ID.
        """
        # Use cached result if available
        if hasattr(self, '_cached_ledger'):
            logger.debug("Returning cached ledger entries")
            return self._cached_ledger
        
        with self.lock:
            try:
                conn = get_db_connection(self.db_file)
                cursor = conn.execute(
                    "SELECT id, timestamp, node_id, features, confidence FROM ledger ORDER BY id"
                )
                rows = cursor.fetchall()
                entries = []
                for row in rows:
                    entry = {
                        'id': row[0],
                        'timestamp': row[1],
                        'node_id': row[2],
                        'features': json.loads(row[3]),
                        'confidence': row[4]
                    }
                    entries.append(entry)
                logger.debug(f"Read {len(entries)} entries from ledger")
                # Cache the result
                self._cached_ledger = entries
                return entries
            except sqlite3.Error as e:
                logger.error(f"Failed to read ledger: {e}")
                raise

    def get_new_entries(self, last_seen_id: int) -> List[Dict[str, Any]]:
        """
        Get entries newer than the last seen ID using efficient SQL query.

        Args:
            last_seen_id: The last seen entry ID.

        Returns:
            List of new entries with IDs greater than last_seen_id.
        """
        with self.lock:
            try:
                conn = get_db_connection(self.db_file)
                cursor = conn.execute(
                    "SELECT id, timestamp, node_id, features, confidence FROM ledger WHERE id > ? ORDER BY id",
                    (last_seen_id,)
                )
                rows = cursor.fetchall()
                entries = []
                for row in rows:
                    entry = {
                        'id': row[0],
                        'timestamp': row[1],
                        'node_id': row[2],
                        'features': json.loads(row[3]),
                        'confidence': row[4]
                    }
                    entries.append(entry)
                logger.debug(f"Retrieved {len(entries)} new entries since ID {last_seen_id}")
                return entries
            except sqlite3.Error as e:
                logger.error(f"Failed to get new entries: {e}")
                raise

    def _invalidate_cache(self) -> None:
        """Invalidate cached data after write operations."""
        if hasattr(self, '_cached_ledger'):
            delattr(self, '_cached_ledger')
        if hasattr(self, '_entry_cache'):
            self._entry_cache.clear()

    def get_entry_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific entry by its ID.

        Args:
            entry_id: The entry ID to retrieve.

        Returns:
            The entry if found, None otherwise.
        """
        # Cache frequently accessed entries
        cache_key = f"entry_{entry_id}"
        if hasattr(self, '_entry_cache') and cache_key in self._entry_cache:
            logger.debug(f"Returning cached entry {entry_id}")
            return self._entry_cache[cache_key]
        
        with self.lock:
            try:
                conn = get_db_connection(self.db_file)
                cursor = conn.execute(
                    "SELECT id, timestamp, node_id, features, confidence FROM ledger WHERE id = ?",
                    (entry_id,)
                )
                row = cursor.fetchone()
                if row:
                    entry = {
                        'id': row[0],
                        'timestamp': row[1],
                        'node_id': row[2],
                        'features': json.loads(row[3]),
                        'confidence': row[4]
                    }
                    logger.debug(f"Retrieved entry with ID {entry_id}")
                    # Cache the entry
                    if not hasattr(self, '_entry_cache'):
                        self._entry_cache = {}
                    self._entry_cache[cache_key] = entry
                    return entry
                logger.debug(f"Entry with ID {entry_id} not found")
                return None
            except sqlite3.Error as e:
                logger.error(f"Failed to get entry by ID {entry_id}: {e}")
                raise