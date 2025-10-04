@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM Decentralized AI Simulation - Comprehensive Testing Script (Windows Batch)
REM =============================================================================
REM This script runs comprehensive tests including unit tests, integration tests,
REM code quality checks, coverage reporting, and performance validation.
REM
REM Usage: test.bat [OPTIONS]
REM Options:
REM   /h, /help          Show this help message
REM   /v, /verbose       Enable verbose output
REM   /f, /fast          Run fast tests only (skip slow integration tests)
REM   /c, /coverage      Generate detailed coverage report
REM   /q, /quality       Run code quality checks (linting, formatting)
REM   /p, /performance   Run performance tests
REM   /r, /report        Generate comprehensive test report
REM   /unit              Run unit tests only
REM   /integration       Run integration tests only
REM   /html              Generate HTML coverage report
REM   /xml               Generate XML coverage report for CI
REM =============================================================================

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "VENV_DIR=%PROJECT_ROOT%.venv"
set "LOG_DIR=%PROJECT_ROOT%logs"
set "LOG_FILE=%LOG_DIR%\test.log"
set "REPORTS_DIR=%PROJECT_ROOT%test_reports"

REM Test configuration
set "VERBOSE=false"
set "FAST_MODE=false"
set "RUN_COVERAGE=false"
set "RUN_QUALITY=false"
set "RUN_PERFORMANCE=false"
set "GENERATE_REPORT=false"
set "UNIT_ONLY=false"
set "INTEGRATION_ONLY=false"
set "HTML_COVERAGE=false"
set "XML_COVERAGE=false"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="/h" goto :show_help
if /i "%~1"=="/help" goto :show_help
if /i "%~1"=="/v" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/verbose" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/f" set "FAST_MODE=true" & shift & goto :parse_args
if /i "%~1"=="/fast" set "FAST_MODE=true" & shift & goto :parse_args
if /i "%~1"=="/c" set "RUN_COVERAGE=true" & shift & goto :parse_args
if /i "%~1"=="/coverage" set "RUN_COVERAGE=true" & shift & goto :parse_args
if /i "%~1"=="/q" set "RUN_QUALITY=true" & shift & goto :parse_args
if /i "%~1"=="/quality" set "RUN_QUALITY=true" & shift & goto :parse_args
if /i "%~1"=="/p" set "RUN_PERFORMANCE=true" & shift & goto :parse_args
if /i "%~1"=="/performance" set "RUN_PERFORMANCE=true" & shift & goto :parse_args
if /i "%~1"=="/r" set "GENERATE_REPORT=true" & shift & goto :parse_args
if /i "%~1"=="/report" set "GENERATE_REPORT=true" & shift & goto :parse_args
if /i "%~1"=="/unit" set "UNIT_ONLY=true" & shift & goto :parse_args
if /i "%~1"=="/integration" set "INTEGRATION_ONLY=true" & shift & goto :parse_args
if /i "%~1"=="/html" set "HTML_COVERAGE=true" & shift & goto :parse_args
if /i "%~1"=="/xml" set "XML_COVERAGE=true" & shift & goto :parse_args
echo [ERROR] Unknown option: %~1
goto :show_help

:args_done

REM Utility Functions
:log
set "level=%~1"
set "message=%~2"
set "timestamp=%date% %time%"
echo [%timestamp%] [%level%] %message%
if "%VERBOSE%"=="true" echo [%timestamp%] [%level%] %message% >> "%LOG_FILE%"
goto :eof

:log_info
call :log "INFO" "%~1"
goto :eof

:log_error
call :log "ERROR" "%~1"
goto :eof

:log_success
call :log "SUCCESS" "%~1"
goto :eof

:show_help
echo.
echo Decentralized AI Simulation - Test Script (Windows)
echo.
echo Usage: test.bat [OPTIONS]
echo.
echo Options:
echo   /h, /help          Show this help message
echo   /v, /verbose       Enable verbose output
echo   /f, /fast          Run fast tests only (skip slow integration tests)
echo   /c, /coverage      Generate detailed coverage report
echo   /q, /quality       Run code quality checks (linting, formatting)
echo   /p, /performance   Run performance tests
echo   /r, /report        Generate comprehensive test report
echo   /unit              Run unit tests only
echo   /integration       Run integration tests only
echo   /html              Generate HTML coverage report
echo   /xml               Generate XML coverage report for CI
echo.
exit /b 0

REM Main execution
:main
call :log_info "Starting comprehensive testing suite..."

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    call :log_error "Virtual environment not found. Please run setup.bat first."
    exit /b 1
)

REM Activate virtual environment
call :log_info "Activating virtual environment..."
call "%VENV_DIR%\Scripts\activate.bat"

REM Create necessary directories
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%REPORTS_DIR%" mkdir "%REPORTS_DIR%"

REM Install test dependencies if needed
call :log_info "Checking test dependencies..."
pip show pytest >nul 2>&1
if errorlevel 1 (
    call :log_info "Installing test dependencies..."
    pip install pytest pytest-cov pytest-html pytest-xdist
)

REM Run code quality checks if requested
if "%RUN_QUALITY%"=="true" (
    call :log_info "Running code quality checks..."
    
    REM Check if quality tools are installed
    pip show black flake8 mypy >nul 2>&1
    if errorlevel 1 (
        call :log_info "Installing code quality tools..."
        pip install black flake8 mypy
    )
    
    call :log_info "Running Black formatter check..."
    black --check --diff .
    
    call :log_info "Running Flake8 linter..."
    flake8 . --max-line-length=88 --extend-ignore=E203,W503
    
    call :log_info "Running MyPy type checker..."
    mypy . --ignore-missing-imports
)

REM Build pytest arguments
set "PYTEST_ARGS=-v"
if "%VERBOSE%"=="true" set "PYTEST_ARGS=%PYTEST_ARGS% -s"
if "%FAST_MODE%"=="true" set "PYTEST_ARGS=%PYTEST_ARGS% -m 'not slow'"

REM Add coverage options
if "%RUN_COVERAGE%"=="true" (
    set "PYTEST_ARGS=%PYTEST_ARGS% --cov=. --cov-report=term-missing"
    if "%HTML_COVERAGE%"=="true" set "PYTEST_ARGS=%PYTEST_ARGS% --cov-report=html:%REPORTS_DIR%\coverage_html"
    if "%XML_COVERAGE%"=="true" set "PYTEST_ARGS=%PYTEST_ARGS% --cov-report=xml:%REPORTS_DIR%\coverage.xml"
)

REM Add report generation
if "%GENERATE_REPORT%"=="true" (
    set "PYTEST_ARGS=%PYTEST_ARGS% --html=%REPORTS_DIR%\test_report.html --self-contained-html"
)

REM Run tests based on selection
if "%UNIT_ONLY%"=="true" (
    call :log_info "Running unit tests only..."
    python -m pytest tests/test_*.py %PYTEST_ARGS%
) else if "%INTEGRATION_ONLY%"=="true" (
    call :log_info "Running integration tests only..."
    python -m pytest tests/integration/ %PYTEST_ARGS%
) else (
    call :log_info "Running all tests..."
    python -m pytest tests/ %PYTEST_ARGS%
)

set "TEST_EXIT_CODE=%errorlevel%"

REM Run performance tests if requested
if "%RUN_PERFORMANCE%"=="true" (
    call :log_info "Running performance tests..."
    python -m pytest tests/performance/ -v --benchmark-only
)

REM Generate summary
if %TEST_EXIT_CODE% equ 0 (
    call :log_success "All tests passed successfully!"
) else (
    call :log_error "Some tests failed. Exit code: %TEST_EXIT_CODE%"
)

REM Show report locations
if "%GENERATE_REPORT%"=="true" (
    call :log_info "Test report generated: %REPORTS_DIR%\test_report.html"
)
if "%HTML_COVERAGE%"=="true" (
    call :log_info "Coverage report generated: %REPORTS_DIR%\coverage_html\index.html"
)

exit /b %TEST_EXIT_CODE%

REM Call main function
call :main %*
