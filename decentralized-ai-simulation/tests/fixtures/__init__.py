"""
Test fixtures and utilities for file management testing.

This module provides shared test fixtures, mock objects, and utility functions
to support comprehensive testing of file management functionality.
"""

import os
import json
import yaml
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock

from ...src.utils.file_manager import FileManager
from ...src.utils.data_manager import DataManager
from ...src.config.config_manager import ConfigLoader
from ...src.utils.migration_helper import MigrationHelper


class TestFixtureManager:
    """Manages test fixtures and temporary test environments."""

    def __init__(self, base_temp_dir: Optional[str] = None):
        """Initialize fixture manager with optional base directory."""
        self.base_temp_dir = Path(base_temp_dir) if base_temp_dir else None
        self.temp_dirs: List[Path] = []
        self.created_files: List[Path] = []

    def create_temp_directory(self, suffix: str = "") -> Path:
        """Create a temporary directory for testing."""
        if self.base_temp_dir:
            temp_dir = self.base_temp_dir / f"test_dir_{suffix}_{len(self.temp_dirs)}"
        else:
            temp_dir = Path(tempfile.mkdtemp(suffix=f"_{suffix}"))

        temp_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def create_test_file(self, temp_dir: Path, file_path: str, content: str = "") -> Path:
        """Create a test file with specified content."""
        full_path = temp_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        self.created_files.append(full_path)
        return full_path

    def create_test_binary_file(self, temp_dir: Path, file_path: str, content: bytes = b"") -> Path:
        """Create a test binary file with specified content."""
        full_path = temp_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        self.created_files.append(full_path)
        return full_path

    def cleanup(self):
        """Clean up all created temporary directories and files."""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

        # Reset tracking lists
        self.temp_dirs.clear()
        self.created_files.clear()


class FileManagementTestFixtures:
    """Provides standard test fixtures for file management testing."""

    @staticmethod
    def create_sample_config_data() -> Dict[str, Any]:
        """Create sample configuration data for testing."""
        return {
            'environment': 'testing',
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'test_db',
                'connection_pool_size': 5,
                'timeout': 30
            },
            'simulation': {
                'default_agents': 50,
                'default_steps': 100,
                'grid_width': 10,
                'grid_height': 10,
                'step_delay': 0.1,
                'anomaly_rate': 0.05
            },
            'agent': {
                'initial_wealth': 1,
                'initial_trust_score': 100,
                'trust_increment': 10,
                'trust_decrement': 20,
                'blacklist_threshold': 50
            },
            'logging': {
                'level': 'INFO',
                'file': 'simulation.log',
                'max_bytes': 10485760,
                'backup_count': 5
            }
        }

    @staticmethod
    def create_sample_json_data() -> Dict[str, Any]:
        """Create sample JSON data for testing."""
        return {
            'users': [
                {'id': 1, 'name': 'Alice', 'active': True, 'score': 95.5},
                {'id': 2, 'name': 'Bob', 'active': False, 'score': 87.2},
                {'id': 3, 'name': 'Charlie', 'active': True, 'score': 92.8}
            ],
            'metadata': {
                'version': '1.0.0',
                'created_at': '2023-01-01T00:00:00Z',
                'total_records': 3
            }
        }

    @staticmethod
    def create_sample_yaml_data() -> Dict[str, Any]:
        """Create sample YAML data for testing."""
        return {
            'server': {
                'host': 'localhost',
                'port': 8080,
                'ssl': {
                    'enabled': True,
                    'certificate': '/path/to/cert.pem'
                }
            },
            'features': [
                'authentication',
                'authorization',
                'logging',
                'monitoring'
            ],
            'settings': {
                'debug': True,
                'max_connections': 100,
                'timeout': 30.5
            }
        }

    @staticmethod
    def create_project_structure() -> Dict[str, Any]:
        """Create sample project directory structure."""
        return {
            'src': {
                'core': {
                    'agents.py': None,
                    'database.py': None,
                    'simulation.py': None
                },
                'utils': {
                    'file_manager.py': None,
                    'data_manager.py': None,
                    'migration_helper.py': None
                },
                'config': {
                    'config.yaml': None,
                    'environments': {
                        'development.yaml': None,
                        'production.yaml': None
                    }
                },
                'ui': {
                    'streamlit_app.py': None,
                    'api_server.py': None
                }
            },
            'tests': {
                'unit': {},
                'integration': {}
            },
            'docs': {
                'README.md': '# Project Documentation',
                'api': {}
            },
            'data': {
                'databases': {},
                'blacklists': {},
                'documents': {}
            }
        }


class MockFileManager:
    """Mock FileManager for testing purposes."""

    def __init__(self):
        """Initialize mock file manager."""
        self.files: Dict[str, Any] = {}
        self.directories: set = set()
        self.write_calls: List[Dict[str, Any]] = []
        self.read_calls: List[Dict[str, Any]] = []

    def mock_safe_write_file(self, file_path: str, content: Any, **kwargs) -> bool:
        """Mock safe_write_file method."""
        self.files[file_path] = content
        self.write_calls.append({
            'file_path': file_path,
            'content': content,
            'kwargs': kwargs
        })
        return True

    def mock_safe_read_file(self, file_path: str, **kwargs) -> Any:
        """Mock safe_read_file method."""
        self.read_calls.append({
            'file_path': file_path,
            'kwargs': kwargs
        })
        return self.files.get(file_path, kwargs.get('default'))

    def mock_create_directory_structure(self, structure: Dict[str, Any]) -> bool:
        """Mock create_directory_structure method."""
        def create_structure(data: Dict[str, Any], base_path: str):
            for key, value in data.items():
                current_path = os.path.join(base_path, key)
                self.directories.add(current_path)

                if isinstance(value, dict):
                    os.makedirs(current_path, exist_ok=True)
                    create_structure(value, current_path)
                else:
                    self.files[current_path] = value or ""

        create_structure(structure, "")
        return True

    def get_write_call_count(self) -> int:
        """Get number of write calls made."""
        return len(self.write_calls)

    def get_read_call_count(self) -> int:
        """Get number of read calls made."""
        return len(self.read_calls)

    def get_created_files(self) -> List[str]:
        """Get list of created file paths."""
        return list(self.files.keys())

    def get_created_directories(self) -> List[str]:
        """Get list of created directory paths."""
        return list(self.directories)


def create_mock_config_loader(config_data: Optional[Dict[str, Any]] = None) -> MagicMock:
    """Create a mock ConfigLoader for testing."""
    if config_data is None:
        config_data = FileManagementTestFixtures.create_sample_config_data()

    mock_loader = MagicMock(spec=ConfigLoader)
    mock_loader.get.side_effect = lambda key, default=None: get_nested_value(config_data, key, default)
    mock_loader.config = config_data
    mock_loader.config_path = "/mock/config.yaml"
    mock_loader.is_production.return_value = config_data.get('environment') == 'production'
    mock_loader.is_development.return_value = config_data.get('environment') == 'development'

    return mock_loader


def get_nested_value(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Get nested dictionary value using dot notation."""
    keys = key.split('.')
    value = data

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value


def create_test_blacklist_entries(count: int = 5) -> List[Dict[str, Any]]:
    """Create test blacklist entries."""
    from ...src.utils.data_manager import BlacklistEntry

    entries = []
    severities = ['low', 'medium', 'high', 'critical']

    for i in range(count):
        entry = BlacklistEntry(
            entity_id=f'user_{i}',
            reason=f'Test reason {i}',
            timestamp=1234567890.0 + i,
            severity=severities[i % len(severities)],
            metadata={'test_data': f'value_{i}'}
        )
        entries.append(entry)

    return entries


def create_large_test_dataset(record_count: int = 1000) -> Dict[str, Any]:
    """Create a large test dataset for performance testing."""
    return {
        'records': [
            {
                'id': i,
                'name': f'User {i}',
                'email': f'user{i}@example.com',
                'active': i % 2 == 0,
                'score': 50.0 + (i % 50),
                'metadata': {
                    'created_at': f'2023-01-{i % 28 + 1:02d}T00:00:00Z',
                    'tags': [f'tag_{j}' for j in range(i % 5)]
                }
            }
            for i in range(record_count)
        ],
        'summary': {
            'total_records': record_count,
            'active_records': record_count // 2,
            'generated_at': '2023-01-01T00:00:00Z'
        }
    }


def assert_file_exists_and_has_content(file_path: Path, expected_content: str):
    """Assertion helper for file existence and content."""
    assert file_path.exists(), f"File {file_path} does not exist"
    assert file_path.is_file(), f"Path {file_path} is not a file"

    with open(file_path, 'r', encoding='utf-8') as f:
        actual_content = f.read()

    assert actual_content == expected_content, f"File content mismatch for {file_path}"


def assert_directory_structure_exists(base_path: Path, structure: Dict[str, Any]):
    """Assertion helper for directory structure existence."""
    def check_structure(data: Dict[str, Any], current_path: Path):
        for key, value in data.items():
            item_path = current_path / key

            if isinstance(value, dict):
                # Should be a directory
                assert item_path.exists(), f"Directory {item_path} does not exist"
                assert item_path.is_dir(), f"Path {item_path} is not a directory"
                check_structure(value, item_path)
            else:
                # Should be a file
                assert item_path.exists(), f"File {item_path} does not exist"
                assert item_path.is_file(), f"Path {item_path} is not a file"

    check_structure(structure, base_path)


def create_temporary_config_file(config_data: Optional[Dict[str, Any]] = None) -> Path:
    """Create a temporary configuration file for testing."""
    if config_data is None:
        config_data = FileManagementTestFixtures.create_sample_config_data()

    temp_dir = Path(tempfile.mkdtemp())
    config_file = temp_dir / "test_config.yaml"

    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f)

    return config_file


def create_temporary_data_file(data: Optional[Dict[str, Any]] = None, format: str = 'json') -> Path:
    """Create a temporary data file for testing."""
    if data is None:
        data = FileManagementTestFixtures.create_sample_json_data()

    temp_dir = Path(tempfile.mkdtemp())
    file_extension = 'json' if format == 'json' else 'yaml'
    data_file = temp_dir / f"test_data.{file_extension}"

    if format == 'json':
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    else:
        with open(data_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)

    return data_file


class PerformanceTestHelper:
    """Helper class for performance testing."""

    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        import time

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        return result, end_time - start_time

    @staticmethod
    def generate_test_files(base_path: Path, count: int, size_kb: int = 1) -> List[Path]:
        """Generate test files for performance testing."""
        files = []
        content = "x" * (size_kb * 1024)

        for i in range(count):
            file_path = base_path / f"perf_test_file_{i}.txt"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            files.append(file_path)

        return files

    @staticmethod
    def cleanup_files(files: List[Path]):
        """Clean up test files."""
        for file_path in files:
            if file_path.exists():
                file_path.unlink()


# Global fixture manager instance
fixture_manager = TestFixtureManager()


def setup_test_environment():
    """Set up common test environment."""
    temp_dir = fixture_manager.create_temp_directory("common")

    # Create common test files
    config_data = FileManagementTestFixtures.create_sample_config_data()
    config_file = fixture_manager.create_test_file(
        temp_dir,
        "config.yaml",
        yaml.dump(config_data)
    )

    json_data = FileManagementTestFixtures.create_sample_json_data()
    json_file = fixture_manager.create_test_file(
        temp_dir,
        "test_data.json",
        json.dumps(json_data, indent=2)
    )

    return temp_dir, config_file, json_file


def teardown_test_environment():
    """Tear down common test environment."""
    fixture_manager.cleanup()