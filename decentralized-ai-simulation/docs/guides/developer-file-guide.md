# Developer File Guide

## Overview

This guide provides step-by-step instructions for developers working with the project's file structure. It covers adding new files, modifying existing files safely, import statement conventions, and testing file-related changes.

## Adding New Files to the Project

### 1. Determine Correct File Location

**Use the file structure overview to determine placement:**

```python
# Core simulation logic → src/core/
# Utility functions → src/utils/
# Configuration files → config/
# Tests → tests/unit/ or tests/integration/
# Documentation → docs/
# Scripts → scripts/
# Data files → data/
```

### 2. Create Files with Proper Initialization

**Python modules must include proper initialization:**

```python
# src/utils/new_utility.py
"""
New Utility Module

This module provides additional utility functions for the project.
"""

from typing import Dict, List, Any, Optional
from decentralized_ai_simulation.src.utils.logging_setup import get_logger

logger = get_logger(__name__)

def new_utility_function(param: str) -> bool:
    """
    Description of what this function does.

    Args:
        param: Description of the parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When parameter is invalid
    """
    if not param:
        raise ValueError("Parameter cannot be empty")

    logger.info(f"Processing parameter: {param}")
    return True
```

**Package directories need `__init__.py`:**

```python
# src/core/new_feature/__init__.py
"""
New Feature Package

This package contains the new feature implementation.
"""

from .new_feature_module import NewFeatureClass

__all__ = ['NewFeatureClass']
```

### 3. Update Import Statements

**Add imports to parent `__init__.py` files:**

```python
# src/core/__init__.py (if adding new core module)
"""
Core simulation modules.
"""

from . import agents
from . import database
from . import simulation
from . import new_feature  # Add new module

__all__ = ['agents', 'database', 'simulation', 'new_feature']
```

### 4. Create Corresponding Tests

**Create tests alongside new functionality:**

```python
# tests/unit/test_new_utility.py
"""
Tests for new_utility module.
"""

import pytest
from decentralized_ai_simulation.src.utils.new_utility import new_utility_function

class TestNewUtility:
    """Test cases for new utility function."""

    def test_new_utility_function_success(self):
        """Test successful execution."""
        result = new_utility_function("test_param")
        assert result is True

    def test_new_utility_function_empty_param(self):
        """Test error handling for empty parameter."""
        with pytest.raises(ValueError, match="Parameter cannot be empty"):
            new_utility_function("")
```

## Modifying Existing Files Safely

### 1. Use File Management Utilities

**Always use `FileManager` for file modifications:**

```python
from decentralized_ai_simulation.src.utils.file_manager import FileManager

file_manager = FileManager()

# Safe file modification with backup
config_content = """{
    "database": {
        "path": "ledger.db",
        "new_setting": "new_value"  # Adding new setting
    }
}"""

success = file_manager.safe_write_file(
    file_path="config/app_config.json",
    content=config_content,
    backup=True  # Creates backup before modifying
)
```

### 2. Follow Import Statement Conventions

**Import order (following PEP 8):**

```python
# 1. Standard library imports
import os
import json
from pathlib import Path
from typing import Dict, List, Any

# 2. Third-party imports
import yaml
from mesa import Agent, Model

# 3. Local imports (relative)
from .utils import helper_function
from ..config.config_manager import get_config

# 4. Local imports (absolute)
from decentralized_ai_simulation.src.core.agents import AnomalyAgent
```

**Import style guidelines:**

```python
# ✅ Good: Import specific functions/classes
from decentralized_ai_simulation.src.utils.file_manager import FileManager
from decentralized_ai_simulation.src.config.config_manager import get_config

# ❌ Avoid: Wildcard imports (except in __init__.py)
# from decentralized_ai_simulation.src.utils import *

# ✅ Good: Use aliases for long module names
from decentralized_ai_simulation.src.utils import file_manager as fm
from decentralized_ai_simulation.src.core.simulation import Simulation as Sim

# ✅ Good: Relative imports within packages
from .exceptions import FileOperationError
from ..config.config_manager import get_config
```

### 3. Update Configuration Files

**When adding new configuration options:**

```python
# 1. Update config_manager.py to include new options
def get_config(key: str, default: Optional[Any] = None) -> Any:
    config_map = {
        'new_feature.enabled': True,
        'new_feature.setting': 'default_value',
        # ... existing config
    }
    return config_map.get(key, default)

# 2. Update config.yaml
new_feature:
  enabled: true
  setting: "default_value"

# 3. Update environment variable support
NEW_FEATURE_ENABLED=true
NEW_FEATURE_SETTING=custom_value
```

## Import Statement Patterns

### 1. Core Module Imports

**From core modules:**

```python
# Import main classes
from decentralized_ai_simulation.src.core.agents import AnomalyAgent
from decentralized_ai_simulation.src.core.database import DatabaseLedger
from decentralized_ai_simulation.src.core.simulation import Simulation

# Import with aliases for convenience
from decentralized_ai_simulation.src.core.agents import AnomalyAgent as Agent
from decentralized_ai_simulation.src.core.simulation import Simulation as Sim
```

### 2. Utility Module Imports

**From utility modules:**

```python
# Import utility classes
from decentralized_ai_simulation.src.utils.file_manager import FileManager
from decentralized_ai_simulation.src.utils.data_manager import DataManager
from decentralized_ai_simulation.src.utils.migration_helper import MigrationHelper

# Import specific functions
from decentralized_ai_simulation.src.utils.logging_setup import get_logger
from decentralized_ai_simulation.src.utils.monitoring import get_monitoring
```

### 3. Configuration Imports

**Configuration access patterns:**

```python
# Standard configuration access
from decentralized_ai_simulation.src.config.config_manager import get_config

db_path = get_config('database.path')
agent_count = get_config('simulation.default_agents', 50)

# Type-safe configuration access
port = get_config_loader().get_config_with_validation(
    key='monitoring.port',
    expected_type=int,
    default=8000,
    min_val=1024,
    max_val=65535
)
```

### 4. Package-Level Imports

**Import entire packages:**

```python
# Import all core modules
from decentralized_ai_simulation.src import core
from decentralized_ai_simulation.src import utils
from decentralized_ai_simulation.src import config

# Access through package
agent = core.agents.AnomalyAgent()
db = core.database.DatabaseLedger()
config_data = config.config_manager.get_config('database.path')
```

## Testing File-Related Changes

### 1. Unit Tests for File Operations

**Test file management utilities:**

```python
# tests/unit/test_file_operations.py
import pytest
import tempfile
import json
from pathlib import Path
from decentralized_ai_simulation.src.utils.file_manager import FileManager

class TestFileManager:
    """Test file management operations."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.file_manager = FileManager(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_safe_write_file(self):
        """Test safe file writing with backup."""
        test_file = self.temp_dir / "test.json"
        content = '{"test": "data"}'

        # Write file
        success = self.file_manager.safe_write_file(
            test_file, content, backup=True
        )
        assert success is True
        assert test_file.exists()

        # Verify content
        loaded = self.file_manager.safe_read_file(test_file)
        assert loaded == content

    def test_file_backup_restore(self):
        """Test backup and restore functionality."""
        test_file = self.temp_dir / "config.json"
        original_content = '{"version": "1.0"}'
        new_content = '{"version": "2.0"}'

        # Write original content
        self.file_manager.safe_write_file(test_file, original_content)

        # Write new content (creates backup)
        self.file_manager.safe_write_file(test_file, new_content, backup=True)

        # Verify new content
        current = self.file_manager.safe_read_file(test_file)
        assert current == new_content

        # Verify backup exists
        backup_file = test_file.with_suffix('.backup')
        assert backup_file.exists()
```

### 2. Integration Tests for File Workflows

**Test complete file operation workflows:**

```python
# tests/integration/test_file_workflows.py
import pytest
import tempfile
from pathlib import Path
from decentralized_ai_simulation.src.utils.file_manager import FileManager
from decentralized_ai_simulation.src.utils.data_manager import DataManager

class TestFileWorkflows:
    """Integration tests for file operation workflows."""

    def setup_method(self):
        """Set up integration test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.file_manager = FileManager(self.temp_dir)
        self.data_manager = DataManager(self.temp_dir)

    def test_complete_data_workflow(self):
        """Test complete data storage and retrieval workflow."""
        # 1. Create directory structure
        structure = {
            "data": {
                "input": {},
                "processed": {},
                "output": {}
            }
        }
        self.file_manager.create_directory_structure(structure)

        # 2. Store data
        test_data = {"records": [1, 2, 3, 4, 5]}
        self.data_manager.store_json_data(
            test_data,
            self.temp_dir / "data" / "input" / "test.json"
        )

        # 3. Process and store results
        processed_data = {"processed_records": len(test_data["records"])}
        self.data_manager.store_json_data(
            processed_data,
            self.temp_dir / "data" / "processed" / "results.json"
        )

        # 4. Verify complete workflow
        input_file = self.temp_dir / "data" / "input" / "test.json"
        processed_file = self.temp_dir / "data" / "processed" / "results.json"

        assert input_file.exists()
        assert processed_file.exists()

        loaded_input = self.data_manager.load_json_data(input_file)
        loaded_processed = self.data_manager.load_json_data(processed_file)

        assert loaded_input == test_data
        assert loaded_processed == processed_data
```

### 3. Configuration Tests

**Test configuration management:**

```python
# tests/unit/test_configuration_management.py
import pytest
import tempfile
import yaml
from pathlib import Path
from decentralized_ai_simulation.src.config.config_manager import ConfigLoader

class TestConfigurationManagement:
    """Test configuration loading and management."""

    def setup_method(self):
        """Set up configuration test."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def test_yaml_configuration_loading(self):
        """Test loading configuration from YAML file."""
        config_data = {
            'database': {
                'path': 'test.db',
                'pool_size': 10
            },
            'simulation': {
                'agents': 50,
                'steps': 100
            }
        }

        config_file = self.temp_dir / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Test loading
        config_loader = ConfigLoader(str(config_file))
        assert config_loader.get('database.path') == 'test.db'
        assert config_loader.get('database.pool_size') == 10
        assert config_loader.get('simulation.agents') == 50

    def test_environment_variable_overrides(self):
        """Test environment variable configuration overrides."""
        config_data = {
            'database': {
                'path': 'default.db',
                'pool_size': 5
            }
        }

        config_file = self.temp_dir / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Set environment variable
        import os
        os.environ['DATABASE_PATH'] = 'override.db'
        os.environ['DATABASE_POOL_SIZE'] = '20'

        try:
            config_loader = ConfigLoader(str(config_file))

            # Should use environment overrides
            assert config_loader.get('database.path') == 'override.db'
            assert config_loader.get('database.pool_size') == 20
        finally:
            # Clean up environment
            del os.environ['DATABASE_PATH']
            del os.environ['DATABASE_POOL_SIZE']
```

## Common Pitfalls and How to Avoid Them

### 1. Import Path Issues

**Problem:** Incorrect import paths after file reorganization.

**Solution:** Always use absolute imports from the project root:

```python
# ✅ Correct
from decentralized_ai_simulation.src.utils.file_manager import FileManager

# ❌ Incorrect (breaks after reorganization)
from utils.file_manager import FileManager
```

### 2. Missing `__init__.py` Files

**Problem:** Python can't import modules without `__init__.py` files.

**Solution:** Ensure all package directories have `__init__.py`:

```bash
# Check for missing __init__.py files
find src/ -type d ! -path "*/__pycache__/*" -exec test ! -e {}/__init__.py \; -print

# Create missing __init__.py files
find src/ -type d ! -path "*/__pycache__/*" -exec touch {}/__init__.py \;
```

### 3. File Permission Issues

**Problem:** File operations fail due to permission issues.

**Solution:** Use proper file permissions and error handling:

```python
import os

# Set appropriate permissions
os.chmod("data/output.json", 0o644)  # Owner: read/write, Group/Others: read

# Handle permission errors gracefully
try:
    with open("restricted_file.txt", 'w') as f:
        f.write("data")
except PermissionError as e:
    logger.error(f"Permission denied: {e}")
    # Handle error appropriately
```

### 4. Configuration Validation Failures

**Problem:** Configuration changes break existing functionality.

**Solution:** Validate configuration changes:

```python
# Test configuration changes before deployment
def validate_config_changes(new_config_path: str) -> List[str]:
    """Validate configuration file for common issues."""
    errors = []

    try:
        # Test loading
        config_loader = ConfigLoader(new_config_path)

        # Test critical paths
        critical_paths = [
            'database.path',
            'simulation.default_agents',
            'logging.level'
        ]

        for path in critical_paths:
            try:
                value = config_loader.get(path)
                if value is None:
                    errors.append(f"Missing critical config: {path}")
            except Exception as e:
                errors.append(f"Error accessing {path}: {e}")

    except Exception as e:
        errors.append(f"Configuration validation failed: {e}")

    return errors
```

### 5. Test Coverage Gaps

**Problem:** File operations not properly tested lead to runtime failures.

**Solution:** Ensure comprehensive test coverage:

```python
# Test file operation edge cases
def test_file_operation_edge_cases():
    """Test edge cases for file operations."""

    # Test with non-existent directories
    # Test with invalid file permissions
    # Test with disk space issues
    # Test with concurrent access
    # Test with large files
    # Test with special characters in paths

    pass
```

## Development Workflow

### 1. Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/new_utility

# 2. Create module structure
mkdir -p src/utils/new_feature/
touch src/utils/new_feature/__init__.py
touch src/utils/new_feature/implementation.py

# 3. Implement feature
# ... add code ...

# 4. Create tests
mkdir -p tests/unit/test_new_feature/
touch tests/unit/test_new_feature/__init__.py
touch tests/unit/test_new_feature/test_implementation.py

# 5. Update imports
# Edit src/utils/__init__.py to include new module

# 6. Run tests
pytest tests/unit/test_new_feature/ -v

# 7. Update documentation
# Edit relevant .md files

# 8. Commit changes
git add .
git commit -m "Add new utility feature"
```

### 2. Modifying Existing Files

```python
# 1. Create backup before modifying
file_manager = FileManager()
file_manager.safe_write_file(
    "important_file.py",
    original_content,
    backup=True
)

# 2. Make changes with proper error handling
try:
    # Make modifications
    modified_content = apply_changes(original_content)

    # Write with backup
    file_manager.safe_write_file(
        "important_file.py",
        modified_content,
        backup=True
    )

    # Run tests to verify changes
    pytest tests/ -v

except Exception as e:
    logger.error(f"Modification failed: {e}")
    # Changes will be rolled back automatically
    raise
```

### 3. Testing File Changes

```bash
# Run all file-related tests
pytest tests/unit/test_file_* -v

# Run integration tests
pytest tests/integration/test_file_workflows.py -v

# Test with different configurations
CONFIG_PATH=test_config.yaml pytest tests/ -v

# Test file operations under load
pytest tests/stress/test_file_operations.py -v
```

## Performance Testing

### File Operation Benchmarks

```python
# benchmarks/test_file_performance.py
import time
import tempfile
from pathlib import Path
from decentralized_ai_simulation.src.utils.file_manager import FileManager

def benchmark_file_operations():
    """Benchmark file operations for performance regression testing."""

    temp_dir = Path(tempfile.mkdtemp())
    file_manager = FileManager(temp_dir)

    # Generate test data
    large_data = {"data": list(range(10000))}

    # Benchmark write operations
    start_time = time.time()
    for i in range(100):
        file_manager.safe_write_file(
            temp_dir / f"test_{i}.json",
            json.dumps(large_data)
        )
    write_time = time.time() - start_time

    # Benchmark read operations
    start_time = time.time()
    for i in range(100):
        data = file_manager.safe_read_file(temp_dir / f"test_{i}.json")
    read_time = time.time() - start_time

    print(f"Write time (100 files): {write_time:.2f}s")
    print(f"Read time (100 files): {read_time:.2f}s")

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
```

## Best Practices Summary

1. **Always use `FileManager` for file operations**
2. **Follow import statement conventions (PEP 8)**
3. **Create comprehensive tests for all file operations**
4. **Use configuration validation for config changes**
5. **Handle errors gracefully with proper logging**
6. **Create backups before major file modifications**
7. **Follow naming conventions consistently**
8. **Update documentation when adding new files**
9. **Test file operations under various conditions**
10. **Use type hints for better code maintainability**

This guide ensures safe, consistent, and maintainable file operations across the project development lifecycle.

## Related Documentation

- **[File Structure Overview](../project/file-structure-overview.md)** - Understanding where to place different types of files
- **[File Management Guidelines](file-management-guidelines.md)** - Detailed usage of file management utilities
- **[Configuration Management Guide](configuration-management.md)** - Managing configuration files during development
- **[Migration Documentation](migration-documentation.md)** - Lessons learned from the file reorganization