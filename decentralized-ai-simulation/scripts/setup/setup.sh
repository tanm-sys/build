#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Enhanced Project Setup Script
# =============================================================================
# Modern bash script for comprehensive development environment setup with
# enhanced validation, cross-platform compatibility, and detailed progress tracking.
#
# This script sets up the complete development environment for the
# decentralized AI simulation project including virtual environment,
# dependencies, configuration, database initialization, and health checks.
#
# Usage: ./setup.sh [OPTIONS]
# Options:
#   -h, --help          Show this help message
#   -v, --verbose       Enable verbose output
#   -f, --force         Force reinstall even if environment exists
#   -p, --python PATH   Specify Python executable path (default: python3)
#   --skip-tests        Skip running initial tests after setup
#   --dev               Setup for development (includes dev dependencies)
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - System requirements not met
#   4 - Installation failed
# =============================================================================

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures
shopt -s globstar   # Enable globstar for recursive globbing
shopt -s extglob    # Enable extended globbing patterns

# Enhanced script configuration with robust path resolution
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly VENV_DIR="${PROJECT_ROOT}/.venv"
readonly LOG_DIR="${PROJECT_ROOT}/logs"
readonly LOG_FILE="${LOG_DIR}/setup.log"
readonly CONFIG_DIR="${PROJECT_ROOT}/config"

# Setup configuration with validation arrays
readonly DEFAULT_PYTHON_CMD="python3"
readonly MIN_PYTHON_VERSION="3.8"
readonly SETUP_TIMEOUT=1800  # 30 minutes
readonly RETRY_ATTEMPTS=3
readonly RETRY_DELAY=5

# Configuration variables with defaults
PYTHON_CMD="${DEFAULT_PYTHON_CMD}"
VERBOSE=false
FORCE_REINSTALL=false
SKIP_TESTS=false
DEV_MODE=false

# Enhanced color palette for better visual feedback
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly BOLD_RED='\033[1;31m'
readonly BOLD_GREEN='\033[1;32m'
readonly BOLD_YELLOW='\033[1;33m'
readonly BOLD_BLUE='\033[1;34m'
readonly BOLD_CYAN='\033[1;36m'
readonly NC='\033[0m' # No Color

# Global variables for tracking setup state
PYTHON_VERSION=""
VIRTUAL_ENV_ACTIVE=false
SETUP_START_TIME=""

# =============================================================================
# Enhanced Utility Functions
# =============================================================================

# Enhanced logging function with structured output and setup tracking
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Create log directory if it doesn't exist
    mkdir -p "${LOG_DIR}"

    # Log to file with structured format
    printf '[%s] [%s] %s\n' "$timestamp" "$level" "$message" >> "$LOG_FILE"

    # Console output with enhanced colors and formatting
    case "$level" in
        "INFO")
            printf '%b[%s]%b %s\n' "${GREEN}" "$level" "${NC}" "$message"
            ;;
        "WARN")
            printf '%b[%s]%b %s\n' "${YELLOW}" "$level" "${NC}" "$message"
            ;;
        "ERROR")
            printf '%b[%s]%b %s\n' "${RED}" "$level" "${NC}" "$message"
            ;;
        "DEBUG")
            if [[ "$VERBOSE" == true ]]; then
                printf '%b[%s]%b %s\n' "${BLUE}" "$level" "${NC}" "$message"
            fi
            ;;
        "SUCCESS")
            printf '%b[%s]%b %s\n' "${BOLD_GREEN}" "$level" "${NC}" "$message"
            ;;
        "SETUP")
            printf '%b[%s]%b %s\n' "${CYAN}" "$level" "${NC}" "$message"
            ;;
    esac
}

# Enhanced Python path validation with version checking and compatibility
validate_python_path() {
    local python_cmd="$1"

    if [[ -n "$python_cmd" ]]; then
        # Check if Python executable exists
        if ! command -v "$python_cmd" &> /dev/null; then
            log "ERROR" "Python executable not found: $python_cmd"
            log "INFO" "Please ensure Python is installed and available in PATH"
            exit 2
        fi

        # Get detailed Python version information
        local python_version_output
        python_version_output=$("$python_cmd" --version 2>&1) || {
            log "ERROR" "Failed to get Python version for: $python_cmd"
            exit 2
        }

        # Extract version number (handle different formats)
        local python_version
        python_version=$(echo "$python_version_output" | grep -oE '[0-9]+\.[0-9]+' | head -1)

        if [[ -z "$python_version" ]]; then
            log "ERROR" "Cannot determine Python version for: $python_cmd"
            exit 2
        fi

        # Compare versions properly
        local major_version
        major_version=$(echo "$python_version" | cut -d'.' -f1)

        if [[ "$major_version" -lt 3 ]]; then
            log "ERROR" "Python 3+ is required, found Python $python_version"
            log "INFO" "Please install Python 3.8 or higher"
            exit 2
        fi

        # Check for minimum version
        if [[ "$python_version" < "$MIN_PYTHON_VERSION" ]]; then
            log "WARN" "Python $python_version detected, recommended version is $MIN_PYTHON_VERSION+"
        fi

        PYTHON_VERSION="$python_version"
        log "DEBUG" "Validated Python executable: $python_cmd (version $python_version_output)"
    fi
}

# Function to check if command exists and is executable
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to retry a command with exponential backoff
retry_command() {
    local command="$1"
    local max_attempts="$2"
    local delay="$3"
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        log "DEBUG" "Attempt $attempt/$max_attempts: $command"

        if eval "$command"; then
            return 0
        fi

        if [[ $attempt -lt $max_attempts ]]; then
            log "WARN" "Command failed, retrying in ${delay}s..."
            sleep "$delay"
            delay=$((delay * 2))  # Exponential backoff
        fi

        ((attempt++))
    done

    log "ERROR" "Command failed after $max_attempts attempts: $command"
    return 1
}

# Enhanced help display with better formatting and setup guidance
show_help() {
    local script_name
    script_name=$(basename "${BASH_SOURCE[0]}")

    cat << EOF
${BOLD_BLUE}Decentralized AI Simulation - Enhanced Setup Script${NC}

${BOLD_YELLOW}USAGE:${NC}
    $script_name [OPTIONS]

${BOLD_YELLOW}OPTIONS:${NC}
    ${BOLD_GREEN}-h, --help${NC}          Show this help message and exit
    ${BOLD_GREEN}-v, --verbose${NC}       Enable verbose output for debugging
    ${BOLD_GREEN}-f, --force${NC}         Force reinstall even if virtual environment exists
    ${BOLD_GREEN}-p, --python PATH${NC}   Specify Python executable path (default: python3)
    ${BOLD_GREEN}--skip-tests${NC}        Skip running initial tests after setup
    ${BOLD_GREEN}--dev${NC}               Setup for development mode (includes additional tools)

${BOLD_YELLOW}EXAMPLES:${NC}
    $script_name                           # Standard setup
    $script_name --verbose --dev           # Development setup with verbose output
    $script_name --force --python python3.11  # Force reinstall with specific Python

${BOLD_YELLOW}DESCRIPTION:${NC}
    This script performs a complete setup of the decentralized AI simulation
    environment including:

    1. ${BOLD_CYAN}Python virtual environment creation and activation${NC}
    2. ${BOLD_CYAN}Installation of all required dependencies${NC}
    3. ${BOLD_CYAN}Configuration file initialization${NC}
    4. ${BOLD_CYAN}Database setup and initialization${NC}
    5. ${BOLD_CYAN}Initial health checks and validation${NC}
    6. ${BOLD_CYAN}Optional test suite execution${NC}

${BOLD_YELLOW}REQUIREMENTS:${NC}
    • Python $MIN_PYTHON_VERSION or higher
    • Internet connection for package downloads
    • Sufficient disk space (recommended: 1GB+)
    • Virtual environment support

${BOLD_YELLOW}EXIT CODES:${NC}
    0 - Success
    1 - General error
    2 - Invalid arguments
    3 - System requirements not met
    4 - Installation failed

${BOLD_BLUE}For more information, see README.md${NC}
EOF
}

check_prerequisites() {
    log "INFO" "Checking system prerequisites..."
    
    # Check if Python is available
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        log "ERROR" "Python ($PYTHON_CMD) is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python version
    local python_version=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log "INFO" "Found Python version: $python_version"
    
    # Check if pip is available
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        log "ERROR" "pip is not available for $PYTHON_CMD"
        exit 1
    fi
    
    # Check if venv module is available
    if ! $PYTHON_CMD -m venv --help &> /dev/null; then
        log "ERROR" "venv module is not available for $PYTHON_CMD"
        log "INFO" "Try installing python3-venv package"
        exit 1
    fi
    
    log "INFO" "All prerequisites satisfied"
}

create_virtual_environment() {
    log "INFO" "Setting up Python virtual environment..."
    
    if [ -d "$VENV_DIR" ] && [ "$FORCE_REINSTALL" = false ]; then
        log "WARN" "Virtual environment already exists at $VENV_DIR"
        log "INFO" "Use --force to reinstall or remove the directory manually"
        return 0
    fi
    
    if [ -d "$VENV_DIR" ] && [ "$FORCE_REINSTALL" = true ]; then
        log "INFO" "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    log "INFO" "Creating virtual environment at $VENV_DIR"
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    log "INFO" "Upgrading pip..."
    pip install --upgrade pip
    
    log "INFO" "Virtual environment created and activated successfully"
}

install_dependencies() {
    log "INFO" "Installing project dependencies..."
    
    # Ensure we're in the virtual environment
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        log "ERROR" "Virtual environment is not activated"
        exit 1
    fi
    
    # Install main dependencies
    if [ -f "$PROJECT_ROOT/decentralized-ai-simulation/config/requirements.txt" ]; then
        log "INFO" "Installing dependencies from requirements.txt..."
        if ! pip install -r "$PROJECT_ROOT/decentralized-ai-simulation/config/requirements.txt"; then
            log "ERROR" "Failed to install dependencies from requirements.txt"
            exit 1
        fi
    else
        log "ERROR" "requirements.txt not found in $PROJECT_ROOT/decentralized-ai-simulation/config/"
        exit 1
    fi
    
    # Install development dependencies if in dev mode
    if [ "$DEV_MODE" = true ]; then
        log "INFO" "Installing development dependencies..."
        pip install pytest-cov black flake8 mypy pre-commit
    fi
    
    log "INFO" "Dependencies installed successfully"
}

setup_configuration() {
    log "INFO" "Setting up configuration files..."
    
    # Check if config.yaml exists
    if [ ! -f "$PROJECT_ROOT/config.yaml" ]; then
        log "WARN" "config.yaml not found, it will be created automatically on first run"
    else
        log "INFO" "Configuration file config.yaml found"
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/logs"
    log "DEBUG" "Created logs directory"
    
    # Set up environment file template
    if [ ! -f "$PROJECT_ROOT/.env.example" ]; then
        cat > "$PROJECT_ROOT/.env.example" << EOF
# Environment Configuration Template
# Copy this file to .env and customize as needed

# Environment type (development, production)
ENVIRONMENT=development

# Database configuration
DATABASE_PATH=ledger.db
DATABASE_CONNECTION_POOL_SIZE=10

# Logging configuration
LOGGING_LEVEL=INFO
LOGGING_FILE=logs/simulation.log

# Simulation configuration
SIMULATION_DEFAULT_AGENTS=50
SIMULATION_DEFAULT_STEPS=100

# Monitoring configuration
MONITORING_HEALTH_CHECK_INTERVAL=30
MONITORING_ENABLE_PROMETHEUS=false
EOF
        log "INFO" "Created .env.example template file"
    fi
    
    log "INFO" "Configuration setup completed"
}

initialize_database() {
    log "INFO" "Initializing database..."
    
    # Ensure we're in the virtual environment
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        log "ERROR" "Virtual environment is not activated"
        exit 1
    fi
    
    # Test database initialization by importing the module
    python -c "
from database import DatabaseLedger
import os

# Initialize database
db = DatabaseLedger()
print('Database initialized successfully')

# Test basic operations
test_entry = {'id': 1, 'type': 'test', 'data': 'initialization_test'}
db.append_entry(test_entry)
entries = db.read_ledger()
print(f'Database test completed. Found {len(entries)} entries.')
" 2>&1 | while read line; do
        log "DEBUG" "DB Init: $line"
    done
    
    log "INFO" "Database initialization completed"
}

run_health_checks() {
    log "INFO" "Running initial health checks..."
    
    # Ensure we're in the virtual environment
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        log "ERROR" "Virtual environment is not activated"
        exit 1
    fi
    
    # Test core imports
    python -c "
import sys
print(f'Python version: {sys.version}')

# Test core imports
try:
    import mesa
    import ray
    import sqlite3
    import yaml
    import numpy as np
    import pandas as pd
    import streamlit
    import plotly
    print('✓ All core dependencies imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)

# Test project modules
try:
    from config_loader import get_config
    from logging_setup import get_logger
    from monitoring import get_monitoring
    from database import DatabaseLedger
    from agents import AnomalyAgent
    from simulation import Simulation
    print('✓ All project modules imported successfully')
except ImportError as e:
    print(f'✗ Project module import error: {e}')
    sys.exit(1)

print('✓ Health checks passed')
" 2>&1 | while read line; do
        log "INFO" "Health Check: $line"
    done
    
    if [ $? -eq 0 ]; then
        log "INFO" "All health checks passed successfully"
    else
        log "ERROR" "Health checks failed"
        exit 1
    fi
}

run_initial_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log "INFO" "Skipping initial tests as requested"
        return 0
    fi
    
    log "INFO" "Running initial test suite..."
    
    # Ensure we're in the virtual environment
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        log "ERROR" "Virtual environment is not activated"
        exit 1
    fi
    
    # Run tests
    if python -m pytest tests/ -v --tb=short; then
        log "INFO" "Initial tests passed successfully"
    else
        log "WARN" "Some tests failed, but setup can continue"
        log "INFO" "Run './test.sh' later to investigate test failures"
    fi
}

# =============================================================================
# Enhanced Main Setup Function
# =============================================================================

main() {
    local start_time
    start_time=$(date '+%Y-%m-%d %H:%M:%S')

    log "INFO" "Starting Decentralized AI Simulation setup at $start_time"
    log "INFO" "Script version: 2.0.0"
    log "INFO" "Process ID: $$"
    log "INFO" "Project root: $PROJECT_ROOT"
    log "INFO" "Python command: $PYTHON_CMD"
    log "INFO" "Development mode: $DEV_MODE"
    log "INFO" "Force reinstall: $FORCE_REINSTALL"

    # Initialize log file with comprehensive session header
    {
        echo "=========================================="
        echo "Setup session started at $start_time"
        echo "Project root: $PROJECT_ROOT"
        echo "Python command: $PYTHON_CMD"
        echo "Virtual environment: $VENV_DIR"
        echo "Log file: $LOG_FILE"
        echo "Development mode: $DEV_MODE"
        echo "Force reinstall: $FORCE_REINSTALL"
        echo "Skip tests: $SKIP_TESTS"
        echo "Verbose mode: $VERBOSE"
        echo "=========================================="
    } > "$LOG_FILE"

    # Core setup flow with comprehensive error handling
    local setup_success=true
    local setup_result=0

    # Phase 1: Prerequisites validation
    if check_prerequisites; then
        log "INFO" "Prerequisites validation completed"
    else
        log "ERROR" "Prerequisites validation failed"
        exit 3
    fi

    # Phase 2: Virtual environment setup
    if create_virtual_environment; then
        log "INFO" "Virtual environment setup completed"
    else
        log "ERROR" "Virtual environment setup failed"
        setup_success=false
        setup_result=4
    fi

    # Phase 3: Dependency installation
    if install_dependencies; then
        log "INFO" "Dependency installation completed"
    else
        log "ERROR" "Dependency installation failed"
        setup_success=false
        setup_result=4
    fi

    # Phase 4: Configuration setup
    if setup_configuration; then
        log "INFO" "Configuration setup completed"
    else
        log "ERROR" "Configuration setup failed"
        setup_success=false
        setup_result=4
    fi

    # Phase 5: Database initialization
    if initialize_database; then
        log "INFO" "Database initialization completed"
    else
        log "ERROR" "Database initialization failed"
        setup_success=false
        setup_result=4
    fi

    # Phase 6: Health validation
    if run_health_checks; then
        log "INFO" "Health checks completed"
    else
        log "ERROR" "Health checks failed"
        setup_success=false
        setup_result=4
    fi

    # Phase 7: Initial testing (optional)
    if [[ "$SKIP_TESTS" == false ]]; then
        if run_initial_tests; then
            log "INFO" "Initial tests completed"
        else
            log "WARN" "Initial tests had issues, but setup can continue"
        fi
    else
        log "INFO" "Skipping initial tests as requested"
    fi

    # Setup completion with detailed summary
    local end_time
    end_time=$(date '+%Y-%m-%d %H:%M:%S')

    if [[ $setup_success == true ]]; then
        log "SUCCESS" "Setup completed successfully at $end_time"
        log "INFO" "Total setup time: $(($(date -d "$end_time" +%s) - $(date -d "$start_time" +%s))) seconds"
        log "INFO" ""
        log "INFO" "Next steps:"
        log "INFO" "1. ${BOLD_GREEN}Activate the virtual environment:${NC} source $VENV_DIR/bin/activate"
        log "INFO" "2. ${BOLD_GREEN}Run the simulation:${NC} ./run.sh"
        log "INFO" "3. ${BOLD_GREEN}Run tests:${NC} ./test.sh"
        log "INFO" "4. ${BOLD_GREEN}Start the UI:${NC} ./run.sh --ui"
        log "INFO" ""
        log "INFO" "For more information, see README.md"
        exit 0
    else
        log "ERROR" "Setup failed with errors"
        log "INFO" "Check the log file for details: $LOG_FILE"
        exit $setup_result
    fi
}

# =============================================================================
# Command Line Argument Parsing
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--force)
            FORCE_REINSTALL=true
            shift
            ;;
        -p|--python)
            PYTHON_CMD="$2"
            validate_python_path "$PYTHON_CMD"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            log "INFO" "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main
