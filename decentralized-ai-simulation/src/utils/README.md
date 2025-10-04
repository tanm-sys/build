# File Management Utilities Documentation

This directory contains comprehensive file management utilities for the Decentralized AI Simulation project. These utilities provide robust file operations, configuration management, data handling, and migration capabilities with comprehensive error handling and logging.

## Overview

The file management system consists of four main components:

1. **FileManager** - Core file operations with atomic writes and rollback
2. **ConfigurationManager** - Environment-specific configuration handling
3. **DataManager** - JSON/YAML data storage and database management
4. **MigrationHelper** - Automated file reorganization and refactoring

## Quick Start

```python
from decentralized_ai_simulation.src.utils.file_manager import FileManager
from decentralized_ai_simulation.src.config.config_manager import ConfigurationManager
from decentralized_ai_simulation.src.utils.data_manager import DataManager
from decentralized_ai_simulation.src.utils.migration_helper import MigrationHelper

# Initialize managers
file_manager = FileManager()
config_manager = ConfigurationManager()
data_manager = DataManager()
migration_helper = MigrationHelper()
```

## FileManager Usage Examples

### Basic File Operations

```python
from pathlib import Path

# Safe file writing with backup
success = file_manager.safe_write_file(
    "config/app_settings.json",
    '{"debug": true, "log_level": "INFO"}',
    backup=True
)

# Safe file reading with default fallback
content = file_manager.safe_read_file(
    "config/missing_file.json",
    default="{}"
)

# Get comprehensive file information
file_info = file_manager.get_file_info("important_data.json")
print(f"File size: {file_info['size']} bytes")
print(f"Last modified: {file_info['modified_time']}")
```

### Directory Structure Management

```python
# Create directory structure from definition
structure = {
    "data": {
        "databases": {},
        "blacklists": {},
        "documents": {}
    },
    "logs": {
        "application.log": "",
        "errors.log": ""
    }
}

success = file_manager.create_directory_structure(structure)

# Validate file structure
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
```

### Atomic Write Operations

```python
# Using context manager for atomic writes
with file_manager.atomic_write_context("critical_config.json") as f:
    f.write('{"setting": "value"}')
    # File is only moved to final location when context exits successfully
```

### Safe File Movement

```python
# Move multiple files with rollback capability
file_mappings = [
    ("old_config.yaml", "config/app_config.yaml"),
    ("legacy_db.db", "data/databases/main.db"),
    ("temp_uploads/", "data/documents/")
]

success = file_manager.move_files_safely(file_mappings)
```

## ConfigurationManager Usage Examples

### Environment-Specific Configuration

```python
# Load configuration for specific environment
config = config_manager.load_environment_config("production")

# Access configuration values
api_port = config["api"]["port"]
debug_mode = config["api"]["debug"]

# Validate configuration
errors = config_manager.validate_configuration(config, config_manager._config_schemas)
if errors:
    print(f"Configuration errors: {errors}")
```

### Configuration Templates

```python
# Generate configuration template for development
dev_template = config_manager.generate_config_template("development")
print(dev_template)

# Generate template for production
prod_template = config_manager.generate_config_template("production")

# Save configuration to file
success = config_manager.save_configuration(
    config,
    "config/production.yaml",
    environment="production"
)
```

### Configuration Merging

```python
# Merge base configuration with overrides
base_config = {"api": {"port": 8000, "debug": False}}
override_config = {"api": {"debug": True}}

merged = config_manager.merge_configurations(base_config, override_config)
# Result: {"api": {"port": 8000, "debug": True}}
```

## DataManager Usage Examples

### JSON/YAML Data Storage

```python
# Store data as JSON with integrity checking
test_data = {
    "agents": 50,
    "simulation_steps": 100,
    "parameters": {"learning_rate": 0.01}
}

success = data_manager.store_json_data(test_data, "data/simulation_config.json")

# Load JSON data with integrity validation
loaded_data = data_manager.load_json_data("data/simulation_config.json")

# Store data as YAML
success = data_manager.store_yaml_data(test_data, "data/simulation_config.yaml")
```

### Data Validation

```python
from decentralized_ai_simulation.src.utils.data_manager import DataValidationRule

# Define validation rules
rules = [
    DataValidationRule(
        field="agents",
        rule_type="required",
        message="Number of agents is required"
    ),
    DataValidationRule(
        field="agents",
        rule_type="range",
        value=(1, 1000),
        message="Agents must be between 1 and 1000"
    ),
    DataValidationRule(
        field="parameters.learning_rate",
        rule_type="range",
        value=(0.0, 1.0),
        message="Learning rate must be between 0 and 1"
    )
]

# Validate data
errors = data_manager.validate_data(test_data, rules)
if errors:
    print(f"Validation errors: {errors}")
```

### Database Management

```python
# Define database schema
schema = {
    "agents": {
        "type": "table",
        "columns": {
            "id": {"type": "INTEGER", "constraints": ["PRIMARY KEY"]},
            "trust_score": {"type": "REAL", "constraints": ["NOT NULL"]},
            "wealth": {"type": "INTEGER", "constraints": ["NOT NULL"]}
        },
        "indexes": [
            {"name": "idx_trust_score", "columns": ["trust_score"]},
            {"name": "idx_wealth", "columns": ["wealth"], "unique": False}
        ]
    }
}

# Create database
success = data_manager.create_database("simulation", schema)

# Execute queries
results = data_manager.query_database(
    "simulation",
    "SELECT * FROM agents WHERE trust_score > ?",
    (50,)
)
```

### Blacklist Management

```python
from decentralized_ai_simulation.src.utils.data_manager import BlacklistEntry

# Add entry to blacklist
entry = BlacklistEntry(
    entity_id="agent_123",
    reason="Suspicious trading behavior",
    timestamp=time.time(),
    severity="high",
    metadata={"incident_count": 3}
)

success = data_manager.add_blacklist_entry(entry)

# Retrieve blacklist entries
entries = data_manager.get_blacklist_entries(
    start_date="2024-01-01",
    end_date="2024-12-31",
    severity="high"
)

for entry in entries:
    print(f"Blacklisted: {entry.entity_id} - {entry.reason}")
```

### Backup and Recovery

```python
# Create data backup
backup_path = data_manager.backup_data()
print(f"Backup created at: {backup_path}")

# Get data summary
summary = data_manager.get_data_summary()
print(f"Total data size: {summary['total_size']} bytes")
print(f"Database files: {summary['file_counts']['databases']}")

# Cleanup old backups (older than 30 days)
removed = data_manager.cleanup_old_backups(max_age_days=30)
print(f"Removed {removed} old backups")
```

## MigrationHelper Usage Examples

### Creating and Executing Migrations

```python
# Create migration plan
migration_id = migration_helper.create_migration_plan(
    "reorganize_project_structure"
)

# Execute migration (dry run first)
result = migration_helper.execute_migration(migration_id, dry_run=True)

print(f"Steps completed: {result.steps_completed}/{result.total_steps}")
if result.warnings:
    print(f"Warnings: {result.warnings}")

# Execute actual migration
if not result.errors:
    result = migration_helper.execute_migration(migration_id, dry_run=False)
```

### Custom Migration Steps

```python
from decentralized_ai_simulation.src.utils.migration_helper import MigrationStep

def custom_backup_step():
    """Custom backup logic"""
    print("Creating custom backup...")
    # Your backup logic here

def custom_cleanup_step():
    """Custom cleanup logic"""
    print("Performing custom cleanup...")
    # Your cleanup logic here

# Define custom migration steps
custom_steps = [
    MigrationStep(
        name="custom_backup",
        description="Create custom backup",
        function=custom_backup_step,
        critical=True
    ),
    MigrationStep(
        name="custom_cleanup",
        description="Perform custom cleanup",
        function=custom_cleanup_step,
        dependencies=["custom_backup"]
    )
]

# Create and execute custom migration
migration_id = migration_helper.create_migration_plan("custom_migration", custom_steps)
result = migration_helper.execute_migration(migration_id)
```

### Import Statement Updates

```python
# Update imports in specific file
success = migration_helper.update_import_statements("src/main.py")

# Reorganize files according to mappings
success = migration_helper.reorganize_files()
```

### Migration Status and Rollback

```python
# Get migration status
status = migration_helper.get_migration_status(migration_id)
print(f"Migration status: {status['status']}")
print(f"Progress: {status['steps_completed']}/{status['total_steps']}")

# Rollback migration if needed
if status['status'] == 'failed':
    success = migration_helper.rollback_migration(migration_id)
    if success:
        print("Migration rolled back successfully")
```

## Error Handling Examples

### Handling File Management Errors

```python
from decentralized_ai_simulation.src.utils.exceptions import (
    FileManagementError,
    ConfigurationError,
    MigrationError
)

try:
    success = file_manager.safe_write_file("config.json", content)
except FileManagementError as e:
    print(f"File operation failed: {e}")
    print(f"Context: {e.context}")
    print(f"File path: {e.file_path}")
    print(f"Operation: {e.operation}")

    # Convert to dictionary for logging/serialization
    error_dict = e.to_dict()
    logger.error(f"File management error: {error_dict}")
```

### Handling Configuration Errors

```python
try:
    config = config_manager.load_environment_config("production")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    print(f"Validation errors: {e.context.get('validation_errors', [])}")

    # Check if it's a retryable error
    if hasattr(e, 'should_retry'):
        if e.should_retry():
            delay = e.get_next_retry_delay()
            print(f"Retrying in {delay} seconds...")
```

### Handling Migration Errors

```python
try:
    result = migration_helper.execute_migration(migration_id)
except MigrationError as e:
    print(f"Migration failed: {e}")
    print(f"Migration step: {e.migration_step}")
    print(f"Rollback attempted: {e.rollback_attempted}")

    # Check if rollback is available
    if not e.rollback_attempted:
        try:
            migration_helper.rollback_migration(migration_id)
        except Exception as rollback_error:
            print(f"Rollback also failed: {rollback_error}")
```

## Best Practices

### 1. Always Use Atomic Operations for Critical Files

```python
# Good - atomic write with backup
with file_manager.atomic_write_context("critical_config.json") as f:
    f.write(json.dumps(config))

# Avoid - direct write without protection
with open("critical_config.json", "w") as f:
    f.write(json.dumps(config))
```

### 2. Validate Configuration Before Use

```python
# Good - validate before using
config = config_manager.load_environment_config("production")
errors = config_manager.validate_configuration(config, config_manager._config_schemas)
if errors:
    raise ConfigurationError(f"Invalid configuration: {errors}")

# Use config safely
api_port = config["api"]["port"]
```

### 3. Use Data Validation for External Data

```python
# Good - validate external data
external_data = load_external_data()
rules = [
    DataValidationRule(field="id", rule_type="required"),
    DataValidationRule(field="score", rule_type="range", value=(0, 100))
]

errors = data_manager.validate_data(external_data, rules)
if errors:
    logger.error(f"Invalid external data: {errors}")
    # Handle validation errors appropriately
```

### 4. Plan Migrations Carefully

```python
# Good - test migration first
migration_id = migration_helper.create_migration_plan("restructure")
result = migration_helper.execute_migration(migration_id, dry_run=True)

if result.errors:
    print(f"Migration issues found: {result.errors}")
    # Fix issues before running actual migration
else:
    result = migration_helper.execute_migration(migration_id, dry_run=False)
```

## Integration with Existing Systems

### Using with Current Config Loader

```python
# The new ConfigurationManager works alongside the existing config_loader
from decentralized_ai_simulation.src.config.config_loader import get_config

# Use existing config loader for simple key access
log_level = get_config('logging.level', 'INFO')

# Use new ConfigurationManager for advanced features
config_manager = ConfigurationManager()
full_config = config_manager.load_environment_config('production')
```

### Using with Logging System

```python
# All utilities integrate with the existing logging system
from decentralized_ai_simulation.src.utils.logging_setup import get_logger

logger = get_logger(__name__)

# File operations are automatically logged
file_manager.safe_write_file("data.json", content)

# Configuration operations are logged
config = config_manager.load_environment_config("production")

# Data operations are logged
data_manager.store_json_data(data, "file.json")
```

## Performance Considerations

### File Operations
- Use atomic writes for critical files to prevent corruption
- Enable backup only for important files to save disk space
- Use appropriate encoding (UTF-8 for text, binary for other data)

### Configuration Management
- Cache configuration in production environments
- Use environment-specific configs for different deployment stages
- Validate configuration once at startup

### Data Management
- Use JSON for structured data, YAML for configuration
- Implement data validation for external data sources
- Regular cleanup of old backups to save disk space

### Migration Operations
- Always run dry-run before actual migration
- Plan migrations during maintenance windows
- Keep backups until migration is validated

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```python
   # Check file permissions before operations
   file_info = file_manager.get_file_info("problematic_file.txt")
   if not file_info['writable']:
       print("File is not writable")
   ```

2. **Configuration Validation Failures**
   ```python
   # Debug configuration issues
   config = config_manager.load_environment_config("development")
   errors = config_manager.validate_configuration(config, config_manager._config_schemas)
   print(f"Validation errors: {errors}")
   ```

3. **Migration Rollback Issues**
   ```python
   # Check migration status and backup availability
   status = migration_helper.get_migration_status(migration_id)
   if status.get('error'):
       print(f"Migration not found: {status['error']}")
   ```

### Debugging Tips

1. Enable debug logging to see detailed operation information
2. Use dry-run mode for migrations to preview changes
3. Check file permissions and disk space before operations
4. Validate data and configuration before processing
5. Keep backups until operations are fully validated

## API Reference

For detailed API documentation, see the docstrings in each module:

- [`file_manager.py`](file_manager.py) - Core file management utilities
- [`config_manager.py`](../config/config_manager.py) - Configuration management
- [`data_manager.py`](data_manager.py) - Data storage and management
- [`migration_helper.py`](migration_helper.py) - Migration utilities
- [`exceptions.py`](exceptions.py) - Custom exception classes