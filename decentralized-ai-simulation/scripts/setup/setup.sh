#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Project Setup Script
# =============================================================================
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
# =============================================================================

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/.venv"
LOG_FILE="$PROJECT_ROOT/setup.log"
PYTHON_CMD="python3"
VERBOSE=false
FORCE_REINSTALL=false
SKIP_TESTS=false
DEV_MODE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    case "$level" in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        "DEBUG")
            if [ "$VERBOSE" = true ]; then
                echo -e "${BLUE}[DEBUG]${NC} $message"
            fi
            ;;
    esac
}

show_help() {
    cat << EOF
Decentralized AI Simulation - Setup Script

USAGE:
    ./setup.sh [OPTIONS]

OPTIONS:
    -h, --help          Show this help message and exit
    -v, --verbose       Enable verbose output for debugging
    -f, --force         Force reinstall even if virtual environment exists
    -p, --python PATH   Specify Python executable path (default: python3)
    --skip-tests        Skip running initial tests after setup
    --dev               Setup for development mode (includes additional tools)

EXAMPLES:
    ./setup.sh                          # Standard setup
    ./setup.sh --verbose --dev          # Development setup with verbose output
    ./setup.sh --force --python python3.11  # Force reinstall with specific Python

DESCRIPTION:
    This script performs a complete setup of the decentralized AI simulation
    environment including:
    
    1. Python virtual environment creation and activation
    2. Installation of all required dependencies
    3. Configuration file initialization
    4. Database setup and initialization
    5. Initial health checks and validation
    6. Optional test suite execution

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
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        log "INFO" "Installing dependencies from requirements.txt..."
        pip install -r "$PROJECT_ROOT/requirements.txt"
    else
        log "ERROR" "requirements.txt not found in $PROJECT_ROOT"
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
# Main Setup Function
# =============================================================================

main() {
    log "INFO" "Starting Decentralized AI Simulation setup..."
    log "INFO" "Project root: $PROJECT_ROOT"
    log "INFO" "Log file: $LOG_FILE"
    
    # Initialize log file
    echo "Setup started at $(date)" > "$LOG_FILE"
    
    check_prerequisites
    create_virtual_environment
    
    # Activate virtual environment for remaining steps
    source "$VENV_DIR/bin/activate"
    
    install_dependencies
    setup_configuration
    initialize_database
    run_health_checks
    run_initial_tests
    
    log "INFO" "Setup completed successfully!"
    log "INFO" ""
    log "INFO" "Next steps:"
    log "INFO" "1. Activate the virtual environment: source .venv/bin/activate"
    log "INFO" "2. Run the simulation: ./run.sh"
    log "INFO" "3. Run tests: ./test.sh"
    log "INFO" "4. Start the UI: ./run.sh --ui"
    log "INFO" ""
    log "INFO" "For more information, see README.md"
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
