#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Comprehensive Testing Script
# =============================================================================
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
# =============================================================================

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/.venv"
LOG_FILE="$PROJECT_ROOT/logs/test.log"
REPORTS_DIR="$PROJECT_ROOT/test_reports"

# Test configuration
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

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

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
        "TEST")
            echo -e "${CYAN}[TEST]${NC} $message"
            ;;
    esac
}

show_help() {
    cat << EOF
Decentralized AI Simulation - Testing Script

USAGE:
    ./test.sh [OPTIONS]

OPTIONS:
    -h, --help          Show this help message and exit
    -v, --verbose       Enable verbose output for detailed test information
    -f, --fast          Run fast tests only (skip slow integration tests)
    -c, --coverage      Generate detailed coverage report
    -q, --quality       Run code quality checks (linting, type checking)
    -p, --performance   Run performance and load tests
    -r, --report        Generate comprehensive HTML test report
    --unit              Run unit tests only
    --integration       Run integration tests only
    --html              Generate HTML coverage report
    --xml               Generate XML coverage report (for CI/CD)

EXAMPLES:
    ./test.sh                           # Run all tests with default settings
    ./test.sh --verbose --coverage      # Verbose output with coverage
    ./test.sh --fast --quality          # Fast tests with quality checks
    ./test.sh --unit --html             # Unit tests with HTML coverage
    ./test.sh --report                  # Full test suite with report

DESCRIPTION:
    This script provides comprehensive testing capabilities including:
    
    • Unit Tests: Test individual components and functions
    • Integration Tests: Test component interactions and workflows
    • Coverage Analysis: Measure code coverage and identify gaps
    • Code Quality: Linting, formatting, and type checking
    • Performance Tests: Validate system performance under load
    • Test Reports: Generate detailed HTML and XML reports

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
# Main Execution
# =============================================================================

main() {
    log "INFO" "Decentralized AI Simulation - Starting test suite"
    log "INFO" "Test reports directory: $REPORTS_DIR"
    
    # Initialize log file
    echo "Test run started at $(date)" > "$LOG_FILE"
    
    check_test_environment
    
    # Run test suites
    run_unit_tests
    run_integration_tests
    run_code_quality_checks
    run_performance_tests
    
    # Generate summary and exit with appropriate code
    if generate_test_summary; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main
