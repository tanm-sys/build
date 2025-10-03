#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Main Execution Script
# =============================================================================
# This script runs the decentralized AI simulation with configurable parameters
# and supports different execution modes including CLI, UI, and testing modes.
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
# =============================================================================

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/.venv"
LOG_FILE="$PROJECT_ROOT/logs/run.log"

# Default parameters
MODE="cli"
VERBOSE=false
AGENTS=""
STEPS=""
PARALLEL=false
SEED=""
CONFIG_FILE=""
ENVIRONMENT=""
LOG_LEVEL=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
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
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
    esac
}

show_help() {
    cat << EOF
Decentralized AI Simulation - Execution Script

USAGE:
    ./run.sh [MODE] [OPTIONS]

MODES:
    cli                 Run simulation in command-line interface mode (default)
    ui                  Launch Streamlit web interface for interactive monitoring
    test                Run in test mode with minimal configuration
    demo                Run demonstration with preset parameters for showcase

OPTIONS:
    -h, --help          Show this help message and exit
    -v, --verbose       Enable verbose output for debugging
    -a, --agents N      Number of agents to simulate (overrides config)
    -s, --steps N       Number of simulation steps to run (overrides config)
    -p, --parallel      Enable parallel execution using Ray framework
    --seed N            Set random seed for reproducible results
    --config FILE       Use custom configuration file (default: config.yaml)
    --env ENV           Set environment mode (development/production)
    --log-level LEVEL   Set logging level (DEBUG/INFO/WARNING/ERROR)

EXAMPLES:
    ./run.sh                                    # Run with default settings
    ./run.sh cli --agents 100 --steps 50       # CLI mode with custom parameters
    ./run.sh ui                                 # Launch web interface
    ./run.sh test --verbose                     # Test mode with verbose output
    ./run.sh demo --parallel                    # Demo mode with parallel execution
    ./run.sh --config custom.yaml --env production  # Production run

ENVIRONMENT VARIABLES:
    You can also set parameters using environment variables:
    
    SIMULATION_DEFAULT_AGENTS=100 ./run.sh      # Set number of agents
    LOGGING_LEVEL=DEBUG ./run.sh --verbose      # Set log level
    ENVIRONMENT=production ./run.sh             # Set environment

EOF
}

check_environment() {
    log "INFO" "Checking execution environment..."
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        log "ERROR" "Virtual environment not found at $VENV_DIR"
        log "INFO" "Please run ./setup.sh first to set up the environment"
        exit 1
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Verify Python environment
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        log "ERROR" "Failed to activate virtual environment"
        exit 1
    fi
    
    log "DEBUG" "Virtual environment activated: $VIRTUAL_ENV"
    
    # Check if required modules are available
    python -c "
import sys
try:
    from simulation import Simulation
    from config_loader import get_config
    from logging_setup import get_logger
    print('✓ Core modules available')
except ImportError as e:
    print(f'✗ Module import error: {e}')
    sys.exit(1)
" || {
        log "ERROR" "Required modules not available"
        log "INFO" "Please run ./setup.sh to install dependencies"
        exit 1
    }
    
    log "INFO" "Environment check passed"
}

build_python_command() {
    local cmd_args=()
    
    # Set environment variables if specified
    if [ -n "$ENVIRONMENT" ]; then
        export ENVIRONMENT="$ENVIRONMENT"
        log "DEBUG" "Set ENVIRONMENT=$ENVIRONMENT"
    fi
    
    if [ -n "$LOG_LEVEL" ]; then
        export LOGGING_LEVEL="$LOG_LEVEL"
        log "DEBUG" "Set LOGGING_LEVEL=$LOG_LEVEL"
    fi
    
    # Build command based on mode
    case "$MODE" in
        "cli")
            cmd_args+=("python" "decentralized_ai_simulation.py")
            ;;
        "ui")
            cmd_args+=("streamlit" "run" "streamlit_app.py")
            ;;
        "test")
            cmd_args+=("python" "decentralized_ai_simulation.py")
            # Override with test parameters
            export SIMULATION_DEFAULT_AGENTS=10
            export SIMULATION_DEFAULT_STEPS=5
            log "INFO" "Test mode: Using minimal configuration (10 agents, 5 steps)"
            ;;
        "demo")
            cmd_args+=("python" "decentralized_ai_simulation.py")
            # Override with demo parameters
            export SIMULATION_DEFAULT_AGENTS=50
            export SIMULATION_DEFAULT_STEPS=20
            log "INFO" "Demo mode: Using demonstration configuration (50 agents, 20 steps)"
            ;;
        *)
            log "ERROR" "Unknown mode: $MODE"
            exit 1
            ;;
    esac
    
    # Add CLI arguments for non-UI modes
    if [ "$MODE" != "ui" ]; then
        if [ -n "$AGENTS" ]; then
            export SIMULATION_DEFAULT_AGENTS="$AGENTS"
            log "DEBUG" "Set agents count: $AGENTS"
        fi
        
        if [ -n "$STEPS" ]; then
            export SIMULATION_DEFAULT_STEPS="$STEPS"
            log "DEBUG" "Set steps count: $STEPS"
        fi
        
        if [ "$PARALLEL" = true ]; then
            export SIMULATION_ENABLE_PARALLEL=true
            log "DEBUG" "Enabled parallel execution"
        fi
        
        if [ -n "$SEED" ]; then
            export SIMULATION_RANDOM_SEED="$SEED"
            log "DEBUG" "Set random seed: $SEED"
        fi
    fi
    
    # Set config file if specified
    if [ -n "$CONFIG_FILE" ]; then
        if [ ! -f "$CONFIG_FILE" ]; then
            log "ERROR" "Configuration file not found: $CONFIG_FILE"
            exit 1
        fi
        export CONFIG_FILE="$CONFIG_FILE"
        log "DEBUG" "Using config file: $CONFIG_FILE"
    fi
    
    echo "${cmd_args[@]}"
}

run_simulation() {
    log "INFO" "Starting simulation in $MODE mode..."
    
    # Build the command
    local cmd
    cmd=$(build_python_command)
    
    log "DEBUG" "Executing command: $cmd"
    
    # Special handling for UI mode
    if [ "$MODE" = "ui" ]; then
        log "INFO" "Launching Streamlit web interface..."
        log "INFO" "The web interface will open in your default browser"
        log "INFO" "Press Ctrl+C to stop the server"
        
        # Run streamlit with proper configuration
        exec $cmd --server.port 8501 --server.address localhost
    else
        # Run CLI simulation
        log "INFO" "Running simulation..."
        
        # Execute the command and capture output
        if [ "$VERBOSE" = true ]; then
            exec $cmd
        else
            $cmd 2>&1 | while IFS= read -r line; do
                # Filter and format output
                if [[ "$line" =~ ^\[.*\].*\[.*\] ]]; then
                    echo "$line"
                elif [[ "$line" =~ ^(INFO|WARN|ERROR|DEBUG) ]]; then
                    echo "$line"
                elif [[ "$line" =~ (completed|finished|started|initialized) ]]; then
                    log "INFO" "$line"
                fi
            done
        fi
    fi
}

show_simulation_info() {
    log "INFO" "Simulation Configuration:"
    log "INFO" "  Mode: $MODE"
    log "INFO" "  Project Root: $PROJECT_ROOT"
    log "INFO" "  Virtual Environment: $VENV_DIR"
    log "INFO" "  Log File: $LOG_FILE"
    
    if [ -n "$AGENTS" ]; then
        log "INFO" "  Agents: $AGENTS"
    fi
    
    if [ -n "$STEPS" ]; then
        log "INFO" "  Steps: $STEPS"
    fi
    
    if [ "$PARALLEL" = true ]; then
        log "INFO" "  Parallel Execution: Enabled"
    fi
    
    if [ -n "$SEED" ]; then
        log "INFO" "  Random Seed: $SEED"
    fi
    
    if [ -n "$CONFIG_FILE" ]; then
        log "INFO" "  Config File: $CONFIG_FILE"
    fi
    
    if [ -n "$ENVIRONMENT" ]; then
        log "INFO" "  Environment: $ENVIRONMENT"
    fi
    
    if [ -n "$LOG_LEVEL" ]; then
        log "INFO" "  Log Level: $LOG_LEVEL"
    fi
}

# =============================================================================
# Signal Handlers
# =============================================================================

cleanup() {
    log "INFO" "Received interrupt signal, cleaning up..."
    
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    log "INFO" "Cleanup completed"
    exit 0
}

trap cleanup SIGINT SIGTERM

# =============================================================================
# Command Line Argument Parsing
# =============================================================================

# Parse mode first
if [[ $# -gt 0 ]] && [[ ! "$1" =~ ^- ]]; then
    case "$1" in
        cli|ui|test|demo)
            MODE="$1"
            shift
            ;;
    esac
fi

# Parse remaining arguments
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
            AGENTS="$2"
            shift 2
            ;;
        -s|--steps)
            STEPS="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        --seed)
            SEED="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            log "INFO" "Use --help for usage information"
            exit 1
            ;;
    esac
done

# =============================================================================
# Main Execution
# =============================================================================

main() {
    log "INFO" "Decentralized AI Simulation - Starting execution"
    
    check_environment
    show_simulation_info
    run_simulation
    
    if [ "$MODE" != "ui" ]; then
        log "SUCCESS" "Simulation completed successfully!"
    fi
}

# Run main function
main
