@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM Decentralized AI Simulation - Main Execution Script (Windows Batch)
REM =============================================================================
REM This script runs the decentralized AI simulation with configurable parameters
REM and supports different execution modes including CLI, UI, and testing modes.
REM
REM Usage: run.bat [MODE] [OPTIONS]
REM Modes:
REM   cli                 Run simulation in CLI mode (default)
REM   ui                  Launch Streamlit web interface
REM   test                Run in test mode with minimal agents
REM   demo                Run demonstration with preset parameters
REM
REM Options:
REM   /h, /help          Show this help message
REM   /v, /verbose       Enable verbose output
REM   /a, /agents N      Number of agents (default: from config)
REM   /s, /steps N       Number of simulation steps (default: from config)
REM   /p, /parallel      Enable parallel execution with Ray
REM   /seed N            Set random seed for reproducibility
REM   /config FILE       Use custom configuration file
REM   /env ENV           Set environment (development/production)
REM   /log-level LEVEL   Set logging level (DEBUG/INFO/WARNING/ERROR)
REM =============================================================================

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "VENV_DIR=%PROJECT_ROOT%.venv"
set "LOG_DIR=%PROJECT_ROOT%logs"
set "LOG_FILE=%LOG_DIR%\run.log"

REM Default parameters
set "MODE=cli"
set "VERBOSE=false"
set "AGENTS="
set "STEPS="
set "PARALLEL=false"
set "SEED="
set "CONFIG_FILE="
set "ENVIRONMENT="
set "LOG_LEVEL="

REM Parse command line arguments
set "first_arg=%~1"
if "%first_arg%"=="cli" set "MODE=cli" & shift
if "%first_arg%"=="ui" set "MODE=ui" & shift
if "%first_arg%"=="test" set "MODE=test" & shift
if "%first_arg%"=="demo" set "MODE=demo" & shift

:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="/h" goto :show_help
if /i "%~1"=="/help" goto :show_help
if /i "%~1"=="/v" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/verbose" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/a" set "AGENTS=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/agents" set "AGENTS=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/s" set "STEPS=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/steps" set "STEPS=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/p" set "PARALLEL=true" & shift & goto :parse_args
if /i "%~1"=="/parallel" set "PARALLEL=true" & shift & goto :parse_args
if /i "%~1"=="/seed" set "SEED=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/config" set "CONFIG_FILE=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/env" set "ENVIRONMENT=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/log-level" set "LOG_LEVEL=%~2" & shift & shift & goto :parse_args
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

:show_help
echo.
echo Decentralized AI Simulation - Run Script (Windows)
echo.
echo Usage: run.bat [MODE] [OPTIONS]
echo.
echo Modes:
echo   cli                 Run simulation in CLI mode (default)
echo   ui                  Launch Streamlit web interface
echo   test                Run in test mode with minimal agents
echo   demo                Run demonstration with preset parameters
echo.
echo Options:
echo   /h, /help          Show this help message
echo   /v, /verbose       Enable verbose output
echo   /a, /agents N      Number of agents (default: from config)
echo   /s, /steps N       Number of simulation steps (default: from config)
echo   /p, /parallel      Enable parallel execution with Ray
echo   /seed N            Set random seed for reproducibility
echo   /config FILE       Use custom configuration file
echo   /env ENV           Set environment (development/production)
echo   /log-level LEVEL   Set logging level (DEBUG/INFO/WARNING/ERROR)
echo.
exit /b 0

REM Main execution
:main
call :log_info "Starting Decentralized AI Simulation..."

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    call :log_error "Virtual environment not found. Please run setup.bat first."
    exit /b 1
)

REM Activate virtual environment
call :log_info "Activating virtual environment..."
call "%VENV_DIR%\Scripts\activate.bat"

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Set environment variables
if not "%ENVIRONMENT%"=="" set "ENVIRONMENT=%ENVIRONMENT%"
if not "%LOG_LEVEL%"=="" set "LOG_LEVEL=%LOG_LEVEL%"

REM Build command arguments
set "CMD_ARGS="
if not "%AGENTS%"=="" set "CMD_ARGS=%CMD_ARGS% --agents %AGENTS%"
if not "%STEPS%"=="" set "CMD_ARGS=%CMD_ARGS% --steps %STEPS%"
if "%PARALLEL%"=="true" set "CMD_ARGS=%CMD_ARGS% --parallel"
if not "%SEED%"=="" set "CMD_ARGS=%CMD_ARGS% --seed %SEED%"
if not "%CONFIG_FILE%"=="" set "CMD_ARGS=%CMD_ARGS% --config %CONFIG_FILE%"
if "%VERBOSE%"=="true" set "CMD_ARGS=%CMD_ARGS% --verbose"

REM Execute based on mode
if "%MODE%"=="cli" (
    call :log_info "Running simulation in CLI mode..."
    python decentralized_ai_simulation.py%CMD_ARGS%
) else if "%MODE%"=="ui" (
    call :log_info "Launching Streamlit web interface..."
    streamlit run streamlit_app.py%CMD_ARGS%
) else if "%MODE%"=="test" (
    call :log_info "Running in test mode..."
    python decentralized_ai_simulation.py --agents 5 --steps 10%CMD_ARGS%
) else if "%MODE%"=="demo" (
    call :log_info "Running demonstration..."
    python decentralized_ai_simulation.py --agents 20 --steps 50 --parallel%CMD_ARGS%
) else (
    call :log_error "Unknown mode: %MODE%"
    exit /b 1
)

if errorlevel 1 (
    call :log_error "Simulation failed with exit code %errorlevel%"
    exit /b %errorlevel%
)

call :log_info "Simulation completed successfully!"
exit /b 0

REM Call main function
call :main %*
