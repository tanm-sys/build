#!/usr/bin/env python3
"""Test script for configuration loader."""

import os
import tempfile
from src.config.config_loader import ConfigLoader

def test_config_loading():
    # Test with existing config
    print("Testing with existing config.yaml...")
    config_loader = ConfigLoader()
    print(f"Environment: {config_loader.get('environment')}")
    print(f"Database path: {config_loader.get('database.path')}")
    
    # Test with non-existing config file
    print("\nTesting with non-existing config file...")
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp:
        tmp_path = tmp.name
    try:
        config_loader = ConfigLoader(config_path=tmp_path)
        print("Config keys:", list(config_loader.config.keys()))
        print(f"Environment: {config_loader.get('environment')}")
        print(f"Database path: {config_loader.get('database.path')}")
    except Exception as e:
        print("Error:", e)
        print("Config keys:", list(config_loader.config.keys()))
        raise
    finally:
        os.unlink(tmp_path)
    
    # Test is_production and is_development
    print(f"\nIs production: {config_loader.is_production()}")
    print(f"Is development: {config_loader.is_development()}")

if __name__ == '__main__':
    test_config_loading()