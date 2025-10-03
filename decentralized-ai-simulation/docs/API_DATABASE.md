# Database Module API Documentation

## Overview

The `database` module provides a comprehensive, thread-safe database layer for the decentralized AI simulation system. It implements SQLite-based immutable ledger storage with advanced connection pooling, caching, and performance optimizations for high-throughput anomaly signature management.

## Data Classes

### DatabaseConfig

**Description:**
Configuration settings for database connections with comprehensive performance tuning options.

```python
@dataclass
class DatabaseConfig:
    path: str = 'ledger.db'
    timeout: int = 30
    check_same_thread: bool = False
    journal_mode: str = 'WAL'
    synchronous_mode: str = 'NORMAL'
    cache_size: int = 10000
    max_connections: int = 10
```

**Fields:**
- `path` (str): Path to the SQLite database file
- `timeout` (int): Connection timeout in seconds
- `check_same_thread` (bool): SQLite thread safety setting
- `journal_mode` (str): WAL (Write-Ahead Logging) for improved concurrency
- `synchronous_mode` (str): Balance between performance and data safety
- `cache_size` (int): SQLite cache size in kilobytes
- `max_connections` (int): Maximum concurrent connections in pool

**Performance Impact:**
- `journal_mode='WAL'`: Enables concurrent readers during writes
- `synchronous_mode='NORMAL'`: Faster than FULL, safer than OFF
- `cache_size=10000`: 10MB cache for frequently accessed pages

### ConnectionPool

**Description:**
Enhanced connection pool with intelligent resource management and thread safety for high-concurrency scenarios.

```python
@dataclass
class ConnectionPool:
    config: DatabaseConfig
    _connections: Dict[int, sqlite3.Connection] = None
    _lock: threading.Lock = None
```

**Features:**
- Thread-local connection storage
- Automatic connection cleanup on thread termination
- Configurable maximum connection limits
- Performance-optimized SQLite settings

## Global Functions

### `get_connection_pool() -> ConnectionPool`

**Description:**
Get or create the global connection pool with configuration-driven initialization.

**Returns:**
`ConnectionPool` instance configured from application settings

**Configuration Integration:**
```python
database:
  path: "ledger.db"
  timeout: 30
  check_same_thread: false
```

**Example:**
```python
from database import get_connection_pool

# Get global connection pool
pool = get_connection_pool()
print(f"Pool max connections: {pool.config.max_connections}")
```

### `get_db_connection() -> Generator[sqlite3.Connection, None, None]`

**Description:**
Context manager for database connections with automatic cleanup and enhanced error handling.

**Returns:**
Generator yielding SQLite connection with proper resource management

**Features:**
- Automatic rollback on exceptions
- Connection health validation
- Comprehensive error logging
- Resource leak prevention

**Example:**
```python
from database import get_db_connection

# Safe database operations with context manager
try:
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM ledger")
        count = cursor.fetchone()[0]
        print(f"Ledger entries: {count}")
except Exception as e:
    print(f"Database error: {e}")
```

### `close_all_connections() -> None`

**Description:**
Close all database connections in the global pool for clean application shutdown.

**Usage:**
```python
from database import close_all_connections

# Clean shutdown
close_all_connections()
```

## Class: DatabaseLedger

### Constructor

```python
DatabaseLedger(db_file: Optional[str] = None) -> None
```

**Description:**
Initialize the ledger with SQLite database and enhanced configuration for immutable record storage.

**Parameters:**
- `db_file` (Optional[str]): Path to the SQLite database file. Uses configuration if None.

**Initialization Process:**
1. Create thread-safe lock for concurrent access
2. Initialize connection pool integration
3. Set up caching with TTL configuration
4. Create optimized database schema
5. Configure performance indexes

**Example:**
```python
from database import DatabaseLedger

# Create ledger with default configuration
ledger = DatabaseLedger()

# Create ledger with custom path
custom_ledger = DatabaseLedger("custom_ledger.db")
```

### Schema Management

#### `_init_db() -> None`

**Description:**
Initialize the database schema with enhanced configuration and performance optimizations.

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    node_id TEXT NOT NULL,
    features TEXT NOT NULL,
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(timestamp, node_id)
)
```

**Indexes Created:**
- `idx_ledger_timestamp`: For time-based queries
- `idx_ledger_node_id`: For node-specific lookups
- `idx_ledger_confidence`: For confidence-based filtering

**Performance Optimizations:**
- Foreign key constraints enabled
- Temporary storage in memory
- Optimized pragma settings

### Entry Management

#### `append_entry(entry: Dict[str, Any]) -> int`

**Description:**
Append a new entry to the ledger with comprehensive validation and error handling.

**Parameters:**
- `entry` (Dict[str, Any]): Entry to append with required fields

**Required Fields:**
- `timestamp` (float): Unix timestamp
- `node_id` (str): Source node identifier
- `features` (list|dict): Anomaly signature features
- `confidence` (float): Confidence score (0.0-1.0)

**Returns:**
Integer ID of the newly inserted entry

**Raises:**
- `ValueError`: If required keys are missing or data is invalid
- `sqlite3.IntegrityError`: If unique constraint is violated

**Example:**
```python
# Append valid entry
entry = {
    'timestamp': time.time(),
    'node_id': 'Node_1',
    'features': [{'packet_size': 500, 'source_ip': '192.168.1.100'}],
    'confidence': 0.85
}

entry_id = ledger.append_entry(entry)
print(f"Appended entry with ID: {entry_id}")
```

#### `_validate_entry(entry: Dict[str, Any]) -> None`

**Description:**
Comprehensive validation of entry data before insertion with detailed error reporting.

**Validation Checks:**
1. Entry must be a dictionary
2. All required keys must be present
3. Data types must be correct
4. Value ranges must be valid
5. String fields must not be empty

**Raises:**
- `ValueError`: Detailed message for each validation failure

**Example:**
```python
# Validation is called automatically by append_entry
try:
    ledger.append_entry(invalid_entry)
except ValueError as e:
    print(f"Validation error: {e}")
```

### Data Retrieval

#### `read_ledger() -> List[Dict[str, Any]]`

**Description:**
Read all entries from the ledger with enhanced caching and performance optimizations.

**Returns:**
List of all ledger entries sorted by ID in ascending order

**Performance Features:**
- Intelligent caching with 5-minute TTL
- Cache invalidation on write operations
- Optimized query with database indexes
- Memory-efficient result processing

**Example:**
```python
# Read all entries (uses cache if available)
entries = ledger.read_ledger()
print(f"Total entries: {len(entries)}")

for entry in entries[-5:]:  # Show last 5 entries
    print(f"ID {entry['id']}: Node {entry['node_id']}, "
          f"Confidence: {entry['confidence']:.3f}")
```

#### `get_new_entries(last_seen_id: int) -> List[Dict[str, Any]]`

**Description:**
Get entries newer than the specified ID with enhanced performance and validation.

**Parameters:**
- `last_seen_id` (int): The last seen entry ID (must be non-negative)

**Returns:**
List of new entries with IDs greater than `last_seen_id`

**Performance Optimizations:**
- Parameterized queries for security
- Efficient index-based retrieval
- Memory-conscious result handling

**Example:**
```python
# Poll for new entries since last seen ID
last_id = 100
new_entries = ledger.get_new_entries(last_id)
print(f"Found {len(new_entries)} new entries")

for entry in new_entries:
    print(f"New entry {entry['id']}: {entry['node_id']}")
```

#### `get_entry_by_id(entry_id: int) -> Optional[Dict[str, Any]]`

**Description:**
Get a specific entry by its ID with enhanced caching and validation.

**Parameters:**
- `entry_id` (int): The entry ID to retrieve (must be positive)

**Returns:**
Entry dictionary if found, None otherwise

**Performance Features:**
- Individual entry caching for frequently accessed items
- Optimized single-row queries
- Comprehensive error handling for corrupted data

**Example:**
```python
# Retrieve specific entry
entry = ledger.get_entry_by_id(123)
if entry:
    print(f"Entry 123: Node {entry['node_id']}, "
          f"Features: {len(entry['features'])}")
else:
    print("Entry 123 not found")
```

#### `get_entries_by_node(node_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]`

**Description:**
Get entries for a specific node with optional limit and comprehensive caching support.

**Parameters:**
- `node_id` (str): The node ID to filter by (must be non-empty)
- `limit` (Optional[int]): Maximum number of entries to return

**Returns:**
List of entries for the specified node, ordered by timestamp (newest first)

**Performance Features:**
- Decorated with `@lru_cache` for automatic caching
- Configurable result limiting
- Optimized queries with node index

**Example:**
```python
# Get recent entries for specific node
node_entries = ledger.get_entries_by_node("Node_1", limit=10)
print(f"Recent entries for Node_1: {len(node_entries)}")

# Get all entries for node (no limit)
all_node_entries = ledger.get_entries_by_node("Node_1")
```

### Cache Management

#### `_is_cache_valid() -> bool`

**Description:**
Check if cached ledger data is still valid based on TTL (Time To Live) configuration.

**Cache TTL:**
- Default: 300 seconds (5 minutes)
- Configurable via `_cache_ttl` attribute

**Returns:**
Boolean indicating whether cache is still valid

#### `_invalidate_cache() -> None`

**Description:**
Invalidate cached data after write operations to ensure data consistency.

**Invalidation Process:**
1. Reset cache timestamp to force refresh
2. Clear cached ledger data
3. Clear individual entry cache

**Automatic Triggers:**
- Called after successful `append_entry` operations
- Triggered after `cleanup_old_entries` operations

### Maintenance Operations

#### `cleanup_old_entries(max_age_seconds: int) -> int`

**Description:**
Clean up old entries based on age for database maintenance and space management.

**Parameters:**
- `max_age_seconds` (int): Maximum age in seconds for entries to keep

**Returns:**
Number of entries deleted

**Process:**
1. Delete entries older than specified age
2. Commit transaction for atomicity
3. Invalidate caches after cleanup
4. Return count of deleted entries

**Example:**
```python
# Clean up entries older than 30 days
thirty_days = 30 * 24 * 60 * 60
deleted_count = ledger.cleanup_old_entries(thirty_days)
print(f"Deleted {deleted_count} old entries")
```

### Error Handling and Recovery

#### Transient Error Detection

```python
def _is_transient_error(self, error: sqlite3.Error) -> bool:
    """Check if error is transient and worth retrying."""
    error_msg = str(error).lower()
    return any(term in error_msg for term in ['locked', 'busy', 'timeout'])
```

**Transient Errors:**
- Database lock conditions
- Busy database states
- Timeout conditions

**Recovery Strategy:**
- Automatic retry for transient errors
- Configurable retry delays
- Comprehensive error logging

#### Exception Types

- **sqlite3.Error**: Base SQLite error class
- **sqlite3.IntegrityError**: Constraint violations (handled as ValueError)
- **ValueError**: Data validation failures
- **RuntimeError**: Critical system errors

### Performance Characteristics

#### Connection Pooling

**Benefits:**
- Reduced connection overhead
- Improved resource utilization
- Thread-safe concurrent access
- Automatic cleanup on thread termination

**Configuration:**
```python
# Optimal settings for different workloads
high_throughput:
  max_connections: 20
  timeout: 60
  cache_size: 50000

low_latency:
  max_connections: 5
  timeout: 10
  synchronous_mode: "OFF"
```

#### Caching Strategy

**Multi-Level Caching:**
1. **Ledger Cache**: Full ledger results (5-minute TTL)
2. **Entry Cache**: Individual entries (LRU, 32 max)
3. **Query Cache**: Node-specific queries (LRU decorated)

**Cache Invalidation:**
- Automatic invalidation on write operations
- TTL-based expiration for read caches
- Manual invalidation methods available

#### Query Optimization

**Index Strategy:**
- Timestamp index for time-based queries
- Node ID index for agent-specific lookups
- Confidence index for threshold filtering

**Query Patterns:**
- Parameterized queries for security
- Optimized SELECT statements
- Efficient pagination support

### Configuration Integration

The DatabaseLedger integrates with the configuration system for runtime parameter management:

```python
# Configuration keys used by DatabaseLedger:
database:
  path: "ledger.db"                    # Database file location
  timeout: 30                         # Connection timeout seconds
  check_same_thread: false            # SQLite thread safety
  # Additional settings inherited from DatabaseConfig
```

### Thread Safety

#### Concurrency Control

**Mechanisms:**
- Thread-local connection storage
- Reentrant lock for critical sections
- Atomic transactions for data consistency

**Thread Safety Guarantees:**
- Multiple readers can access simultaneously
- Single writer blocks other operations
- Connection pool is thread-safe
- Cache operations are atomic

#### Best Practices

```python
# Correct usage patterns
from database import get_db_connection

# Pattern 1: Context manager (recommended)
with get_db_connection() as conn:
    # Safe concurrent operations
    pass

# Pattern 2: Explicit pool management
pool = get_connection_pool()
conn = pool.get_connection()
try:
    # Database operations
    pass
finally:
    # Connection automatically managed by pool
    pass
```

### Monitoring and Diagnostics

#### Performance Metrics

**Available Metrics:**
- Connection pool utilization
- Cache hit/miss ratios
- Query execution times
- Error rates and types

**Monitoring Integration:**
```python
# Integration with monitoring systems
from monitoring import get_monitoring

monitoring = get_monitoring()
monitoring.record_metric('db_connections_active', len(pool._connections))
monitoring.record_metric('db_cache_hit_rate', calculate_cache_hit_rate())
```

### Integration Patterns

#### With Simulation Framework

```python
from database import DatabaseLedger
from simulation import Simulation

class MonitoredSimulation(Simulation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ledger = DatabaseLedger()
        # Custom monitoring setup
```

#### With Custom Data Sources

```python
class CustomLedger(DatabaseLedger):
    def append_custom_entry(self, custom_data):
        # Validate and transform custom data
        entry = self._transform_custom_data(custom_data)
        return self.append_entry(entry)
```

### Best Practices

#### Performance Optimization

1. **Connection Management**: Use context managers for automatic cleanup
2. **Batch Operations**: Group multiple operations when possible
3. **Cache Utilization**: Monitor and optimize cache hit rates
4. **Index Usage**: Structure queries to leverage database indexes

#### Reliability Patterns

1. **Error Handling**: Always handle database exceptions appropriately
2. **Transaction Management**: Use transactions for multi-step operations
3. **Resource Cleanup**: Ensure proper connection cleanup
4. **Data Validation**: Validate all data before database operations

#### Maintenance Procedures

1. **Regular Cleanup**: Schedule old entry cleanup based on retention policies
2. **Index Maintenance**: Monitor index usage and rebuild if necessary
3. **Connection Monitoring**: Track connection pool utilization
4. **Cache Tuning**: Adjust cache TTL based on access patterns

### Troubleshooting

#### Common Issues

**Database Lock Errors:**
- Increase timeout values in configuration
- Check for long-running transactions
- Monitor concurrent access patterns

**High Memory Usage:**
- Reduce cache TTL for less frequently accessed data
- Monitor connection pool size
- Check for connection leaks

**Slow Query Performance:**
- Verify index usage in query plans
- Consider query restructuring
- Monitor cache hit rates for optimization opportunities

**Connection Pool Exhaustion:**
- Increase max_connections in configuration
- Monitor for connection leaks
- Implement connection health checks

### API Version History

- **v1.0**: Basic SQLite ledger implementation
- **v1.1**: Added connection pooling
- **v1.2**: Enhanced caching and performance optimizations
- **v1.3**: Comprehensive error handling and recovery
- **v1.4**: Advanced monitoring and diagnostics
- **v1.5**: Modern type hints and configuration integration