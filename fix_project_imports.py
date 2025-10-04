#!/usr/bin/env python3
"""
Script to fix import statements in project files after reorganization.
Focuses only on project files, not virtual environment files.
"""

import os
import sys
import re
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, '/home/tanmay/Desktop/build')

def is_project_file(file_path):
    """Check if a file is part of the project (not virtual environment)."""
    path_str = str(file_path)
    return not any(x in path_str for x in [
        'venv/', 'lib/python', 'site-packages/', '__pycache__/',
        'node_modules/', '.git/', 'test_env/', 'backend_test_env/',
        'config_test_env/', 'security-audit-env/'
    ])

def scan_project_imports():
    """Scan only project Python files for import statements."""
    python_files = []

    # Walk through project directories only
    project_root = Path('/home/tanmay/Desktop/build')
    for py_file in project_root.rglob("*.py"):
        if is_project_file(py_file):
            python_files.append(py_file)

    return python_files

def analyze_project_imports(file_path):
    """Analyze import statements in a project Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        imports = []
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append((i, line))

        return imports

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def identify_broken_imports(imports):
    """Identify imports that need to be updated based on reorganization."""
    broken_imports = []

    # Patterns for old vs new import styles
    import_patterns = {
        # Old style -> New style mappings
        'from agents import': 'from src.core.agents import',
        'from database import': 'from src.core.database import',
        'from simulation import': 'from src.core.simulation import',
        'from config_loader import': 'from src.config.config_loader import',
        'from logging_setup import': 'from src.utils.logging_setup import',
        'from monitoring import': 'from src.utils.monitoring import',
        'from data_transformers import': 'from backend.data_transformers import',
        'from main import': 'from backend.main import',
    }

    for line_num, import_line in imports:
        for old_pattern, new_pattern in import_patterns.items():
            if old_pattern in import_line and new_pattern not in import_line:
                broken_imports.append((line_num, import_line, old_pattern, new_pattern))

    return broken_imports

def fix_import_line(import_line, old_pattern, new_pattern):
    """Fix a single import line."""
    return import_line.replace(old_pattern, new_pattern)

def main():
    print("Scanning project files for import issues...")
    python_files = scan_project_imports()
    print(f"Found {len(python_files)} project Python files")

    # Find files with broken imports
    files_with_issues = {}

    for py_file in python_files:
        imports = analyze_project_imports(py_file)
        broken_imports = identify_broken_imports(imports)

        if broken_imports:
            files_with_issues[py_file] = broken_imports

    # Display results
    print(f"\nFound {len(files_with_issues)} files with import issues:")
    print("="*80)

    for file_path, issues in files_with_issues.items():
        rel_path = os.path.relpath(file_path, '/home/tanmay/Desktop/build')
        print(f"\n{rel_path}:")
        for line_num, old_import, old_pattern, new_pattern in issues:
            new_import = fix_import_line(old_import, old_pattern, new_pattern)
            print(f"  {line_num:3}: {old_import}")
            print(f"       -> {new_import}")

    # Summary
    total_issues = sum(len(issues) for issues in files_with_issues.values())
    print(f"\nSummary:")
    print(f"Files with import issues: {len(files_with_issues)}")
    print(f"Total import issues found: {total_issues}")

    return files_with_issues

if __name__ == "__main__":
    files_with_issues = main()