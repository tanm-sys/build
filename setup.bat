@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM Decentralized AI Simulation - Project Setup Script (Windows Batch)
REM =============================================================================
REM This script sets up the complete development environment for the 
REM decentralized AI simulation project including virtual environment,
REM dependencies, configuration, database initialization, and health checks.
REM
REM Usage: setup.bat [OPTIONS]
REM Options:
REM   /h, /help          Show this help message
REM   /v, /verbose       Enable verbose output
REM   /f, /force         Force reinstall even if environment exists
REM   /p, /python PATH   Specify Python executable path (default: python)
REM   /skip-tests        Skip running initial tests after setup
REM   /dev               Setup for development (includes dev dependencies)
REM =============================================================================

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "VENV_DIR=%PROJECT_ROOT%.venv"
set "LOG_FILE=%PROJECT_ROOT%setup.log"
set "PYTHON_CMD=python"
set "VERBOSE=false"
set "FORCE_REINSTALL=false"
set "SKIP_TESTS=false"
set "DEV_MODE=false"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="/h" goto :show_help
if /i "%~1"=="/help" goto :show_help
if /i "%~1"=="/v" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/verbose" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/f" set "FORCE_REINSTALL=true" & shift & goto :parse_args
if /i "%~1"=="/force" set "FORCE_REINSTALL=true" & shift & goto :parse_args
if /i "%~1"=="/p" set "PYTHON_CMD=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/python" set "PYTHON_CMD=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/skip-tests" set "SKIP_TESTS=true" & shift & goto :parse_args
if /i "%~1"=="/dev" set "DEV_MODE=true" & shift & goto :parse_args
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
echo Decentralized AI Simulation - Setup Script (Windows)
echo.
echo Usage: setup.bat [OPTIONS]
echo.
echo Options:
echo   /h, /help          Show this help message
echo   /v, /verbose       Enable verbose output
echo   /f, /force         Force reinstall even if environment exists
echo   /p, /python PATH   Specify Python executable path (default: python)
echo   /skip-tests        Skip running initial tests after setup
echo   /dev               Setup for development (includes dev dependencies)
echo.
exit /b 0

REM Main execution
:main
call :log_info "Starting Decentralized AI Simulation setup..."

REM Check Python installation
call :log_info "Checking Python installation..."
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Python not found. Please install Python 3.8+ and ensure it's in PATH"
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set "PYTHON_VERSION=%%i"
call :log_info "Found Python %PYTHON_VERSION%"

REM Check if virtual environment exists
if exist "%VENV_DIR%" (
    if "%FORCE_REINSTALL%"=="true" (
        call :log_info "Removing existing virtual environment..."
        rmdir /s /q "%VENV_DIR%"
    ) else (
        call :log_info "Virtual environment already exists. Use /force to reinstall."
        goto :activate_venv
    )
)

REM Create virtual environment
call :log_info "Creating virtual environment..."
%PYTHON_CMD% -m venv "%VENV_DIR%"
if errorlevel 1 (
    call :log_error "Failed to create virtual environment"
    exit /b 1
)

:activate_venv
REM Activate virtual environment
call :log_info "Activating virtual environment..."
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
call :log_info "Upgrading pip..."
python -m pip install --upgrade pip

REM Install dependencies
call :log_info "Installing dependencies..."
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        call :log_error "Failed to install dependencies"
        exit /b 1
    )
) else (
    call :log_error "requirements.txt not found"
    exit /b 1
)

REM Install development dependencies if in dev mode
if "%DEV_MODE%"=="true" (
    call :log_info "Installing development dependencies..."
    pip install pytest pytest-cov black flake8 mypy
)

REM Create necessary directories
call :log_info "Creating necessary directories..."
if not exist "logs" mkdir logs
if not exist "test_reports" mkdir test_reports
if not exist "backups" mkdir backups

REM Initialize configuration
call :log_info "Initializing configuration..."
if not exist "config.yaml" (
    call :log_info "Creating default configuration file..."
    echo # Default configuration > config.yaml
)

REM Run initial tests if not skipped
if "%SKIP_TESTS%"=="false" (
    call :log_info "Running initial tests..."
    python -m pytest tests/ -v
    if errorlevel 1 (
        call :log_error "Initial tests failed"
        exit /b 1
    )
)

call :log_success "Setup completed successfully!"
call :log_info "Virtual environment created at: %VENV_DIR%"
call :log_info "To activate: %VENV_DIR%\Scripts\activate.bat"
call :log_info "To run simulation: run.bat"

exit /b 0

REM Call main function
call :main %*
