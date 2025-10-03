# Shell Scripts Documentation

This directory contains comprehensive shell scripts for managing the Decentralized AI Simulation project. Each script is designed with proper error handling, logging, and documentation following shell scripting best practices.

## 🌐 Cross-Platform Support

The project provides scripts for both **Unix/Linux** and **Windows** environments:

### Unix/Linux Scripts (.sh)
- Designed for Bash shell environments
- Compatible with Linux, macOS, and WSL
- Use forward slashes for paths
- Execute with: `./script.sh`

### Windows Scripts
Each Unix script has two Windows equivalents:

#### Batch Scripts (.bat)
- Compatible with Windows Command Prompt
- Use backslashes for paths
- Execute with: `script.bat`
- Basic functionality with wide compatibility

#### PowerShell Scripts (.ps1)
- Advanced Windows functionality
- Better error handling and output formatting
- Execute with: `.\script.ps1`
- May require execution policy changes: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 📋 Available Scripts

### 🚀 Project Setup Scripts
**Purpose**: Complete project initialization and environment setup

#### Unix/Linux Usage
**Usage**: `./setup.sh [OPTIONS]`

**Options**:
- `-h, --help`: Show help message
- `-v, --verbose`: Enable verbose output
- `-f, --force`: Force reinstall even if environment exists
- `-p, --python PATH`: Specify Python executable
- `--skip-tests`: Skip initial test execution
- `--dev`: Install development dependencies

**Example**:
```bash
./setup.sh --verbose --dev    # Development setup with verbose output
```

#### Windows Usage

**Batch Script**: `setup.bat [OPTIONS]`
```cmd
setup.bat /verbose /dev    # Development setup with verbose output
setup.bat /force /python python3.9    # Force reinstall with specific Python
```

**PowerShell Script**: `.\setup.ps1 [OPTIONS]`
```powershell
.\setup.ps1 -Verbose -DevMode    # Development setup with verbose output
.\setup.ps1 -Force -PythonPath "python3.9"    # Force reinstall with specific Python
```

**Key Features**:
- Creates and activates Python virtual environment
- Installs all dependencies from requirements.txt
- Sets up configuration files and directories
- Initializes database with test data
- Runs comprehensive health checks
- Supports development mode with additional tools

### 🏃 Main Execution Scripts
**Purpose**: Run the simulation with configurable parameters and modes

#### Unix/Linux Usage
**Usage**: `./run.sh [MODE] [OPTIONS]`

**Examples**:
```bash
./run.sh                                    # Default CLI mode
./run.sh ui                                 # Launch web interface
./run.sh cli --agents 100 --steps 50       # Custom parameters
./run.sh demo --parallel                    # Demo with parallel execution
```

#### Windows Usage

**Batch Script**: `run.bat [MODE] [OPTIONS]`
```cmd
run.bat                                     # Default CLI mode
run.bat ui                                  # Launch web interface
run.bat cli /agents 100 /steps 50          # Custom parameters
run.bat demo /parallel                      # Demo with parallel execution
```

**PowerShell Script**: `.\run.ps1 [MODE] [OPTIONS]`
```powershell
.\run.ps1                                   # Default CLI mode
.\run.ps1 ui                                # Launch web interface
.\run.ps1 cli -Agents 100 -Steps 50        # Custom parameters
.\run.ps1 demo -Parallel                    # Demo with parallel execution
```

**Modes**:
- `cli`: Command-line interface mode (default)
- `ui`: Launch Streamlit web interface
- `test`: Test mode with minimal configuration
- `demo`: Demonstration mode with preset parameters

**Key Features**:
- Multiple execution modes (CLI, UI, test, demo)
- Configurable agent count and simulation steps
- Parallel execution support with Ray
- Environment variable overrides
- Comprehensive logging and error handling

**Common Options**:
- Agents: Number of agents to simulate
- Steps: Number of simulation steps
- Parallel: Enable parallel execution
- Seed: Set random seed for reproducibility
- Config: Custom configuration file
- Environment: Set environment (development/production)

### 🧪 Comprehensive Testing Scripts
**Purpose**: Run comprehensive test suites with coverage and quality checks

#### Unix/Linux Usage
**Usage**: `./test.sh [OPTIONS]`

**Examples**:
```bash
./test.sh --coverage --html                # Tests with HTML coverage
./test.sh --quality --performance          # Quality and performance tests
./test.sh --unit --verbose                 # Unit tests with verbose output
```

#### Windows Usage

**Batch Script**: `test.bat [OPTIONS]`
```cmd
test.bat /coverage /html                   # Tests with HTML coverage
test.bat /quality /performance             # Quality and performance tests
test.bat /unit /verbose                    # Unit tests with verbose output
```

**PowerShell Script**: `.\test.ps1 [OPTIONS]`
```powershell
.\test.ps1 -Coverage -HtmlCoverage         # Tests with HTML coverage
.\test.ps1 -Quality -Performance           # Quality and performance tests
.\test.ps1 -UnitOnly -Verbose              # Unit tests with verbose output
```

**Key Features**:
- Unit and integration testing
- Code coverage reporting (HTML/XML)
- Code quality checks (linting, formatting)
- Performance testing
- Comprehensive test reports
- CI/CD integration support

**Common Options**:
- Coverage: Generate coverage reports
- Quality: Run code quality checks (linting, formatting)
- Performance: Run performance benchmarks
- Report: Generate HTML test reports
- UnitOnly: Run unit tests only
- IntegrationOnly: Run integration tests only
- HtmlCoverage: Generate HTML coverage report
- XmlCoverage: Generate XML coverage for CI

### 🚀 Production Deployment Scripts
**Purpose**: Deploy application to production environments

#### Unix/Linux Usage
**Usage**: `./deploy.sh [ENVIRONMENT] [OPTIONS]`

**Examples**:
```bash
./deploy.sh staging --backup               # Staging deploy with backup
./deploy.sh production --dry-run           # Show production deployment plan
./deploy.sh docker --config docker.yaml   # Docker deployment
```

#### Windows Usage

**Batch Script**: `deploy.bat [ENVIRONMENT] [OPTIONS]`
```cmd
deploy.bat staging /backup                 # Staging deploy with backup
deploy.bat production /check               # Production health check only
deploy.bat development /force              # Force development deployment
```

**PowerShell Script**: `.\deploy.ps1 [ENVIRONMENT] [OPTIONS]`
```powershell
.\deploy.ps1 staging -Backup              # Staging deploy with backup
.\deploy.ps1 production -HealthCheckOnly  # Production health check only
.\deploy.ps1 development -Force           # Force development deployment
```

**Environments**:
- `development`: Deploy to development environment
- `staging`: Deploy to staging environment
- `production`: Deploy to production environment

**Key Features**:
- Environment-specific configuration
- Pre-deployment validation and testing
- Database optimization for production
- Security configuration and hardening
- Post-deployment health validation
- Backup and rollback capabilities

**Common Options**:
- Backup: Create backup before deployment
- Force: Force deployment despite validation failures
- ConfigFile: Use custom configuration
- SkipTests: Skip pre-deployment tests
- HealthCheckOnly: Run health checks only
- Rollback: Rollback to previous deployment

### 🧹 Maintenance and Cleanup Scripts
**Purpose**: Clean temporary files, logs, and perform maintenance

#### Unix/Linux Usage
**Usage**: `./cleanup.sh [OPTIONS]`

**Examples**:
```bash
./cleanup.sh --logs --cache                # Clean logs and cache
./cleanup.sh --all --dry-run               # Preview complete cleanup
./cleanup.sh --database --force            # Reset database (destructive!)
```

#### Windows Usage

**Batch Script**: `cleanup.bat [OPTIONS]`
```cmd
cleanup.bat /logs /cache                   # Clean logs and cache
cleanup.bat /all /dry-run                  # Preview complete cleanup
cleanup.bat /database /force               # Reset database (destructive!)
```

**PowerShell Script**: `.\cleanup.ps1 [OPTIONS]`
```powershell
.\cleanup.ps1 -Logs -Cache                 # Clean logs and cache
.\cleanup.ps1 -All -DryRun                 # Preview complete cleanup
.\cleanup.ps1 -Database -Force             # Reset database (destructive!)
```

**Key Features**:
- Selective cleanup of different file types
- Log rotation and management
- Database reset capabilities
- Space usage reporting
- Safe removal with confirmation prompts
- Dry-run mode for preview

**Common Options**:
- All: Complete cleanup of all categories
- Logs: Clean log files only
- Cache: Clear cache files only
- Temp: Remove temporary files only
- Database: Reset database (destructive!)
- Reports: Remove test reports
- DryRun: Preview cleanup without executing
- Force: Skip confirmation prompts
- KeepDays: Keep files newer than N days

## 🛠️ Script Features

### Cross-Platform Compatibility
**Unix/Linux Scripts (.sh)**:
- `set -e`: Exit on any error
- `set -u`: Exit on undefined variables
- Bash-specific features and syntax
- POSIX-compliant where possible

**Windows Batch Scripts (.bat)**:
- `setlocal enabledelayedexpansion`: Enhanced variable handling
- Error level checking with `if errorlevel`
- Windows-specific path handling (backslashes)
- Command Prompt compatibility

**Windows PowerShell Scripts (.ps1)**:
- Advanced error handling with try-catch blocks
- PowerShell-specific cmdlets and features
- Object-oriented approach
- Enhanced parameter validation

### Logging System
Consistent logging across all platforms:
- Timestamped log entries
- Multiple log levels (INFO, WARN, ERROR, DEBUG)
- Color-coded console output (platform-appropriate)
- Persistent log files in `logs/` directory
- Verbose mode for detailed debugging

### Configuration Management
- Command-line argument parsing with validation
- Environment variable support
- Configuration file overrides
- Help text and usage examples
- Default value handling
- Platform-specific path resolution

### Safety Features
- Confirmation prompts for destructive operations
- Dry-run modes for preview
- Backup creation before major changes
- Virtual environment validation
- Prerequisite checking
- Platform-appropriate file operations

## 🚦 Quick Start Guide

### 1. Initial Setup

#### Unix/Linux
```bash
# Make scripts executable (if needed)
chmod +x *.sh

# Set up the project environment
./setup.sh --verbose

# Verify installation
./test.sh --fast
```

#### Windows Command Prompt
```cmd
# Set up the project environment
setup.bat /verbose

# Verify installation
test.bat /fast
```

#### Windows PowerShell
```powershell
# Set up the project environment
.\setup.ps1 -Verbose

# Verify installation
.\test.ps1 -Fast
```

### 2. Running Simulations

#### Unix/Linux
```bash
# Basic simulation
./run.sh

# Web interface
./run.sh ui

# Custom simulation
./run.sh cli --agents 200 --steps 100 --parallel
```

#### Windows Command Prompt
```cmd
# Basic simulation
run.bat

# Web interface
run.bat ui

# Custom simulation
run.bat cli /agents 200 /steps 100 /parallel
```

#### Windows PowerShell
```powershell
# Basic simulation
.\run.ps1

# Web interface
.\run.ps1 ui

# Custom simulation
.\run.ps1 cli -Agents 200 -Steps 100 -Parallel
```

### 3. Testing and Quality

#### Unix/Linux
```bash
# Run all tests with coverage
./test.sh --coverage --html

# Quality checks only
./test.sh --quality

# Performance testing
./test.sh --performance
```

#### Windows Command Prompt
```cmd
# Run all tests with coverage
test.bat /coverage /html

# Quality checks only
test.bat /quality

# Performance testing
test.bat /performance
```

#### Windows PowerShell
```powershell
# Run all tests with coverage
.\test.ps1 -Coverage -HtmlCoverage

# Quality checks only
.\test.ps1 -Quality

# Performance testing
.\test.ps1 -Performance
```

### 4. Deployment

#### Unix/Linux
```bash
# Deploy to staging
./deploy.sh staging --backup

# Production deployment (with caution)
./deploy.sh production --dry-run  # Preview first
./deploy.sh production --backup   # Actual deployment
```

#### Windows Command Prompt
```cmd
# Deploy to staging
deploy.bat staging /backup

# Production deployment (with caution)
deploy.bat production /check      # Health check first
deploy.bat production /backup     # Actual deployment
```

#### Windows PowerShell
```powershell
# Deploy to staging
.\deploy.ps1 staging -Backup

# Production deployment (with caution)
.\deploy.ps1 production -HealthCheckOnly  # Health check first
.\deploy.ps1 production -Backup           # Actual deployment
```

### 5. Maintenance

#### Unix/Linux
```bash
# Regular cleanup
./cleanup.sh --logs --cache --temp

# Complete cleanup (preview first)
./cleanup.sh --all --dry-run
./cleanup.sh --all --force
```

#### Windows Command Prompt
```cmd
# Regular cleanup
cleanup.bat /logs /cache /temp

# Complete cleanup (preview first)
cleanup.bat /all /dry-run
cleanup.bat /all /force
```

#### Windows PowerShell
```powershell
# Regular cleanup
.\cleanup.ps1 -Logs -Cache -Temp

# Complete cleanup (preview first)
.\cleanup.ps1 -All -DryRun
.\cleanup.ps1 -All -Force
```

## 🔧 Troubleshooting

### Common Issues

#### Unix/Linux Issues

**Permission Denied**:
```bash
chmod +x *.sh  # Make scripts executable
```

**Virtual Environment Issues**:
```bash
./setup.sh --force  # Force recreate environment
```

**Test Failures**:
```bash
./test.sh --verbose  # Get detailed test output
```

**Deployment Issues**:
```bash
./deploy.sh --dry-run --verbose  # Preview with details
```

#### Windows Issues

**PowerShell Execution Policy**:
```powershell
# Allow PowerShell script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Virtual Environment Issues**:
```cmd
# Command Prompt
setup.bat /force

# PowerShell
.\setup.ps1 -Force
```

**Path Issues**:
```cmd
# Ensure Python is in PATH
python --version
# If not found, add Python to system PATH or use full path
```

**Test Failures**:
```cmd
# Command Prompt
test.bat /verbose

# PowerShell
.\test.ps1 -Verbose
```

### Log Files
All scripts create log files in the `logs/` directory:
- `setup.log`: Setup script logs
- `run.log`: Execution logs
- `test.log`: Test execution logs
- `deploy.log`: Deployment logs
- `cleanup.log`: Cleanup operation logs

### Getting Help
Each script provides comprehensive help:
```bash
./script_name.sh --help
```

## 📝 Best Practices

1. **Always run setup first**: `./setup.sh` before using other scripts
2. **Use dry-run for destructive operations**: Preview changes first
3. **Check logs for troubleshooting**: Review log files in `logs/` directory
4. **Use verbose mode for debugging**: Add `--verbose` flag
5. **Create backups before deployment**: Use `--backup` option
6. **Test before deploying**: Run `./test.sh` before `./deploy.sh`

## 🔒 Security Considerations

- Scripts validate virtual environment before execution
- Confirmation prompts for destructive operations
- Secure file permissions in production deployments
- Environment variable validation
- Safe cleanup with confirmation prompts

## 🤝 Contributing

When modifying scripts:
1. Follow existing error handling patterns
2. Add appropriate logging statements
3. Update help text and documentation
4. Test with `--dry-run` and `--verbose` modes
5. Ensure backward compatibility
