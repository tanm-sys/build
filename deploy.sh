#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Production Deployment Script
# =============================================================================
# This script prepares and deploys the application for production environments
# with proper configuration, security settings, and health validation.
#
# Usage: ./deploy.sh [ENVIRONMENT] [OPTIONS]
# Environments:
#   staging             Deploy to staging environment
#   production          Deploy to production environment
#   docker              Prepare for Docker deployment
#
# Options:
#   -h, --help          Show this help message
#   -v, --verbose       Enable verbose output
#   -f, --force         Force deployment even if validation fails
#   -c, --config FILE   Use custom configuration file
#   -b, --backup        Create backup before deployment
#   --skip-tests        Skip pre-deployment tests
#   --skip-health       Skip health checks after deployment
#   --dry-run           Show what would be done without executing
# =============================================================================

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/.venv"
LOG_FILE="$PROJECT_ROOT/logs/deploy.log"
BACKUP_DIR="$PROJECT_ROOT/backups"

# Deployment configuration
ENVIRONMENT="staging"
VERBOSE=false
FORCE_DEPLOY=false
CUSTOM_CONFIG=""
CREATE_BACKUP=false
SKIP_TESTS=false
SKIP_HEALTH=false
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# Utility Functions
# =============================================================================

# Input validation functions
validate_config_file() {
    local file="$1"

    if [ -n "$file" ]; then
        if [ ! -f "$file" ]; then
            log "ERROR" "Configuration file not found: $file"
            exit 1
        fi

        # Check if file is readable
        if [ ! -r "$file" ]; then
            log "ERROR" "Configuration file not readable: $file"
            exit 1
        fi

        log "DEBUG" "Validated config file: $file"
    fi
}

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Create logs directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    case "$level" in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        "DEBUG")
            if [ "$VERBOSE" = true ]; then
                echo -e "${BLUE}[DEBUG]${NC} $message"
            fi
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "DEPLOY")
            echo -e "${PURPLE}[DEPLOY]${NC} $message"
            ;;
    esac
}

show_help() {
    cat << EOF
Decentralized AI Simulation - Deployment Script

USAGE:
    ./deploy.sh [ENVIRONMENT] [OPTIONS]

ENVIRONMENTS:
    staging             Deploy to staging environment (default)
    production          Deploy to production environment
    docker              Prepare for Docker containerized deployment

OPTIONS:
    -h, --help          Show this help message and exit
    -v, --verbose       Enable verbose output for detailed deployment info
    -f, --force         Force deployment even if validation fails
    -c, --config FILE   Use custom configuration file for deployment
    -b, --backup        Create backup of current deployment before update
    --skip-tests        Skip pre-deployment test validation
    --skip-health       Skip post-deployment health checks
    --dry-run           Show deployment plan without executing changes

EXAMPLES:
    ./deploy.sh                         # Deploy to staging with defaults
    ./deploy.sh production --backup     # Production deploy with backup
    ./deploy.sh staging --verbose       # Staging deploy with verbose output
    ./deploy.sh docker --dry-run        # Show Docker deployment plan
    ./deploy.sh production --config prod.yaml  # Custom config deployment

DESCRIPTION:
    This script handles production deployment including:
    
    • Environment-specific configuration setup
    • Pre-deployment validation and testing
    • Database migration and optimization
    • Security configuration and hardening
    • Service configuration and startup
    • Post-deployment health validation
    • Rollback capabilities with backup support

EOF
}

check_deployment_prerequisites() {
    log "INFO" "Checking deployment prerequisites..."
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        log "ERROR" "Virtual environment not found at $VENV_DIR"
        log "INFO" "Please run ./setup.sh first to set up the environment"
        exit 1
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Verify Python environment
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        log "ERROR" "Failed to activate virtual environment"
        exit 1
    fi
    
    log "DEBUG" "Virtual environment activated: $VIRTUAL_ENV"
    
    # Check if all required files exist
    local required_files=("config.yaml" "requirements.txt" "simulation.py" "database.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$file" ]; then
            log "ERROR" "Required file not found: $PROJECT_ROOT/$file"
            exit 1
        fi
    done
    
    # Check system resources (platform-independent approach)
    local available_memory_kb=0
    local available_disk_kb=0

    case "$(uname -s)" in
        "Linux")
            available_memory_kb=$(free -k | awk 'NR==2{print $7}')
            available_disk_kb=$(df "$PROJECT_ROOT" | awk 'NR==2{print $4}')
            ;;
        "Darwin")  # macOS
            available_memory_kb=$(vm_stat | awk '/Pages free/ {print $3}' | tr -d '.' | awk '{print $1 * 4096 / 1024}')
            available_disk_kb=$(df "$PROJECT_ROOT" | awk 'NR==2{print $4}')
            ;;
        *)
            log "WARN" "Cannot check system resources on this platform: $(uname -s)"
            ;;
    esac

    if [ "$available_memory_kb" -gt 0 ]; then
        local available_memory_mb=$((available_memory_kb / 1024))
        if [ "$available_memory_mb" -lt 512 ]; then
            log "WARN" "Low available memory: ${available_memory_mb}MB (recommended: 512MB+)"
        fi
    fi

    if [ "$available_disk_kb" -gt 0 ]; then
        if [ "$available_disk_kb" -lt 1048576 ]; then  # 1GB in KB
            log "WARN" "Low available disk space: ${available_disk_kb}KB (recommended: 1GB+)"
        fi
    fi
    
    log "INFO" "Prerequisites check completed"
}

create_backup() {
    if [ "$CREATE_BACKUP" = false ]; then
        log "INFO" "Skipping backup creation"
        return 0
    fi
    
    log "DEPLOY" "Creating deployment backup..."
    
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_path="$BACKUP_DIR/backup_${ENVIRONMENT}_${backup_timestamp}"
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "[DRY RUN] Would create backup at: $backup_path"
        return 0
    fi
    
    mkdir -p "$backup_path"
    
    # Backup configuration files
    cp -r "$PROJECT_ROOT"/*.yaml "$backup_path/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT"/*.py "$backup_path/" 2>/dev/null || true
    
    # Backup database if it exists
    if [ -f "$PROJECT_ROOT/ledger.db" ]; then
        cp "$PROJECT_ROOT/ledger.db" "$backup_path/"
    fi
    
    # Backup logs
    if [ -d "$PROJECT_ROOT/logs" ]; then
        cp -r "$PROJECT_ROOT/logs" "$backup_path/"
    fi
    
    log "SUCCESS" "Backup created at: $backup_path"
}

setup_environment_config() {
    log "DEPLOY" "Setting up $ENVIRONMENT environment configuration..."
    
    local config_file="$PROJECT_ROOT/config.yaml"
    local env_config_file="$PROJECT_ROOT/config_${ENVIRONMENT}.yaml"
    
    # Use custom config if specified
    if [ -n "$CUSTOM_CONFIG" ]; then
        # Validation is already done in argument parsing, but double-check
        if [ ! -f "$CUSTOM_CONFIG" ]; then
            log "ERROR" "Custom configuration file not found: $CUSTOM_CONFIG"
            exit 1
        fi

        # Check if file is readable
        if [ ! -r "$CUSTOM_CONFIG" ]; then
            log "ERROR" "Custom configuration file not readable: $CUSTOM_CONFIG"
            exit 1
        fi

        # Validate that it's a valid config file by checking for basic structure
        if ! grep -q "^[[:space:]]*environment:" "$CUSTOM_CONFIG" 2>/dev/null; then
            log "WARN" "Custom configuration file may be invalid or missing environment section: $CUSTOM_CONFIG"
        fi

        config_file="$CUSTOM_CONFIG"
        log "INFO" "Using custom configuration: $CUSTOM_CONFIG"
    fi
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "[DRY RUN] Would configure for $ENVIRONMENT environment"
        return 0
    fi
    
    # Create environment-specific configuration
    case "$ENVIRONMENT" in
        "staging")
            cat > "$env_config_file" << EOF
# Staging Environment Configuration
environment: staging

database:
  path: /var/lib/simulation/staging_ledger.db
  connection_pool_size: 10
  timeout: 30

logging:
  level: INFO
  file: /var/log/simulation/staging.log
  max_bytes: 52428800  # 50MB
  backup_count: 5

monitoring:
  health_check_interval: 30
  enable_prometheus: true
  metrics_port: 9090

simulation:
  default_agents: 50
  default_steps: 100
  enable_parallel: true

security:
  enable_ssl: false
  allowed_hosts: ["localhost", "staging.example.com"]
EOF
            ;;
        "production")
            cat > "$env_config_file" << EOF
# Production Environment Configuration
environment: production

database:
  path: /var/lib/simulation/production_ledger.db
  connection_pool_size: 20
  timeout: 60

logging:
  level: WARNING
  file: /var/log/simulation/production.log
  max_bytes: 104857600  # 100MB
  backup_count: 10

monitoring:
  health_check_interval: 60
  enable_prometheus: true
  metrics_port: 9090

simulation:
  default_agents: 100
  default_steps: 200
  enable_parallel: true

security:
  enable_ssl: true
  allowed_hosts: ["production.example.com"]
  
performance:
  cache_size: 1000
  max_workers: 4
EOF
            ;;
        "docker")
            cat > "$env_config_file" << EOF
# Docker Environment Configuration
environment: production

database:
  path: /app/data/ledger.db
  connection_pool_size: 15
  timeout: 45

logging:
  level: INFO
  file: /app/logs/simulation.log
  max_bytes: 52428800  # 50MB
  backup_count: 3

monitoring:
  health_check_interval: 30
  enable_prometheus: true
  metrics_port: 9090

simulation:
  default_agents: 75
  default_steps: 150
  enable_parallel: true

security:
  enable_ssl: false
  allowed_hosts: ["*"]
EOF
            ;;
    esac
    
    # Set environment variable to use the specific config
    export CONFIG_FILE="$env_config_file"
    
    log "SUCCESS" "Environment configuration created: $env_config_file"
}

run_pre_deployment_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log "INFO" "Skipping pre-deployment tests"
        return 0
    fi
    
    log "DEPLOY" "Running pre-deployment tests..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "[DRY RUN] Would run pre-deployment test suite"
        return 0
    fi
    
    # Run fast test suite
    if ./test.sh --fast --quality; then
        log "SUCCESS" "Pre-deployment tests passed"
    else
        if [ "$FORCE_DEPLOY" = true ]; then
            log "WARN" "Pre-deployment tests failed, but continuing due to --force"
        else
            log "ERROR" "Pre-deployment tests failed"
            log "INFO" "Use --force to deploy anyway or fix the issues"
            exit 1
        fi
    fi
}

setup_production_directories() {
    log "DEPLOY" "Setting up production directories..."
    
    local directories=(
        "/var/lib/simulation"
        "/var/log/simulation"
        "/etc/simulation"
    )
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "[DRY RUN] Would create directories: ${directories[*]}"
        return 0
    fi
    
    for dir in "${directories[@]}"; do
        if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "staging" ]; then
            # Only create system directories for production/staging
            if [ -w "$(dirname "$dir")" ] || [ "$(id -u)" -eq 0 ]; then
                mkdir -p "$dir"
                log "DEBUG" "Created directory: $dir"
            else
                log "WARN" "Cannot create system directory: $dir (insufficient permissions)"
            fi
        fi
    done
    
    # Always create local directories
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$BACKUP_DIR"
    
    log "SUCCESS" "Production directories setup completed"
}

optimize_database() {
    log "DEPLOY" "Optimizing database for production..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "[DRY RUN] Would optimize database configuration"
        return 0
    fi
    
    # Run database optimization
    python -c "
from database import DatabaseLedger
import os

# Initialize database with production settings
db = DatabaseLedger()

# Run VACUUM to optimize database
try:
    conn = db._get_connection()
    conn.execute('VACUUM;')
    conn.execute('ANALYZE;')
    conn.commit()
    print('Database optimization completed')
except Exception as e:
    print(f'Database optimization failed: {e}')
" 2>&1 | while read line; do
        log "DEBUG" "DB Optimize: $line"
    done
    
    log "SUCCESS" "Database optimization completed"
}

deploy_application() {
    log "DEPLOY" "Deploying application for $ENVIRONMENT environment..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "[DRY RUN] Would deploy application to $ENVIRONMENT"
        return 0
    fi
    
    # Set environment variables
    export ENVIRONMENT="$ENVIRONMENT"
    
    # Install/update dependencies
    log "INFO" "Installing production dependencies..."
    pip install --no-deps -r requirements.txt
    
    # Compile Python files for better performance
    log "INFO" "Compiling Python files..."
    python -m compileall -b .
    
    # Set appropriate file permissions
    if [ "$ENVIRONMENT" = "production" ]; then
        find "$PROJECT_ROOT" -name "*.py" -exec chmod 644 {} \;
        find "$PROJECT_ROOT" -name "*.sh" -exec chmod 755 {} \;
        chmod 600 "$PROJECT_ROOT"/*.yaml 2>/dev/null || true
    fi
    
    log "SUCCESS" "Application deployment completed"
}

run_health_checks() {
    if [ "$SKIP_HEALTH" = true ]; then
        log "INFO" "Skipping post-deployment health checks"
        return 0
    fi
    
    log "DEPLOY" "Running post-deployment health checks..."
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "[DRY RUN] Would run post-deployment health checks"
        return 0
    fi
    
    # Test application startup
    python -c "
from monitoring import get_monitoring
from config_loader import get_config
from database import DatabaseLedger

try:
    # Test configuration loading
    config = get_config('environment')
    print(f'✓ Configuration loaded: {config}')
    
    # Test database connection
    db = DatabaseLedger()
    print('✓ Database connection successful')
    
    # Test monitoring system
    monitoring = get_monitoring()
    health = monitoring.get_system_health()
    print(f'✓ Monitoring system: {health.status}')
    
    print('✓ All health checks passed')
except Exception as e:
    print(f'✗ Health check failed: {e}')
    exit(1)
" 2>&1 | while read line; do
        log "INFO" "Health Check: $line"
    done
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Post-deployment health checks passed"
    else
        log "ERROR" "Post-deployment health checks failed"
        if [ "$FORCE_DEPLOY" = false ]; then
            exit 1
        fi
    fi
}

show_deployment_summary() {
    log "INFO" "Deployment Summary:"
    log "INFO" "  Environment: $ENVIRONMENT"
    log "INFO" "  Project Root: $PROJECT_ROOT"
    log "INFO" "  Configuration: ${CONFIG_FILE:-config.yaml}"
    log "INFO" "  Backup Created: $CREATE_BACKUP"
    log "INFO" "  Tests Run: $([ "$SKIP_TESTS" = true ] && echo "No" || echo "Yes")"
    log "INFO" "  Health Checks: $([ "$SKIP_HEALTH" = true ] && echo "No" || echo "Yes")"
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "  Mode: DRY RUN (no changes made)"
    fi
    
    log "SUCCESS" "Deployment completed successfully!"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        log "INFO" ""
        log "INFO" "Production deployment checklist:"
        log "INFO" "  □ Monitor application logs: tail -f /var/log/simulation/production.log"
        log "INFO" "  □ Check system health: ./run.sh --env production"
        log "INFO" "  □ Verify monitoring metrics: http://localhost:9090"
        log "INFO" "  □ Test application functionality"
    fi
}

# =============================================================================
# Command Line Argument Parsing
# =============================================================================

# Parse environment first
if [[ $# -gt 0 ]] && [[ ! "$1" =~ ^- ]]; then
    case "$1" in
        staging|production|docker)
            ENVIRONMENT="$1"
            shift
            ;;
    esac
fi

# Parse remaining arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--force)
            FORCE_DEPLOY=true
            shift
            ;;
        -c|--config)
            CUSTOM_CONFIG="$2"
            validate_config_file "$CUSTOM_CONFIG"
            shift 2
            ;;
        -b|--backup)
            CREATE_BACKUP=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-health)
            SKIP_HEALTH=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            log "INFO" "Use --help for usage information"
            exit 1
            ;;
    esac
done

# =============================================================================
# Main Execution
# =============================================================================

main() {
    log "INFO" "Decentralized AI Simulation - Starting deployment to $ENVIRONMENT"
    
    # Initialize log file
    echo "Deployment started at $(date)" > "$LOG_FILE"
    
    check_deployment_prerequisites
    create_backup
    setup_environment_config
    run_pre_deployment_tests
    setup_production_directories
    optimize_database
    deploy_application
    run_health_checks
    show_deployment_summary
}

# Run main function
main
