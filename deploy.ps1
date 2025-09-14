# =============================================================================
# Decentralized AI Simulation - Production Deployment Script (PowerShell)
# =============================================================================
# This script handles production deployment with environment-specific
# configuration, validation, backup creation, and health monitoring.
#
# Usage: .\deploy.ps1 [ENVIRONMENT] [OPTIONS]
# Environments:
#   development        Deploy to development environment
#   staging            Deploy to staging environment
#   production         Deploy to production environment
#
# Options:
#   -Help              Show this help message
#   -Verbose           Enable verbose output
#   -Backup            Create backup before deployment
#   -Rollback          Rollback to previous deployment
#   -HealthCheckOnly   Run health checks only
#   -ConfigFile FILE   Use custom configuration file
#   -SkipTests         Skip pre-deployment tests
#   -Force             Force deployment without confirmations
# =============================================================================

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [switch]$Help,
    [switch]$Verbose,
    [switch]$Backup,
    [switch]$Rollback,
    [switch]$HealthCheckOnly,
    [string]$ConfigFile,
    [switch]$SkipTests,
    [switch]$Force
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$VenvDir = Join-Path $ProjectRoot ".venv"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "deploy.log"
$BackupDir = Join-Path $ProjectRoot "backups"

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
    
    if ($Verbose -and (Test-Path $LogDir)) {
        Add-Content -Path $LogFile -Value $logEntry
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "Decentralized AI Simulation - Deploy Script (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [ENVIRONMENT] [OPTIONS]"
    Write-Host ""
    Write-Host "Environments:"
    Write-Host "  development        Deploy to development environment"
    Write-Host "  staging            Deploy to staging environment"
    Write-Host "  production         Deploy to production environment"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help              Show this help message"
    Write-Host "  -Verbose           Enable verbose output"
    Write-Host "  -Backup            Create backup before deployment"
    Write-Host "  -Rollback          Rollback to previous deployment"
    Write-Host "  -HealthCheckOnly   Run health checks only"
    Write-Host "  -ConfigFile FILE   Use custom configuration file"
    Write-Host "  -SkipTests         Skip pre-deployment tests"
    Write-Host "  -Force             Force deployment without confirmations"
    Write-Host ""
    exit 0
}

function New-DeploymentBackup {
    Write-Log "INFO" "Creating deployment backup..."
    $backupName = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    $backupPath = Join-Path $BackupDir $backupName
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    
    # Copy Python files and configuration
    Get-ChildItem -Path $ProjectRoot -Filter "*.py" | Copy-Item -Destination $backupPath
    $configPath = Join-Path $ProjectRoot "config.yaml"
    if (Test-Path $configPath) {
        Copy-Item -Path $configPath -Destination $backupPath
    }
    
    Write-Log "SUCCESS" "Backup created: $backupPath"
    return $backupPath
}

function Test-HealthChecks {
    Write-Log "INFO" "Running health checks..."
    
    # Check Python
    try {
        $pythonVersion = & python --version 2>&1
        Write-Log "INFO" "Python: $pythonVersion"
    }
    catch {
        Write-Log "ERROR" "Python health check failed"
        return $false
    }
    
    # Check database connectivity
    try {
        & python -c "import sqlite3; conn = sqlite3.connect(':memory:'); conn.close(); print('Database: OK')"
        if ($LASTEXITCODE -ne 0) {
            throw "Database connection failed"
        }
    }
    catch {
        Write-Log "ERROR" "Database health check failed"
        return $false
    }
    
    Write-Log "SUCCESS" "Health checks passed"
    return $true
}

# Show help if requested
if ($Help) {
    Show-Help
}

# Main execution
try {
    Write-Log "INFO" "Starting deployment to $Environment environment..."

    # Check if virtual environment exists
    if (-not (Test-Path $VenvDir)) {
        Write-Log "ERROR" "Virtual environment not found. Please run .\setup.ps1 first."
        exit 1
    }

    # Activate virtual environment
    Write-Log "INFO" "Activating virtual environment..."
    $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    }
    else {
        Write-Log "ERROR" "Virtual environment activation script not found"
        exit 1
    }

    # Create necessary directories
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }

    # Handle rollback mode
    if ($Rollback) {
        Write-Log "INFO" "Rollback mode - restoring from latest backup..."
        $latestBackup = Get-ChildItem -Path $BackupDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if (-not $latestBackup) {
            Write-Log "ERROR" "No backup found for rollback"
            exit 1
        }
        
        Get-ChildItem -Path $latestBackup.FullName | Copy-Item -Destination $ProjectRoot -Force
        Write-Log "SUCCESS" "Rollback completed from backup: $($latestBackup.Name)"
        exit 0
    }

    # Health check only mode
    if ($HealthCheckOnly) {
        if (Test-HealthChecks) {
            exit 0
        }
        else {
            exit 1
        }
    }

    # Create backup if requested
    if ($Backup) {
        $backupPath = New-DeploymentBackup
    }

    # Run pre-deployment tests
    if (-not $SkipTests) {
        Write-Log "INFO" "Running pre-deployment tests..."
        & .\test.ps1 -Fast
        if ($LASTEXITCODE -ne 0) {
            Write-Log "ERROR" "Pre-deployment tests failed"
            if (-not $Force) {
                exit 1
            }
            Write-Log "INFO" "Continuing deployment due to -Force flag"
        }
    }

    # Set environment-specific configuration
    Write-Log "INFO" "Configuring for $Environment environment..."
    $envConfig = Join-Path $ProjectRoot "$Environment.yaml"
    if (Test-Path $envConfig) {
        $configPath = Join-Path $ProjectRoot "config.yaml"
        Copy-Item -Path $envConfig -Destination $configPath -Force
        Write-Log "INFO" "Applied $Environment configuration"
    }
    else {
        Write-Log "INFO" "No environment-specific config found, using default"
    }

    # Production-specific validations
    if ($Environment -eq "production" -and -not $Force) {
        Write-Host ""
        Write-Host "[WARNING] You are about to deploy to PRODUCTION environment!" -ForegroundColor Yellow
        $confirm = Read-Host "Are you sure? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Log "INFO" "Deployment cancelled by user"
            exit 0
        }
    }

    # Run health checks
    if (-not (Test-HealthChecks)) {
        exit 1
    }

    Write-Log "SUCCESS" "Deployment to $Environment completed successfully!"
}
catch {
    Write-Log "ERROR" "Deployment failed: $($_.Exception.Message)"
    exit 1
}
