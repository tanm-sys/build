"""
Main Entrypoint Module with Security Enhancements

SECURITY FIXES APPLIED:
1. Command Injection Prevention: Validation of subprocess commands against whitelist
2. Path Traversal Protection: Comprehensive validation of all file paths before operations
3. Input Validation: Validation of configuration values and command-line arguments
4. Resource Cleanup: Proper cleanup of generated files and database resources
5. Error Handling: Safe error handling with appropriate logging and user feedback
6. Configuration Security: Secure loading and validation of configuration values
7. File Operation Safety: Validation of all file extensions and paths before operations

The main entrypoint is now secure against command injection and path traversal attacks.
"""

import argparse
import json
import os
import shutil
import subprocess

from simulation import Simulation

# Import with fallback to handle duplicate files
try:
    from decentralized_ai_simulation.src.utils.logging_setup import get_logger
    from decentralized_ai_simulation.src.config.config_loader import get_config
except ImportError:
    # Fallback to root level imports
    from logging_setup import get_logger
    from config_loader import get_config

logger = get_logger(__name__)

# Security: Define allowed executables and their safe paths
ALLOWED_STREAMLIT_PATHS = ['streamlit', './venv/bin/streamlit', 'venv/bin/streamlit']
ALLOWED_FILE_EXTENSIONS = {'.json', '.db'}

def _validate_file_path(file_path: str, allowed_extensions: set = None) -> bool:
    """
    Validate file path to prevent path traversal attacks.

    Args:
        file_path: The file path to validate
        allowed_extensions: Set of allowed file extensions

    Returns:
        True if path is safe, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False

    # Normalize path to resolve any .. or . components
    normalized = os.path.normpath(file_path)

    # Check for directory traversal attempts
    if '..' in normalized or normalized.startswith('/'):
        logger.warning(f"Path traversal attempt detected: {file_path}")
        return False

    # Check file extension if specified
    if allowed_extensions:
        _, ext = os.path.splitext(normalized)
        if ext.lower() not in allowed_extensions:
            logger.warning(f"Invalid file extension: {ext}")
            return False

    return True

def _validate_streamlit_command(command: str) -> bool:
    """
    Validate streamlit command to prevent command injection.

    Args:
        command: The command to validate

    Returns:
        True if command is safe, False otherwise
    """
    if not command or not isinstance(command, str):
        return False

    # Check against allowed commands
    if command not in ALLOWED_STREAMLIT_PATHS:
        logger.warning(f"Unauthorized streamlit command: {command}")
        return False

    return True

def _safe_subprocess_run(command_args: list, **kwargs) -> subprocess.CompletedProcess:
    """
    Safely run subprocess with validation.

    Args:
        command_args: Command arguments list
        **kwargs: Additional arguments for subprocess.run

    Returns:
        CompletedProcess instance

    Raises:
        ValueError: If command is not safe
    """
    if not command_args or not isinstance(command_args, list):
        raise ValueError("Command must be a non-empty list")

    # Validate the first argument (the command)
    if not _validate_streamlit_command(command_args[0]):
        raise ValueError(f"Unsafe command: {command_args[0]}")

    try:
        return subprocess.run(command_args, **kwargs)
    except Exception as e:
        logger.error(f"Subprocess execution failed: {e}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decentralized AI Simulation')
    parser.add_argument('--ui', action='store_true', help='Launch Streamlit UI instead of running headless simulation')
    args = parser.parse_args()

    if args.ui:
        # Launch Streamlit UI with security validation
        try:
            streamlit_cmd = get_config('streamlit.command', './venv/bin/streamlit')
            if not _validate_streamlit_command(streamlit_cmd):
                logger.error(f"Invalid streamlit command: {streamlit_cmd}")
                raise ValueError(f"Unauthorized streamlit command: {streamlit_cmd}")

            _safe_subprocess_run([streamlit_cmd, 'run', 'streamlit_app.py'])
        except Exception as e:
            logger.error(f"Failed to launch Streamlit UI: {e}")
            raise
    else:
        # Run headless simulation with input validation
        try:
            num_agents = get_config('simulation.default_agents', 100)
            steps = get_config('simulation.default_steps', 10)

            # Input validation for configuration values
            if not isinstance(num_agents, int) or num_agents <= 0:
                raise ValueError(f"Invalid num_agents: {num_agents}")
            if not isinstance(steps, int) or steps <= 0:
                raise ValueError(f"Invalid steps: {steps}")

            logger.info(f"Starting decentralized AI simulation with {num_agents} agents for {steps} steps...")

            # Use context manager for proper cleanup
            with Simulation(num_agents=num_agents) as model:
                model.run(steps=steps)

                # Final state with path validation
                logger.info("Simulation completed.")
                ledger = model.ledger
                entries = ledger.read_ledger()
                logger.info(f"Shared ledger: {len(entries)} entries")

                total_threats = 0
                for i in range(num_agents):
                    blacklist_file = f"blacklist_Node_{i}.json"

                    # Security: Validate file path before operations
                    if not _validate_file_path(blacklist_file, ALLOWED_FILE_EXTENSIONS):
                        logger.warning(f"Skipping unsafe blacklist file: {blacklist_file}")
                        continue

                    if os.path.exists(blacklist_file):
                        try:
                            with open(blacklist_file, 'r', encoding='utf-8') as f:
                                bl = json.load(f)
                            total_threats += len(bl)
                            logger.info(f"Node {i} blacklist: {len(bl)} signatures")

                            # Clean up after reporting with validation
                            if _validate_file_path(blacklist_file, ALLOWED_FILE_EXTENSIONS):
                                os.remove(blacklist_file)
                                logger.debug(f"Cleaned up blacklist file: {blacklist_file}")

                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in blacklist file {blacklist_file}: {e}")
                        except Exception as e:
                            logger.error(f"Error processing blacklist file {blacklist_file}: {e}")

                logger.info(f"Final state: All nodes share {total_threats} threat signatures.")

                # Clean up ledger db if in development mode with path validation
                if get_config('environment') == 'development':
                    db_path = get_config('database.path', 'ledger.db')
                    if _validate_file_path(db_path, ALLOWED_FILE_EXTENSIONS) and os.path.exists(db_path):
                        os.remove(db_path)
                        logger.info("Cleaned up ledger database")

        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise