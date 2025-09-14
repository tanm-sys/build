@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM Decentralized AI Simulation - Maintenance and Cleanup Script (Windows Batch)
REM =============================================================================
REM This script performs comprehensive cleanup including temporary files,
REM logs, cache, generated files, and database maintenance operations.
REM
REM Usage: cleanup.bat [OPTIONS]
REM Options:
REM   /h, /help          Show this help message
REM   /v, /verbose       Enable verbose output
REM   /dry-run           Show what would be cleaned without actually doing it
REM   /all               Clean everything (logs, cache, temp, database)
REM   /logs              Clean log files only
REM   /cache             Clean cache files only
REM   /temp              Clean temporary files only
REM   /database          Reset database (WARNING: destructive)
REM   /reports           Clean test reports and coverage files
REM   /force             Skip confirmation prompts
REM   /keep-days N       Keep files newer than N days (default: 7)
REM =============================================================================

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "VENV_DIR=%PROJECT_ROOT%.venv"
set "LOG_DIR=%PROJECT_ROOT%logs"
set "CACHE_DIR=%PROJECT_ROOT%__pycache__"
set "REPORTS_DIR=%PROJECT_ROOT%test_reports"
set "TEMP_DIR=%PROJECT_ROOT%temp"

REM Default parameters
set "VERBOSE=false"
set "DRY_RUN=false"
set "CLEAN_ALL=false"
set "CLEAN_LOGS=false"
set "CLEAN_CACHE=false"
set "CLEAN_TEMP=false"
set "RESET_DATABASE=false"
set "CLEAN_REPORTS=false"
set "FORCE_CLEAN=false"
set "KEEP_DAYS=7"

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="/h" goto :show_help
if /i "%~1"=="/help" goto :show_help
if /i "%~1"=="/v" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/verbose" set "VERBOSE=true" & shift & goto :parse_args
if /i "%~1"=="/dry-run" set "DRY_RUN=true" & shift & goto :parse_args
if /i "%~1"=="/all" set "CLEAN_ALL=true" & shift & goto :parse_args
if /i "%~1"=="/logs" set "CLEAN_LOGS=true" & shift & goto :parse_args
if /i "%~1"=="/cache" set "CLEAN_CACHE=true" & shift & goto :parse_args
if /i "%~1"=="/temp" set "CLEAN_TEMP=true" & shift & goto :parse_args
if /i "%~1"=="/database" set "RESET_DATABASE=true" & shift & goto :parse_args
if /i "%~1"=="/reports" set "CLEAN_REPORTS=true" & shift & goto :parse_args
if /i "%~1"=="/force" set "FORCE_CLEAN=true" & shift & goto :parse_args
if /i "%~1"=="/keep-days" set "KEEP_DAYS=%~2" & shift & shift & goto :parse_args
echo [ERROR] Unknown option: %~1
goto :show_help

:args_done

REM If /all is specified, enable all cleanup options
if "%CLEAN_ALL%"=="true" (
    set "CLEAN_LOGS=true"
    set "CLEAN_CACHE=true"
    set "CLEAN_TEMP=true"
    set "CLEAN_REPORTS=true"
)

REM If no specific options, default to safe cleanup
if "%CLEAN_LOGS%"=="false" if "%CLEAN_CACHE%"=="false" if "%CLEAN_TEMP%"=="false" if "%RESET_DATABASE%"=="false" if "%CLEAN_REPORTS%"=="false" (
    set "CLEAN_CACHE=true"
    set "CLEAN_TEMP=true"
)

REM Utility Functions
:log
set "level=%~1"
set "message=%~2"
set "timestamp=%date% %time%"
echo [%timestamp%] [%level%] %message%
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
echo Decentralized AI Simulation - Cleanup Script (Windows)
echo.
echo Usage: cleanup.bat [OPTIONS]
echo.
echo Options:
echo   /h, /help          Show this help message
echo   /v, /verbose       Enable verbose output
echo   /dry-run           Show what would be cleaned without actually doing it
echo   /all               Clean everything (logs, cache, temp, database)
echo   /logs              Clean log files only
echo   /cache             Clean cache files only
echo   /temp              Clean temporary files only
echo   /database          Reset database (WARNING: destructive)
echo   /reports           Clean test reports and coverage files
echo   /force             Skip confirmation prompts
echo   /keep-days N       Keep files newer than N days (default: 7)
echo.
exit /b 0

:clean_logs
call :log_info "Cleaning log files..."
if exist "%LOG_DIR%" (
    if "%DRY_RUN%"=="true" (
        call :log_info "[DRY RUN] Would clean: %LOG_DIR%\*.log"
    ) else (
        forfiles /p "%LOG_DIR%" /m *.log /d -%KEEP_DAYS% /c "cmd /c del @path" 2>nul
        call :log_success "Log files cleaned (kept files newer than %KEEP_DAYS% days)"
    )
) else (
    call :log_info "No log directory found"
)
goto :eof

:clean_cache
call :log_info "Cleaning Python cache files..."
if "%DRY_RUN%"=="true" (
    call :log_info "[DRY RUN] Would clean: __pycache__ directories and .pyc files"
) else (
    REM Clean __pycache__ directories
    for /d /r "%PROJECT_ROOT%" %%d in (__pycache__) do (
        if exist "%%d" (
            rmdir /s /q "%%d" 2>nul
            if "%VERBOSE%"=="true" call :log_info "Removed: %%d"
        )
    )
    
    REM Clean .pyc files
    for /r "%PROJECT_ROOT%" %%f in (*.pyc) do (
        del "%%f" 2>nul
        if "%VERBOSE%"=="true" call :log_info "Removed: %%f"
    )
    
    call :log_success "Python cache files cleaned"
)
goto :eof

:clean_temp
call :log_info "Cleaning temporary files..."
if "%DRY_RUN%"=="true" (
    call :log_info "[DRY RUN] Would clean: temp directories and temporary files"
) else (
    REM Clean temp directory
    if exist "%TEMP_DIR%" (
        rmdir /s /q "%TEMP_DIR%" 2>nul
        call :log_success "Temp directory cleaned"
    )
    
    REM Clean other temporary files
    for %%ext in (tmp bak backup old) do (
        for /r "%PROJECT_ROOT%" %%f in (*.%%ext) do (
            del "%%f" 2>nul
            if "%VERBOSE%"=="true" call :log_info "Removed: %%f"
        )
    )
    
    call :log_success "Temporary files cleaned"
)
goto :eof

:clean_reports
call :log_info "Cleaning test reports and coverage files..."
if "%DRY_RUN%"=="true" (
    call :log_info "[DRY RUN] Would clean: %REPORTS_DIR%"
) else (
    if exist "%REPORTS_DIR%" (
        rmdir /s /q "%REPORTS_DIR%" 2>nul
        call :log_success "Test reports cleaned"
    ) else (
        call :log_info "No reports directory found"
    )
    
    REM Clean coverage files
    for %%file in (.coverage coverage.xml) do (
        if exist "%PROJECT_ROOT%\%%file" (
            del "%PROJECT_ROOT%\%%file" 2>nul
            if "%VERBOSE%"=="true" call :log_info "Removed: %%file"
        )
    )
)
goto :eof

:reset_database
call :log_info "Resetting database..."
if "%FORCE_CLEAN%"=="false" (
    echo.
    echo [WARNING] This will permanently delete all simulation data!
    set /p "confirm=Are you sure you want to reset the database? (yes/no): "
    if not "!confirm!"=="yes" (
        call :log_info "Database reset cancelled"
        goto :eof
    )
)

if "%DRY_RUN%"=="true" (
    call :log_info "[DRY RUN] Would reset: simulation.db and related database files"
) else (
    for %%file in (simulation.db simulation.db-wal simulation.db-shm) do (
        if exist "%PROJECT_ROOT%\%%file" (
            del "%PROJECT_ROOT%\%%file" 2>nul
            if "%VERBOSE%"=="true" call :log_info "Removed: %%file"
        )
    )
    call :log_success "Database reset completed"
)
goto :eof

REM Main execution
:main
call :log_info "Starting cleanup process..."

if "%DRY_RUN%"=="true" (
    call :log_info "DRY RUN MODE - No files will be actually deleted"
)

REM Execute cleanup operations
if "%CLEAN_LOGS%"=="true" call :clean_logs
if "%CLEAN_CACHE%"=="true" call :clean_cache
if "%CLEAN_TEMP%"=="true" call :clean_temp
if "%CLEAN_REPORTS%"=="true" call :clean_reports
if "%RESET_DATABASE%"=="true" call :reset_database

call :log_success "Cleanup process completed!"

if "%DRY_RUN%"=="true" (
    call :log_info "To actually perform cleanup, run without /dry-run flag"
)

exit /b 0

REM Call main function
call :main %*
