#!/usr/bin/env python3
"""Test script for logging setup."""

import os
import tempfile
import logging
from unittest.mock import patch
from src.utils.logging_setup import setup_logging, get_logger

def test_logging_setup():
    """Test logging configuration with different log levels."""
    
    # Clear existing handlers to avoid interference
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
        log_file = tmp.name
    
    try:
        # Mock get_config to return our test values
        with patch('src.utils.logging_setup.get_config') as mock_get_config:
            mock_get_config.side_effect = lambda key, default=None: {
                'logging.level': 'DEBUG',
                'logging.file': log_file,
                'logging.max_bytes': 1000000,
                'logging.backup_count': 3,
                'logging.format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }.get(key, default)
            
            # Re-initialize logging with mocked config
            setup_logging()
        
        # Get a logger and test different log levels
        logger = get_logger('test_logger')
        
        # Test log messages at different levels
        logger.debug("This is a DEBUG message")
        logger.info("This is an INFO message")
        logger.warning("This is a WARNING message")
        logger.error("This is an ERROR message")
        
        # Verify log file was created and contains messages
        assert os.path.exists(log_file), "Log file was not created"
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Check that all log levels are present
        assert "DEBUG" in log_content, "DEBUG messages not found"
        assert "INFO" in log_content, "INFO messages not found"
        assert "WARNING" in log_content, "WARNING messages not found"
        assert "ERROR" in log_content, "ERROR messages not found"
        
        print("✓ Logging test passed - all levels and format correct")
        
    finally:
        # Clean up
        if os.path.exists(log_file):
            os.unlink(log_file)

def test_log_level_filtering():
    """Test that log level filtering works correctly."""
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
        log_file = tmp.name
    
    try:
        # Mock get_config to return WARNING level only
        with patch('src.utils.logging_setup.get_config') as mock_get_config:
            mock_get_config.side_effect = lambda key, default=None: {
                'logging.level': 'WARNING',
                'logging.file': log_file,
                'logging.max_bytes': 1000000,
                'logging.backup_count': 3,
                'logging.format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }.get(key, default)
            
            # Re-initialize logging with mocked config
            setup_logging()
        
        # Get a logger
        logger = get_logger('test_logger_filter')
        
        # Test log messages at different levels
        logger.debug("This DEBUG message should not appear")
        logger.info("This INFO message should not appear")
        logger.warning("This WARNING message should appear")
        logger.error("This ERROR message should appear")
        
        # Verify log file was created
        assert os.path.exists(log_file), "Log file was not created"
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Check that only WARNING and above levels are present
        assert "DEBUG" not in log_content, "DEBUG messages should not appear"
        assert "INFO" not in log_content, "INFO messages should not appear"
        assert "WARNING" in log_content, "WARNING messages should appear"
        assert "ERROR" in log_content, "ERROR messages should appear"
        
        print("✓ Log level filtering test passed")
        
    finally:
        # Clean up
        if os.path.exists(log_file):
            os.unlink(log_file)

if __name__ == "__main__":
    test_logging_setup()
    test_log_level_filtering()
    print("All logging tests passed!")