#!/usr/bin/env python3
"""
Script to fix all import statements in project files after reorganization.
This script will systematically update all broken imports identified in the scan.
"""

import os
import sys
import re
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, '/home/tanmay/Desktop/build')

def backup_file(file_path):
    """Create a backup of the file before modifying it."""
    backup_path = str(file_path) + '.bak'
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"  Created backup: {backup_path}")
        return True
    except Exception as e:
        print(f"  Failed to create backup for {file_path}: {e}")
        return False

def fix_imports_in_file(file_path):
    """Fix all import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Import pattern mappings (old -> new)
        import_patterns = [
            # Core modules
            ('from agents import', 'from src.core.agents import'),
            ('from database import', 'from src.core.database import'),
            ('from simulation import', 'from src.core.simulation import'),

            # Config modules
            ('from config_loader import', 'from src.config.config_loader import'),

            # Utils modules
            ('from logging_setup import', 'from src.utils.logging_setup import'),
            ('from monitoring import', 'from src.utils.monitoring import'),

            # Backend modules
            ('from data_transformers import', 'from backend.data_transformers import'),
            ('from main import', 'from backend.main import'),
        ]

        # Apply all import fixes
        for old_pattern, new_pattern in import_patterns:
            content = content.replace(old_pattern, new_pattern)

        # Write back if changed
        if content != original_content:
            # Create backup first
            backup_file(file_path)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, original_content, content

        return False, None, None

    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False, None, None

def main():
    print("Starting comprehensive import fixes...")
    print("="*80)

    # Files that need import fixes (from our previous scan)
    files_to_fix = [
        # Backend files
        'backend/test_integration.py',
        'backend/test_performance.py',
        'backend/data_transformers.py',
        'backend/main.py',

        # Test files
        'tests/test_agents.py',
        'tests/test_database.py',
        'tests/test_simulation.py',

        # Script files
        'decentralized-ai-simulation/scripts/test_env_override.py',
        'decentralized-ai-simulation/scripts/test_db_pooling.py',
        'decentralized-ai-simulation/scripts/test_config.py',
        'decentralized-ai-simulation/scripts/test_caching.py',
        'decentralized-ai-simulation/scripts/utils.py',
        'decentralized-ai-simulation/scripts/testing/benchmark_performance.py',
        'decentralized-ai-simulation/scripts/runtime/decentralized_ai_simulation.py',
        'decentralized-ai-simulation/scripts/runtime/streamlit_app.py',

        # Test files in new structure
        'decentralized-ai-simulation/tests/unit/test_agents.py',
        'decentralized-ai-simulation/tests/unit/test_env_override.py',
        'decentralized-ai-simulation/tests/unit/test_db_pooling.py',
        'decentralized-ai-simulation/tests/unit/test_config.py',
        'decentralized-ai-simulation/tests/unit/test_caching.py',
        'decentralized-ai-simulation/tests/unit/test_database.py',
        'decentralized-ai-simulation/tests/unit/test_simulation.py',
        'decentralized-ai-simulation/tests/integration/test_integration.py',
        'decentralized-ai-simulation/tests/integration/test_api_integration.py',

        # Core and utils files that need internal import fixes
        'decentralized-ai-simulation/src/utils/monitoring.py',
        'decentralized-ai-simulation/src/config/config_manager.py',
        'decentralized-ai-simulation/src/ui/api_server.py',
        'decentralized-ai-simulation/src/ui/streamlit_app.py',
        'decentralized-ai-simulation/src/core/database/ledger_manager.py',
        'decentralized-ai-simulation/src/core/simulation/simulation_engine.py',
        'decentralized-ai-simulation/src/core/agents/agent_manager.py',
        'decentralized-ai-simulation/src/utils/logging/logger.py',
        'decentralized-ai-simulation/src/utils/monitoring/monitor.py',
    ]

    fixed_count = 0
    error_count = 0

    for file_path in files_to_fix:
        full_path = Path('/home/tanmay/Desktop/build') / file_path
        if full_path.exists():
            print(f"\nProcessing: {file_path}")
            success, old_content, new_content = fix_imports_in_file(full_path)

            if success:
                fixed_count += 1
                print(f"  ✓ Fixed imports in {file_path}")
            else:
                print(f"  - No changes needed in {file_path}")
        else:
            print(f"  ✗ File not found: {file_path}")
            error_count += 1

    print("\n" + "="*80)
    print("IMPORT FIX SUMMARY")
    print("="*80)
    print(f"Files processed: {len(files_to_fix)}")
    print(f"Files fixed: {fixed_count}")
    print(f"Files with errors: {error_count}")
    print(f"Success rate: {(fixed_count / len(files_to_fix) * 100):.1f}%")

    print(f"\nNext steps:")
    print("1. Run tests to verify all imports work correctly")
    print("2. Check for any remaining import issues")
    print("3. Remove backup files (.bak) if everything works")

if __name__ == "__main__":
    main()