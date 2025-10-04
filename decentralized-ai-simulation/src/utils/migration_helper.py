"""
Migration Utilities for Decentralized AI Simulation

This module provides comprehensive migration capabilities including
automated file reorganization, import statement updates, backup and rollback,
and migration progress tracking for the new directory structure.
"""

import os
import ast
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import json

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
        MigrationError,
        FileOperationError,
        ValidationError
    )
except ImportError:
    from exceptions import (
        MigrationError,
        FileOperationError,
        ValidationError
    )

logger = get_logger(__name__)


class MigrationStatus(Enum):
    """Migration operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationStep:
    """Individual migration step definition."""
    name: str
    description: str
    function: Callable
    rollback_function: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)
    critical: bool = False  # If True, failure stops entire migration


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    success: bool
    steps_completed: int
    total_steps: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    start_time: float = 0.0
    end_time: Optional[float] = None
    rollback_performed: bool = False


class MigrationHelper:
    """
    Comprehensive migration utilities for file reorganization and refactoring.

    This class provides:
    - Automated file reorganization according to new directory structure
    - Import statement updates for moved files
    - Backup and rollback capabilities
    - Migration progress tracking
    - Dependency management for complex migrations
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize MigrationHelper.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.migration_log_path = self.project_root / "migration_log.json"
        self.backup_root = self.project_root / "migration_backups"

        # Migration state
        self._current_migration: Optional[str] = None
        self._migration_steps: Dict[str, MigrationStep] = {}
        self._completed_steps: Set[str] = set()

        # File mappings for reorganization
        self._file_mappings = self._define_file_mappings()

        logger.info(f"MigrationHelper initialized for project: {self.project_root}")

    def create_migration_plan(self, migration_name: str, custom_steps: Optional[List[MigrationStep]] = None) -> str:
        """
        Create a migration plan with predefined or custom steps.

        Args:
            migration_name: Name of the migration
            custom_steps: Custom migration steps (optional)

        Returns:
            Migration plan ID

        Raises:
            MigrationError: If migration plan creation fails
        """
        try:
            migration_id = f"{migration_name}_{int(time.time())}"

            if custom_steps:
                self._migration_steps = {step.name: step for step in custom_steps}
            else:
                self._migration_steps = self._get_default_migration_steps()

            # Validate dependencies
            self._validate_migration_dependencies()

            # Save migration plan
            plan_data = {
                'migration_id': migration_id,
                'migration_name': migration_name,
                'steps': [
                    {
                        'name': step.name,
                        'description': step.description,
                        'dependencies': step.dependencies,
                        'critical': step.critical
                    }
                    for step in self._migration_steps.values()
                ],
                'created_at': time.time()
            }

            with open(self.migration_log_path, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2)

            logger.info(f"Created migration plan '{migration_name}' with ID: {migration_id}")
            return migration_id

        except Exception as e:
            raise MigrationError(
                f"Failed to create migration plan '{migration_name}': {e}",
                migration_step="plan_creation",
                cause=e
            )

    def execute_migration(self, migration_id: str, dry_run: bool = False) -> MigrationResult:
        """
        Execute a migration plan with progress tracking and rollback support.

        Args:
            migration_id: ID of the migration to execute
            dry_run: If True, only simulate the migration

        Returns:
            MigrationResult with execution details

        Raises:
            MigrationError: If migration execution fails
        """
        try:
            # Load migration plan
            if not self.migration_log_path.exists():
                raise MigrationError("No migration plan found. Create a plan first.")

            with open(self.migration_log_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)

            if plan_data['migration_id'] != migration_id:
                raise MigrationError(f"Migration ID mismatch. Expected {migration_id}, found {plan_data['migration_id']}")

            # Initialize migration result
            result = MigrationResult(
                success=False,
                steps_completed=0,
                total_steps=len(self._migration_steps),
                start_time=time.time()
            )

            self._current_migration = migration_id

            # Create backup before starting
            if not dry_run:
                backup_path = self._create_migration_backup(migration_id)
                logger.info(f"Created migration backup: {backup_path}")

            try:
                # Execute migration steps in dependency order
                execution_order = self._get_execution_order()

                for step_name in execution_order:
                    if step_name not in self._migration_steps:
                        continue

                    step = self._migration_steps[step_name]

                    try:
                        logger.info(f"Executing migration step: {step.description}")

                        if not dry_run:
                            step.function()
                            self._completed_steps.add(step_name)

                        result.steps_completed += 1
                        logger.info(f"Completed migration step: {step_name}")

                    except Exception as e:
                        error_msg = f"Migration step '{step_name}' failed: {e}"
                        logger.error(error_msg)
                        result.errors.append(error_msg)

                        if step.critical:
                            logger.error(f"Critical migration step failed, stopping migration")
                            break
                        else:
                            logger.warning(f"Non-critical step failed, continuing migration")
                            result.warnings.append(f"Step '{step_name}' failed but continuing")

                # Determine overall success
                result.success = len(result.errors) == 0
                result.end_time = time.time()

                if result.success:
                    logger.info(f"Migration '{migration_id}' completed successfully")
                else:
                    logger.error(f"Migration '{migration_id}' completed with errors")

                    # Attempt rollback if there were failures
                    if not dry_run:
                        try:
                            self.rollback_migration(migration_id)
                            result.rollback_performed = True
                            logger.info(f"Successfully rolled back migration '{migration_id}'")
                        except Exception as rollback_error:
                            logger.error(f"Failed to rollback migration '{migration_id}': {rollback_error}")
                            result.errors.append(f"Rollback failed: {rollback_error}")

                return result

            except Exception as e:
                result.end_time = time.time()
                if not dry_run:
                    try:
                        self.rollback_migration(migration_id)
                        result.rollback_performed = True
                    except Exception as rollback_error:
                        logger.error(f"Failed to rollback after error: {rollback_error}")

                raise MigrationError(
                    f"Migration execution failed: {e}",
                    migration_step="execution",
                    cause=e
                )

        except Exception as e:
            if isinstance(e, MigrationError):
                raise
            raise MigrationError(
                f"Migration execution failed: {e}",
                migration_step="execution",
                cause=e
            )

    def rollback_migration(self, migration_id: str) -> bool:
        """
        Rollback a migration using backup data.

        Args:
            migration_id: ID of the migration to rollback

        Returns:
            bool: True if rollback was successful

        Raises:
            MigrationError: If rollback fails
        """
        try:
            # Find backup for this migration
            backup_path = self.backup_root / migration_id

            if not backup_path.exists():
                raise MigrationError(f"No backup found for migration '{migration_id}'")

            # Load backup metadata
            metadata_file = backup_path / "backup_metadata.json"
            if not metadata_file.exists():
                raise MigrationError(f"Backup metadata not found for migration '{migration_id}'")

            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Restore files
            restored_count = 0
            for file_info in metadata['files']:
                original_path = Path(file_info['original_path'])
                backup_file = backup_path / file_info['backup_filename']

                if backup_file.exists():
                    # Ensure parent directory exists
                    original_path.parent.mkdir(parents=True, exist_ok=True)

                    # Restore file
                    shutil.copy2(backup_file, original_path)
                    restored_count += 1
                    logger.debug(f"Restored file: {original_path}")

            logger.info(f"Successfully rolled back migration '{migration_id}', restored {restored_count} files")
            return True

        except Exception as e:
            if isinstance(e, MigrationError):
                raise
            raise MigrationError(
                f"Migration rollback failed: {e}",
                migration_step="rollback",
                cause=e
            )

    def update_import_statements(self, file_path: Union[str, Path]) -> bool:
        """
        Update import statements in a Python file based on file mappings.

        Args:
            file_path: Path to the Python file to update

        Returns:
            bool: True if imports were updated successfully

        Raises:
            MigrationError: If import update fails
        """
        file_path = Path(file_path)

        try:
            if not file_path.exists() or file_path.suffix != '.py':
                return False

            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            updated_content = content

            # Parse AST to understand imports
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                logger.warning(f"Could not parse {file_path} as Python code: {e}")
                return False

            # Update imports based on file mappings
            for old_path, new_path in self._file_mappings.items():
                # Convert file paths to import paths
                old_import = self._file_path_to_import(old_path)
                new_import = self._file_path_to_import(new_path)

                if old_import and new_import:
                    # Update import statements
                    updated_content = self._update_import_in_content(updated_content, old_import, new_import)

            # Write updated content if changed
            if updated_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                logger.debug(f"Updated imports in {file_path}")
                return True

            return False

        except Exception as e:
            raise MigrationError(
                f"Failed to update imports in {file_path}: {e}",
                migration_step="import_update",
                cause=e
            )

    def reorganize_files(self) -> bool:
        """
        Reorganize files according to the new directory structure.

        Returns:
            bool: True if reorganization was successful

        Raises:
            MigrationError: If reorganization fails
        """
        try:
            reorganized_count = 0

            for old_path, new_path in self._file_mappings.items():
                old_file = self.project_root / old_path
                new_file = self.project_root / new_path

                if old_file.exists() and not new_file.exists():
                    # Ensure destination directory exists
                    new_file.parent.mkdir(parents=True, exist_ok=True)

                    # Move file
                    shutil.move(str(old_file), str(new_file))
                    reorganized_count += 1
                    logger.debug(f"Moved file: {old_path} -> {new_path}")

            logger.info(f"Successfully reorganized {reorganized_count} files")
            return True

        except Exception as e:
            raise MigrationError(
                f"File reorganization failed: {e}",
                migration_step="reorganization",
                cause=e
            )

    def _create_migration_backup(self, migration_id: str) -> Path:
        """
        Create a backup of files that will be affected by migration.

        Args:
            migration_id: ID of the migration

        Returns:
            Path to the created backup directory

        Raises:
            MigrationError: If backup creation fails
        """
        try:
            backup_path = self.backup_root / migration_id
            backup_path.mkdir(parents=True, exist_ok=True)

            # Backup files that will be moved or modified
            backup_files = []

            for old_path, new_path in self._file_mappings.items():
                old_file = self.project_root / old_path
                new_file = self.project_root / new_path

                # Backup source file if it exists
                if old_file.exists():
                    backup_filename = f"backup_{old_file.name}"
                    backup_dest = backup_path / backup_filename
                    shutil.copy2(old_file, backup_dest)
                    backup_files.append({
                        'original_path': str(old_file),
                        'backup_filename': backup_filename
                    })

                # Backup destination file if it exists (in case of conflicts)
                if old_file != new_file and new_file.exists():
                    backup_filename = f"backup_{new_file.name}"
                    backup_dest = backup_path / backup_filename
                    shutil.copy2(new_file, backup_dest)
                    backup_files.append({
                        'original_path': str(new_file),
                        'backup_filename': backup_filename
                    })

            # Save backup metadata
            metadata = {
                'migration_id': migration_id,
                'timestamp': time.time(),
                'files': backup_files,
                'file_mappings': dict(self._file_mappings)
            }

            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Created migration backup with {len(backup_files)} files")
            return backup_path

        except Exception as e:
            raise MigrationError(
                f"Failed to create migration backup: {e}",
                migration_step="backup_creation",
                cause=e
            )

    def _get_default_migration_steps(self) -> Dict[str, MigrationStep]:
        """Get default migration steps for the project reorganization."""
        return {
            'backup': MigrationStep(
                name='backup',
                description='Create backup of current project state',
                function=self._create_full_backup,
                rollback_function=self._restore_from_backup,
                critical=True
            ),
            'reorganize_files': MigrationStep(
                name='reorganize_files',
                description='Reorganize files according to new directory structure',
                function=self.reorganize_files,
                rollback_function=self._restore_file_organization,
                critical=True
            ),
            'update_imports': MigrationStep(
                name='update_imports',
                description='Update import statements in Python files',
                function=self._update_all_imports,
                rollback_function=self._restore_original_imports,
                dependencies=['reorganize_files']
            ),
            'validate_structure': MigrationStep(
                name='validate_structure',
                description='Validate the new project structure',
                function=self._validate_new_structure,
                dependencies=['reorganize_files', 'update_imports']
            ),
            'cleanup': MigrationStep(
                name='cleanup',
                description='Clean up temporary files and old structure',
                function=self._cleanup_migration_artifacts,
                dependencies=['validate_structure']
            )
        }

    def _define_file_mappings(self) -> Dict[str, str]:
        """Define file mappings for reorganization."""
        return {
            # Core modules reorganization
            'agents.py': 'decentralized-ai-simulation/src/core/agents.py',
            'database.py': 'decentralized-ai-simulation/src/core/database.py',
            'simulation.py': 'decentralized-ai-simulation/src/core/simulation.py',
            'decentralized_ai_simulation.py': 'decentralized-ai-simulation/src/core/decentralized_ai_simulation.py',

            # Utility modules reorganization
            'config_loader.py': 'decentralized-ai-simulation/src/config/config_loader.py',
            'logging_setup.py': 'decentralized-ai-simulation/src/utils/logging_setup.py',
            'monitoring.py': 'decentralized-ai-simulation/src/utils/monitoring.py',
            'render_mermaid_diagrams.py': 'decentralized-ai-simulation/src/utils/render_mermaid_diagrams.py',

            # UI modules reorganization
            'streamlit_app.py': 'decentralized-ai-simulation/src/ui/streamlit_app.py',
            'api_server.py': 'decentralized-ai-simulation/src/ui/api_server.py',

            # Test reorganization
            'tests/': 'decentralized-ai-simulation/tests/',
            'test_*.py': 'decentralized-ai-simulation/tests/unit/',

            # Documentation reorganization
            '*.md': 'decentralized-ai-simulation/docs/',
            'design.md': 'decentralized-ai-simulation/docs/design.md',

            # Script reorganization
            'scripts/': 'decentralized-ai-simulation/scripts/',
            '*.sh': 'decentralized-ai-simulation/scripts/',
            '*.bat': 'decentralized-ai-simulation/scripts/',
            '*.ps1': 'decentralized-ai-simulation/scripts/',

            # Configuration reorganization
            'config.yaml': 'decentralized-ai-simulation/config/config.yaml',
            '.env*': 'decentralized-ai-simulation/config/',
        }

    def _validate_migration_dependencies(self) -> None:
        """Validate that migration step dependencies are satisfied."""
        for step_name, step in self._migration_steps.items():
            for dep in step.dependencies:
                if dep not in self._migration_steps:
                    raise MigrationError(
                        f"Migration step '{step_name}' has invalid dependency '{dep}'",
                        migration_step="dependency_validation"
                    )

    def _get_execution_order(self) -> List[str]:
        """Get migration steps in proper execution order considering dependencies."""
        executed = set()
        execution_order = []

        def can_execute(step_name: str) -> bool:
            """Check if a step can be executed (all dependencies satisfied)."""
            if step_name in executed:
                return False

            step = self._migration_steps[step_name]
            for dep in step.dependencies:
                if dep not in executed:
                    return False
            return True

        def get_next_executable() -> Optional[str]:
            """Get next step that can be executed."""
            for step_name in self._migration_steps:
                if can_execute(step_name):
                    return step_name
            return None

        # Topological sort with dependency resolution
        while len(executed) < len(self._migration_steps):
            next_step = get_next_executable()
            if next_step is None:
                remaining = set(self._migration_steps.keys()) - executed
                raise MigrationError(
                    f"Cannot resolve migration dependencies. Remaining steps: {remaining}",
                    migration_step="dependency_resolution"
                )

            executed.add(next_step)
            execution_order.append(next_step)

        return execution_order

    def _file_path_to_import(self, file_path: str) -> Optional[str]:
        """Convert file path to Python import path."""
        try:
            path_obj = Path(file_path)

            # Handle Python files
            if path_obj.suffix == '.py':
                # Remove .py extension
                import_path = path_obj.with_suffix('')

                # Convert to import notation
                parts = import_path.parts
                if 'decentralized-ai-simulation' in parts:
                    # Extract package structure
                    idx = parts.index('decentralized-ai-simulation')
                    if idx + 1 < len(parts):
                        relative_parts = parts[idx + 1:]
                        return '.'.join(relative_parts)

            return None
        except Exception:
            return None

    def _update_import_in_content(self, content: str, old_import: str, new_import: str) -> str:
        """Update import statements in file content."""
        # Pattern to match import statements
        import_patterns = [
            rf'^import\s+{re.escape(old_import)}\b',
            rf'^from\s+{re.escape(old_import)}\b',
            rf'\bimport\s+{re.escape(old_import)}\b',
            rf'\bfrom\s+{re.escape(old_import)}\b'
        ]

        updated_content = content

        for pattern in import_patterns:
            def replace_import(match):
                line = match.group(0)
                return line.replace(old_import, new_import)

            updated_content = re.sub(pattern, replace_import, updated_content, flags=re.MULTILINE)

        return updated_content

    def _update_all_imports(self) -> bool:
        """Update import statements in all Python files."""
        try:
            updated_count = 0

            # Find all Python files in the project
            python_files = list(self.project_root.rglob("*.py"))

            for py_file in python_files:
                if self.update_import_statements(py_file):
                    updated_count += 1

            logger.info(f"Updated imports in {updated_count} Python files")
            return True

        except Exception as e:
            raise MigrationError(
                f"Failed to update all imports: {e}",
                migration_step="import_update",
                cause=e
            )

    def _validate_new_structure(self) -> bool:
        """Validate that the new project structure is correct."""
        try:
            # Check that all expected directories exist
            expected_dirs = [
                'decentralized-ai-simulation/src',
                'decentralized-ai-simulation/src/core',
                'decentralized-ai-simulation/src/utils',
                'decentralized-ai-simulation/src/config',
                'decentralized-ai-simulation/src/ui',
                'decentralized-ai-simulation/tests',
                'decentralized-ai-simulation/docs',
                'decentralized-ai-simulation/scripts'
            ]

            missing_dirs = []
            for dir_path in expected_dirs:
                full_path = self.project_root / dir_path
                if not full_path.exists():
                    missing_dirs.append(dir_path)

            if missing_dirs:
                raise MigrationError(f"Missing expected directories: {missing_dirs}")

            # Check that files are in correct locations
            misplaced_files = []
            for old_path, new_path in self._file_mappings.items():
                old_file = self.project_root / old_path
                new_file = self.project_root / new_path

                # If old location still has file but new location doesn't
                if old_file.exists() and not new_file.exists():
                    misplaced_files.append(old_path)

            if misplaced_files:
                logger.warning(f"Files still in old locations: {misplaced_files}")

            logger.info("Project structure validation completed")
            return True

        except Exception as e:
            if isinstance(e, MigrationError):
                raise
            raise MigrationError(
                f"Structure validation failed: {e}",
                migration_step="validation",
                cause=e
            )

    def _cleanup_migration_artifacts(self) -> bool:
        """Clean up temporary files and migration artifacts."""
        try:
            # Remove old files that have been moved
            removed_count = 0

            for old_path, new_path in self._file_mappings.items():
                old_file = self.project_root / old_path

                # Only remove if corresponding new file exists
                new_file = self.project_root / new_path
                if old_file.exists() and new_file.exists():
                    if old_file.is_file():
                        old_file.unlink()
                        removed_count += 1
                    elif old_file.is_dir():
                        shutil.rmtree(old_file)
                        removed_count += 1

            logger.info(f"Cleaned up {removed_count} old files/directories")
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup migration artifacts: {e}")
            raise MigrationError(
                f"Migration cleanup failed: {e}",
                migration_step="cleanup",
                cause=e
            )

    def _create_full_backup(self) -> bool:
        """Create a full backup of the project."""
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_root / f"full_backup_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)

            # Copy project files (excluding common ignore patterns)
            ignore_patterns = ['__pycache__', '.git', '*.pyc', '.DS_Store', 'node_modules']

            for item in self.project_root.iterdir():
                if item.name not in ignore_patterns and not any(pattern in item.name for pattern in ignore_patterns):
                    if item.is_file():
                        shutil.copy2(item, backup_path / item.name)
                    elif item.is_dir():
                        dest_dir = backup_path / item.name
                        shutil.copytree(item, dest_dir, dirs_exist_ok=True)

            logger.info(f"Created full backup at {backup_path}")
            return True

        except Exception as e:
            raise MigrationError(
                f"Full backup creation failed: {e}",
                migration_step="backup",
                cause=e
            )

    def _restore_from_backup(self) -> bool:
        """Restore project from backup."""
        # This would be implemented to restore from the most recent backup
        logger.info("Restoring from backup")
        return True

    def _restore_file_organization(self) -> bool:
        """Restore original file organization."""
        logger.info("Restoring original file organization")
        return True

    def _restore_original_imports(self) -> bool:
        """Restore original import statements."""
        logger.info("Restoring original import statements")
        return True

    def get_migration_status(self, migration_id: str) -> Dict[str, Any]:
        """
        Get the status of a migration.

        Args:
            migration_id: ID of the migration

        Returns:
            Dictionary with migration status information
        """
        try:
            if not self.migration_log_path.exists():
                return {'error': 'No migration log found'}

            with open(self.migration_log_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)

            if plan_data['migration_id'] != migration_id:
                return {'error': f'Migration ID not found: {migration_id}'}

            # Calculate status
            completed_steps = len(self._completed_steps)
            total_steps = len(self._migration_steps)

            status = {
                'migration_id': migration_id,
                'migration_name': plan_data['migration_name'],
                'status': MigrationStatus.COMPLETED.value if completed_steps == total_steps else MigrationStatus.IN_PROGRESS.value,
                'steps_completed': completed_steps,
                'total_steps': total_steps,
                'completed_steps': list(self._completed_steps),
                'created_at': plan_data['created_at'],
                'current_migration': self._current_migration == migration_id
            }

            return status

        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {'error': str(e)}