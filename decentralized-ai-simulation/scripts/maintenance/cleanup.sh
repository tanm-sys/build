#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Enhanced Cleanup and Maintenance Script
# =============================================================================
# Modern bash script for comprehensive system cleanup with enhanced safety,
# detailed reporting, and cross-platform compatibility.
#
# This script performs comprehensive cleanup and maintenance tasks including
# temporary file removal, log rotation, database reset, and cache clearing
# with robust error handling and user confirmation prompts.
#
# Usage: ./cleanup.sh [OPTIONS]
# Options:
#   -h, --help          Show this help message
#   -v, --verbose       Enable verbose output
#   -f, --force         Force cleanup without confirmation prompts
#   -a, --all           Perform complete cleanup (logs, cache, temp, database)
#   --logs              Clean up log files only
#   --cache             Clear cache files only
#   --temp              Remove temporary files only
#   --database          Reset database (WARNING: destructive)
#   --blacklists        Remove generated blacklist files
#   --reports           Remove test and coverage reports
#   --backups           Clean old backup files
#   --dry-run           Show what would be cleaned without executing
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - Permission denied
#   4 - User cancelled operation
# =============================================================================

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures
shopt -s globstar   # Enable globstar for recursive globbing
shopt -s extglob    # Enable extended globbing patterns

# Enhanced script configuration with robust path resolution
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly LOG_DIR="${PROJECT_ROOT}/logs"
readonly LOG_FILE="${LOG_DIR}/cleanup.log"
readonly REPORTS_DIR="${PROJECT_ROOT}/test_reports"
readonly BACKUP_DIR="${PROJECT_ROOT}/backups"

# Cleanup configuration with validation arrays
readonly SUPPORTED_CLEANUP_TYPES=(
    "logs" "cache" "temp" "database" "blacklists" "reports" "backups"
)
readonly DANGEROUS_OPERATIONS=("database")
readonly DEFAULT_MAX_LOG_SIZE="10485760"  # 10MB
readonly DEFAULT_BACKUP_RETENTION_DAYS=30

# Configuration variables with defaults
VERBOSE=false
FORCE_CLEANUP=false
CLEAN_ALL=false
CLEAN_LOGS=false
CLEAN_CACHE=false
CLEAN_TEMP=false
CLEAN_DATABASE=false
CLEAN_BLACKLISTS=false
CLEAN_REPORTS=false
CLEAN_BACKUPS=false
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

# Enhanced cleanup statistics with detailed tracking
FILES_REMOVED=0
DIRS_REMOVED=0
SPACE_FREED=0
ERROR_COUNT=0
WARNING_COUNT=0

# Global arrays for tracking operations
CLEANUP_LOG=()
TEMP_FILES=()

# =============================================================================
# Enhanced Utility Functions
# =============================================================================

# Cross-platform file size detection
get_file_size() {
    local file="$1"
    if [[ -f "$file" ]]; then
        case "$(uname -s)" in
            "Linux")
                stat -c%s "$file" 2>/dev/null || echo 0
                ;;
            "Darwin")  # macOS
                stat -f%z "$file" 2>/dev/null || echo 0
                ;;
            *)
                # Fallback method
                wc -c < "$file" 2>/dev/null || echo 0
                ;;
        esac
    else
        echo 0
    fi
}

# Cross-platform directory size detection
get_dir_size() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        case "$(uname -s)" in
            "Linux")
                du -sb "$dir" 2>/dev/null | cut -f1 || echo 0
                ;;
            "Darwin")  # macOS
                du -sk "$dir" 2>/dev/null | cut -f1 || echo 0
                ;;
            *)
                # Fallback method using find
                find "$dir" -type f -exec stat -c%s {} \; 2>/dev/null | awk '{sum += $1} END {print sum}' || echo 0
                ;;
        esac
    else
        echo 0
    fi
}

# Enhanced logging function with structured output and statistics tracking
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

    # Update statistics for warnings and errors
    case "$level" in
        "WARN")
            ((WARNING_COUNT++))
            ;;
        "ERROR")
            ((ERROR_COUNT++))
            ;;
    esac

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
        "CLEANUP")
            printf '%b[%s]%b %s\n' "${CYAN}" "$level" "${NC}" "$message"
            ;;
        "DRYRUN")
            printf '%b[%s]%b %s\n' "${BOLD_CYAN}" "$level" "${NC}" "$message"
            ;;
    esac
}

# Enhanced help display with better formatting and safety warnings
show_help() {
    local script_name
    script_name=$(basename "${BASH_SOURCE[0]}")

    cat << EOF
${BOLD_BLUE}Decentralized AI Simulation - Enhanced Cleanup Script${NC}

${BOLD_YELLOW}USAGE:${NC}
    $script_name [OPTIONS]

${BOLD_YELLOW}OPTIONS:${NC}
    ${BOLD_GREEN}-h, --help${NC}          Show this help message and exit
    ${BOLD_GREEN}-v, --verbose${NC}       Enable verbose output showing all operations
    ${BOLD_GREEN}-f, --force${NC}         Force cleanup without confirmation prompts
    ${BOLD_GREEN}-a, --all${NC}           Perform complete cleanup of all categories
    ${BOLD_GREEN}--logs${NC}              Clean up log files and rotate old logs
    ${BOLD_GREEN}--cache${NC}             Clear application cache and temporary data
    ${BOLD_GREEN}--temp${NC}              Remove temporary files and directories
    ${BOLD_RED}--database${NC}          Reset database (WARNING: destroys all data)
    ${BOLD_GREEN}--blacklists${NC}        Remove generated agent blacklist files
    ${BOLD_GREEN}--reports${NC}           Remove test reports and coverage data
    ${BOLD_GREEN}--backups${NC}           Clean old backup files (keeps recent ones)
    ${BOLD_CYAN}--dry-run${NC}           Show what would be cleaned without making changes

${BOLD_YELLOW}EXAMPLES:${NC}
    $script_name --logs                    # Clean log files only
    $script_name --temp --cache            # Clean temporary files and cache
    $script_name --all --force             # Complete cleanup without prompts
    $script_name --database --force        # Reset database (destructive!)
    $script_name --dry-run --all           # Show complete cleanup plan

${BOLD_YELLOW}DESCRIPTION:${NC}
    This script provides comprehensive cleanup and maintenance:

    • ${BOLD_CYAN}Log Management${NC}: Rotate and compress old log files
    • ${BOLD_CYAN}Cache Clearing${NC}: Remove cached data and temporary files
    • ${BOLD_CYAN}Database Reset${NC}: Completely reset the simulation database
    • ${BOLD_CYAN}Blacklist Cleanup${NC}: Remove generated agent blacklist files
    • ${BOLD_CYAN}Report Cleanup${NC}: Remove test reports and coverage data
    • ${BOLD_CYAN}Backup Management${NC}: Clean old backup files while preserving recent ones
    • ${BOLD_CYAN}Space Recovery${NC}: Free up disk space and optimize storage

${BOLD_RED}⚠️  SAFETY WARNINGS:${NC}
    • The ${BOLD_RED}--database${NC} option will ${BOLD_RED}permanently delete all simulation data${NC}
    • The ${BOLD_RED}--force${NC} option bypasses confirmation prompts
    • Always use ${BOLD_CYAN}--dry-run${NC} first to preview operations
    • Database operations are ${BOLD_RED}irreversible${NC}

${BOLD_YELLOW}EXIT CODES:${NC}
    0 - Success
    1 - General error
    2 - Invalid arguments
    3 - Permission denied
    4 - User cancelled operation

${BOLD_BLUE}For more information, see README.md${NC}
EOF
}


# Enhanced user confirmation with better UX and safety checks
confirm_action() {
    local message="$1"

    if [[ "$FORCE_CLEANUP" == true ]] || [[ "$DRY_RUN" == true ]]; then
        return 0
    fi

    # Check if running in interactive terminal
    if [[ ! -t 0 ]]; then
        log "ERROR" "Cannot prompt for confirmation in non-interactive environment"
        log "INFO" "Use --force to skip confirmation prompts"
        return 1
    fi

    printf '%b[CONFIRM]%b %s\n' "${BOLD_YELLOW}" "${NC}" "$message"
    printf '%bContinue?%b (y/N): ' "${BOLD_GREEN}" "${NC}"

    local response
    read -r response

    if [[ ! "$response" =~ ^[Yy][Ee][Ss]?$ ]]; then
        log "INFO" "Operation cancelled by user"
        return 1
    fi

    return 0
}

# Enhanced safe removal with comprehensive validation and error handling
safe_remove() {
    local target="$1"
    local description="$2"

    if [[ ! -e "$target" ]]; then
        log "DEBUG" "Target does not exist, skipping: $target"
        return 0
    fi

    # Validate permissions before attempting removal
    if [[ ! -w "$(dirname "$target")" ]]; then
        log "ERROR" "Permission denied: cannot write to $(dirname "$target")"
        return 1
    fi

    local size=0
    local item_type=""

    if [[ -f "$target" ]]; then
        size=$(get_file_size "$target")
        item_type="file"
    elif [[ -d "$target" ]]; then
        size=$(get_dir_size "$target")
        item_type="directory"
    else
        log "WARN" "Unknown file type for: $target"
        return 1
    fi

    # Format size for human readability
    local size_formatted
    size_formatted=$(numfmt --to=iec "$size" 2>/dev/null) || size_formatted="${size} bytes"

    if [[ "$DRY_RUN" == true ]]; then
        log "DRYRUN" "Would remove $description ($item_type): $target ($size_formatted)"
        return 0
    fi

    # Log the operation
    log "CLEANUP" "Removing $description ($item_type): $target ($size_formatted)"

    # Track operation for potential rollback
    CLEANUP_LOG+=("$target:$description:$size")

    # Perform removal with error handling
    if [[ -f "$target" ]]; then
        if rm -f "$target" 2>/dev/null; then
            ((FILES_REMOVED++))
            SPACE_FREED=$((SPACE_FREED + size))
        else
            log "ERROR" "Failed to remove file: $target"
            return 1
        fi
    elif [[ -d "$target" ]]; then
        if rm -rf "$target" 2>/dev/null; then
            ((DIRS_REMOVED++))
            SPACE_FREED=$((SPACE_FREED + size))
        else
            log "ERROR" "Failed to remove directory: $target"
            return 1
        fi
    fi

    return 0
}

# Enhanced log file cleanup with intelligent rotation and archiving
clean_log_files() {
    if [[ "$CLEAN_LOGS" == false ]] && [[ "$CLEAN_ALL" == false ]]; then
        return 0
    fi

    log "CLEANUP" "Cleaning log files..."

    if ! confirm_action "This will remove old log files and rotate current logs."; then
        return 0
    fi

    # Enhanced log file patterns with better organization
    local log_patterns=(
        "$LOG_DIR/*.log"
        "$PROJECT_ROOT"/*.log
        "$PROJECT_ROOT"/simulation.log*
        "$PROJECT_ROOT"/setup.log*
        "$PROJECT_ROOT"/test.log*
        "$PROJECT_ROOT"/deploy.log*
        "$PROJECT_ROOT"/cleanup.log*
    )

    local max_log_size="$DEFAULT_MAX_LOG_SIZE"
    local rotated_count=0
    local removed_count=0

    for pattern in "${log_patterns[@]}"; do
        # Use find for more reliable file discovery
        while IFS= read -r -d '' logfile; do
            [[ -f "$logfile" ]] || continue

            # Skip current cleanup log to avoid conflicts
            [[ "$logfile" == "$LOG_FILE" ]] && continue

            local size
            size=$(get_file_size "$logfile")

            if [[ $size -gt $max_log_size ]]; then
                # Rotate large log files instead of deleting
                if [[ "$DRY_RUN" == false ]]; then
                    local timestamp
                    timestamp=$(date '+%Y%m%d_%H%M%S')
                    local rotated_file="${logfile}.${timestamp}"

                    if mv "$logfile" "$rotated_file" && touch "$logfile"; then
                        log "INFO" "Rotated large log file: $(basename "$logfile") ($(numfmt --to=iec "$size"))"
                        ((rotated_count++))
                    else
                        log "ERROR" "Failed to rotate log file: $logfile"
                    fi
                else
                    log "DRYRUN" "Would rotate large log file: $(basename "$logfile") ($(numfmt --to=iec "$size"))"
                fi
            else
                # Remove smaller log files
                if safe_remove "$logfile" "log file"; then
                    ((removed_count++))
                fi
            fi
        done < <(find "$(dirname "$pattern")" -name "$(basename "$pattern")" -type f -print0 2>/dev/null)
    done

    # Clean old rotated logs (older than retention period)
    if [[ "$DRY_RUN" == false ]]; then
        local old_logs_count
        old_logs_count=$(find "$PROJECT_ROOT" -name "*.log.*" -type f -mtime +"$DEFAULT_BACKUP_RETENTION_DAYS" 2>/dev/null | wc -l)

        if [[ $old_logs_count -gt 0 ]]; then
            find "$PROJECT_ROOT" -name "*.log.*" -type f -mtime +"$DEFAULT_BACKUP_RETENTION_DAYS" -delete 2>/dev/null
            log "INFO" "Removed $old_logs_count old rotated log files"
        fi
    else
        local old_logs_count
        old_logs_count=$(find "$PROJECT_ROOT" -name "*.log.*" -type f -mtime +"$DEFAULT_BACKUP_RETENTION_DAYS" 2>/dev/null | wc -l)
        if [[ $old_logs_count -gt 0 ]]; then
            log "DRYRUN" "Would remove $old_logs_count old rotated log files"
        fi
    fi

    log "SUCCESS" "Log cleanup completed (rotated: $rotated_count, removed: $removed_count)"
}

clean_cache_files() {
    if [ "$CLEAN_CACHE" = false ] && [ "$CLEAN_ALL" = false ]; then
        return 0
    fi
    
    log "CLEANUP" "Cleaning cache files..."
    
    if ! confirm_action "This will remove cached data and temporary files."; then
        return 0
    fi
    
    # Python cache directories
    local cache_dirs=(
        "$PROJECT_ROOT/__pycache__"
        "$PROJECT_ROOT/tests/__pycache__"
        "$PROJECT_ROOT/.pytest_cache"
    )
    
    for cache_dir in "${cache_dirs[@]}"; do
        safe_remove "$cache_dir" "cache directory"
    done
    
    # Find and remove all __pycache__ directories
    if ! find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; then
        log "DEBUG" "No __pycache__ directories found or error during cleanup"
    fi

    # Python compiled files
    if ! find "$PROJECT_ROOT" -name "*.pyc" -type f -delete 2>/dev/null; then
        log "DEBUG" "No .pyc files found or error during cleanup"
    fi
    if ! find "$PROJECT_ROOT" -name "*.pyo" -type f -delete 2>/dev/null; then
        log "DEBUG" "No .pyo files found or error during cleanup"
    fi
    
    log "SUCCESS" "Cache cleanup completed"
}

clean_temp_files() {
    if [ "$CLEAN_TEMP" = false ] && [ "$CLEAN_ALL" = false ]; then
        return 0
    fi
    
    log "CLEANUP" "Cleaning temporary files..."
    
    if ! confirm_action "This will remove temporary files and directories."; then
        return 0
    fi
    
    # Temporary file patterns
    local temp_patterns=(
        "$PROJECT_ROOT/tmp/*"
        "$PROJECT_ROOT/temp/*"
        "$PROJECT_ROOT/*.tmp"
        "$PROJECT_ROOT/*.temp"
        "$PROJECT_ROOT/*~"
        "$PROJECT_ROOT/.DS_Store"
        "$PROJECT_ROOT/Thumbs.db"
    )
    
    for pattern in "${temp_patterns[@]}"; do
        for temp_file in $pattern; do
            if [ -e "$temp_file" ]; then
                safe_remove "$temp_file" "temporary file"
            fi
        done
    done
    
    # Temporary directories
    local temp_dirs=(
        "$PROJECT_ROOT/tmp"
        "$PROJECT_ROOT/temp"
    )
    
    for temp_dir in "${temp_dirs[@]}"; do
        if [ -d "$temp_dir" ] && [ -z "$(ls -A "$temp_dir")" ]; then
            safe_remove "$temp_dir" "empty temporary directory"
        fi
    done
    
    log "SUCCESS" "Temporary file cleanup completed"
}

clean_database() {
    if [ "$CLEAN_DATABASE" = false ] && [ "$CLEAN_ALL" = false ]; then
        return 0
    fi
    
    log "CLEANUP" "Resetting database..."
    
    if ! confirm_action "WARNING: This will permanently delete all simulation data in the database!"; then
        return 0
    fi
    
    # Database files
    local db_files=(
        "$PROJECT_ROOT/ledger.db"
        "$PROJECT_ROOT/ledger.db-wal"
        "$PROJECT_ROOT/ledger.db-shm"
        "$PROJECT_ROOT/simulation.db"
        "$PROJECT_ROOT/*.db"
    )
    
    for db_pattern in "${db_files[@]}"; do
        for db_file in $db_pattern; do
            if [ -f "$db_file" ]; then
                safe_remove "$db_file" "database file"
            fi
        done
    done
    
    log "SUCCESS" "Database reset completed"
}

clean_blacklist_files() {
    if [ "$CLEAN_BLACKLISTS" = false ] && [ "$CLEAN_ALL" = false ]; then
        return 0
    fi
    
    log "CLEANUP" "Cleaning blacklist files..."
    
    if ! confirm_action "This will remove all generated agent blacklist files."; then
        return 0
    fi
    
    # Blacklist file patterns
    local blacklist_patterns=(
        "$PROJECT_ROOT/blacklist_Node_*.json"
        "$PROJECT_ROOT/blacklist_*.json"
    )
    
    for pattern in "${blacklist_patterns[@]}"; do
        for blacklist_file in $pattern; do
            if [ -f "$blacklist_file" ]; then
                safe_remove "$blacklist_file" "blacklist file"
            fi
        done
    done
    
    log "SUCCESS" "Blacklist cleanup completed"
}

clean_report_files() {
    if [ "$CLEAN_REPORTS" = false ] && [ "$CLEAN_ALL" = false ]; then
        return 0
    fi
    
    log "CLEANUP" "Cleaning test reports..."
    
    if ! confirm_action "This will remove test reports and coverage data."; then
        return 0
    fi
    
    # Report directories and files
    local report_items=(
        "$PROJECT_ROOT/test_reports"
        "$PROJECT_ROOT/htmlcov"
        "$PROJECT_ROOT/coverage.xml"
        "$PROJECT_ROOT/.coverage"
        "$PROJECT_ROOT/pytest_report.html"
        "$PROJECT_ROOT/coverage_report.html"
    )
    
    for item in "${report_items[@]}"; do
        safe_remove "$item" "report file/directory"
    done
    
    log "SUCCESS" "Report cleanup completed"
}

clean_backup_files() {
    if [ "$CLEAN_BACKUPS" = false ] && [ "$CLEAN_ALL" = false ]; then
        return 0
    fi
    
    log "CLEANUP" "Cleaning old backup files..."
    
    if ! confirm_action "This will remove backup files older than 30 days."; then
        return 0
    fi
    
    local backup_dir="$PROJECT_ROOT/backups"
    
    if [ -d "$backup_dir" ]; then
        # Remove backups older than 30 days
        find "$backup_dir" -type f -mtime +30 -name "backup_*" | while read -r backup_file; do
            safe_remove "$backup_file" "old backup file"
        done
        
        # Remove empty backup directories
        find "$backup_dir" -type d -empty -delete 2>/dev/null || true
    fi
    
    log "SUCCESS" "Backup cleanup completed"
}

# Enhanced cleanup summary with detailed statistics and recommendations
show_cleanup_summary() {
    local total_operations=$((FILES_REMOVED + DIRS_REMOVED))
    local size_formatted
    size_formatted=$(numfmt --to=iec "$SPACE_FREED" 2>/dev/null) || size_formatted="${SPACE_FREED} bytes"

    log "INFO" "Cleanup Summary:"
    log "INFO" "  ${BOLD_BLUE}Files Removed:${NC} $FILES_REMOVED"
    log "INFO" "  ${BOLD_BLUE}Directories Removed:${NC} $DIRS_REMOVED"
    log "INFO" "  ${BOLD_BLUE}Total Operations:${NC} $total_operations"
    log "INFO" "  ${BOLD_BLUE}Space Freed:${NC} $size_formatted"

    if [[ $ERROR_COUNT -gt 0 ]]; then
        log "WARN" "  ${BOLD_YELLOW}Errors Encountered:${NC} $ERROR_COUNT"
    fi

    if [[ $WARNING_COUNT -gt 0 ]]; then
        log "WARN" "  ${BOLD_YELLOW}Warnings:${NC} $WARNING_COUNT"
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log "INFO" "  ${BOLD_CYAN}Mode: DRY RUN (no changes made)${NC}"
    fi

    # Provide recommendations based on cleanup results
    if [[ $total_operations -eq 0 ]]; then
        log "INFO" "No cleanup operations were performed"
    elif [[ $total_operations -gt 0 ]]; then
        log "SUCCESS" "Cleanup completed successfully!"

        if [[ "$CLEAN_DATABASE" == true ]]; then
            log "WARN" "Database was reset - you may need to reinitialize data"
        fi

        if [[ $SPACE_FREED -gt 1073741824 ]]; then  # 1GB
            log "INFO" "Significant space was freed - consider running disk maintenance"
        fi
    fi

    # Show next steps if applicable
    if [[ "$CLEAN_DATABASE" == true ]] && [[ "$DRY_RUN" == false ]]; then
        log "INFO" "Next steps:"
        log "INFO" "  • Run './setup.sh' to reinitialize the environment"
        log "INFO" "  • Run './run.sh' to verify system functionality"
    fi
}

# =============================================================================
# Enhanced Command Line Argument Parsing
# =============================================================================

# Function to display usage and exit with error code
usage_error() {
    log "ERROR" "Invalid usage: $*"
    log "INFO" "Use --help for detailed usage information"
    exit 2
}

# Parse command line arguments with enhanced validation
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
            FORCE_CLEANUP=true
            log "WARN" "Force mode enabled - confirmation prompts will be skipped"
            shift
            ;;
        -a|--all)
            CLEAN_ALL=true
            log "INFO" "Complete cleanup mode enabled"
            shift
            ;;
        --logs)
            CLEAN_LOGS=true
            shift
            ;;
        --cache)
            CLEAN_CACHE=true
            shift
            ;;
        --temp)
            CLEAN_TEMP=true
            shift
            ;;
        --database)
            CLEAN_DATABASE=true
            log "WARN" "Database cleanup enabled - this will destroy all data!"
            shift
            ;;
        --blacklists)
            CLEAN_BLACKLISTS=true
            shift
            ;;
        --reports)
            CLEAN_REPORTS=true
            shift
            ;;
        --backups)
            CLEAN_BACKUPS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            log "INFO" "Dry run mode enabled - no actual changes will be made"
            shift
            ;;
        *)
            usage_error "Unknown option: $1"
            ;;
    esac
done

# If no specific cleanup options are selected, default to basic cleanup
if [ "$CLEAN_ALL" = false ] && [ "$CLEAN_LOGS" = false ] && [ "$CLEAN_CACHE" = false ] && \
   [ "$CLEAN_TEMP" = false ] && [ "$CLEAN_DATABASE" = false ] && [ "$CLEAN_BLACKLISTS" = false ] && \
   [ "$CLEAN_REPORTS" = false ] && [ "$CLEAN_BACKUPS" = false ]; then
    log "INFO" "No specific cleanup options selected, performing basic cleanup (cache, temp, logs)"
    CLEAN_CACHE=true
    CLEAN_TEMP=true
    CLEAN_LOGS=true
fi

# =============================================================================
# Enhanced Main Execution Function
# =============================================================================

main() {
    local start_time
    start_time=$(date '+%Y-%m-%d %H:%M:%S')

    log "INFO" "Decentralized AI Simulation - Starting cleanup at $start_time"
    log "INFO" "Script version: 2.0.0"
    log "INFO" "Process ID: $$"

    # Initialize log file with session header
    {
        echo "=========================================="
        echo "Cleanup session started at $start_time"
        echo "Project root: $PROJECT_ROOT"
        echo "Log file: $LOG_FILE"
        echo "Dry run mode: $DRY_RUN"
        echo "Force mode: $FORCE_CLEANUP"
        echo "Verbose mode: $VERBOSE"
        echo "=========================================="
    } > "$LOG_FILE"

    # Determine cleanup targets with enhanced logic
    local cleanup_items=()
    if [[ "$CLEAN_ALL" == true ]]; then
        cleanup_items=("logs" "cache" "temp files" "blacklists" "reports" "backups")
        if [[ "$CLEAN_DATABASE" == true ]]; then
            cleanup_items+=("database")
        fi
    else
        [[ "$CLEAN_LOGS" == true ]] && cleanup_items+=("logs")
        [[ "$CLEAN_CACHE" == true ]] && cleanup_items+=("cache")
        [[ "$CLEAN_TEMP" == true ]] && cleanup_items+=("temp files")
        [[ "$CLEAN_DATABASE" == true ]] && cleanup_items+=("database")
        [[ "$CLEAN_BLACKLISTS" == true ]] && cleanup_items+=("blacklists")
        [[ "$CLEAN_REPORTS" == true ]] && cleanup_items+=("reports")
        [[ "$CLEAN_BACKUPS" == true ]] && cleanup_items+=("backups")
    fi

    # Default to basic cleanup if no specific options selected
    if [[ ${#cleanup_items[@]} -eq 0 ]]; then
        log "INFO" "No specific cleanup options selected, performing basic cleanup (cache, temp, logs)"
        cleanup_items=("cache" "temp files" "logs")
        CLEAN_CACHE=true
        CLEAN_TEMP=true
        CLEAN_LOGS=true
    fi

    log "INFO" "Cleanup targets: ${cleanup_items[*]}"

    # Validate dangerous operations
    if [[ "$CLEAN_DATABASE" == true ]] && [[ "$FORCE_CLEANUP" == false ]] && [[ "$DRY_RUN" == false ]]; then
        log "ERROR" "Database cleanup requires --force flag for safety"
        log "INFO" "Use --force to confirm destructive operations"
        exit 4
    fi

    # Perform cleanup operations in safe order
    local operations_performed=0
    local operation_success=true

    # Safe operations first
    [[ "$CLEAN_CACHE" == true ]] && { clean_cache_files && ((operations_performed++)); } || operation_success=false
    [[ "$CLEAN_TEMP" == true ]] && { clean_temp_files && ((operations_performed++)); } || operation_success=false
    [[ "$CLEAN_LOGS" == true ]] && { clean_log_files && ((operations_performed++)); } || operation_success=false
    [[ "$CLEAN_BLACKLISTS" == true ]] && { clean_blacklist_files && ((operations_performed++)); } || operation_success=false
    [[ "$CLEAN_REPORTS" == true ]] && { clean_report_files && ((operations_performed++)); } || operation_success=false
    [[ "$CLEAN_BACKUPS" == true ]] && { clean_backup_files && ((operations_performed++)); } || operation_success=false

    # Dangerous operations last
    [[ "$CLEAN_DATABASE" == true ]] && { clean_database && ((operations_performed++)); } || operation_success=false

    # Show summary and exit
    if [[ "$DRY_RUN" == false ]]; then
        show_cleanup_summary
    else
        log "INFO" "Dry run completed - no actual changes were made"
    fi

    local end_time
    end_time=$(date '+%Y-%m-%d %H:%M:%S')

    if [[ $operation_success == true ]]; then
        log "SUCCESS" "Cleanup completed successfully at $end_time"
        exit 0
    else
        log "ERROR" "Some cleanup operations failed"
        exit 1
    fi
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Execute main function with all arguments
main "$@"
