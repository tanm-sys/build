# =============================================================================
# Decentralized AI Simulation - Project Setup Script (PowerShell)
# =============================================================================
# This script sets up the complete development environment for the 
# decentralized AI simulation project including virtual environment,
# dependencies, configuration, database initialization, and health checks.
#
# Usage: .\setup.ps1 [OPTIONS]
# Options:
#   -Help              Show this help message
#   -Verbose           Enable verbose output
#   -Force             Force reinstall even if environment exists
#   -PythonPath PATH   Specify Python executable path (default: python)
#   -SkipTests         Skip running initial tests after setup
#   -DevMode           Setup for development (includes dev dependencies)
# =============================================================================

[CmdletBinding()]
param(
    [switch]$Help,
    [switch]$Verbose,
    [switch]$Force,
    [string]$PythonPath = "python",
    [switch]$SkipTests,
    [switch]$DevMode
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$VenvDir = Join-Path $ProjectRoot ".venv"
$LogFile = Join-Path $ProjectRoot "setup.log"

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
    
    if ($Verbose) {
        Add-Content -Path $LogFile -Value $logEntry
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "Decentralized AI Simulation - Setup Script (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\setup.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help              Show this help message"
    Write-Host "  -Verbose           Enable verbose output"
    Write-Host "  -Force             Force reinstall even if environment exists"
    Write-Host "  -PythonPath PATH   Specify Python executable path (default: python)"
    Write-Host "  -SkipTests         Skip running initial tests after setup"
    Write-Host "  -DevMode           Setup for development (includes dev dependencies)"
    Write-Host ""
    exit 0
}

# Show help if requested
if ($Help) {
    Show-Help
}

# Main execution
try {
    Write-Log "INFO" "Starting Decentralized AI Simulation setup..."

    # Check Python installation
    Write-Log "INFO" "Checking Python installation..."
    try {
        $pythonVersion = & $PythonPath --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python command failed"
        }
        Write-Log "INFO" "Found $pythonVersion"
    }
    catch {
        Write-Log "ERROR" "Python not found. Please install Python 3.8+ and ensure it's in PATH"
        exit 1
    }

    # Check if virtual environment exists
    if (Test-Path $VenvDir) {
        if ($Force) {
            Write-Log "INFO" "Removing existing virtual environment..."
            Remove-Item -Path $VenvDir -Recurse -Force
        }
        else {
            Write-Log "INFO" "Virtual environment already exists. Use -Force to reinstall."
            $activateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
            if (Test-Path $activateScript) {
                Write-Log "INFO" "To activate: & '$activateScript'"
            }
            exit 0
        }
    }

    # Create virtual environment
    Write-Log "INFO" "Creating virtual environment..."
    & $PythonPath -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR" "Failed to create virtual environment"
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

    # Upgrade pip
    Write-Log "INFO" "Upgrading pip..."
    & python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR" "Failed to upgrade pip"
        exit 1
    }

    # Install dependencies
    Write-Log "INFO" "Installing dependencies..."
    $requirementsFile = Join-Path $ProjectRoot "requirements.txt"
    if (Test-Path $requirementsFile) {
        & pip install -r $requirementsFile
        if ($LASTEXITCODE -ne 0) {
            Write-Log "ERROR" "Failed to install dependencies"
            exit 1
        }
    }
    else {
        Write-Log "ERROR" "requirements.txt not found"
        exit 1
    }

    # Install development dependencies if in dev mode
    if ($DevMode) {
        Write-Log "INFO" "Installing development dependencies..."
        & pip install pytest pytest-cov black flake8 mypy
        if ($LASTEXITCODE -ne 0) {
            Write-Log "WARNING" "Some development dependencies failed to install"
        }
    }

    # Create necessary directories
    Write-Log "INFO" "Creating necessary directories..."
    $directories = @("logs", "test_reports", "backups")
    foreach ($dir in $directories) {
        $dirPath = Join-Path $ProjectRoot $dir
        if (-not (Test-Path $dirPath)) {
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        }
    }

    # Initialize configuration
    Write-Log "INFO" "Initializing configuration..."
    $configFile = Join-Path $ProjectRoot "config.yaml"
    if (-not (Test-Path $configFile)) {
        Write-Log "INFO" "Creating default configuration file..."
        "# Default configuration" | Out-File -FilePath $configFile -Encoding UTF8
    }

    # Run initial tests if not skipped
    if (-not $SkipTests) {
        Write-Log "INFO" "Running initial tests..."
        $testsDir = Join-Path $ProjectRoot "tests"
        if (Test-Path $testsDir) {
            & python -m pytest $testsDir -v
            if ($LASTEXITCODE -ne 0) {
                Write-Log "ERROR" "Initial tests failed"
                exit 1
            }
        }
        else {
            Write-Log "WARNING" "Tests directory not found, skipping tests"
        }
    }

    Write-Log "SUCCESS" "Setup completed successfully!"
    Write-Log "INFO" "Virtual environment created at: $VenvDir"
    Write-Log "INFO" "To activate: & '$activateScript'"
    Write-Log "INFO" "To run simulation: .\run.ps1"

}
catch {
    Write-Log "ERROR" "Setup failed: $($_.Exception.Message)"
    exit 1
}
