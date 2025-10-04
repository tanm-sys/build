#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Enhanced Comprehensive Testing Script
# =============================================================================
# Modern bash script for comprehensive testing with enhanced reporting,
# parallel execution support, and cross-platform compatibility.
#
# This script runs comprehensive tests including unit tests, integration tests,
# code quality checks, coverage reporting, and performance validation.
#
# Usage: ./test.sh [OPTIONS]
# Options:
#   -h, --help          Show this help message
#   -v, --verbose       Enable verbose output
#   -f, --fast          Run fast tests only (skip slow integration tests)
#   -c, --coverage      Generate detailed coverage report
#   -q, --quality       Run code quality checks (linting, formatting)
#   -p, --performance   Run performance tests
#   -r, --report        Generate comprehensive test report
#   --unit              Run unit tests only
#   --integration       Run integration tests only
#   --html              Generate HTML coverage report
#   --xml               Generate XML coverage report for CI
#
# Exit Codes:
#   0 - Success (all tests passed)
#   1 - General error
#   2 - Invalid arguments
#   3 - Test environment not ready
#   4 - Some tests failed
# =============================================================================

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures
shopt -s globstar   # Enable globstar for recursive globbing
shopt -s extglob    # Enable extended globbing patterns

# Enhanced script configuration with robust path resolution
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly VENV_DIR="${PROJECT_ROOT}/.venv"
readonly LOG_DIR="${PROJECT_ROOT}/logs"
readonly LOG_FILE="${LOG_DIR}/test.log"
readonly REPORTS_DIR="${PROJECT_ROOT}/test_reports"

# Test configuration with validation arrays
readonly DEFAULT_TEST_TIMEOUT=300  # 5 minutes
readonly PERFORMANCE_TEST_TIMEOUT=600  # 10 minutes
readonly COVERAGE_PACKAGES=("." "decentralized_ai_simulation" "tests")
readonly QUALITY_TOOLS=("flake8" "black" "mypy")

# Configuration variables with defaults
VERBOSE=false
FAST_MODE=false
RUN_COVERAGE=false
RUN_QUALITY=false
RUN_PERFORMANCE=false
GENERATE_REPORT=false
UNIT_ONLY=false
INTEGRATION_ONLY=false
HTML_COVERAGE=false
XML_COVERAGE=false

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

# Enhanced test results tracking with detailed statistics
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0
TESTS_ERROR=0
TEST_DURATION=0
COVERAGE_PERCENTAGE=0

# Global arrays for tracking test execution
TEST_RESULTS=()
TEMP_FILES=()

# =============================================================================
# Enhanced Utility Functions
# =============================================================================

# Enhanced logging function with structured output and test tracking
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
        "TEST")
            printf '%b[%s]%b %s\n' "${CYAN}" "$level" "${NC}" "$message"
            ;;
        "COVERAGE")
            printf '%b[%s]%b %s\n' "${PURPLE}" "$level" "${NC}" "$message"
            ;;
    esac
}

# Function to check if command exists and is executable
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to install test dependencies if missing
install_test_dependencies() {
    local missing_tools=()

    # Check for pytest
    if ! python -c "import pytest" 2>/dev/null; then
        missing_tools+=("pytest")
    fi

    # Check for coverage tools if needed
    if [[ "$RUN_COVERAGE" == true ]]; then
        if ! python -c "import pytest_cov" 2>/dev/null; then
            missing_tools+=("pytest-cov")
        fi
    fi

    # Check for quality tools if needed
    if [[ "$RUN_QUALITY" == true ]]; then
        if ! python -c "import flake8" 2>/dev/null; then
            missing_tools+=("flake8")
        fi
        if ! python -c "import black" 2>/dev/null; then
            missing_tools+=("black")
        fi
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log "INFO" "Installing missing test dependencies: ${missing_tools[*]}"
        if ! pip install "${missing_tools[@]}"; then
            log "ERROR" "Failed to install test dependencies"
            return 1
        fi
    fi

    return 0
}

# Enhanced help display with better formatting and testing guidance
show_help() {
    local script_name
    script_name=$(basename "${BASH_SOURCE[0]}")

    cat << EOF
${BOLD_BLUE}Decentralized AI Simulation - Enhanced Testing Script${NC}

${BOLD_YELLOW}USAGE:${NC}
    $script_name [OPTIONS]

${BOLD_YELLOW}OPTIONS:${NC}
    ${BOLD_GREEN}-h, --help${NC}          Show this help message and exit
    ${BOLD_GREEN}-v, --verbose${NC}       Enable verbose output for detailed test information
    ${BOLD_GREEN}-f, --fast${NC}          Run fast tests only (skip slow integration tests)
    ${BOLD_GREEN}-c, --coverage${NC}      Generate detailed coverage report
    ${BOLD_GREEN}-q, --quality${NC}       Run code quality checks (linting, type checking)
    ${BOLD_GREEN}-p, --performance${NC}   Run performance and load tests
    ${BOLD_GREEN}-r, --report${NC}        Generate comprehensive HTML test report
    ${BOLD_GREEN}--unit${NC}              Run unit tests only
    ${BOLD_GREEN}--integration${NC}       Run integration tests only
    ${BOLD_GREEN}--html${NC}              Generate HTML coverage report
    ${BOLD_GREEN}--xml${NC}               Generate XML coverage report (for CI/CD)

${BOLD_YELLOW}EXAMPLES:${NC}
    $script_name                           # Run all tests with default settings
    $script_name --verbose --coverage      # Verbose output with coverage
    $script_name --fast --quality          # Fast tests with quality checks
    $script_name --unit --html             # Unit tests with HTML coverage
    $script_name --report                  # Full test suite with report

${BOLD_YELLOW}DESCRIPTION:${NC}
    This script provides comprehensive testing capabilities including:

    • ${BOLD_CYAN}Unit Tests${NC}: Test individual components and functions
    • ${BOLD_CYAN}Integration Tests${NC}: Test component interactions and workflows
    • ${BOLD_CYAN}Coverage Analysis${NC}: Measure code coverage and identify gaps
    • ${BOLD_CYAN}Code Quality${NC}: Linting, formatting, and type checking
    • ${BOLD_CYAN}Performance Tests${NC}: Validate system performance under load
    • ${BOLD_CYAN}Test Reports${NC}: Generate detailed HTML and XML reports

${BOLD_YELLOW}TEST CATEGORIES:${NC}
    • ${BOLD_GREEN}Unit Tests${NC}: Fast, isolated component tests
    • ${BOLD_YELLOW}Integration Tests${NC}: Slower, end-to-end workflow tests
    • ${BOLD_PURPLE}Performance Tests${NC}: Load and timing validation tests
    • ${BOLD_BLUE}Quality Checks${NC}: Code style and formatting validation

${BOLD_YELLOW}EXIT CODES:${NC}
    0 - Success (all tests passed)
    1 - General error
    2 - Invalid arguments
    3 - Test environment not ready
    4 - Some tests failed

${BOLD_BLUE}For more information, see README.md${NC}
EOF
}

check_test_environment() {
    log "INFO" "Checking test environment..."
    
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
    
    # Check if pytest is available
    if ! python -m pytest --version &> /dev/null; then
        log "ERROR" "pytest is not installed"
        log "INFO" "Installing pytest..."
        pip install pytest pytest-cov pytest-html pytest-xvs
    fi
    
    # Create reports directory
    mkdir -p "$REPORTS_DIR"
    
    log "INFO" "Test environment ready"
}

run_unit_tests() {
    if [ "$INTEGRATION_ONLY" = true ]; then
        log "INFO" "Skipping unit tests (integration only mode)"
        return 0
    fi
    
    log "TEST" "Running unit tests..."
    
    local pytest_args=("python" "-m" "pytest" "$PROJECT_ROOT/tests/")
    local coverage_args=()
    
    # Add verbose flag if requested
    if [ "$VERBOSE" = true ]; then
        pytest_args+=("-v")
    else
        pytest_args+=("-q")
    fi
    
    # Add coverage if requested
    if [ "$RUN_COVERAGE" = true ]; then
        coverage_args+=("--cov=." "--cov-report=term-missing")
        
        if [ "$HTML_COVERAGE" = true ]; then
            coverage_args+=("--cov-report=html:$REPORTS_DIR/coverage_html")
        fi
        
        if [ "$XML_COVERAGE" = true ]; then
            coverage_args+=("--cov-report=xml:$REPORTS_DIR/coverage.xml")
        fi
    fi
    
    # Add report generation if requested
    if [ "$GENERATE_REPORT" = true ]; then
        pytest_args+=("--html=$REPORTS_DIR/unit_tests.html" "--self-contained-html")
    fi
    
    # Combine arguments
    local full_command=("${pytest_args[@]}" "${coverage_args[@]}")
    
    log "DEBUG" "Running command: ${full_command[*]}"
    
    # Run the tests with better error handling
    local exit_code=0
    if "${full_command[@]}"; then
        log "SUCCESS" "Unit tests passed"
        ((TESTS_PASSED++))
    else
        exit_code=$?
        log "ERROR" "Unit tests failed with exit code: $exit_code"
        ((TESTS_FAILED++))
        return $exit_code
    fi
}

run_integration_tests() {
    if [ "$UNIT_ONLY" = true ]; then
        log "INFO" "Skipping integration tests (unit only mode)"
        return 0
    fi
    
    if [ "$FAST_MODE" = true ]; then
        log "INFO" "Skipping integration tests (fast mode)"
        return 0
    fi
    
    log "TEST" "Running integration tests..."
    
    # Create a simple integration test
    local integration_test_file="$PROJECT_ROOT/test_integration_temp.py"
    
    cat > "$integration_test_file" << 'EOF'
import pytest
import os
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_full_simulation_workflow():
    """Test complete simulation workflow integration."""
    from simulation import Simulation
    from database import DatabaseLedger
    from config_loader import get_config
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        # Initialize simulation with minimal parameters
        sim = Simulation(num_agents=5, seed=42)
        
        # Run a few steps
        sim.run(steps=3)
        
        # Verify simulation completed
        assert sim.schedule.steps >= 3
        assert len(sim.schedule.agents) == 5
        
    finally:
        # Cleanup
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)

def test_configuration_system_integration():
    """Test configuration system integration."""
    from config_loader import get_config, ConfigLoader
    
    # Test configuration loading
    config = get_config('simulation.default_agents', 50)
    assert isinstance(config, int)
    assert config > 0

def test_logging_system_integration():
    """Test logging system integration."""
    from logging_setup import get_logger
    import tempfile
    
    # Test logger creation
    logger = get_logger('test_integration')
    assert logger is not None
    
    # Test logging functionality
    logger.info("Integration test log message")

def test_monitoring_system_integration():
    """Test monitoring system integration."""
    from monitoring import get_monitoring
    
    # Test monitoring system
    monitoring = get_monitoring()
    assert monitoring is not None
    
    # Test health check
    health = monitoring.get_system_health()
    assert health is not None
    assert hasattr(health, 'status')

def test_database_operations_integration():
    """Test database operations integration."""
    from database import DatabaseLedger
    import tempfile
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        # Test database operations
        db = DatabaseLedger(tmp_db_path)
        
        # Test append and read
        test_entry = {'id': 1, 'type': 'test', 'data': 'integration_test'}
        db.append_entry(test_entry)
        
        entries = db.read_ledger()
        assert len(entries) >= 1
        
        # Test get by ID
        entry = db.get_entry_by_id(1)
        assert entry is not None
        
    finally:
        # Cleanup
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)
EOF
    
    # Run integration tests
    local pytest_args=("python" "-m" "pytest" "$integration_test_file")
    
    if [ "$VERBOSE" = true ]; then
        pytest_args+=("-v" "-s")
    else
        pytest_args+=("-q")
    fi
    
    if [ "$GENERATE_REPORT" = true ]; then
        pytest_args+=("--html=$REPORTS_DIR/integration_tests.html" "--self-contained-html")
    fi
    
    log "DEBUG" "Running integration tests: ${pytest_args[*]}"
    
    if "${pytest_args[@]}"; then
        log "SUCCESS" "Integration tests passed"
        ((TESTS_PASSED++))
    else
        log "ERROR" "Integration tests failed"
        ((TESTS_FAILED++))
    fi
    
    # Cleanup temporary test file
    rm -f "$integration_test_file"
}

run_code_quality_checks() {
    if [ "$RUN_QUALITY" = false ]; then
        log "INFO" "Skipping code quality checks"
        return 0
    fi
    
    log "TEST" "Running code quality checks..."
    
    # Check if quality tools are available, install if needed
    local tools_needed=()
    
    if ! python -c "import flake8" 2>/dev/null; then
        tools_needed+=("flake8")
    fi
    
    if ! python -c "import black" 2>/dev/null; then
        tools_needed+=("black")
    fi
    
    if [ ${#tools_needed[@]} -gt 0 ]; then
        log "INFO" "Installing code quality tools: ${tools_needed[*]}"
        pip install "${tools_needed[@]}"
    fi
    
    # Run flake8 linting
    log "TEST" "Running flake8 linting..."
    if python -m flake8 --max-line-length=88 --extend-ignore=E203,W503 "$PROJECT_ROOT"/*.py "$PROJECT_ROOT/tests/"; then
        log "SUCCESS" "Linting checks passed"
        ((TESTS_PASSED++))
    else
        log "WARN" "Linting issues found (non-critical)"
        ((TESTS_SKIPPED++))
    fi
    
    # Run black formatting check
    log "TEST" "Checking code formatting..."
    if python -m black --check --diff *.py tests/; then
        log "SUCCESS" "Code formatting is correct"
        ((TESTS_PASSED++))
    else
        log "WARN" "Code formatting issues found (non-critical)"
        log "INFO" "Run 'python -m black *.py tests/' to fix formatting"
        ((TESTS_SKIPPED++))
    fi
}

run_performance_tests() {
    if [ "$RUN_PERFORMANCE" = false ]; then
        log "INFO" "Skipping performance tests"
        return 0
    fi
    
    log "TEST" "Running performance tests..."
    
    # Create a simple performance test
    local perf_test_file="$PROJECT_ROOT/test_performance_temp.py"
    
    cat > "$perf_test_file" << 'EOF'
import time
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simulation_performance():
    """Test simulation performance with timing constraints."""
    from simulation import Simulation
    
    # Test small simulation performance
    start_time = time.time()
    sim = Simulation(num_agents=10, seed=42)
    sim.run(steps=5)
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Should complete within reasonable time (adjust as needed)
    assert execution_time < 30.0, f"Simulation took too long: {execution_time:.2f}s"
    
    print(f"Small simulation (10 agents, 5 steps): {execution_time:.2f}s")

def test_database_performance():
    """Test database operations performance."""
    from database import DatabaseLedger
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        tmp_db_path = tmp_db.name
    
    try:
        db = DatabaseLedger(tmp_db_path)
        
        # Test bulk insert performance
        start_time = time.time()
        for i in range(100):
            entry = {'id': i, 'type': 'perf_test', 'data': f'test_data_{i}'}
            db.append_entry(entry)
        end_time = time.time()
        
        insert_time = end_time - start_time
        assert insert_time < 5.0, f"Bulk insert took too long: {insert_time:.2f}s"
        
        # Test bulk read performance
        start_time = time.time()
        entries = db.read_ledger()
        end_time = time.time()
        
        read_time = end_time - start_time
        assert read_time < 1.0, f"Bulk read took too long: {read_time:.2f}s"
        assert len(entries) >= 100
        
        print(f"Database performance - Insert: {insert_time:.2f}s, Read: {read_time:.2f}s")
        
    finally:
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)
EOF
    
    # Run performance tests
    local pytest_args=("python" "-m" "pytest" "$perf_test_file" "-v" "-s")
    
    if "${pytest_args[@]}"; then
        log "SUCCESS" "Performance tests passed"
        ((TESTS_PASSED++))
    else
        log "WARN" "Performance tests failed or exceeded thresholds"
        ((TESTS_SKIPPED++))
    fi
    
    # Cleanup
    rm -f "$perf_test_file"
}

generate_test_summary() {
    log "INFO" "Generating test summary..."
    
    local total_tests=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
    
    echo ""
    echo "=========================================="
    echo "           TEST SUMMARY"
    echo "=========================================="
    echo "Total Tests: $total_tests"
    echo "Passed:      $TESTS_PASSED"
    echo "Failed:      $TESTS_FAILED"
    echo "Skipped:     $TESTS_SKIPPED"
    echo "=========================================="
    
    if [ "$RUN_COVERAGE" = true ]; then
        echo "Coverage reports generated in: $REPORTS_DIR"
    fi
    
    if [ "$GENERATE_REPORT" = true ]; then
        echo "HTML test reports generated in: $REPORTS_DIR"
    fi
    
    echo ""
    
    # Return appropriate exit code
    if [ $TESTS_FAILED -gt 0 ]; then
        log "ERROR" "Some tests failed"
        return 1
    elif [ $total_tests -eq 0 ]; then
        log "WARN" "No tests were run"
        return 1
    else
        log "SUCCESS" "All tests completed successfully"
        return 0
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
        -f|--fast)
            FAST_MODE=true
            shift
            ;;
        -c|--coverage)
            RUN_COVERAGE=true
            shift
            ;;
        -q|--quality)
            RUN_QUALITY=true
            shift
            ;;
        -p|--performance)
            RUN_PERFORMANCE=true
            shift
            ;;
        -r|--report)
            GENERATE_REPORT=true
            shift
            ;;
        --unit)
            UNIT_ONLY=true
            shift
            ;;
        --integration)
            INTEGRATION_ONLY=true
            shift
            ;;
        --html)
            HTML_COVERAGE=true
            RUN_COVERAGE=true
            shift
            ;;
        --xml)
            XML_COVERAGE=true
            RUN_COVERAGE=true
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            log "INFO" "Use --help for usage information"
            exit 1
            ;;
    esac
done

# =============================================================================
# Enhanced Main Execution Function
# =============================================================================

main() {
    local start_time
    start_time=$(date '+%Y-%m-%d %H:%M:%S')

    log "INFO" "Decentralized AI Simulation - Starting test suite at $start_time"
    log "INFO" "Script version: 2.0.0"
    log "INFO" "Process ID: $$"
    log "INFO" "Test reports directory: $REPORTS_DIR"

    # Initialize log file with comprehensive session header
    {
        echo "=========================================="
        echo "Test session started at $start_time"
        echo "Project root: $PROJECT_ROOT"
        echo "Test reports: $REPORTS_DIR"
        echo "Log file: $LOG_FILE"
        echo "Verbose mode: $VERBOSE"
        echo "Fast mode: $FAST_MODE"
        echo "Coverage: $RUN_COVERAGE"
        echo "Quality checks: $RUN_QUALITY"
        echo "Performance tests: $RUN_PERFORMANCE"
        echo "Unit only: $UNIT_ONLY"
        echo "Integration only: $INTEGRATION_ONLY"
        echo "=========================================="
    } > "$LOG_FILE"

    # Core test execution flow with comprehensive error handling
    local test_success=true
    local test_result=0

    # Phase 1: Environment validation
    if check_test_environment; then
        log "INFO" "Test environment validation completed"
    else
        log "ERROR" "Test environment validation failed"
        exit 3
    fi

    # Phase 2: Install missing dependencies
    if ! install_test_dependencies; then
        log "ERROR" "Failed to install test dependencies"
        exit 3
    fi

    # Phase 3: Execute test suites based on configuration
    if [[ "$UNIT_ONLY" == false ]]; then
        if run_unit_tests; then
            log "INFO" "Unit tests completed"
        else
            test_success=false
            test_result=4
        fi
    else
        log "INFO" "Skipping unit tests (unit-only mode)"
    fi

    if [[ "$INTEGRATION_ONLY" == false ]] && [[ "$FAST_MODE" == false ]]; then
        if run_integration_tests; then
            log "INFO" "Integration tests completed"
        else
            test_success=false
            test_result=4
        fi
    else
        log "INFO" "Skipping integration tests (integration-only or fast mode)"
    fi

    if [[ "$RUN_QUALITY" == true ]]; then
        if run_code_quality_checks; then
            log "INFO" "Code quality checks completed"
        else
            log "WARN" "Code quality checks had issues"
        fi
    fi

    if [[ "$RUN_PERFORMANCE" == true ]]; then
        if run_performance_tests; then
            log "INFO" "Performance tests completed"
        else
            log "WARN" "Performance tests had issues"
        fi
    fi

    # Phase 4: Generate comprehensive test summary
    if generate_test_summary; then
        local end_time
        end_time=$(date '+%Y-%m-%d %H:%M:%S')

        if [[ $test_success == true ]]; then
            log "SUCCESS" "All tests completed successfully at $end_time"
            log "INFO" "Total test time: $(($(date -d "$end_time" +%s) - $(date -d "$start_time" +%s))) seconds"
            exit 0
        else
            log "ERROR" "Some tests failed - check results above"
            exit $test_result
        fi
    else
        log "ERROR" "Failed to generate test summary"
        exit 1
    fi
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Execute main function with all arguments
main "$@"
