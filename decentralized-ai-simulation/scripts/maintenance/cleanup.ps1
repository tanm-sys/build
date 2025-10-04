# =============================================================================
# Decentralized AI Simulation - Maintenance and Cleanup Script (PowerShell)
# =============================================================================
# This script performs comprehensive cleanup including temporary files,
# logs, cache, generated files, and database maintenance operations.
#
# Usage: .\cleanup.ps1 [OPTIONS]
# Options:
#   -Help              Show this help message
#   -Verbose           Enable verbose output
#   -DryRun            Show what would be cleaned without actually doing it
#   -All               Clean everything (logs, cache, temp, database)
#   -Logs              Clean log files only
#   -Cache             Clean cache files only
#   -Temp              Clean temporary files only
#   -Database          Reset database (WARNING: destructive)
#   -Reports           Clean test reports and coverage files
#   -Force             Skip confirmation prompts
#   -KeepDays N        Keep files newer than N days (default: 7)
# =============================================================================

[CmdletBinding()]
param(
    [switch]$Help,
    [switch]$Verbose,
    [switch]$DryRun,
    [switch]$All,
    [switch]$Logs,
    [switch]$Cache,
    [switch]$Temp,
    [switch]$Database,
    [switch]$Reports,
    [switch]$Force,
    [int]$KeepDays = 7
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$VenvDir = Join-Path $ProjectRoot ".venv"
$LogDir = Join-Path $ProjectRoot "logs"
$CacheDir = Join-Path $ProjectRoot "__pycache__"
$ReportsDir = Join-Path $ProjectRoot "test_reports"
$TempDir = Join-Path $ProjectRoot "temp"

# Utility Functions
function Write-Log {
    param(
        [string]$Level,
        [string]$Message
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        default { Write-Host $logEntry -ForegroundColor White }
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "Decentralized AI Simulation - Cleanup Script (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\cleanup.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help              Show this help message"
    Write-Host "  -Verbose           Enable verbose output"
    Write-Host "  -DryRun            Show what would be cleaned without actually doing it"
    Write-Host "  -All               Clean everything (logs, cache, temp, database)"
    Write-Host "  -Logs              Clean log files only"
    Write-Host "  -Cache             Clean cache files only"
    Write-Host "  -Temp              Clean temporary files only"
    Write-Host "  -Database          Reset database (WARNING: destructive)"
    Write-Host "  -Reports           Clean test reports and coverage files"
    Write-Host "  -Force             Skip confirmation prompts"
    Write-Host "  -KeepDays N        Keep files newer than N days (default: 7)"
    Write-Host ""
    exit 0
}

function Remove-LogFiles {
    Write-Log "INFO" "Cleaning log files..."
    if (Test-Path $LogDir) {
        $cutoffDate = (Get-Date).AddDays(-$KeepDays)
        $logFiles = Get-ChildItem -Path $LogDir -Filter "*.log" | Where-Object { $_.LastWriteTime -lt $cutoffDate }
        
        if ($logFiles) {
            foreach ($file in $logFiles) {
                if ($DryRun) {
                    Write-Log "INFO" "[DRY RUN] Would remove: $($file.FullName)"
                }
                else {
                    Remove-Item -Path $file.FullName -Force
                    if ($Verbose) {
                        Write-Log "INFO" "Removed: $($file.FullName)"
                    }
                }
            }
            Write-Log "SUCCESS" "Log files cleaned (kept files newer than $KeepDays days)"
        }
        else {
            Write-Log "INFO" "No old log files found"
        }
    }
    else {
        Write-Log "INFO" "No log directory found"
    }
}

function Remove-CacheFiles {
    Write-Log "INFO" "Cleaning Python cache files..."
    
    if ($DryRun) {
        Write-Log "INFO" "[DRY RUN] Would clean: __pycache__ directories and .pyc files"
    }
    else {
        # Clean __pycache__ directories
        $pycacheDirs = Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue
        foreach ($dir in $pycacheDirs) {
            $fullPath = Join-Path $ProjectRoot $dir
            Remove-Item -Path $fullPath -Recurse -Force -ErrorAction SilentlyContinue
            if ($Verbose) {
                Write-Log "INFO" "Removed: $fullPath"
            }
        }
        
        # Clean .pyc files
        $pycFiles = Get-ChildItem -Path $ProjectRoot -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
        foreach ($file in $pycFiles) {
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            if ($Verbose) {
                Write-Log "INFO" "Removed: $($file.FullName)"
            }
        }
        
        Write-Log "SUCCESS" "Python cache files cleaned"
    }
}

function Remove-TempFiles {
    Write-Log "INFO" "Cleaning temporary files..."
    
    if ($DryRun) {
        Write-Log "INFO" "[DRY RUN] Would clean: temp directories and temporary files"
    }
    else {
        # Clean temp directory
        if (Test-Path $TempDir) {
            Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
            Write-Log "SUCCESS" "Temp directory cleaned"
        }
        
        # Clean other temporary files
        $tempExtensions = @("*.tmp", "*.bak", "*.backup", "*.old")
        foreach ($pattern in $tempExtensions) {
            $tempFiles = Get-ChildItem -Path $ProjectRoot -Recurse -Filter $pattern -ErrorAction SilentlyContinue
            foreach ($file in $tempFiles) {
                Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
                if ($Verbose) {
                    Write-Log "INFO" "Removed: $($file.FullName)"
                }
            }
        }
        
        Write-Log "SUCCESS" "Temporary files cleaned"
    }
}

function Remove-ReportFiles {
    Write-Log "INFO" "Cleaning test reports and coverage files..."
    
    if ($DryRun) {
        Write-Log "INFO" "[DRY RUN] Would clean: $ReportsDir"
    }
    else {
        if (Test-Path $ReportsDir) {
            Remove-Item -Path $ReportsDir -Recurse -Force -ErrorAction SilentlyContinue
            Write-Log "SUCCESS" "Test reports cleaned"
        }
        else {
            Write-Log "INFO" "No reports directory found"
        }
        
        # Clean coverage files
        $coverageFiles = @(".coverage", "coverage.xml")
        foreach ($file in $coverageFiles) {
            $filePath = Join-Path $ProjectRoot $file
            if (Test-Path $filePath) {
                Remove-Item -Path $filePath -Force -ErrorAction SilentlyContinue
                if ($Verbose) {
                    Write-Log "INFO" "Removed: $filePath"
                }
            }
        }
    }
}

function Reset-Database {
    Write-Log "INFO" "Resetting database..."
    
    if (-not $Force) {
        Write-Host ""
        Write-Host "[WARNING] This will permanently delete all simulation data!" -ForegroundColor Yellow
        $confirm = Read-Host "Are you sure you want to reset the database? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Log "INFO" "Database reset cancelled"
            return
        }
    }
    
    if ($DryRun) {
        Write-Log "INFO" "[DRY RUN] Would reset: simulation.db and related database files"
    }
    else {
        $dbFiles = @("simulation.db", "simulation.db-wal", "simulation.db-shm", "ledger.db", "ledger.db-wal", "ledger.db-shm")
        foreach ($file in $dbFiles) {
            $filePath = Join-Path $ProjectRoot $file
            if (Test-Path $filePath) {
                Remove-Item -Path $filePath -Force -ErrorAction SilentlyContinue
                if ($Verbose) {
                    Write-Log "INFO" "Removed: $filePath"
                }
            }
        }
        Write-Log "SUCCESS" "Database reset completed"
    }
}

# Show help if requested
if ($Help) {
    Show-Help
}

# If -All is specified, enable all cleanup options
if ($All) {
    $Logs = $true
    $Cache = $true
    $Temp = $true
    $Reports = $true
}

# If no specific options, default to safe cleanup
if (-not ($Logs -or $Cache -or $Temp -or $Database -or $Reports)) {
    $Cache = $true
    $Temp = $true
}

# Main execution
try {
    Write-Log "INFO" "Starting cleanup process..."
    
    if ($DryRun) {
        Write-Log "INFO" "DRY RUN MODE - No files will be actually deleted"
    }
    
    # Execute cleanup operations
    if ($Logs) { Remove-LogFiles }
    if ($Cache) { Remove-CacheFiles }
    if ($Temp) { Remove-TempFiles }
    if ($Reports) { Remove-ReportFiles }
    if ($Database) { Reset-Database }
    
    Write-Log "SUCCESS" "Cleanup process completed!"
    
    if ($DryRun) {
        Write-Log "INFO" "To actually perform cleanup, run without -DryRun flag"
    }
}
catch {
    Write-Log "ERROR" "Cleanup failed: $($_.Exception.Message)"
    exit 1
}
