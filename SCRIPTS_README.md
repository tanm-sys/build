# Shell Scripts Documentation

This directory contains comprehensive shell scripts for managing the Decentralized AI Simulation project. Each script is designed with proper error handling, logging, and documentation following shell scripting best practices.

## 📋 Available Scripts

### 🚀 setup.sh - Project Setup Script
**Purpose**: Complete project initialization and environment setup

**Usage**: `./setup.sh [OPTIONS]`

**Key Features**:
- Creates and activates Python virtual environment
- Installs all dependencies from requirements.txt
- Sets up configuration files and directories
- Initializes database with test data
- Runs comprehensive health checks
- Supports development mode with additional tools

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

### 🏃 run.sh - Main Execution Script
**Purpose**: Run the simulation with configurable parameters and modes

**Usage**: `./run.sh [MODE] [OPTIONS]`

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

**Options**:
- `-a, --agents N`: Number of agents
- `-s, --steps N`: Number of simulation steps
- `-p, --parallel`: Enable parallel execution
- `--seed N`: Set random seed
- `--config FILE`: Custom configuration file
- `--env ENV`: Set environment (development/production)

**Examples**:
```bash
./run.sh                                    # Default CLI mode
./run.sh ui                                 # Launch web interface
./run.sh cli --agents 100 --steps 50       # Custom parameters
./run.sh demo --parallel                    # Demo with parallel execution
```

### 🧪 test.sh - Comprehensive Testing Script
**Purpose**: Run comprehensive test suites with coverage and quality checks

**Usage**: `./test.sh [OPTIONS]`

**Key Features**:
- Unit and integration testing
- Code coverage reporting (HTML/XML)
- Code quality checks (linting, formatting)
- Performance testing
- Comprehensive test reports
- CI/CD integration support

**Options**:
- `-c, --coverage`: Generate coverage reports
- `-q, --quality`: Run code quality checks
- `-p, --performance`: Run performance tests
- `-r, --report`: Generate HTML test reports
- `--unit`: Run unit tests only
- `--integration`: Run integration tests only
- `--html`: Generate HTML coverage report
- `--xml`: Generate XML coverage for CI

**Examples**:
```bash
./test.sh --coverage --html                # Tests with HTML coverage
./test.sh --quality --performance          # Quality and performance tests
./test.sh --unit --verbose                 # Unit tests with verbose output
```

### 🚀 deploy.sh - Production Deployment Script
**Purpose**: Deploy application to production environments

**Usage**: `./deploy.sh [ENVIRONMENT] [OPTIONS]`

**Environments**:
- `staging`: Deploy to staging environment (default)
- `production`: Deploy to production environment
- `docker`: Prepare for Docker deployment

**Key Features**:
- Environment-specific configuration
- Pre-deployment validation and testing
- Database optimization for production
- Security configuration and hardening
- Post-deployment health validation
- Backup and rollback capabilities

**Options**:
- `-b, --backup`: Create backup before deployment
- `-f, --force`: Force deployment despite validation failures
- `-c, --config FILE`: Use custom configuration
- `--skip-tests`: Skip pre-deployment tests
- `--dry-run`: Show deployment plan without executing

**Examples**:
```bash
./deploy.sh staging --backup               # Staging deploy with backup
./deploy.sh production --dry-run           # Show production deployment plan
./deploy.sh docker --config docker.yaml   # Docker deployment
```

### 🧹 cleanup.sh - Maintenance and Cleanup Script
**Purpose**: Clean temporary files, logs, and perform maintenance

**Usage**: `./cleanup.sh [OPTIONS]`

**Key Features**:
- Selective cleanup of different file types
- Log rotation and management
- Database reset capabilities
- Space usage reporting
- Safe removal with confirmation prompts
- Dry-run mode for preview

**Options**:
- `-a, --all`: Complete cleanup of all categories
- `--logs`: Clean log files only
- `--cache`: Clear cache files only
- `--temp`: Remove temporary files only
- `--database`: Reset database (destructive!)
- `--blacklists`: Remove generated blacklist files
- `--reports`: Remove test reports
- `--dry-run`: Preview cleanup without executing

**Examples**:
```bash
./cleanup.sh --logs --cache                # Clean logs and cache
./cleanup.sh --all --dry-run               # Preview complete cleanup
./cleanup.sh --database --force            # Reset database (destructive!)
```

## 🛠️ Script Features

### Error Handling
All scripts implement robust error handling:
- `set -e`: Exit on any error
- `set -u`: Exit on undefined variables
- Comprehensive error messages with context
- Graceful cleanup on interruption (SIGINT/SIGTERM)

### Logging System
Consistent logging across all scripts:
- Timestamped log entries
- Multiple log levels (INFO, WARN, ERROR, DEBUG)
- Color-coded console output
- Persistent log files in `logs/` directory
- Verbose mode for detailed debugging

### Configuration Management
- Command-line argument parsing with validation
- Environment variable support
- Configuration file overrides
- Help text and usage examples
- Default value handling

### Safety Features
- Confirmation prompts for destructive operations
- Dry-run modes for preview
- Backup creation before major changes
- Virtual environment validation
- Prerequisite checking

## 🚦 Quick Start Guide

### 1. Initial Setup
```bash
# Make scripts executable (if needed)
chmod +x *.sh

# Set up the project environment
./setup.sh --verbose

# Verify installation
./test.sh --fast
```

### 2. Running Simulations
```bash
# Basic simulation
./run.sh

# Web interface
./run.sh ui

# Custom simulation
./run.sh cli --agents 200 --steps 100 --parallel
```

### 3. Testing and Quality
```bash
# Run all tests with coverage
./test.sh --coverage --html

# Quality checks only
./test.sh --quality

# Performance testing
./test.sh --performance
```

### 4. Deployment
```bash
# Deploy to staging
./deploy.sh staging --backup

# Production deployment (with caution)
./deploy.sh production --dry-run  # Preview first
./deploy.sh production --backup   # Actual deployment
```

### 5. Maintenance
```bash
# Regular cleanup
./cleanup.sh --logs --cache --temp

# Complete cleanup (preview first)
./cleanup.sh --all --dry-run
./cleanup.sh --all --force
```

## 🔧 Troubleshooting

### Common Issues

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
