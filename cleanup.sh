#!/bin/bash

# =============================================================================
# Decentralized AI Simulation - Cleanup and Maintenance Script
# =============================================================================
# This script performs comprehensive cleanup and maintenance tasks including
# temporary file removal, log rotation, database reset, and cache clearing.
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
# =============================================================================

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
LOG_FILE="$PROJECT_ROOT/logs/cleanup.log"

# Cleanup configuration
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

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Cleanup statistics
FILES_REMOVED=0
DIRS_REMOVED=0
SPACE_FREED=0

# =============================================================================
# Utility Functions
# =============================================================================

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
        "CLEANUP")
            echo -e "${CYAN}[CLEANUP]${NC} $message"
            ;;
    esac
}

show_help() {
    cat << EOF
Decentralized AI Simulation - Cleanup Script

USAGE:
    ./cleanup.sh [OPTIONS]

OPTIONS:
    -h, --help          Show this help message and exit
    -v, --verbose       Enable verbose output showing all operations
    -f, --force         Force cleanup without confirmation prompts
    -a, --all           Perform complete cleanup of all categories
    --logs              Clean up log files and rotate old logs
    --cache             Clear application cache and temporary data
    --temp              Remove temporary files and directories
    --database          Reset database (WARNING: destroys all data)
    --blacklists        Remove generated agent blacklist files
    --reports           Remove test reports and coverage data
    --backups           Clean old backup files (keeps recent ones)
    --dry-run           Show what would be cleaned without making changes

EXAMPLES:
    ./cleanup.sh --logs                 # Clean log files only
    ./cleanup.sh --temp --cache         # Clean temporary files and cache
    ./cleanup.sh --all --force          # Complete cleanup without prompts
    ./cleanup.sh --database --force     # Reset database (destructive!)
    ./cleanup.sh --dry-run --all        # Show complete cleanup plan

DESCRIPTION:
    This script provides comprehensive cleanup and maintenance:
    
    • Log Management: Rotate and compress old log files
    • Cache Clearing: Remove cached data and temporary files
    • Database Reset: Completely reset the simulation database
    • Blacklist Cleanup: Remove generated agent blacklist files
    • Report Cleanup: Remove test reports and coverage data
    • Backup Management: Clean old backup files while preserving recent ones
    • Space Recovery: Free up disk space and optimize storage

WARNING:
    The --database option will permanently delete all simulation data.
    Use --dry-run first to see what will be affected.

EOF
}

get_file_size() {
    local file="$1"
    if [ -f "$file" ]; then
        stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0
    else
        echo 0
    fi
}

get_dir_size() {
    local dir="$1"
    if [ -d "$dir" ]; then
        du -sb "$dir" 2>/dev/null | cut -f1 || echo 0
    else
        echo 0
    fi
}

confirm_action() {
    local message="$1"
    
    if [ "$FORCE_CLEANUP" = true ] || [ "$DRY_RUN" = true ]; then
        return 0
    fi
    
    echo -e "${YELLOW}[CONFIRM]${NC} $message"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "INFO" "Operation cancelled by user"
        return 1
    fi
    return 0
}

safe_remove() {
    local target="$1"
    local description="$2"
    
    if [ ! -e "$target" ]; then
        log "DEBUG" "Target does not exist: $target"
        return 0
    fi
    
    local size=0
    if [ -f "$target" ]; then
        size=$(get_file_size "$target")
    elif [ -d "$target" ]; then
        size=$(get_dir_size "$target")
    fi
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "[DRY RUN] Would remove $description: $target ($(numfmt --to=iec $size))"
        return 0
    fi
    
    log "CLEANUP" "Removing $description: $target ($(numfmt --to=iec $size))"
    
    if [ -f "$target" ]; then
        rm -f "$target"
        ((FILES_REMOVED++))
    elif [ -d "$target" ]; then
        rm -rf "$target"
        ((DIRS_REMOVED++))
    fi
    
    SPACE_FREED=$((SPACE_FREED + size))
}

clean_log_files() {
    if [ "$CLEAN_LOGS" = false ] && [ "$CLEAN_ALL" = false ]; then
        return 0
    fi
    
    log "CLEANUP" "Cleaning log files..."
    
    if ! confirm_action "This will remove old log files and rotate current logs."; then
        return 0
    fi
    
    # Find and clean log files
    local log_patterns=(
        "$PROJECT_ROOT/logs/*.log"
        "$PROJECT_ROOT/*.log"
        "$PROJECT_ROOT/simulation.log*"
        "$PROJECT_ROOT/setup.log*"
        "$PROJECT_ROOT/test.log*"
        "$PROJECT_ROOT/deploy.log*"
    )
    
    for pattern in "${log_patterns[@]}"; do
        for logfile in $pattern; do
            if [ -f "$logfile" ] && [ "$logfile" != "$LOG_FILE" ]; then
                # Keep current cleanup log
                if [[ "$logfile" =~ cleanup\.log$ ]]; then
                    continue
                fi
                
                # Rotate large log files instead of deleting
                local size=$(get_file_size "$logfile")
                if [ $size -gt 10485760 ]; then  # 10MB
                    if [ "$DRY_RUN" = false ]; then
                        mv "$logfile" "${logfile}.$(date +%Y%m%d_%H%M%S)"
                        touch "$logfile"
                        log "INFO" "Rotated large log file: $logfile"
                    else
                        log "INFO" "[DRY RUN] Would rotate large log file: $logfile"
                    fi
                else
                    safe_remove "$logfile" "log file"
                fi
            fi
        done
    done
    
    # Clean old rotated logs (older than 30 days)
    find "$PROJECT_ROOT" -name "*.log.*" -type f -mtime +30 -exec rm -f {} \; 2>/dev/null || true
    
    log "SUCCESS" "Log cleanup completed"
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
    find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Python compiled files
    find "$PROJECT_ROOT" -name "*.pyc" -type f -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*.pyo" -type f -delete 2>/dev/null || true
    
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

show_cleanup_summary() {
    log "INFO" "Cleanup Summary:"
    log "INFO" "  Files Removed: $FILES_REMOVED"
    log "INFO" "  Directories Removed: $DIRS_REMOVED"
    log "INFO" "  Space Freed: $(numfmt --to=iec $SPACE_FREED)"
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "  Mode: DRY RUN (no changes made)"
    fi
    
    log "SUCCESS" "Cleanup completed successfully!"
}

# =============================================================================
# Command Line Argument Parsing
# =============================================================================

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
            shift
            ;;
        -a|--all)
            CLEAN_ALL=true
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
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            log "INFO" "Use --help for usage information"
            exit 1
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
# Main Execution
# =============================================================================

main() {
    log "INFO" "Decentralized AI Simulation - Starting cleanup"
    
    # Initialize log file
    echo "Cleanup started at $(date)" > "$LOG_FILE"
    
    # Show what will be cleaned
    local cleanup_items=()
    [ "$CLEAN_LOGS" = true ] || [ "$CLEAN_ALL" = true ] && cleanup_items+=("logs")
    [ "$CLEAN_CACHE" = true ] || [ "$CLEAN_ALL" = true ] && cleanup_items+=("cache")
    [ "$CLEAN_TEMP" = true ] || [ "$CLEAN_ALL" = true ] && cleanup_items+=("temp files")
    [ "$CLEAN_DATABASE" = true ] || [ "$CLEAN_ALL" = true ] && cleanup_items+=("database")
    [ "$CLEAN_BLACKLISTS" = true ] || [ "$CLEAN_ALL" = true ] && cleanup_items+=("blacklists")
    [ "$CLEAN_REPORTS" = true ] || [ "$CLEAN_ALL" = true ] && cleanup_items+=("reports")
    [ "$CLEAN_BACKUPS" = true ] || [ "$CLEAN_ALL" = true ] && cleanup_items+=("backups")
    
    log "INFO" "Cleanup targets: ${cleanup_items[*]}"
    
    # Perform cleanup operations
    clean_cache_files
    clean_temp_files
    clean_log_files
    clean_blacklist_files
    clean_report_files
    clean_backup_files
    clean_database  # Database cleanup last due to destructive nature
    
    show_cleanup_summary
}

# Run main function
main
