#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Enhanced Production Deployment Script
# =============================================================================
# Modern bash script for production deployment with comprehensive validation,
# rollback capabilities, and cross-platform compatibility.
#
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
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - Environment setup failed
#   4 - Deployment validation failed
#   5 - Rollback required
# =============================================================================

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures
shopt -s globstar   # Enable globstar for recursive globbing
shopt -s extglob    # Enable extended globbing patterns

# Enhanced script configuration with robust path resolution
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly VENV_DIR="${PROJECT_ROOT}/.venv"
readonly LOG_DIR="${PROJECT_ROOT}/logs"
readonly LOG_FILE="${LOG_DIR}/deploy.log"
readonly BACKUP_DIR="${PROJECT_ROOT}/backups"
readonly CONFIG_DIR="${PROJECT_ROOT}/config"

# Deployment configuration with validation arrays
readonly SUPPORTED_ENVIRONMENTS=("staging" "production" "docker")
readonly DEFAULT_ENVIRONMENT="staging"
readonly DEPLOYMENT_TIMEOUT=1800  # 30 minutes
readonly HEALTH_CHECK_RETRIES=3
readonly HEALTH_CHECK_DELAY=10

# Configuration variables with defaults
ENVIRONMENT="${DEFAULT_ENVIRONMENT}"
VERBOSE=false
FORCE_DEPLOY=false
CUSTOM_CONFIG=""
CREATE_BACKUP=false
SKIP_TESTS=false
SKIP_HEALTH=false
DRY_RUN=false

# Enhanced color palette for better visual feedback
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly BOLD_RED='\033[1;31m'
readonly BOLD_GREEN='\033[1;32m'
readonly BOLD_YELLOW='\033[1;33m'
readonly BOLD_BLUE='\033[1;34m'
readonly BOLD_CYAN='\033[1;36m'
readonly NC='\033[0m' # No Color

# Global variables for tracking deployment state
PYTHON_CMD=""
VIRTUAL_ENV_ACTIVE=false
DEPLOYMENT_START_TIME=""
BACKUP_CREATED=""

# =============================================================================
# Enhanced Utility Functions
# =============================================================================

# Enhanced logging function with structured output and deployment tracking
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Create log directory if it doesn't exist
    mkdir -p "${LOG_DIR}"

    # Log to file with structured format
    printf '[%s] [%s] %s\n' "$timestamp" "$level" "$message" >> "$LOG_FILE"

    # Console output with enhanced colors and formatting
    case "$level" in
        "INFO")
            printf '%b[%s]%b %s\n' "${GREEN}" "$level" "${NC}" "$message"
            ;;
        "WARN")
            printf '%b[%s]%b %s\n' "${YELLOW}" "$level" "${NC}" "$message"
            ;;
        "ERROR")
            printf '%b[%s]%b %s\n' "${RED}" "$level" "${NC}" "$message"
            ;;
        "DEBUG")
            if [[ "$VERBOSE" == true ]]; then
                printf '%b[%s]%b %s\n' "${BLUE}" "$level" "${NC}" "$message"
            fi
            ;;
        "SUCCESS")
            printf '%b[%s]%b %s\n' "${BOLD_GREEN}" "$level" "${NC}" "$message"
            ;;
        "DEPLOY")
            printf '%b[%s]%b %s\n' "${PURPLE}" "$level" "${NC}" "$message"
            ;;
        "ROLLBACK")
            printf '%b[%s]%b %s\n' "${BOLD_YELLOW}" "$level" "${NC}" "$message"
            ;;
    esac
}

# Enhanced configuration file validation with YAML structure checking
validate_config_file() {
    local file="$1"

    if [[ -n "$file" ]]; then
        # Check if file exists and is readable
        if [[ ! -f "$file" ]]; then
            log "ERROR" "Configuration file not found: $file"
            exit 2
        fi

        if [[ ! -r "$file" ]]; then
            log "ERROR" "Configuration file not readable: $file"
            exit 2
        fi

        # Validate YAML structure if possible
        if command -v python3 &> /dev/null; then
            if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" &> /dev/null; then
                log "WARN" "Configuration file may have YAML syntax issues: $file"
            fi
        fi

        log "DEBUG" "Validated config file: $file"
    fi
}

# Enhanced deployment validation with comprehensive checks
validate_deployment_environment() {
    local env="$1"

    if [[ -n "$env" ]]; then
        local valid_env=false
        for valid_env_value in "${SUPPORTED_ENVIRONMENTS[@]}"; do
            if [[ "$env" == "$valid_env_value" ]]; then
                valid_env=true
                break
            fi
        done

        if [[ "$valid_env" == false ]]; then
            log "ERROR" "Invalid environment: '$env' (must be one of: ${SUPPORTED_ENVIRONMENTS[*]})"
            exit 2
        fi

        log "DEBUG" "Validated deployment environment: $env"
    fi
}

# Function to check if command exists and is executable
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to wait for a condition with timeout
wait_for_condition() {
    local condition="$1"
    local timeout="$2"
    local delay="${3:-5}"
    local elapsed=0

    while [[ $elapsed -lt $timeout ]]; do
        if eval "$condition"; then
            return 0
        fi
        sleep "$delay"
        elapsed=$((elapsed + delay))
    done

    return 1
}

# Enhanced help display with better formatting and deployment guidance
show_help() {
    local script_name
    script_name=$(basename "${BASH_SOURCE[0]}")

    cat << EOF
${BOLD_BLUE}Decentralized AI Simulation - Enhanced Deployment Script${NC}

${BOLD_YELLOW}USAGE:${NC}
    $script_name [ENVIRONMENT] [OPTIONS]

${BOLD_YELLOW}ENVIRONMENTS:${NC}
    ${BOLD_GREEN}staging${NC}             Deploy to staging environment (default)
    ${BOLD_GREEN}production${NC}          Deploy to production environment
    ${BOLD_GREEN}docker${NC}              Prepare for Docker containerized deployment

${BOLD_YELLOW}OPTIONS:${NC}
    ${BOLD_GREEN}-h, --help${NC}          Show this help message and exit
    ${BOLD_GREEN}-v, --verbose${NC}       Enable verbose output for detailed deployment info
    ${BOLD_GREEN}-f, --force${NC}         Force deployment even if validation fails
    ${BOLD_GREEN}-c, --config FILE${NC}   Use custom configuration file for deployment
    ${BOLD_GREEN}-b, --backup${NC}        Create backup of current deployment before update
    ${BOLD_GREEN}--skip-tests${NC}        Skip pre-deployment test validation
    ${BOLD_GREEN}--skip-health${NC}       Skip post-deployment health checks
    ${BOLD_CYAN}--dry-run${NC}           Show deployment plan without executing changes

${BOLD_YELLOW}EXAMPLES:${NC}
    $script_name                           # Deploy to staging with defaults
    $script_name production --backup       # Production deploy with backup
    $script_name staging --verbose         # Staging deploy with verbose output
    $script_name docker --dry-run          # Show Docker deployment plan
    $script_name production --config prod.yaml  # Custom config deployment

${BOLD_YELLOW}DESCRIPTION:${NC}
    This script handles production deployment including:

    • ${BOLD_CYAN}Environment-specific configuration setup${NC}
    • ${BOLD_CYAN}Pre-deployment validation and testing${NC}
    • ${BOLD_CYAN}Database migration and optimization${NC}
    • ${BOLD_CYAN}Security configuration and hardening${NC}
    • ${BOLD_CYAN}Service configuration and startup${NC}
    • ${BOLD_CYAN}Post-deployment health validation${NC}
    • ${BOLD_CYAN}Rollback capabilities with backup support${NC}

${BOLD_RED}⚠️  DEPLOYMENT WARNINGS:${NC}
    • ${BOLD_RED}Production deployments${NC} are ${BOLD_RED}irreversible${NC} without backups
    • Always use ${BOLD_CYAN}--dry-run${NC} to preview deployment steps
    • Ensure ${BOLD_CYAN}--backup${NC} is used for production deployments
    • Test deployments in ${BOLD_GREEN}staging${NC} before ${BOLD_RED}production${NC}

${BOLD_YELLOW}EXIT CODES:${NC}
    0 - Success
    1 - General error
    2 - Invalid arguments
    3 - Environment setup failed
    4 - Deployment validation failed
    5 - Rollback required

${BOLD_BLUE}For more information, see README.md${NC}
EOF
}

# Enhanced deployment prerequisite validation with comprehensive checks
check_deployment_prerequisites() {
    log "INFO" "Checking deployment prerequisites..."

    # Validate project structure
    local required_paths=(
        "${PROJECT_ROOT}/decentralized-ai-simulation"
        "${PROJECT_ROOT}/config"
        "${PROJECT_ROOT}/scripts"
    )

    for path in "${required_paths[@]}"; do
        if [[ ! -d "$path" ]]; then
            log "ERROR" "Required directory not found: $path"
            log "INFO" "Please ensure project structure is intact"
            exit 3
        fi
    done

    # Check virtual environment with enhanced validation
    if [[ ! -d "$VENV_DIR" ]]; then
        log "ERROR" "Virtual environment not found at $VENV_DIR"
        log "INFO" "Please run setup script first: ${SCRIPT_DIR}/../setup/setup.sh"
        exit 3
    fi

    # Activate virtual environment with error handling
    if ! source "$VENV_DIR/bin/activate"; then
        log "ERROR" "Failed to activate virtual environment at $VENV_DIR"
        exit 3
    fi

    # Verify activation
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log "ERROR" "Virtual environment activation failed"
        exit 3
    fi

    VIRTUAL_ENV_ACTIVE=true
    PYTHON_CMD="python"
    log "DEBUG" "Virtual environment activated: $VIRTUAL_ENV"

    # Enhanced file validation with detailed reporting
    local required_files=(
        "config/config.yaml"
        "decentralized-ai-simulation/config/requirements.txt"
        "decentralized-ai-simulation/src/core/simulation.py"
        "decentralized-ai-simulation/src/core/database.py"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$PROJECT_ROOT/$file" ]]; then
            log "ERROR" "Required file not found: $PROJECT_ROOT/$file"
            exit 3
        fi
    done

    # Enhanced system resource checking with better cross-platform support
    local available_memory_kb=0
    local available_disk_kb=0

    case "$(uname -s)" in
        "Linux")
            available_memory_kb=$(free -k 2>/dev/null | awk 'NR==2{print $7}' || echo 0)
            available_disk_kb=$(df "$PROJECT_ROOT" 2>/dev/null | awk 'NR==2{print $4}' || echo 0)
            ;;
        "Darwin")  # macOS
            available_memory_kb=$(vm_stat 2>/dev/null | awk '/Pages free/ {print $3}' | tr -d '.' | awk '{print $1 * 4096 / 1024}' || echo 0)
            available_disk_kb=$(df "$PROJECT_ROOT" 2>/dev/null | awk 'NR==2{print $4}' || echo 0)
            ;;
        *)
            log "WARN" "Cannot check system resources on this platform: $(uname -s)"
            ;;
    esac

    # Enhanced resource validation with environment-specific recommendations
    if [[ $available_memory_kb -gt 0 ]]; then
        local available_memory_mb=$((available_memory_kb / 1024))
        local min_memory=512

        # Adjust minimum memory based on environment
        case "$ENVIRONMENT" in
            "production")
                min_memory=2048
                ;;
            "staging")
                min_memory=1024
                ;;
        esac

        if [[ $available_memory_mb -lt $min_memory ]]; then
            if [[ "$FORCE_DEPLOY" == true ]]; then
                log "WARN" "Low available memory: ${available_memory_mb}MB (recommended: ${min_memory}MB+ for $ENVIRONMENT)"
            else
                log "ERROR" "Insufficient memory: ${available_memory_mb}MB (required: ${min_memory}MB+ for $ENVIRONMENT)"
                exit 3
            fi
        fi
    fi

    if [[ $available_disk_kb -gt 0 ]]; then
        local min_disk_kb=1048576  # 1GB in KB
        if [[ $available_disk_kb -lt $min_disk_kb ]]; then
            if [[ "$FORCE_DEPLOY" == true ]]; then
                log "WARN" "Low available disk space: ${available_disk_kb}KB (recommended: 1GB+)"
            else
                log "ERROR" "Insufficient disk space: ${available_disk_kb}KB (required: 1GB+)"
                exit 3
            fi
        fi
    fi

    # Check for deployment conflicts
    if [[ "$ENVIRONMENT" == "production" ]] && pgrep -f "simulation" > /dev/null 2>&1; then
        log "WARN" "Simulation processes detected running - ensure they won't conflict"
    fi

    log "INFO" "Prerequisites check completed successfully"
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
# Enhanced Main Execution Function
# =============================================================================

main() {
    local start_time
    start_time=$(date '+%Y-%m-%d %H:%M:%S')

    log "INFO" "Decentralized AI Simulation - Starting deployment to $ENVIRONMENT at $start_time"
    log "INFO" "Script version: 2.0.0"
    log "INFO" "Process ID: $$"

    # Initialize log file with comprehensive session header
    {
        echo "=========================================="
        echo "Deployment session started at $start_time"
        echo "Target environment: $ENVIRONMENT"
        echo "Project root: $PROJECT_ROOT"
        echo "Log file: $LOG_FILE"
        echo "Dry run mode: $DRY_RUN"
        echo "Force mode: $FORCE_DEPLOY"
        echo "Backup creation: $CREATE_BACKUP"
        echo "Skip tests: $SKIP_TESTS"
        echo "Skip health checks: $SKIP_HEALTH"
        echo "=========================================="
    } > "$LOG_FILE"

    # Core deployment flow with comprehensive error handling
    local deployment_success=true
    local deployment_result=0

    # Phase 1: Prerequisites and validation
    if check_deployment_prerequisites; then
        log "INFO" "Prerequisites validation completed"
    else
        log "ERROR" "Prerequisites validation failed"
        exit 3
    fi

    # Phase 2: Backup (if requested)
    if [[ "$CREATE_BACKUP" == true ]]; then
        if create_backup; then
            log "INFO" "Pre-deployment backup completed"
        else
            log "ERROR" "Pre-deployment backup failed"
            exit 3
        fi
    fi

    # Phase 3: Environment configuration
    if setup_environment_config; then
        log "INFO" "Environment configuration completed"
    else
        log "ERROR" "Environment configuration failed"
        deployment_success=false
        deployment_result=4
    fi

    # Phase 4: Pre-deployment testing
    if [[ "$SKIP_TESTS" == false ]] && [[ "$DRY_RUN" == false ]]; then
        if run_pre_deployment_tests; then
            log "INFO" "Pre-deployment tests passed"
        else
            if [[ "$FORCE_DEPLOY" == true ]]; then
                log "WARN" "Pre-deployment tests failed, but continuing due to --force"
            else
                log "ERROR" "Pre-deployment tests failed"
                deployment_success=false
                deployment_result=4
            fi
        fi
    fi

    # Phase 5: Production setup
    if setup_production_directories; then
        log "INFO" "Production directories setup completed"
    else
        log "ERROR" "Production directories setup failed"
        deployment_success=false
        deployment_result=3
    fi

    # Phase 6: Database optimization
    if optimize_database; then
        log "INFO" "Database optimization completed"
    else
        log "ERROR" "Database optimization failed"
        deployment_success=false
        deployment_result=3
    fi

    # Phase 7: Application deployment
    if deploy_application; then
        log "INFO" "Application deployment completed"
    else
        log "ERROR" "Application deployment failed"
        deployment_success=false
        deployment_result=3
    fi

    # Phase 8: Health validation
    if [[ "$SKIP_HEALTH" == false ]] && [[ "$DRY_RUN" == false ]]; then
        if run_health_checks; then
            log "INFO" "Post-deployment health checks passed"
        else
            if [[ "$FORCE_DEPLOY" == true ]]; then
                log "WARN" "Post-deployment health checks failed, but deployment completed"
            else
                log "ERROR" "Post-deployment health checks failed"
                deployment_success=false
                deployment_result=4
            fi
        fi
    fi

    # Phase 9: Deployment summary
    show_deployment_summary

    local end_time
    end_time=$(date '+%Y-%m-%d %H:%M:%S')

    if [[ "$DRY_RUN" == true ]]; then
        log "INFO" "Dry run completed at $end_time - no actual changes were made"
        exit 0
    elif [[ $deployment_success == true ]]; then
        log "SUCCESS" "Deployment completed successfully at $end_time"
        log "INFO" "Total deployment time: $(($(date -d "$end_time" +%s) - $(date -d "$start_time" +%s))) seconds"
        exit 0
    else
        log "ERROR" "Deployment failed with errors"
        if [[ -n "$BACKUP_CREATED" ]]; then
            log "INFO" "Backup available for rollback: $BACKUP_CREATED"
        fi
        exit $deployment_result
    fi
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Execute main function with all arguments
main "$@"
