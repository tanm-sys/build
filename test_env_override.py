#!/usr/bin/env python3
"""Test script for environment variable overrides."""

import os
import tempfile
from config_loader import ConfigLoader

def test_environment_override():
    # Test environment variable override
    print("Testing environment variable override...")
    
    # Set environment variables
    os.environ['SIMULATION_DEFAULT_AGENTS'] = '200'
    os.environ['DATABASE_PATH'] = 'test_ledger.db'
    os.environ['ENVIRONMENT'] = 'production'
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as tmp:
        tmp_path = tmp.name
        tmp.write(b"""
environment: development
database:
  path: ledger.db
  timeout: 30
simulation:
  default_agents: 100
  default_steps: 50
""")
        tmp.flush()
    
    try:
        config_loader = ConfigLoader(config_path=tmp_path)
        
        # Test that environment variables override config file
        print(f"Environment: {config_loader.get('environment')} (should be production)")
        print(f"Database path: {config_loader.get('database.path')} (should be test_ledger.db)")
        print(f"Simulation agents: {config_loader.get('simulation.default_agents')} (should be 200)")
        
        # Clean up environment variables
        del os.environ['SIMULATION_DEFAULT_AGENTS']
        del os.environ['DATABASE_PATH']
        del os.environ['ENVIRONMENT']
        
    finally:
        os.unlink(tmp_path)

if __name__ == '__main__':
    test_environment_override()