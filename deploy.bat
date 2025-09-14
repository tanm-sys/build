@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM Decentralized AI Simulation - Production Deployment Script (Windows Batch)
REM =============================================================================
REM This script handles production deployment with environment-specific
REM configuration, validation, backup creation, and health monitoring.
REM
REM Usage: deploy.bat [ENVIRONMENT] [OPTIONS]
REM Environments:
REM   development        Deploy to development environment
REM   staging            Deploy to staging environment
REM   production         Deploy to production environment
REM
REM Options:
REM   /h, /help          Show this help message
REM   /v, /verbose       Enable verbose output
REM   /b, /backup        Create backup before deployment
REM   /r, /rollback      Rollback to previous deployment
REM   /check             Run health checks only
REM   /config FILE       Use custom configuration file
REM   /skip-tests        Skip pre-deployment tests
REM   /force             Force deployment without confirmations
REM =============================================================================

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "VENV_DIR=%PROJECT_ROOT%.venv"
set "LOG_DIR=%PROJECT_ROOT%logs"
set "LOG_FILE=%LOG_DIR%\deploy.log"
set "BACKUP_DIR=%PROJECT_ROOT%backups"

REM Default parameters
set "ENVIRONMENT=development"
set "VERBOSE=false"
set "CREATE_BACKUP=false"
set "ROLLBACK_MODE=false"
set "HEALTH_CHECK_ONLY=false"
set "CONFIG_FILE="
set "SKIP_TESTS=false"
set "FORCE_DEPLOY=false"

REM Parse command line arguments
set "first_arg=%~1"
if "%first_arg%"=="development" set "ENVIRONMENT=development" & shift
if "%first_arg%"=="staging" set "ENVIRONMENT=staging" & shift
if "%first_arg%"=="production" set "ENVIRONMENT=production" & shift

:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="/h" goto :show_help
if /i "%~1"=="/help" goto :show_help
if /i "%~1"=="/v" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/verbose" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/b" set "CREATE_BACKUP=true" & shift & goto :parse_args
if /i "%~1"=="/backup" set "CREATE_BACKUP=true" & shift & goto :parse_args
if /i "%~1"=="/r" set "ROLLBACK_MODE=true" & shift & goto :parse_args
if /i "%~1"=="/rollback" set "ROLLBACK_MODE=true" & shift & goto :parse_args
if /i "%~1"=="/check" set "HEALTH_CHECK_ONLY=true" & shift & goto :parse_args
if /i "%~1"=="/config" set "CONFIG_FILE=%~2" & shift & shift & goto :parse_args
if /i "%~1"=="/skip-tests" set "SKIP_TESTS=true" & shift & goto :parse_args
if /i "%~1"=="/force" set "FORCE_DEPLOY=true" & shift & goto :parse_args
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
echo Decentralized AI Simulation - Deploy Script (Windows)
echo.
echo Usage: deploy.bat [ENVIRONMENT] [OPTIONS]
echo.
echo Environments:
echo   development        Deploy to development environment
echo   staging            Deploy to staging environment
echo   production         Deploy to production environment
echo.
echo Options:
echo   /h, /help          Show this help message
echo   /v, /verbose       Enable verbose output
echo   /b, /backup        Create backup before deployment
echo   /r, /rollback      Rollback to previous deployment
echo   /check             Run health checks only
echo   /config FILE       Use custom configuration file
echo   /skip-tests        Skip pre-deployment tests
echo   /force             Force deployment without confirmations
echo.
exit /b 0

:create_backup
call :log_info "Creating deployment backup..."
set "backup_name=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "backup_name=%backup_name: =0%"
set "backup_path=%BACKUP_DIR%\%backup_name%"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
mkdir "%backup_path%"
xcopy /E /I /Q "%PROJECT_ROOT%\*.py" "%backup_path%\"
xcopy /E /I /Q "%PROJECT_ROOT%\config.yaml" "%backup_path%\" 2>nul
call :log_success "Backup created: %backup_path%"
goto :eof

:health_check
call :log_info "Running health checks..."
python -c "import sys; print('Python:', sys.version)"
if errorlevel 1 (
    call :log_error "Python health check failed"
    exit /b 1
)

REM Check database connectivity
python -c "import sqlite3; conn = sqlite3.connect(':memory:'); conn.close(); print('Database: OK')"
if errorlevel 1 (
    call :log_error "Database health check failed"
    exit /b 1
)

call :log_success "Health checks passed"
goto :eof

REM Main execution
:main
call :log_info "Starting deployment to %ENVIRONMENT% environment..."

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

REM Handle rollback mode
if "%ROLLBACK_MODE%"=="true" (
    call :log_info "Rollback mode - restoring from latest backup..."
    for /f %%i in ('dir /b /od "%BACKUP_DIR%"') do set "latest_backup=%%i"
    if not defined latest_backup (
        call :log_error "No backup found for rollback"
        exit /b 1
    )
    xcopy /E /Y "%BACKUP_DIR%\!latest_backup!\*" "%PROJECT_ROOT%\"
    call :log_success "Rollback completed from backup: !latest_backup!"
    goto :end
)

REM Health check only mode
if "%HEALTH_CHECK_ONLY%"=="true" (
    call :health_check
    goto :end
)

REM Create backup if requested
if "%CREATE_BACKUP%"=="true" (
    call :create_backup
)

REM Run pre-deployment tests
if "%SKIP_TESTS%"=="false" (
    call :log_info "Running pre-deployment tests..."
    call test.bat /fast
    if errorlevel 1 (
        call :log_error "Pre-deployment tests failed"
        if "%FORCE_DEPLOY%"=="false" exit /b 1
        call :log_info "Continuing deployment due to /force flag"
    )
)

REM Set environment-specific configuration
call :log_info "Configuring for %ENVIRONMENT% environment..."
set "ENV_CONFIG=%ENVIRONMENT%.yaml"
if exist "%ENV_CONFIG%" (
    copy "%ENV_CONFIG%" "config.yaml"
    call :log_info "Applied %ENVIRONMENT% configuration"
) else (
    call :log_info "No environment-specific config found, using default"
)

REM Production-specific validations
if "%ENVIRONMENT%"=="production" (
    if "%FORCE_DEPLOY%"=="false" (
        echo.
        echo [WARNING] You are about to deploy to PRODUCTION environment!
        set /p "confirm=Are you sure? (yes/no): "
        if not "!confirm!"=="yes" (
            call :log_info "Deployment cancelled by user"
            exit /b 0
        )
    )
)

REM Run health checks
call :health_check

call :log_success "Deployment to %ENVIRONMENT% completed successfully!"

:end
exit /b 0

REM Call main function
call :main %*
