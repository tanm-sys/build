#!/usr/bin/env bash

# =============================================================================
# Decentralized AI Simulation - Enhanced Project Setup Script
# =============================================================================
# Modern, robust bash script for comprehensive development environment setup with
# enhanced validation, cross-platform compatibility, and detailed progress tracking.
#
# This script sets up the complete development environment for the
# decentralized AI simulation project including virtual environment,
# dependencies, configuration, database initialization, and health checks.
#
# Features:
#   • Robust file validation with fallback mechanisms
#   • Cross-platform compatibility (Linux, macOS, WSL)
#   • Modern bash syntax and error handling
#   • Comprehensive logging and progress tracking
#   • Interactive fallback options for missing files
#   • Automatic dependency resolution
#
# Usage: ./setup.sh [OPTIONS]
# Options:
#   -h, --help              Show this help message and exit
#   -v, --verbose           Enable verbose output for debugging
#   -f, --force             Force reinstall even if environment exists
#   -p, --python PATH       Specify Python executable path (default: python3)
#   --skip-tests            Skip running initial tests after setup
#   --skip-deps             Skip dependency installation (for manual setup)
#   --dev                   Setup for development (includes dev dependencies)
#   --create-requirements   Create default requirements.txt if missing
#   --yes                   Answer 'yes' to all prompts (non-interactive)
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - System requirements not met
#   4 - Installation failed
#   5 - File validation failed
# =============================================================================

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures
shopt -s globstar   # Enable globstar for recursive globbing
shopt -s extglob    # Enable extended globbing patterns

# Enable extended error handling for better debugging
set -o errtrace     # Trap ERR from shell functions, command substitutions, etc

# Enhanced script configuration with robust path resolution and validation
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly VENV_DIR="${PROJECT_ROOT}/.venv"
readonly LOG_DIR="${PROJECT_ROOT}/logs"
readonly LOG_FILE="${LOG_DIR}/setup.log"
readonly CONFIG_DIR="${PROJECT_ROOT}/config"
readonly REQUIREMENTS_FILE="${PROJECT_ROOT}/config/requirements.txt"
readonly BACKUP_REQUIREMENTS_DIR="${PROJECT_ROOT}/scripts/setup/fallback-requirements"

# Setup configuration with validation arrays
readonly DEFAULT_PYTHON_CMD="python3"
readonly MIN_PYTHON_VERSION="3.8"
readonly SETUP_TIMEOUT=1800  # 30 minutes
readonly RETRY_ATTEMPTS=3
readonly RETRY_DELAY=5

# Enhanced configuration variables with defaults
PYTHON_CMD="${DEFAULT_PYTHON_CMD}"
VERBOSE=false
FORCE_REINSTALL=false
SKIP_TESTS=false
SKIP_DEPS=false
DEV_MODE=false
CREATE_REQUIREMENTS=false
NON_INTERACTIVE=false

# Global arrays for tracking missing files and validation status
MISSING_FILES=()
CRITICAL_FILES=(
    "${PROJECT_ROOT}/config"
    "${PROJECT_ROOT}/src"
    "${PROJECT_ROOT}/scripts"
)

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

# Enhanced file validation with detailed error reporting
validate_file_exists() {
    local file_path="$1"
    local file_description="$2"
    local is_critical="${3:-false}"

    if [[ ! -e "$file_path" ]]; then
        if [[ "$is_critical" == true ]]; then
            log "ERROR" "$file_description not found: $file_path"
            MISSING_FILES+=("$file_path:$file_description")
            return 1
        else
            log "WARN" "$file_description not found: $file_path"
            MISSING_FILES+=("$file_path:$file_description")
            return 0
        fi
    elif [[ ! -r "$file_path" ]]; then
        log "ERROR" "Cannot read $file_description: $file_path (permission denied)"
        return 1
    else
        log "DEBUG" "Validated $file_description: $file_path"
        return 0
    fi
}

# Enhanced directory validation with creation option
validate_directory() {
    local dir_path="$1"
    local dir_description="$2"
    local create_if_missing="${3:-false}"

    if [[ ! -d "$dir_path" ]]; then
        if [[ "$create_if_missing" == true ]]; then
            if mkdir -p "$dir_path" 2>/dev/null; then
                log "INFO" "Created $dir_description: $dir_path"
                return 0
            else
                log "ERROR" "Failed to create $dir_description: $dir_path"
                return 1
            fi
        else
            log "ERROR" "$dir_description not found: $dir_path"
            return 1
        fi
    else
        log "DEBUG" "Validated $dir_description: $dir_path"
        return 0
    fi
}

# Interactive prompt with fallback options
prompt_user() {
    local prompt_message="$1"
    local options=("${@:2}")

    if [[ "$NON_INTERACTIVE" == true ]]; then
        log "INFO" "Non-interactive mode: selecting first option"
        return 0
    fi

    echo
    log "INFO" "$prompt_message"

    if [[ ${#options[@]} -gt 0 ]]; then
        for i in "${!options[@]}"; do
            printf '%b[%d]%b %s\n' "${CYAN}" "$((i+1))" "${NC}" "${options[i]}"
        done
        echo
        read -p "$(printf '%bChoice [1-%d]:%b ' "${BOLD_YELLOW}" "${#options[@]}" "${NC}")" choice

        if [[ "$choice" =~ ^[0-9]+$ ]] && [[ $choice -ge 1 ]] && [[ $choice -le ${#options[@]} ]]; then
            return $((choice-1))
        else
            log "WARN" "Invalid choice, selecting first option"
            return 0
        fi
    else
        read -p "$(printf '%b[y/N]:%b ' "${BOLD_YELLOW}" "${NC}")" response
        [[ "$response" =~ ^[Yy][Ee][Ss]|[Yy]$ ]] && return 0 || return 1
    fi
}

# Create default requirements.txt with essential dependencies
create_default_requirements() {
    local requirements_path="$1"

    log "INFO" "Creating default requirements.txt with essential dependencies..."

    cat > "$requirements_path" << 'EOF'
# =============================================================================
# Default Requirements - Generated by setup.sh
# =============================================================================
# This file contains essential dependencies for the decentralized AI simulation.
# It was created automatically when the original requirements.txt was missing.
#
# To customize dependencies, edit this file and run setup again, or create
# your own requirements.txt file in the same location.

# Core scientific computing
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0

# Machine learning and AI
scikit-learn>=1.0.0
torch>=1.9.0
ray[default]>=1.0.0

# Agent-based modeling
mesa>=0.9.0

# Database and data processing
sqlalchemy>=1.4.0
alembic>=1.7.0

# Web framework and API
fastapi>=0.68.0
uvicorn[standard]>=0.15.0

# Configuration and utilities
pyyaml>=5.4.0
python-dotenv>=0.19.0
click>=8.0.0

# Logging and monitoring
structlog>=21.1.0

# Development dependencies (installed separately in dev mode)
# pytest>=6.2.0
# black>=21.7.0
# flake8>=3.9.0
# mypy>=0.910

# Optional: Visualization
# plotly>=5.0.0
# streamlit>=1.0.0
# matplotlib>=3.4.0

# Optional: Async support
# aiohttp>=3.7.0
# asyncio>=3.4.3

# Optional: Cryptography (for secure communications)
# cryptography>=3.4.0

# Optional: Performance monitoring
# psutil>=5.8.0

# Note: For production deployment, consider pinning exact versions
# and using a requirements.txt with hash verification for security.
EOF

    log "INFO" "Created default requirements.txt at: $requirements_path"
    log "INFO" "Please review and customize the dependencies as needed"
}

# Enhanced requirements.txt validation with fallback options
validate_requirements() {
    local requirements_path="$REQUIREMENTS_FILE"

    if [[ ! -f "$requirements_path" ]]; then
        log "WARN" "requirements.txt not found at: $requirements_path"

        if [[ "$CREATE_REQUIREMENTS" == true ]]; then
            create_default_requirements "$requirements_path"
            return 0
        fi

        if [[ "$NON_INTERACTIVE" == false ]]; then
            local options=(
                "Create default requirements.txt and continue"
                "Skip dependency installation"
                "Exit setup"
            )

            if prompt_user "requirements.txt is missing. What would you like to do?" "${options[@]}"; then
                # Option 1: Create default requirements.txt
                create_default_requirements "$requirements_path"
                return 0
            elif [[ $? -eq 1 ]]; then
                # Option 2: Skip dependency installation
                log "INFO" "Skipping dependency installation"
                SKIP_DEPS=true
                return 0
            else
                # Option 3: Exit setup
                log "ERROR" "Setup cannot continue without requirements.txt"
                exit 5
            fi
        else
            log "ERROR" "requirements.txt not found and non-interactive mode enabled"
            log "INFO" "Use --create-requirements to auto-create or provide requirements.txt"
            exit 5
        fi
    else
        log "INFO" "Found requirements.txt: $requirements_path"
        return 0
    fi
}

# Enhanced project structure validation
validate_project_structure() {
    log "INFO" "Validating project structure..."

    local validation_failed=false

    # Check critical directories
    for dir_info in "${CRITICAL_FILES[@]}"; do
        local dir_path="$dir_info"
        local dir_name=$(basename "$dir_path")

        if [[ ! -d "$dir_path" ]]; then
            log "ERROR" "Critical directory missing: $dir_path"
            validation_failed=true
        else
            log "DEBUG" "Validated directory: $dir_path"
        fi
    done

    # Check for requirements.txt specifically
    validate_requirements

    if [[ "$validation_failed" == true ]]; then
        log "ERROR" "Project structure validation failed"
        log "INFO" "Please ensure all required directories exist"
        exit 5
    fi

    log "INFO" "Project structure validation completed"
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
    ${BOLD_GREEN}-h, --help${NC}              Show this help message and exit
    ${BOLD_GREEN}-v, --verbose${NC}           Enable verbose output for debugging
    ${BOLD_GREEN}-f, --force${NC}             Force reinstall even if virtual environment exists
    ${BOLD_GREEN}-p, --python PATH${NC}       Specify Python executable path (default: python3)
    ${BOLD_GREEN}--skip-tests${NC}            Skip running initial tests after setup
    ${BOLD_GREEN}--skip-deps${NC}             Skip dependency installation (for manual setup)
    ${BOLD_GREEN}--dev${NC}                   Setup for development mode (includes dev tools)
    ${BOLD_GREEN}--create-requirements${NC}    Auto-create requirements.txt if missing
    ${BOLD_GREEN}--yes${NC}                   Answer 'yes' to all prompts (non-interactive)

${BOLD_YELLOW}EXAMPLES:${NC}
    $script_name                                    # Standard setup
    $script_name --verbose --dev                    # Development setup with verbose output
    $script_name --force --python python3.11       # Force reinstall with specific Python
    $script_name --create-requirements --yes       # Non-interactive setup with auto requirements
    $script_name --skip-deps                        # Setup without installing dependencies

${BOLD_YELLOW}DESCRIPTION:${NC}
    This script performs a complete setup of the decentralized AI simulation
    environment with enhanced error handling and fallback mechanisms:

    1. ${BOLD_CYAN}Project structure validation${NC}
    2. ${BOLD_CYAN}Python virtual environment creation and activation${NC}
    3. ${BOLD_CYAN}Smart dependency installation with fallback options${NC}
    4. ${BOLD_CYAN}Configuration file initialization${NC}
    5. ${BOLD_CYAN}Database setup and initialization${NC}
    6. ${BOLD_CYAN}Initial health checks and validation${NC}
    7. ${BOLD_CYAN}Optional test suite execution${NC}

${BOLD_YELLOW}FALLBACK MECHANISMS:${NC}
    • Auto-creates requirements.txt if missing (with --create-requirements)
    • Interactive prompts for missing files
    • Non-interactive mode for automated deployments
    • Graceful degradation when optional components fail

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
    5 - File validation failed

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
    # Skip if requested
    if [[ "$SKIP_DEPS" == true ]]; then
        log "INFO" "Skipping dependency installation as requested"
        return 0
    fi

    log "INFO" "Installing project dependencies..."

    # Ensure we're in the virtual environment
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log "ERROR" "Virtual environment is not activated"
        exit 1
    fi

    # Validate requirements.txt with enhanced error handling
    if ! validate_requirements; then
        log "ERROR" "Requirements validation failed"
        exit 5
    fi

    # Install main dependencies with retry mechanism
    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        log "INFO" "Installing dependencies from requirements.txt..."
        local install_cmd="pip install --upgrade pip"

        if [[ "$FORCE_REINSTALL" == true ]]; then
            install_cmd="$install_cmd && pip install --force-reinstall -r \"$REQUIREMENTS_FILE\""
        else
            install_cmd="$install_cmd && pip install -r \"$REQUIREMENTS_FILE\""
        fi

        if ! retry_command "$install_cmd" "$RETRY_ATTEMPTS" "$RETRY_DELAY"; then
            log "ERROR" "Failed to install dependencies from requirements.txt"
            log "INFO" "You may need to install dependencies manually or check your internet connection"
            exit 4
        fi
    else
        log "ERROR" "requirements.txt not found after validation: $REQUIREMENTS_FILE"
        exit 5
    fi

    # Install development dependencies if in dev mode
    if [[ "$DEV_MODE" == true ]]; then
        log "INFO" "Installing development dependencies..."
        local dev_deps="pytest-cov black flake8 mypy pre-commit"

        if [[ "$FORCE_REINSTALL" == true ]]; then
            retry_command "pip install --force-reinstall $dev_deps" "$RETRY_ATTEMPTS" "$RETRY_DELAY" || {
                log "WARN" "Failed to install some development dependencies"
            }
        else
            retry_command "pip install $dev_deps" "$RETRY_ATTEMPTS" "$RETRY_DELAY" || {
                log "WARN" "Failed to install some development dependencies"
            }
        fi
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
    log "INFO" "Script version: 3.0.0"
    log "INFO" "Process ID: $$"
    log "INFO" "Project root: $PROJECT_ROOT"
    log "INFO" "Python command: $PYTHON_CMD"
    log "INFO" "Development mode: $DEV_MODE"
    log "INFO" "Force reinstall: $FORCE_REINSTALL"
    log "INFO" "Skip dependencies: $SKIP_DEPS"
    log "INFO" "Create requirements: $CREATE_REQUIREMENTS"
    log "INFO" "Non-interactive mode: $NON_INTERACTIVE"

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
        echo "Skip dependencies: $SKIP_DEPS"
        echo "Create requirements: $CREATE_REQUIREMENTS"
        echo "Non-interactive mode: $NON_INTERACTIVE"
        echo "Verbose mode: $VERBOSE"
        echo "=========================================="
    } > "$LOG_FILE"

    # Core setup flow with comprehensive error handling
    local setup_success=true
    local setup_result=0

    # Phase 1: Project structure validation
    if validate_project_structure; then
        log "INFO" "Project structure validation completed"
    else
        log "ERROR" "Project structure validation failed"
        exit 5
    fi

    # Phase 2: Prerequisites validation
    if check_prerequisites; then
        log "INFO" "Prerequisites validation completed"
    else
        log "ERROR" "Prerequisites validation failed"
        exit 3
    fi

    # Phase 3: Virtual environment setup
    if create_virtual_environment; then
        log "INFO" "Virtual environment setup completed"
    else
        log "ERROR" "Virtual environment setup failed"
        setup_success=false
        setup_result=4
    fi

    # Phase 4: Dependency installation
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
        if [[ "$SKIP_DEPS" == true ]]; then
            log "INFO" "${BOLD_YELLOW}Note:${NC} Dependencies were skipped. Install manually when ready:"
            log "INFO" "     ${BOLD_CYAN}pip install -r decentralized-ai-simulation/config/requirements.txt${NC}"
        fi
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
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        --create-requirements)
            CREATE_REQUIREMENTS=true
            shift
            ;;
        --yes)
            NON_INTERACTIVE=true
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            log "INFO" "Use --help for usage information"
            exit 2
            ;;
    esac
done

# Run main function
main
