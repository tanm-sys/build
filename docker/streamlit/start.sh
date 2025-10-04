#!/bin/bash

# =============================================================================
# Enhanced Startup Script for Streamlit Container with API Server
# =============================================================================
# Modern bash script for Docker container startup with comprehensive
# initialization, health checks, and graceful process management.
#
# This script initializes the simulation environment, starts the API server,
# and launches the Streamlit web interface for the 3D AI Simulation Platform.
#
# Exit Codes:
#   0 - Success
#   1 - Initialization failed
#   2 - API server failed
#   3 - Streamlit startup failed
# =============================================================================

set -euo pipefail  # Exit on any error, undefined variables, and pipe failures

# Script configuration
readonly APP_DIR="/app"
readonly SCRIPT_DIR="${APP_DIR}/decentralized-ai-simulation"
readonly LOG_DIR="${APP_DIR}/logs"
readonly LOG_FILE="${LOG_DIR}/container-startup.log"

# Container configuration
readonly API_PORT=8502
readonly STREAMLIT_PORT=8501
readonly SIMULATION_AGENTS=100
readonly STARTUP_TIMEOUT=60
readonly HEALTH_CHECK_RETRIES=5
readonly HEALTH_CHECK_DELAY=10

# Colors for output
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly BOLD_GREEN='\033[1;32m'
readonly BOLD_RED='\033[1;31m'
readonly NC='\033[0m' # No Color

# Global variables for process management
API_SERVER_PID=""
STREAMLIT_PID=""

# Enhanced logging function
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

   # Console output with colors
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
       "SUCCESS")
           printf '%b[%s]%b %s\n' "${BOLD_GREEN}" "$level" "${NC}" "$message"
           ;;
   esac
}

# Function to check if a port is available
port_available() {
   local port="$1"
   # Use /dev/tcp if available (Linux), otherwise use netstat
   if command -v netstat &> /dev/null; then
       netstat -tuln 2>/dev/null | grep -q ":$port "
   else
       # Fallback: try to connect (this might not work in all environments)
       timeout 1 bash -c "echo >/dev/tcp/127.0.0.1/$port" 2>/dev/null || return 1
   fi
}

# Function to wait for service to be ready
wait_for_service() {
   local url="$1"
   local service_name="$2"
   local retries="$HEALTH_CHECK_RETRIES"
   local delay="$HEALTH_CHECK_DELAY"

   log "INFO" "Waiting for $service_name to be ready at $url"

   for ((i=1; i<=retries; i++)); do
       if curl -f -s "$url" > /dev/null 2>&1; then
           log "SUCCESS" "$service_name is ready!"
           return 0
       fi

       log "INFO" "Attempt $i/$retries: $service_name not ready, waiting ${delay}s..."
       sleep "$delay"
   done

   log "ERROR" "$service_name failed to become ready after $retries attempts"
   return 1
}

# Cleanup function for graceful shutdown
cleanup() {
   local exit_code=$?
   local signal="$1"

   log "INFO" "Received signal ${signal:-"EXIT"}, cleaning up..."

   # Stop API server if running
   if [[ -n "$API_SERVER_PID" ]] && kill -0 "$API_SERVER_PID" 2>/dev/null; then
       log "INFO" "Stopping API server (PID: $API_SERVER_PID)"
       kill -TERM "$API_SERVER_PID" 2>/dev/null || true
       wait "$API_SERVER_PID" 2>/dev/null || true
   fi

   # Stop Streamlit if running
   if [[ -n "$STREAMLIT_PID" ]] && kill -0 "$STREAMLIT_PID" 2>/dev/null; then
       log "INFO" "Stopping Streamlit (PID: $STREAMLIT_PID)"
       kill -TERM "$STREAMLIT_PID" 2>/dev/null || true
       wait "$STREAMLIT_PID" 2>/dev/null || true
   fi

   log "INFO" "Cleanup completed"
   exit $exit_code
}

# Trap signals for cleanup
trap 'cleanup SIGINT' SIGINT
trap 'cleanup SIGTERM' SIGTERM
trap 'cleanup EXIT' EXIT

# Enhanced initialization function
initialize_simulation() {
   log "INFO" "Initializing simulation for API server..."

   # Set Python path for imports
   export PYTHONPATH="${APP_DIR}:${SCRIPT_DIR}"

   # Initialize simulation with error handling
   if python -c "
import sys, os
sys.path.insert(0, '${APP_DIR}')
sys.path.insert(0, '${SCRIPT_DIR}')

try:
   from decentralized_ai_simulation.src.ui.api_server import initialize_api_simulation
   print('🚀 Initializing simulation with ${SIMULATION_AGENTS} agents...')
   success = initialize_api_simulation(${SIMULATION_AGENTS})
   if success:
       print('✅ Simulation initialized successfully')
       sys.exit(0)
   else:
       print('❌ Failed to initialize simulation')
       sys.exit(1)
except ImportError as e:
   print(f'❌ Import error: {e}')
   sys.exit(1)
except Exception as e:
   print(f'❌ Initialization error: {e}')
   sys.exit(1)
"; then
       log "SUCCESS" "Simulation initialization completed"
       return 0
   else
       log "ERROR" "Simulation initialization failed"
       return 1
   fi
}

# Enhanced API server startup
start_api_server() {
   log "INFO" "Starting API server on port $API_PORT..."

   # Check if port is available
   if port_available "$API_PORT"; then
       log "WARN" "Port $API_PORT appears to be in use"
   fi

   # Start API server in background with process management
   python -c "
import sys, os
import signal
import threading
sys.path.insert(0, '${APP_DIR}')
sys.path.insert(0, '${SCRIPT_DIR}')

from decentralized_ai_simulation.src.ui.api_server import start_api_server

print('🌐 Starting API server on port ${API_PORT}...')
try:
   server = start_api_server(${API_PORT})
   print('✅ API server started successfully')
except Exception as e:
   print(f'❌ Failed to start API server: {e}')
   sys.exit(1)
" &

   API_SERVER_PID=$!
   log "INFO" "API server started with PID: $API_SERVER_PID"

   # Wait for API server to be ready
   if wait_for_service "http://localhost:$API_PORT/health" "API server"; then
       log "SUCCESS" "API server is ready and responding"
       return 0
   else
       log "ERROR" "API server failed to become ready"
       return 2
   fi
}

# Enhanced Streamlit startup
start_streamlit() {
   log "INFO" "Starting Streamlit UI on port $STREAMLIT_PORT..."

   # Check if port is available
   if port_available "$STREAMLIT_PORT"; then
       log "WARN" "Port $STREAMLIT_PORT appears to be in use"
   fi

   # Start Streamlit with enhanced configuration
   streamlit run "${SCRIPT_DIR}/src/ui/streamlit_app.py" \
       --server.port "$STREAMLIT_PORT" \
       --server.address 0.0.0.0 \
       --server.headless true \
       --browser.gatherUsageStats false \
       --theme.base dark &

   STREAMLIT_PID=$!
   log "INFO" "Streamlit started with PID: $STREAMLIT_PID"

   # Wait for Streamlit to be ready
   if wait_for_service "http://localhost:$STREAMLIT_PORT" "Streamlit"; then
       log "SUCCESS" "Streamlit UI is ready at http://localhost:$STREAMLIT_PORT"
       return 0
   else
       log "ERROR" "Streamlit failed to become ready"
       return 3
   fi
}

# Main execution function
main() {
   local start_time
   start_time=$(date '+%Y-%m-%d %H:%M:%S')

   log "INFO" "Starting 3D AI Simulation Platform at $start_time"
   log "INFO" "Container configuration:"
   log "INFO" "  App directory: $APP_DIR"
   log "INFO" "  Script directory: $SCRIPT_DIR"
   log "INFO" "  Log file: $LOG_FILE"
   log "INFO" "  API port: $API_PORT"
   log "INFO" "  Streamlit port: $STREAMLIT_PORT"
   log "INFO" "  Simulation agents: $SIMULATION_AGENTS"

   # Initialize log file
   {
       echo "=========================================="
       echo "Container startup session started at $start_time"
       echo "App directory: $APP_DIR"
       echo "API port: $API_PORT"
       echo "Streamlit port: $STREAMLIT_PORT"
       echo "Simulation agents: $SIMULATION_AGENTS"
       echo "=========================================="
   } > "$LOG_FILE"

   # Phase 1: Initialize simulation
   if initialize_simulation; then
       log "INFO" "Simulation initialization phase completed"
   else
       log "ERROR" "Simulation initialization phase failed"
       exit 1
   fi

   # Phase 2: Start API server
   if start_api_server; then
       log "INFO" "API server startup phase completed"
   else
       log "ERROR" "API server startup phase failed"
       exit 2
   fi

   # Phase 3: Start Streamlit UI
   if start_streamlit; then
       log "INFO" "Streamlit UI startup phase completed"
   else
       log "ERROR" "Streamlit UI startup phase failed"
       exit 3
   fi

   # All services started successfully
   local end_time
   end_time=$(date '+%Y-%m-%d %H:%M:%S')

   log "SUCCESS" "3D AI Simulation Platform started successfully at $end_time"
   log "INFO" "Services available:"
   log "INFO" "  🌐 API Server: http://localhost:$API_PORT"
   log "INFO" "  📱 Streamlit UI: http://localhost:$STREAMLIT_PORT"
   log "INFO" "  📊 Simulation: $SIMULATION_AGENTS agents initialized"
   log "INFO" ""
   log "INFO" "Press Ctrl+C to stop all services"

   # Wait for processes (this will run indefinitely until interrupted)
   wait
}

# Execute main function
main "$@"