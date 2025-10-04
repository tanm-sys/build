# File Management Guidelines

## Overview

This guide provides comprehensive instructions for using the project's file management utilities, including the `FileManager`, `DataManager`, and `ConfigurationManager` classes. These utilities provide robust, thread-safe file operations with comprehensive error handling and rollback capabilities.

## Core File Management Utilities

### FileManager (`src/utils/file_manager.py`)

The `FileManager` class provides atomic file operations, directory management, and file validation with comprehensive error handling.

#### Basic Usage

```python
from decentralized_ai_simulation.src.utils.file_manager import FileManager

# Initialize with project root
file_manager = FileManager("/path/to/project")

# Or use default (current working directory)
file_manager = FileManager()
```

#### Safe File Writing

**Atomic writes with backup support:**

```python
# Safe write with automatic backup
success = file_manager.safe_write_file(
    file_path="config/app_settings.json",
    content='{"setting": "value"}',
    backup=True  # Creates .backup file before writing
)

# Write binary data
with open("data.bin", "rb") as f:
    binary_data = f.read()

success = file_manager.safe_write_file(
    file_path="data/config.bin",
    content=binary_data,
    mode='wb'  # Binary mode
)
```

**Context manager for atomic writes:**

```python
# Atomic write context manager
with file_manager.atomic_write_context("temp_config.yaml") as f:
    f.write("setting: value\n")
    f.write("another_setting: 123\n")
    # File is atomically moved when context exits
```

#### Safe File Reading

```python
# Read with default value if file doesn't exist
content = file_manager.safe_read_file(
    file_path="config/missing.json",
    default="{}"
)

# Read with encoding specification
content = file_manager.safe_read_file(
    file_path="docs/README.md",
    encoding='utf-8'
)
```

#### Directory Structure Management

**Create directory structure from dictionary:**

```python
structure = {
    "data": {
        "databases": {},
        "blacklists": {
            "nodes": {}
        },
        "documents": {}
    },
    "logs": {
        "application.log": "",
        "errors.log": ""
    }
}

success = file_manager.create_directory_structure(structure)
```

#### File Movement with Rollback

```python
# Move multiple files safely
file_mappings = [
    ("old_config.yaml", "config/app.yaml"),
    ("legacy_db.db", "data/databases/main.db"),
    ("temp_upload.json", "data/processed/data.json")
]

success = file_manager.move_files_safely(file_mappings)
```

#### File Validation and Information

```python
# Validate file structure matches expected layout
expected_structure = {
    "src": {
        "core": {},
        "utils": {},
        "config": {}
    }
}

errors = file_manager.validate_file_structure(expected_structure)
if errors:
    print(f"Structure validation errors: {errors}")

# Get comprehensive file information
info = file_manager.get_file_info("data/ledger.db")
print(f"File size: {info['size']} bytes")
print(f"Last modified: {info['modified_time']}")
print(f"Checksum: {info['checksum']}")
```

### DataManager (`src/utils/data_manager.py`)

The `DataManager` class handles JSON/YAML data storage, database management, and blacklist operations.

#### JSON Data Management

```python
from decentralized_ai_simulation.src.utils.data_manager import DataManager

data_manager = DataManager("data")

# Store data with validation and backup
config_data = {
    "database": {"path": "ledger.db"},
    "simulation": {"agents": 100}
}

success = data_manager.store_json_data(
    data=config_data,
    file_path="config/simulation.json",
    indent=2
)

# Load with integrity validation
loaded_data = data_manager.load_json_data(
    file_path="config/simulation.json",
    default={}
)
```

#### YAML Data Management

```python
# Store configuration as YAML
yaml_data = {
    "environment": "production",
    "monitoring": {
        "health_check_interval": 30,
        "enable_metrics": True
    }
}

success = data_manager.store_yaml_data(yaml_data, "config/app.yaml")

# Load YAML data
config = data_manager.load_yaml_data("config/app.yaml", {})
```

#### Data Validation

```python
from decentralized_ai_simulation.src.utils.data_manager import DataValidationRule

# Define validation rules
rules = [
    DataValidationRule(
        field="database.path",
        rule_type="required",
        message="Database path is required"
    ),
    DataValidationRule(
        field="simulation.agents",
        rule_type="range",
        value=(1, 1000),
        message="Agent count must be between 1 and 1000"
    ),
    DataValidationRule(
        field="monitoring.interval",
        rule_type="type",
        value=int,
        message="Monitoring interval must be an integer"
    )
]

# Validate data
errors = data_manager.validate_data(config_data, rules)
if errors:
    print(f"Validation errors: {errors}")
```

#### Database Management

```python
# Create database with schema
schema = {
    "ledger": {
        "type": "table",
        "columns": {
            "id": {"type": "INTEGER", "constraints": ["PRIMARY KEY"]},
            "timestamp": {"type": "REAL", "constraints": ["NOT NULL"]},
            "data": {"type": "TEXT", "constraints": ["NOT NULL"]}
        },
        "indexes": [
            {"name": "idx_timestamp", "columns": ["timestamp"]},
            {"name": "idx_data", "columns": ["data"], "unique": True}
        ]
    }
}

success = data_manager.create_database("main_ledger", schema)

# Query database
results = data_manager.query_database(
    db_name="main_ledger",
    query="SELECT * FROM ledger WHERE timestamp > ?",
    parameters=(time.time() - 3600,)  # Last hour
)
```

#### Blacklist Management

```python
from decentralized_ai_simulation.src.utils.data_manager import BlacklistEntry

# Add blacklist entry
entry = BlacklistEntry(
    entity_id="malicious_node_001",
    reason="Suspicious traffic pattern detected",
    timestamp=time.time(),
    severity="high",
    metadata={"source_ip": "192.168.1.100"}
)

success = data_manager.add_blacklist_entry(entry)

# Retrieve blacklist entries
entries = data_manager.get_blacklist_entries(
    start_date="2024-01-01",
    end_date="2024-01-31",
    severity="high"
)

# Filter by entity
malicious_entries = data_manager.get_blacklist_entries(
    entity_id="malicious_node_001"
)
```

#### Backup and Recovery

```python
# Create full data backup
backup_path = data_manager.backup_data()
print(f"Backup created at: {backup_path}")

# Custom backup location
backup_path = data_manager.backup_data("/custom/backup/location")

# Cleanup old backups (older than 30 days)
removed_count = data_manager.cleanup_old_backups(max_age_days=30)
print(f"Removed {removed_count} old backups")
```

### ConfigurationManager (`src/config/config_manager.py`)

The `ConfigurationManager` provides secure configuration loading with environment variable overrides and validation.

#### Basic Configuration Access

```python
from decentralized_ai_simulation.src.config.config_manager import get_config

# Get configuration values with dot notation
db_path = get_config('database.path')
agent_count = get_config('simulation.default_agents')
log_level = get_config('logging.level', 'INFO')  # With default

# Check environment
if get_config('environment') == 'production':
    print("Running in production mode")
```

#### Configuration with Validation

```python
# Get with type validation and range checking
port = get_config_loader().get_config_with_validation(
    key='monitoring.metrics_port',
    expected_type=int,
    default=8000,
    min_val=1024,
    max_val=65535
)

# Validate configuration values
is_valid = get_config_loader().validate_config_value(
    key='database.timeout',
    value=30,
    expected_type=int
)
```

#### Environment Variable Overrides

```bash
# Override any configuration via environment variables
export DATABASE_PATH="/custom/path/ledger.db"
export SIMULATION_DEFAULT_AGENTS="200"
export LOGGING_LEVEL="DEBUG"
export MONITORING_ENABLE_PROMETHEUS="true"
```

```python
# Access overridden values
custom_db_path = get_config('database.path')  # Returns "/custom/path/ledger.db"
agent_count = get_config('simulation.default_agents')  # Returns 200
```

## Best Practices

### Error Handling

**Always handle file operation errors:**

```python
from decentralized_ai_simulation.src.utils.exceptions import FileOperationError

try:
    success = file_manager.safe_write_file("config.json", data)
except FileOperationError as e:
    logger.error(f"Failed to write config: {e}")
    # Handle error appropriately
```

**Use context managers for automatic cleanup:**

```python
# Automatic transaction management
with data_manager.database_transaction("my_database") as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO table VALUES (?)", (value,))
    # Transaction automatically committed on success
```

### Performance Considerations

**Batch operations for multiple files:**

```python
# Instead of individual operations
for file_path, content in files_to_write.items():
    file_manager.safe_write_file(file_path, content)

# Use batch operations when available
file_manager.move_files_safely(file_mappings)
```

**Enable caching for frequently accessed configurations:**

```python
# Pre-load frequently accessed keys
frequently_used = [
    'database.path',
    'simulation.default_agents',
    'logging.level'
]
get_config_loader().optimize_config_access(frequently_used)
```

**Use appropriate data formats:**

```python
# JSON for structured data with fast parsing
data_manager.store_json_data(structured_data, "data.json")

# YAML for human-readable configuration
data_manager.store_yaml_data(config_data, "config.yaml")
```

### Security Considerations

**Validate all file paths:**

```python
# Always validate paths before operations
if not _validate_config_path(user_provided_path):
    raise ValueError(f"Unsafe path: {user_provided_path}")
```

**Use secure file permissions:**

```python
import os

# Set appropriate permissions for sensitive files
os.chmod("config/database.json", 0o600)  # Owner read/write only
```

**Sanitize configuration values:**

```python
# Validate configuration values before use
value = get_config('user_input')
if not _validate_config_value('user_input', value):
    logger.warning(f"Potentially unsafe configuration value: {value}")
```

## Common Patterns

### Configuration-Driven File Operations

```python
# Use configuration to determine file locations
config = get_config_loader()
data_dir = config.get('data.directory', 'data')
log_dir = config.get('logging.directory', 'logs')

# Create configured directory structure
structure = {
    data_dir: {
        'databases': {},
        'blacklists': {},
        'documents': {}
    },
    log_dir: {
        'application.log': '',
        'errors.log': ''
    }
}

file_manager.create_directory_structure(structure)
```

### Backup Before Major Operations

```python
# Always backup before bulk operations
def safe_bulk_operation(file_mappings, data_updates):
    # Create backup
    backup_path = data_manager.backup_data()

    try:
        # Perform operations
        file_manager.move_files_safely(file_mappings)
        for file_path, data in data_updates.items():
            data_manager.store_json_data(data, file_path)
    except Exception as e:
        logger.error(f"Bulk operation failed: {e}")
        # Restore from backup
        data_manager.restore_from_backup(backup_path)
        raise
```

### Monitoring File Operations

```python
# Monitor file operation performance
import time

start_time = time.time()
success = file_manager.safe_write_file("large_file.json", data)
end_time = time.time()

# Record metrics
get_monitoring().record_metric(
    'file_operation_duration',
    end_time - start_time,
    {'operation': 'write', 'file_size': len(data)}
)
```

## Troubleshooting

### Common Issues

**File permission errors:**
```bash
# Check and fix file permissions
chmod 644 config/*.json
chmod 755 scripts/*.sh
```

**Disk space issues:**
```python
# Check available space
import shutil
total, used, free = shutil.disk_usage("/")
print(f"Available space: {free / (1024**3):.2f} GB")
```

**Database locking issues:**
```python
# Use proper connection management
with data_manager.database_transaction("my_db") as conn:
    # All operations within transaction
    pass
```

**Configuration validation errors:**
```python
# Debug configuration loading
try:
    config = get_config_loader()
    value = config.get('problematic.key')
except Exception as e:
    logger.error(f"Configuration error: {e}")
    # Check config file syntax and environment variables
```

## Performance Monitoring

### File Operation Metrics

```python
# Monitor file operation performance
def monitored_file_operation(operation_name, file_path, operation_func):
    start_time = time.time()

    try:
        result = operation_func()
        success = True
    except Exception as e:
        logger.error(f"File operation failed: {e}")
        success = False
        raise
    finally:
        duration = time.time() - start_time

        # Record metrics
        get_monitoring().record_metric(
            'file_operation_duration',
            duration,
            {
                'operation': operation_name,
                'file_path': file_path,
                'success': success
            }
        )

        if duration > 5.0:  # Log slow operations
            logger.warning(f"Slow file operation: {operation_name} took {duration:.2f}s")
```

### Data Validation Metrics

```python
# Track validation performance
validation_start = time.time()
errors = data_manager.validate_data(data, rules)
validation_duration = time.time() - validation_start

get_monitoring().record_metric(
    'data_validation_duration',
    validation_duration,
    {
        'data_size': len(str(data)),
        'rule_count': len(rules),
        'error_count': len(errors)
    }
)
```

This comprehensive file management system ensures data integrity, provides robust error handling, and supports scalable file operations across the decentralized AI simulation platform.

## Related Documentation

- **[File Structure Overview](../project/file-structure-overview.md)** - Understanding the project's directory organization
- **[Developer File Guide](developer-file-guide.md)** - Best practices for file operations in development
- **[Configuration Management Guide](configuration-management.md)** - Managing configuration files and settings
- **[Migration Documentation](migration-documentation.md)** - How file management utilities were used in the reorganization