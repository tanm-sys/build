# =============================================================================
# Decentralized AI Simulation - Comprehensive Testing Script (PowerShell)
# =============================================================================
# This script runs comprehensive tests including unit tests, integration tests,
# code quality checks, coverage reporting, and performance validation.
#
# Usage: .\test.ps1 [OPTIONS]
# Options:
#   -Help              Show this help message
#   -Verbose           Enable verbose output
#   -Fast              Run fast tests only (skip slow integration tests)
#   -Coverage          Generate detailed coverage report
#   -Quality           Run code quality checks (linting, formatting)
#   -Performance       Run performance tests
#   -Report            Generate comprehensive test report
#   -UnitOnly          Run unit tests only
#   -IntegrationOnly   Run integration tests only
#   -HtmlCoverage      Generate HTML coverage report
#   -XmlCoverage       Generate XML coverage report for CI
# =============================================================================

[CmdletBinding()]
param(
    [switch]$Help,
    [switch]$Verbose,
    [switch]$Fast,
    [switch]$Coverage,
    [switch]$Quality,
    [switch]$Performance,
    [switch]$Report,
    [switch]$UnitOnly,
    [switch]$IntegrationOnly,
    [switch]$HtmlCoverage,
    [switch]$XmlCoverage
)

# Script configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$VenvDir = Join-Path $ProjectRoot ".venv"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "test.log"
$ReportsDir = Join-Path $ProjectRoot "test_reports"

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
    Write-Host "Decentralized AI Simulation - Test Script (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\test.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help              Show this help message"
    Write-Host "  -Verbose           Enable verbose output"
    Write-Host "  -Fast              Run fast tests only (skip slow integration tests)"
    Write-Host "  -Coverage          Generate detailed coverage report"
    Write-Host "  -Quality           Run code quality checks (linting, formatting)"
    Write-Host "  -Performance       Run performance tests"
    Write-Host "  -Report            Generate comprehensive test report"
    Write-Host "  -UnitOnly          Run unit tests only"
    Write-Host "  -IntegrationOnly   Run integration tests only"
    Write-Host "  -HtmlCoverage      Generate HTML coverage report"
    Write-Host "  -XmlCoverage       Generate XML coverage report for CI"
    Write-Host ""
    exit 0
}

# Show help if requested
if ($Help) {
    Show-Help
}

# Main execution
try {
    Write-Log "INFO" "Starting comprehensive testing suite..."

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
    if (-not (Test-Path $ReportsDir)) {
        New-Item -ItemType Directory -Path $ReportsDir -Force | Out-Null
    }

    # Install test dependencies if needed
    Write-Log "INFO" "Checking test dependencies..."
    try {
        & pip show pytest | Out-Null
    }
    catch {
        Write-Log "INFO" "Installing test dependencies..."
        & pip install pytest pytest-cov pytest-html pytest-xdist
    }

    # Run code quality checks if requested
    if ($Quality) {
        Write-Log "INFO" "Running code quality checks..."
        
        # Check if quality tools are installed
        try {
            & pip show black flake8 mypy | Out-Null
        }
        catch {
            Write-Log "INFO" "Installing code quality tools..."
            & pip install black flake8 mypy
        }
        
        Write-Log "INFO" "Running Black formatter check..."
        & black --check --diff .
        
        Write-Log "INFO" "Running Flake8 linter..."
        & flake8 . --max-line-length=88 --extend-ignore=E203,W503
        
        Write-Log "INFO" "Running MyPy type checker..."
        & mypy . --ignore-missing-imports
    }

    # Build pytest arguments
    $pytestArgs = @("-v")
    if ($Verbose) { $pytestArgs += "-s" }
    if ($Fast) { $pytestArgs += "-m", "not slow" }

    # Add coverage options
    if ($Coverage) {
        $pytestArgs += "--cov=.", "--cov-report=term-missing"
        if ($HtmlCoverage) {
            $htmlCovPath = Join-Path $ReportsDir "coverage_html"
            $pytestArgs += "--cov-report=html:$htmlCovPath"
        }
        if ($XmlCoverage) {
            $xmlCovPath = Join-Path $ReportsDir "coverage.xml"
            $pytestArgs += "--cov-report=xml:$xmlCovPath"
        }
    }

    # Add report generation
    if ($Report) {
        $reportPath = Join-Path $ReportsDir "test_report.html"
        $pytestArgs += "--html=$reportPath", "--self-contained-html"
    }

    # Run tests based on selection
    if ($UnitOnly) {
        Write-Log "INFO" "Running unit tests only..."
        $testsPath = Join-Path $ProjectRoot "tests\test_*.py"
        & python -m pytest $testsPath @pytestArgs
    }
    elseif ($IntegrationOnly) {
        Write-Log "INFO" "Running integration tests only..."
        $integrationPath = Join-Path $ProjectRoot "tests\integration"
        & python -m pytest $integrationPath @pytestArgs
    }
    else {
        Write-Log "INFO" "Running all tests..."
        $testsPath = Join-Path $ProjectRoot "tests"
        & python -m pytest $testsPath @pytestArgs
    }

    $testExitCode = $LASTEXITCODE

    # Run performance tests if requested
    if ($Performance) {
        Write-Log "INFO" "Running performance tests..."
        $perfPath = Join-Path $ProjectRoot "tests\performance"
        & python -m pytest $perfPath -v --benchmark-only
    }

    # Generate summary
    if ($testExitCode -eq 0) {
        Write-Log "SUCCESS" "All tests passed successfully!"
    }
    else {
        Write-Log "ERROR" "Some tests failed. Exit code: $testExitCode"
    }

    # Show report locations
    if ($Report) {
        $reportPath = Join-Path $ReportsDir "test_report.html"
        Write-Log "INFO" "Test report generated: $reportPath"
    }
    if ($HtmlCoverage) {
        $htmlCovPath = Join-Path $ReportsDir "coverage_html\index.html"
        Write-Log "INFO" "Coverage report generated: $htmlCovPath"
    }

    exit $testExitCode
}
catch {
    Write-Log "ERROR" "Testing failed: $($_.Exception.Message)"
    exit 1
}
