# =============================================================================
# Decentralized AI Simulation - Main Execution Script (PowerShell)
# =============================================================================
# This script runs the decentralized AI simulation with configurable parameters
# and supports different execution modes including CLI, UI, and testing modes.
#
# Usage: .\run.ps1 [MODE] [OPTIONS]
# Modes:
#   cli                 Run simulation in CLI mode (default)
#   ui                  Launch Streamlit web interface
#   test                Run in test mode with minimal agents
#   demo                Run demonstration with preset parameters
#
# Options:
#   -Help              Show this help message
#   -Verbose           Enable verbose output
#   -Agents N          Number of agents (default: from config)
#   -Steps N           Number of simulation steps (default: from config)
#   -Parallel          Enable parallel execution with Ray
#   -Seed N            Set random seed for reproducibility
#   -ConfigFile FILE   Use custom configuration file
#   -Environment ENV   Set environment (development/production)
#   -LogLevel LEVEL    Set logging level (DEBUG/INFO/WARNING/ERROR)
# =============================================================================

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("cli", "ui", "test", "demo")]
    [string]$Mode = "cli",
    
    [switch]$Help,
    [switch]$Verbose,
    [int]$Agents,
    [int]$Steps,
    [switch]$Parallel,
    [int]$Seed,
    [string]$ConfigFile,
    [string]$Environment,
    [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR")]
    [string]$LogLevel
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$VenvDir = Join-Path $ProjectRoot ".venv"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "run.log"

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
    Write-Host "Decentralized AI Simulation - Run Script (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\run.ps1 [MODE] [OPTIONS]"
    Write-Host ""
    Write-Host "Modes:"
    Write-Host "  cli                 Run simulation in CLI mode (default)"
    Write-Host "  ui                  Launch Streamlit web interface"
    Write-Host "  test                Run in test mode with minimal agents"
    Write-Host "  demo                Run demonstration with preset parameters"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help              Show this help message"
    Write-Host "  -Verbose           Enable verbose output"
    Write-Host "  -Agents N          Number of agents (default: from config)"
    Write-Host "  -Steps N           Number of simulation steps (default: from config)"
    Write-Host "  -Parallel          Enable parallel execution with Ray"
    Write-Host "  -Seed N            Set random seed for reproducibility"
    Write-Host "  -ConfigFile FILE   Use custom configuration file"
    Write-Host "  -Environment ENV   Set environment (development/production)"
    Write-Host "  -LogLevel LEVEL    Set logging level (DEBUG/INFO/WARNING/ERROR)"
    Write-Host ""
    exit 0
}

# Show help if requested
if ($Help) {
    Show-Help
}

# Main execution
try {
    Write-Log "INFO" "Starting Decentralized AI Simulation..."

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

    # Create logs directory if it doesn't exist
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }

    # Set environment variables
    if ($Environment) {
        $env:ENVIRONMENT = $Environment
    }
    if ($LogLevel) {
        $env:LOG_LEVEL = $LogLevel
    }

    # Build command arguments
    $cmdArgs = @()
    if ($Agents) { $cmdArgs += "--agents", $Agents }
    if ($Steps) { $cmdArgs += "--steps", $Steps }
    if ($Parallel) { $cmdArgs += "--parallel" }
    if ($Seed) { $cmdArgs += "--seed", $Seed }
    if ($ConfigFile) { $cmdArgs += "--config", $ConfigFile }
    if ($Verbose) { $cmdArgs += "--verbose" }

    # Execute based on mode
    switch ($Mode) {
        "cli" {
            Write-Log "INFO" "Running simulation in CLI mode..."
            & python decentralized_ai_simulation.py @cmdArgs
        }
        "ui" {
            Write-Log "INFO" "Launching Streamlit web interface..."
            & streamlit run streamlit_app.py @cmdArgs
        }
        "test" {
            Write-Log "INFO" "Running in test mode..."
            & python decentralized_ai_simulation.py --agents 5 --steps 10 @cmdArgs
        }
        "demo" {
            Write-Log "INFO" "Running demonstration..."
            & python decentralized_ai_simulation.py --agents 20 --steps 50 --parallel @cmdArgs
        }
        default {
            Write-Log "ERROR" "Unknown mode: $Mode"
            exit 1
        }
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Log "ERROR" "Simulation failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }

    Write-Log "SUCCESS" "Simulation completed successfully!"
}
catch {
    Write-Log "ERROR" "Simulation failed: $($_.Exception.Message)"
    exit 1
}
