#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Main Execution Script
# =============================================================================
# Modern bash script for running the decentralized AI simulation with enhanced
# error handling, comprehensive logging, and cross-platform compatibility.
#
# This script supports multiple execution modes and provides robust validation,
# environment management, and graceful error recovery.
#
# Usage: ./run.sh [MODE] [OPTIONS]
# Modes:
#   cli                 Run simulation in CLI mode (default)
#   ui                  Launch Streamlit web interface
#   test                Run in test mode with minimal agents
#   demo                Run demonstration with preset parameters
#
# Options:
#   -h, --help          Show this help message
#   -v, --verbose       Enable verbose output
#   -a, --agents N      Number of agents (default: from config)
#   -s, --steps N       Number of simulation steps (default: from config)
#   -p, --parallel      Enable parallel execution with Ray
#   --seed N            Set random seed for reproducibility
#   --config FILE       Use custom configuration file
#   --env ENV           Set environment (development/production)
#   --log-level LEVEL   Set logging level (DEBUG/INFO/WARNING/ERROR)
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - Environment setup failed
# =============================================================================

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures
shopt -s globstar   # Enable globstar for recursive globbing
shopt -s extglob    # Enable extended globbing patterns

# Script configuration with enhanced path resolution and validation
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly VENV_DIR="${PROJECT_ROOT}/.venv"
readonly LOG_DIR="${PROJECT_ROOT}/logs"
readonly LOG_FILE="${LOG_DIR}/run.log"

# Default parameters with type hints for documentation
readonly DEFAULT_MODE="cli"
readonly DEFAULT_LOG_LEVEL="INFO"
readonly SUPPORTED_MODES=("cli" "ui" "test" "demo")
readonly SUPPORTED_ENVIRONMENTS=("development" "staging" "production" "docker")
readonly SUPPORTED_LOG_LEVELS=("DEBUG" "INFO" "WARNING" "ERROR")

# Configuration variables with validation
MODE="${DEFAULT_MODE}"
VERBOSE=false
AGENTS=""
STEPS=""
PARALLEL=false
SEED=""
CONFIG_FILE=""
ENVIRONMENT=""
LOG_LEVEL="${DEFAULT_LOG_LEVEL}"

# Color codes for enhanced terminal output with bold variants
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
readonly NC='\033[0m' # No Color

# Global variables for tracking execution state
PYTHON_CMD=""
VIRTUAL_ENV_ACTIVE=false

# =============================================================================
# Utility Functions
# =============================================================================

# Enhanced input validation functions with better error handling
validate_numeric() {
    local value="$1"
    local param_name="$2"
    local min_value="${3:-1}"

    if [[ -n "$value" ]]; then
        # Use more robust numeric validation
        if ! [[ "$value" =~ ^[0-9]+$ ]]; then
            log "ERROR" "Invalid $param_name: '$value' (must be a positive integer)"
            exit 2
        fi

        if [[ "$value" -lt "$min_value" ]]; then
            log "ERROR" "Invalid $param_name: '$value' (must be >= $min_value)"
            exit 2
        fi

        log "DEBUG" "Validated $param_name: $value"
    fi
}

validate_seed() {
    local value="$1"

    if [[ -n "$value" ]]; then
        # Allow negative seeds for randomization flexibility
        if ! [[ "$value" =~ ^-?[0-9]+$ ]]; then
            log "ERROR" "Invalid seed: '$value' (must be an integer)"
            exit 2
        fi

        log "DEBUG" "Validated seed: $value"
    fi
}

validate_config_file() {
    local file="$1"

    if [[ -n "$file" ]]; then
        # Check if file exists and is readable
        if [[ ! -f "$file" ]]; then
            log "ERROR" "Configuration file not found: $file"
            exit 2
        fi

        if [[ ! -r "$file" ]]; then
            log "ERROR" "Configuration file not readable: $file"
            exit 2
        fi

        # Validate YAML structure if possible
        if command -v python3 &> /dev/null; then
            if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" &> /dev/null; then
                log "WARN" "Configuration file may have YAML syntax issues: $file"
            fi
        fi

        log "DEBUG" "Validated config file: $file"
    fi
}

validate_environment() {
    local env="$1"

    if [[ -n "$env" ]]; then
        local valid_env=false
        for valid_env_value in "${SUPPORTED_ENVIRONMENTS[@]}"; do
            if [[ "$env" == "$valid_env_value" ]]; then
                valid_env=true
                break
            fi
        done

        if [[ "$valid_env" == false ]]; then
            log "ERROR" "Invalid environment: '$env' (must be one of: ${SUPPORTED_ENVIRONMENTS[*]})"
            exit 2
        fi

        log "DEBUG" "Validated environment: $env"
    fi
}

validate_log_level() {
    local level="$1"

    if [[ -n "$level" ]]; then
        local valid_level=false
        for valid_level_value in "${SUPPORTED_LOG_LEVELS[@]}"; do
            if [[ "$level" == "$valid_level_value" ]]; then
                valid_level=true
                break
            fi
        done

        if [[ "$valid_level" == false ]]; then
            log "ERROR" "Invalid log level: '$level' (must be one of: ${SUPPORTED_LOG_LEVELS[*]})"
            exit 2
        fi

        log "DEBUG" "Validated log level: $level"
    fi
}

validate_mode() {
    local mode="$1"

    if [[ -n "$mode" ]]; then
        local valid_mode=false
        for valid_mode_value in "${SUPPORTED_MODES[@]}"; do
            if [[ "$mode" == "$valid_mode_value" ]]; then
                valid_mode=true
                break
            fi
        done

        if [[ "$valid_mode" == false ]]; then
            log "ERROR" "Invalid mode: '$mode' (must be one of: ${SUPPORTED_MODES[*]})"
            exit 2
        fi

        log "DEBUG" "Validated mode: $mode"
    fi
}

# Enhanced logging function with timestamp and structured output
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

    # Console output with colors and formatting
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
        "DEPLOY"|"CLEANUP"|"TEST")
            printf '%b[%s]%b %s\n' "${CYAN}" "$level" "${NC}" "$message"
            ;;
    esac
}


# Enhanced help display with better formatting and examples
show_help() {
    local script_name
    script_name=$(basename "${BASH_SOURCE[0]}")

    cat << EOF
${BOLD_BLUE}Decentralized AI Simulation - Execution Script${NC}

${BOLD_YELLOW}USAGE:${NC}
    $script_name [MODE] [OPTIONS]

${BOLD_YELLOW}MODES:${NC}
    ${BOLD_GREEN}cli${NC}                 Run simulation in command-line interface mode (default)
    ${BOLD_GREEN}ui${NC}                  Launch Streamlit web interface for interactive monitoring
    ${BOLD_GREEN}test${NC}                Run in test mode with minimal configuration
    ${BOLD_GREEN}demo${NC}                Run demonstration with preset parameters for showcase

${BOLD_YELLOW}OPTIONS:${NC}
    ${BOLD_GREEN}-h, --help${NC}          Show this help message and exit
    ${BOLD_GREEN}-v, --verbose${NC}       Enable verbose output for debugging
    ${BOLD_GREEN}-a, --agents N${NC}      Number of agents to simulate (overrides config)
    ${BOLD_GREEN}-s, --steps N${NC}       Number of simulation steps to run (overrides config)
    ${BOLD_GREEN}-p, --parallel${NC}      Enable parallel execution using Ray framework
    ${BOLD_GREEN}--seed N${NC}            Set random seed for reproducible results
    ${BOLD_GREEN}--config FILE${NC}       Use custom configuration file (default: config.yaml)
    ${BOLD_GREEN}--env ENV${NC}           Set environment mode (development/staging/production/docker)
    ${BOLD_GREEN}--log-level LEVEL${NC}   Set logging level (DEBUG/INFO/WARNING/ERROR)

${BOLD_YELLOW}EXAMPLES:${NC}
    $script_name                                    # Run with default settings
    $script_name cli --agents 100 --steps 50       # CLI mode with custom parameters
    $script_name ui                                 # Launch web interface
    $script_name test --verbose                     # Test mode with verbose output
    $script_name demo --parallel                    # Demo mode with parallel execution
    $script_name --config custom.yaml --env production  # Production run

${BOLD_YELLOW}ENVIRONMENT VARIABLES:${NC}
    You can also set parameters using environment variables:

    ${BOLD_CYAN}SIMULATION_DEFAULT_AGENTS=100${NC} $script_name      # Set number of agents
    ${BOLD_CYAN}LOGGING_LEVEL=DEBUG${NC} $script_name --verbose      # Set log level
    ${BOLD_CYAN}ENVIRONMENT=production${NC} $script_name             # Set environment

${BOLD_YELLOW}EXIT CODES:${NC}
    0 - Success
    1 - General error
    2 - Invalid arguments
    3 - Environment setup failed

${BOLD_BLUE}For more information, see README.md${NC}
EOF
}

# Cleanup function for graceful shutdown
cleanup() {
    local exit_code=$?
    local signal="$1"

    log "INFO" "Received signal ${signal:-"EXIT"}, cleaning up..."

    # Kill any background processes
    if [[ -n "${BACKGROUND_PIDS:-}" ]]; then
        kill "${BACKGROUND_PIDS[@]}" 2>/dev/null || true
        wait "${BACKGROUND_PIDS[@]}" 2>/dev/null || true
    fi

    # Deactivate virtual environment if active
    if [[ "$VIRTUAL_ENV_ACTIVE" == true ]] && [[ -n "${VIRTUAL_ENV:-}" ]]; then
        deactivate 2>/dev/null || true
    fi

    log "INFO" "Cleanup completed"
    exit $exit_code
}

# Trap signals for cleanup
trap 'cleanup SIGINT' SIGINT
trap 'cleanup SIGTERM' SIGTERM
trap 'cleanup EXIT' EXIT

# Enhanced environment validation with comprehensive checks
check_environment() {
    log "INFO" "Checking execution environment..."

    # Validate project structure
    local required_paths=(
        "${PROJECT_ROOT}/decentralized-ai-simulation"
        "${PROJECT_ROOT}/config"
    )

    for path in "${required_paths[@]}"; do
        if [[ ! -d "$path" ]]; then
            log "ERROR" "Required directory not found: $path"
            log "INFO" "Please ensure project structure is intact"
            exit 3
        fi
    done

    # Validate critical files
    local required_files=(
        "${PROJECT_ROOT}/decentralized-ai-simulation/config/requirements.txt"
        "${PROJECT_ROOT}/config/config.yaml"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log "ERROR" "Required file not found: $file"
            log "INFO" "Please run setup script first: ${SCRIPT_DIR}/../setup/setup.sh"
            exit 3
        fi

        if [[ ! -r "$file" ]]; then
            log "ERROR" "Required file not readable: $file"
            log "INFO" "Please check file permissions"
            exit 3
        fi
    done

    # Check virtual environment
    if [[ ! -d "$VENV_DIR" ]]; then
        log "ERROR" "Virtual environment not found at $VENV_DIR"
        log "INFO" "Please run setup script first: ${SCRIPT_DIR}/../setup/setup.sh"
        exit 3
    fi

    # Activate virtual environment with error handling
    if ! source "$VENV_DIR/bin/activate"; then
        log "ERROR" "Failed to activate virtual environment at $VENV_DIR"
        exit 3
    fi

    # Verify activation
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log "ERROR" "Virtual environment activation failed"
        exit 3
    fi

    VIRTUAL_ENV_ACTIVE=true
    PYTHON_CMD="python"
    log "DEBUG" "Virtual environment activated: $VIRTUAL_ENV"

    # Set PYTHONPATH for module imports
    export PYTHONPATH="${PROJECT_ROOT}:${PROJECT_ROOT}/decentralized-ai-simulation:${PYTHONPATH:-}"
    log "DEBUG" "Set PYTHONPATH for module resolution"

    # Validate Python modules with detailed error reporting
    local module_check_result
    module_check_result=$(python -c "
import sys
import importlib.util

required_modules = [
    'decentralized_ai_simulation.simulation',
    'decentralized_ai_simulation.config.config_loader',
    'decentralized_ai_simulation.src.utils.logging_setup',
    'decentralized_ai_simulation.src.core.agents',
    'decentralized_ai_simulation.src.core.database'
]

missing_modules = []
for module in required_modules:
    if importlib.util.find_spec(module) is None:
        missing_modules.append(module)

if missing_modules:
    print(f'ERROR: Missing modules: {missing_modules}')
    sys.exit(1)
else:
    print('SUCCESS: All required modules found')
" 2>&1)

    if [[ $? -eq 0 ]]; then
        log "INFO" "Module validation passed"
    else
        log "ERROR" "Module validation failed: $module_check_result"
        log "INFO" "Please run setup script to install dependencies"
        exit 3
    fi

    # Check system resources for large simulations
    if [[ -n "$AGENTS" ]] && [[ "$AGENTS" -gt 1000 ]]; then
        log "WARN" "Large simulation requested ($AGENTS agents) - ensure adequate system resources"
    fi

    log "INFO" "Environment validation completed successfully"
}

# Enhanced command builder with better validation and error handling
build_python_command() {
    local cmd_args=()

    # Set environment variables with validation
    if [[ -n "$ENVIRONMENT" ]]; then
        export ENVIRONMENT="$ENVIRONMENT"
        log "DEBUG" "Set ENVIRONMENT=$ENVIRONMENT"
    fi

    if [[ -n "$LOG_LEVEL" ]]; then
        export LOGGING_LEVEL="$LOG_LEVEL"
        log "DEBUG" "Set LOGGING_LEVEL=$LOG_LEVEL"
    fi

    # Build command based on mode with enhanced validation
    case "$MODE" in
        "cli")
            cmd_args+=("$PYTHON_CMD")
            cmd_args+=("$PROJECT_ROOT/decentralized_ai_simulation.py")
            ;;
        "ui")
            # Check if streamlit is available
            if ! command -v streamlit &> /dev/null; then
                log "ERROR" "Streamlit not found. Install with: pip install streamlit"
                exit 3
            fi
            cmd_args+=("streamlit" "run")
            cmd_args+=("$PROJECT_ROOT/decentralized-ai-simulation/src/ui/streamlit_app.py")
            ;;
        "test")
            cmd_args+=("$PYTHON_CMD")
            cmd_args+=("$PROJECT_ROOT/decentralized_ai_simulation.py")
            # Override with test parameters
            export SIMULATION_DEFAULT_AGENTS=10
            export SIMULATION_DEFAULT_STEPS=5
            log "INFO" "Test mode: Using minimal configuration (10 agents, 5 steps)"
            ;;
        "demo")
            cmd_args+=("$PYTHON_CMD")
            cmd_args+=("$PROJECT_ROOT/decentralized_ai_simulation.py")
            # Override with demo parameters
            export SIMULATION_DEFAULT_AGENTS=50
            export SIMULATION_DEFAULT_STEPS=20
            log "INFO" "Demo mode: Using demonstration configuration (50 agents, 20 steps)"
            ;;
        *)
            log "ERROR" "Unknown mode: $MODE"
            exit 2
            ;;
    esac

    # Add CLI arguments for non-UI modes with enhanced validation
    if [[ "$MODE" != "ui" ]]; then
        if [[ -n "$AGENTS" ]]; then
            export SIMULATION_DEFAULT_AGENTS="$AGENTS"
            log "DEBUG" "Set agents count: $AGENTS"
        fi

        if [[ -n "$STEPS" ]]; then
            export SIMULATION_DEFAULT_STEPS="$STEPS"
            log "DEBUG" "Set steps count: $STEPS"
        fi

        if [[ "$PARALLEL" == true ]]; then
            export SIMULATION_ENABLE_PARALLEL=true
            log "DEBUG" "Enabled parallel execution"
        fi

        if [[ -n "$SEED" ]]; then
            export SIMULATION_RANDOM_SEED="$SEED"
            log "DEBUG" "Set random seed: $SEED"
        fi
    fi

    # Set config file if specified with enhanced validation
    if [[ -n "$CONFIG_FILE" ]]; then
        # Additional validation for config file
        if [[ ! -f "$CONFIG_FILE" ]]; then
            log "ERROR" "Configuration file not found: $CONFIG_FILE"
            exit 2
        fi

        if [[ ! -r "$CONFIG_FILE" ]]; then
            log "ERROR" "Configuration file not readable: $CONFIG_FILE"
            exit 2
        fi

        # Validate YAML structure if possible
        if command -v python3 &> /dev/null; then
            if ! python3 -c "import yaml; yaml.safe_load(open('$CONFIG_FILE'))" &> /dev/null; then
                log "WARN" "Configuration file may have YAML syntax issues: $CONFIG_FILE"
            fi
        fi

        export CONFIG_FILE="$CONFIG_FILE"
        log "DEBUG" "Using config file: $CONFIG_FILE"
    fi

    # Return the complete command as a string
    printf '%s\n' "${cmd_args[*]}"
}

# Enhanced simulation runner with better process management and error handling
run_simulation() {
    log "INFO" "Starting simulation in $MODE mode..."

    # Build the command with validation
    local cmd
    if ! cmd=$(build_python_command); then
        log "ERROR" "Failed to build simulation command"
        exit 3
    fi

    log "DEBUG" "Executing command: $cmd"

    # Special handling for UI mode with enhanced process management
    if [[ "$MODE" == "ui" ]]; then
        log "INFO" "Launching Streamlit web interface..."
        log "INFO" "The web interface will be available at http://localhost:8501"
        log "INFO" "Press Ctrl+C to stop the server"

        # Change to project root for UI mode to ensure proper module resolution
        cd "$PROJECT_ROOT" || {
            log "ERROR" "Failed to change to project directory: $PROJECT_ROOT"
            exit 3
        }

        # Run streamlit with enhanced configuration and error handling
        exec $cmd --server.port 8501 \
                  --server.address 0.0.0.0 \
                  --server.headless true \
                  --browser.gatherUsageStats false \
                  --theme.base dark
    else
        # Run CLI simulation with enhanced output processing
        log "INFO" "Running simulation..."

        # Execute the command with comprehensive error handling
        local exit_code=0
        local temp_output_file
        temp_output_file=$(mktemp)

        if [[ "$VERBOSE" == true ]]; then
            # Verbose mode: direct execution with full output
            $cmd 2>&1 || exit_code=$?
        else
            # Normal mode: filtered output with progress indicators
            $cmd > "$temp_output_file" 2>&1 || exit_code=$?

            if [[ $exit_code -eq 0 ]]; then
                # Process output for relevant information
                while IFS= read -r line; do
                    # Filter and format output for important messages
                    if [[ "$line" =~ ^\[.*\].*\[.*\] ]] || \
                       [[ "$line" =~ ^(INFO|WARN|ERROR|DEBUG|SUCCESS) ]] || \
                       [[ "$line" =~ (completed|finished|started|initialized|progress|step) ]]; then
                        echo "$line"
                    fi
                done < "$temp_output_file"
            fi
        fi

        # Clean up temporary file
        [[ -f "$temp_output_file" ]] && rm -f "$temp_output_file"

        # Handle exit codes with detailed error reporting
        if [[ $exit_code -ne 0 ]]; then
            log "ERROR" "Simulation command failed with exit code: $exit_code"
            log "INFO" "Check the log file for details: $LOG_FILE"

            # Provide context-specific error messages
            case $exit_code in
                1) log "INFO" "General simulation error - check configuration and dependencies" ;;
                2) log "INFO" "Command line argument error - use --help for usage" ;;
                3) log "INFO" "Environment or dependency error - run setup script" ;;
                *) log "INFO" "Unexpected error occurred during simulation" ;;
            esac
            exit $exit_code
        fi
    fi
}

# Enhanced configuration display with comprehensive system information
show_simulation_info() {
    log "INFO" "Simulation Configuration Summary:"
    log "INFO" "  ${BOLD_BLUE}Mode:${NC} $MODE"
    log "INFO" "  ${BOLD_BLUE}Project Root:${NC} $PROJECT_ROOT"
    log "INFO" "  ${BOLD_BLUE}Virtual Environment:${NC} $VENV_DIR"
    log "INFO" "  ${BOLD_BLUE}Log File:${NC} $LOG_FILE"
    log "INFO" "  ${BOLD_BLUE}Python Command:${NC} $PYTHON_CMD"

    if [[ -n "$AGENTS" ]]; then
        log "INFO" "  ${BOLD_BLUE}Agents:${NC} $AGENTS"
    fi

    if [[ -n "$STEPS" ]]; then
        log "INFO" "  ${BOLD_BLUE}Steps:${NC} $STEPS"
    fi

    if [[ "$PARALLEL" == true ]]; then
        log "INFO" "  ${BOLD_BLUE}Parallel Execution:${NC} ${BOLD_GREEN}Enabled${NC}"
    fi

    if [[ -n "$SEED" ]]; then
        log "INFO" "  ${BOLD_BLUE}Random Seed:${NC} $SEED"
    fi

    if [[ -n "$CONFIG_FILE" ]]; then
        log "INFO" "  ${BOLD_BLUE}Config File:${NC} $CONFIG_FILE"
    fi

    if [[ -n "$ENVIRONMENT" ]]; then
        log "INFO" "  ${BOLD_BLUE}Environment:${NC} $ENVIRONMENT"
    fi

    if [[ -n "$LOG_LEVEL" ]]; then
        log "INFO" "  ${BOLD_BLUE}Log Level:${NC} $LOG_LEVEL"
    fi

    # Show system information for context
    log "DEBUG" "System Information:"
    log "DEBUG" "  Platform: $(uname -s) $(uname -r)"
    log "DEBUG" "  Bash Version: $BASH_VERSION"
    log "DEBUG" "  Script Directory: $SCRIPT_DIR"

    # Show environment variables that will be set
    if [[ "$VERBOSE" == true ]]; then
        log "DEBUG" "Environment Variables:"
        log "DEBUG" "  PYTHONPATH: ${PYTHONPATH:-"(not set)"}"
        log "DEBUG" "  VIRTUAL_ENV: ${VIRTUAL_ENV:-"(not set)"}"
    fi
}

# =============================================================================
# Enhanced Signal Handlers and Process Management
# =============================================================================

# Global array to track background process IDs
BACKGROUND_PIDS=()

# Enhanced cleanup function with comprehensive process management
cleanup() {
    local exit_code=$?
    local signal="$1"

    log "INFO" "Received signal ${signal:-"EXIT"}, initiating cleanup..."

    # Kill any background processes we spawned
    if [[ ${#BACKGROUND_PIDS[@]} -gt 0 ]]; then
        log "DEBUG" "Terminating ${#BACKGROUND_PIDS[@]} background processes"
        for pid in "${BACKGROUND_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                log "DEBUG" "Terminating process $pid"
                kill -TERM "$pid" 2>/dev/null || true

                # Wait a moment then force kill if necessary
                sleep 2
                if kill -0 "$pid" 2>/dev/null; then
                    kill -KILL "$pid" 2>/dev/null || true
                fi
            fi
        done

        # Wait for processes to complete
        wait "${BACKGROUND_PIDS[@]}" 2>/dev/null || true
    fi

    # Clean up any temporary files
    if [[ -n "${TEMP_FILES:-}" ]]; then
        rm -f "${TEMP_FILES[@]}" 2>/dev/null || true
    fi

    # Deactivate virtual environment if active
    if [[ "$VIRTUAL_ENV_ACTIVE" == true ]] && [[ -n "${VIRTUAL_ENV:-}" ]]; then
        log "DEBUG" "Deactivating virtual environment"
        deactivate 2>/dev/null || true
    fi

    log "INFO" "Cleanup completed"
    exit $exit_code
}

# Register signal handlers for graceful shutdown
trap 'cleanup SIGINT' SIGINT
trap 'cleanup SIGTERM' SIGTERM
trap 'cleanup EXIT' EXIT

# =============================================================================
# Enhanced Command Line Argument Parsing
# =============================================================================

# Function to display usage and exit
usage_error() {
    log "ERROR" "Invalid usage: $*"
    log "INFO" "Use --help for detailed usage information"
    exit 2
}

# Parse mode first (positional argument)
if [[ $# -gt 0 ]] && [[ ! "$1" =~ ^- ]]; then
    if [[ "$1" =~ ^(cli|ui|test|demo)$ ]]; then
        MODE="$1"
        shift
    else
        usage_error "Invalid mode: $1"
    fi
fi

# Parse remaining arguments with enhanced validation
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
        -a|--agents)
            if [[ $# -lt 2 ]] || [[ ! "$2" =~ ^[0-9]+$ ]]; then
                usage_error "Option --agents requires a numeric argument"
            fi
            AGENTS="$2"
            validate_numeric "$AGENTS" "agents" 1
            shift 2
            ;;
        -s|--steps)
            if [[ $# -lt 2 ]] || [[ ! "$2" =~ ^[0-9]+$ ]]; then
                usage_error "Option --steps requires a numeric argument"
            fi
            STEPS="$2"
            validate_numeric "$STEPS" "steps" 1
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        --seed)
            if [[ $# -lt 2 ]]; then
                usage_error "Option --seed requires an argument"
            fi
            SEED="$2"
            validate_seed "$SEED"
            shift 2
            ;;
        --config)
            if [[ $# -lt 2 ]] || [[ -z "$2" ]]; then
                usage_error "Option --config requires a file path argument"
            fi
            CONFIG_FILE="$2"
            validate_config_file "$CONFIG_FILE"
            shift 2
            ;;
        --env)
            if [[ $# -lt 2 ]] || [[ -z "$2" ]]; then
                usage_error "Option --env requires an environment argument"
            fi
            ENVIRONMENT="$2"
            validate_environment "$ENVIRONMENT"
            shift 2
            ;;
        --log-level)
            if [[ $# -lt 2 ]] || [[ -z "$2" ]]; then
                usage_error "Option --log-level requires a level argument"
            fi
            LOG_LEVEL="$2"
            validate_log_level "$LOG_LEVEL"
            shift 2
            ;;
        *)
            usage_error "Unknown option: $1"
            ;;
    esac
done

# Validate that mutually exclusive options aren't both set
if [[ -n "$AGENTS" ]] && [[ -n "$STEPS" ]] && [[ "$MODE" == "test" ]]; then
    log "WARN" "Custom agents/steps settings ignored in test mode"
fi

# =============================================================================
# Main Execution Function
# =============================================================================

main() {
    local start_time
    start_time=$(date '+%Y-%m-%d %H:%M:%S')

    log "INFO" "Decentralized AI Simulation - Starting execution at $start_time"
    log "INFO" "Script version: 2.0.0"
    log "INFO" "Process ID: $$"

    # Core execution flow with error handling
    local execution_result=0

    if check_environment; then
        log "INFO" "Environment validation completed"
    else
        log "ERROR" "Environment validation failed"
        exit 3
    fi

    if show_simulation_info; then
        log "DEBUG" "Configuration display completed"
    else
        log "ERROR" "Failed to display configuration"
        exit 3
    fi

    if run_simulation; then
        log "INFO" "Simulation execution completed"
    else
        execution_result=$?
        log "ERROR" "Simulation execution failed with code: $execution_result"
    fi

    # Completion message for non-UI modes
    if [[ "$MODE" != "ui" ]]; then
        local end_time
        end_time=$(date '+%Y-%m-%d %H:%M:%S')
        log "SUCCESS" "Simulation completed successfully at $end_time"
        log "INFO" "Total execution time: $(date -d "$end_time" +%s) - $(date -d "$start_time" +%s) seconds"
        log "INFO" "Log file available at: $LOG_FILE"
    fi

    # Exit with appropriate code
    exit $execution_result
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Execute main function with all arguments
main "$@"
