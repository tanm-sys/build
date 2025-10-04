#!/usr/bin/env python3
"""
Script to scan for broken imports after file reorganization.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, '/home/tanmay/Desktop/build')

def scan_python_files():
    """Scan all Python files for import statements."""
    python_files = []

    # Walk through all directories to find Python files
    for root, dirs, files in os.walk('/home/tanmay/Desktop/build'):
        # Skip common directories that shouldn't be scanned
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files

def analyze_imports(file_path):
    """Analyze import statements in a Python file."""
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
        return []

def main():
    print("Scanning for Python files and their imports...")
    python_files = scan_python_files()
    print(f"Found {len(python_files)} Python files")

    # Group files by their location for better organization
    files_by_location = {}

    for py_file in python_files:
        rel_path = os.path.relpath(py_file, '/home/tanmay/Desktop/build')

        # Analyze imports
        imports = analyze_imports(py_file)

        if imports or True:  # Show all files for context
            if rel_path not in files_by_location:
                files_by_location[rel_path] = []

            files_by_location[rel_path].extend(imports)

    # Display results organized by file location
    print("\n" + "="*80)
    print("IMPORT ANALYSIS RESULTS")
    print("="*80)

    for file_path in sorted(files_by_location.keys()):
        imports = files_by_location[file_path]

        if imports:
            print(f"\n{file_path}:")
            for line_num, import_line in imports:
                print(f"  {line_num:3}: {import_line}")

    print(f"\nTotal Python files analyzed: {len(python_files)}")

    # Summary
    files_with_imports = len([f for f in files_by_location.values() if f])
    print(f"Files with import statements: {files_with_imports}")

if __name__ == "__main__":
    main()