#!/bin/bash

# =============================================================================
# Decentralized AI Simulation Platform - Run Script
# =============================================================================
# This script provides multiple options to run the platform in different modes:
# - Docker Compose (recommended for production)
# - Local Development (backend, frontend, streamlit)
# - Individual components
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker and Docker Compose
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        return 1
    fi
    
    print_success "Docker and Docker Compose are installed"
    return 0
}

# Check Python
check_python() {
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        return 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python $python_version is installed"
    return 0
}

# Check Node.js
check_node() {
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        echo "Visit: https://nodejs.org/"
        return 1
    fi

    node_version=$(node --version)
    print_success "Node.js $node_version is installed"
    return 0
}

# =============================================================================
# Port Management Functions
# =============================================================================

# Check if a port is in use
is_port_in_use() {
    local port=$1

    # Try lsof first (most reliable)
    if command_exists lsof; then
        lsof -i ":$port" -sTCP:LISTEN -t >/dev/null 2>&1
        return $?
    fi

    # Fallback to netstat
    if command_exists netstat; then
        netstat -tuln | grep -q ":$port "
        return $?
    fi

    # Fallback to ss
    if command_exists ss; then
        ss -tuln | grep -q ":$port "
        return $?
    fi

    # If no tools available, assume port is free
    return 1
}

# Get PID of process using a port
get_port_pid() {
    local port=$1

    if command_exists lsof; then
        lsof -i ":$port" -sTCP:LISTEN -t 2>/dev/null | head -n 1
    elif command_exists netstat; then
        netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -n 1
    elif command_exists ss; then
        ss -tulnp 2>/dev/null | grep ":$port " | sed 's/.*pid=\([0-9]*\).*/\1/' | head -n 1
    fi
}

# Get process name using a port
get_port_process() {
    local port=$1

    if command_exists lsof; then
        lsof -i ":$port" -sTCP:LISTEN 2>/dev/null | tail -n 1 | awk '{print $1}'
    elif command_exists netstat; then
        netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f2
    elif command_exists ss; then
        ss -tulnp 2>/dev/null | grep ":$port " | sed 's/.*"\([^"]*\)".*/\1/'
    fi
}

# Kill process on a specific port
kill_port_process() {
    local port=$1
    local force=${2:-false}

    if ! is_port_in_use "$port"; then
        return 0
    fi

    local pid=$(get_port_pid "$port")
    local process=$(get_port_process "$port")

    if [ -z "$pid" ]; then
        print_warning "Could not determine PID for port $port"
        return 1
    fi

    print_warning "Port $port is in use by $process (PID: $pid)"

    if [ "$force" = "true" ]; then
        print_info "Killing process $pid..."
        kill -9 "$pid" 2>/dev/null || sudo kill -9 "$pid" 2>/dev/null
        sleep 1

        if is_port_in_use "$port"; then
            print_error "Failed to kill process on port $port"
            return 1
        else
            print_success "Process on port $port killed"
            return 0
        fi
    else
        read -p "Kill this process? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill -9 "$pid" 2>/dev/null || sudo kill -9 "$pid" 2>/dev/null
            sleep 1

            if is_port_in_use "$port"; then
                print_error "Failed to kill process on port $port"
                return 1
            else
                print_success "Process on port $port killed"
                return 0
            fi
        else
            print_info "Skipping port $port"
            return 1
        fi
    fi
}

# Check and free multiple ports
check_and_free_ports() {
    local force=${1:-false}
    shift
    local ports=("$@")
    local conflicts=()

    print_info "Checking ports: ${ports[*]}"

    # First, identify all conflicts
    for port in "${ports[@]}"; do
        if is_port_in_use "$port"; then
            conflicts+=("$port")
        fi
    done

    if [ ${#conflicts[@]} -eq 0 ]; then
        print_success "All required ports are available"
        return 0
    fi

    # Display all conflicts
    echo ""
    print_warning "Port conflicts detected:"
    for port in "${conflicts[@]}"; do
        local pid=$(get_port_pid "$port")
        local process=$(get_port_process "$port")
        echo "  Port $port: $process (PID: $pid)"
    done
    echo ""

    # Ask to kill all at once if not forced
    if [ "$force" != "true" ]; then
        read -p "Kill all conflicting processes? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Cannot proceed with port conflicts. Exiting."
            return 1
        fi
        force="true"
    fi

    # Kill all conflicting processes
    local failed=0
    for port in "${conflicts[@]}"; do
        if ! kill_port_process "$port" "$force"; then
            failed=1
        fi
    done

    if [ $failed -eq 1 ]; then
        print_error "Some ports could not be freed"
        return 1
    fi

    print_success "All ports freed successfully"
    return 0
}

# Setup Python virtual environment
setup_python_venv() {
    print_info "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt
    fi
    
    print_success "Python dependencies installed"
}

# Setup Node.js dependencies
setup_node_deps() {
    print_info "Setting up Node.js dependencies..."
    
    if [ -d "frontend" ]; then
        cd frontend
        if [ ! -d "node_modules" ]; then
            npm install
            print_success "Frontend dependencies installed"
        else
            print_info "Frontend dependencies already installed"
        fi
        cd ..
    fi
}

# =============================================================================
# Run Functions
# =============================================================================

run_docker_compose() {
    print_header "Running with Docker Compose"

    if ! check_docker; then
        exit 1
    fi

    # Check and free required ports
    local ports=(8000 8501 8502 8503)

    # Add additional ports based on profile
    local profile="${1:-}"
    if [ "$profile" = "with-monitoring" ]; then
        ports+=(9090 3001)  # Prometheus, Grafana
    elif [ "$profile" = "with-database" ]; then
        ports+=(5432)  # PostgreSQL
    elif [ "$profile" = "with-nginx" ]; then
        ports+=(80 443)  # Nginx
    fi

    # Check for --force flag
    local force="false"
    if [ "$2" = "--force" ] || [ "$2" = "-f" ]; then
        force="true"
    fi

    if ! check_and_free_ports "$force" "${ports[@]}"; then
        print_error "Port conflicts must be resolved before starting"
        return 1
    fi

    local compose_cmd="docker-compose"

    # Check if using docker compose (v2) or docker-compose (v1)
    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi

    if [ -n "$profile" ]; then
        print_info "Starting with profile: $profile"
        $compose_cmd --profile "$profile" up --build
    else
        print_info "Starting default services (backend + streamlit)"
        $compose_cmd up --build
    fi
}

run_docker_compose_detached() {
    print_header "Running with Docker Compose (Detached)"

    if ! check_docker; then
        exit 1
    fi

    # Check and free required ports
    local ports=(8000 8501 8502 8503)

    # Add additional ports based on profile
    local profile="${1:-}"
    if [ "$profile" = "with-monitoring" ]; then
        ports+=(9090 3001)  # Prometheus, Grafana
    elif [ "$profile" = "with-database" ]; then
        ports+=(5432)  # PostgreSQL
    elif [ "$profile" = "with-nginx" ]; then
        ports+=(80 443)  # Nginx
    fi

    # Check for --force flag
    local force="false"
    if [ "$2" = "--force" ] || [ "$2" = "-f" ]; then
        force="true"
    fi

    if ! check_and_free_ports "$force" "${ports[@]}"; then
        print_error "Port conflicts must be resolved before starting"
        return 1
    fi

    local compose_cmd="docker-compose"

    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi

    if [ -n "$profile" ]; then
        print_info "Starting with profile: $profile"
        $compose_cmd --profile "$profile" up --build -d
    else
        print_info "Starting default services (backend + streamlit)"
        $compose_cmd up --build -d
    fi

    print_success "Services started in background"
    print_info "View logs with: $compose_cmd logs -f"
    print_info "Stop services with: $compose_cmd down"
}

run_backend_local() {
    print_header "Running Backend Locally"

    if ! check_python; then
        exit 1
    fi

    # Check and free port 8000
    local port=8000
    if is_port_in_use "$port"; then
        print_warning "Port $port is already in use"
        if ! kill_port_process "$port" "false"; then
            print_error "Cannot start backend with port conflict"
            return 1
        fi
    fi

    setup_python_venv

    print_info "Starting FastAPI backend server on port $port..."
    cd backend

    # Set environment variables
    export PYTHONPATH="${SCRIPT_DIR}:${SCRIPT_DIR}/decentralized-ai-simulation:${PYTHONPATH}"
    export BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
    export BACKEND_PORT="${BACKEND_PORT:-$port}"
    export BACKEND_RELOAD="${BACKEND_RELOAD:-true}"

    python3 -m uvicorn main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --reload
}

run_frontend_local() {
    print_header "Running Frontend Locally"

    if ! check_node; then
        exit 1
    fi

    # Check and free port 3000 (default Vite port)
    local port=3000
    if is_port_in_use "$port"; then
        print_warning "Port $port is already in use"
        if ! kill_port_process "$port" "false"; then
            print_warning "Port conflict detected. Vite will try to use next available port."
        fi
    fi

    setup_node_deps

    print_info "Starting React frontend..."
    cd frontend
    npm run dev
}

run_streamlit_local() {
    print_header "Running Streamlit UI Locally"

    if ! check_python; then
        exit 1
    fi

    # Check and free Streamlit ports (8501, 8502, 8503)
    local ports=(8501 8502 8503)
    if ! check_and_free_ports "false" "${ports[@]}"; then
        print_error "Cannot start Streamlit with port conflicts"
        return 1
    fi

    setup_python_venv

    print_info "Starting Streamlit application..."

    # Set environment variables
    export PYTHONPATH="${SCRIPT_DIR}:${SCRIPT_DIR}/decentralized-ai-simulation:${PYTHONPATH}"
    export STREAMLIT_SERVER_PORT=8501
    export API_SERVER_PORT=8502
    export WEBSOCKET_SERVER_PORT=8503

    # Find streamlit app file
    if [ -f "streamlit/app.py" ]; then
        streamlit run streamlit/app.py --server.port 8501
    elif [ -f "decentralized-ai-simulation/src/ui/streamlit_app.py" ]; then
        streamlit run decentralized-ai-simulation/src/ui/streamlit_app.py --server.port 8501
    elif [ -f "decentralized-ai-simulation/streamlit_app.py" ]; then
        streamlit run decentralized-ai-simulation/streamlit_app.py --server.port 8501
    else
        print_error "Streamlit app file not found"
        exit 1
    fi
}

run_full_local() {
    print_header "Running Full Stack Locally"

    print_warning "This will start multiple processes. Press Ctrl+C to stop all."

    # Check and free all required ports at once
    local ports=(8000 8501 8502 8503)
    if [ -d "frontend" ]; then
        ports+=(3000)
    fi

    if ! check_and_free_ports "false" "${ports[@]}"; then
        print_error "Cannot start full stack with port conflicts"
        return 1
    fi

    # Start backend in background
    print_info "Starting backend..."
    (run_backend_local) &
    BACKEND_PID=$!

    sleep 5

    # Start frontend in background
    if [ -d "frontend" ]; then
        print_info "Starting frontend..."
        (run_frontend_local) &
        FRONTEND_PID=$!
    fi

    # Wait for processes
    wait
}

stop_docker_compose() {
    print_header "Stopping Docker Compose Services"

    local compose_cmd="docker-compose"
    if docker compose version >/dev/null 2>&1; then
        compose_cmd="docker compose"
    fi

    $compose_cmd down
    print_success "Services stopped"
}

check_ports_status() {
    print_header "Port Status Check"

    local ports=(8000 8501 8502 8503 3000 3001 5432 6379 9090 80 443)

    echo ""
    echo "Checking common ports used by the platform:"
    echo ""
    printf "%-10s %-15s %-10s %-20s\n" "PORT" "STATUS" "PID" "PROCESS"
    printf "%-10s %-15s %-10s %-20s\n" "----" "------" "---" "-------"

    for port in "${ports[@]}"; do
        if is_port_in_use "$port"; then
            local pid=$(get_port_pid "$port")
            local process=$(get_port_process "$port")
            printf "%-10s ${RED}%-15s${NC} %-10s %-20s\n" "$port" "IN USE" "$pid" "$process"
        else
            printf "%-10s ${GREEN}%-15s${NC} %-10s %-20s\n" "$port" "AVAILABLE" "-" "-"
        fi
    done

    echo ""
}

kill_all_platform_ports() {
    print_header "Kill All Platform Processes"

    local ports=(8000 8501 8502 8503 3000 3001)

    print_warning "This will kill all processes using platform ports"

    if ! check_and_free_ports "false" "${ports[@]}"; then
        print_info "Operation cancelled or some ports could not be freed"
        return 1
    fi

    print_success "All platform ports freed"
}

# =============================================================================
# Main Menu
# =============================================================================

show_menu() {
    clear
    print_header "Decentralized AI Simulation Platform"
    echo ""
    echo "Select run mode:"
    echo ""
    echo "  Docker Compose (Recommended):"
    echo "    1) Run with Docker Compose (default profile)"
    echo "    2) Run with Docker Compose (detached mode)"
    echo "    3) Run with monitoring (Prometheus + Grafana)"
    echo "    4) Run with database (PostgreSQL)"
    echo "    5) Run with all services (full stack)"
    echo "    6) Stop Docker Compose services"
    echo ""
    echo "  Local Development:"
    echo "    7) Run Backend only (FastAPI)"
    echo "    8) Run Frontend only (React)"
    echo "    9) Run Streamlit UI only"
    echo "   10) Run Full Stack locally"
    echo ""
    echo "  Port Management:"
    echo "   11) Check port status"
    echo "   12) Kill all platform processes"
    echo ""
    echo "  Setup:"
    echo "   13) Setup Python environment"
    echo "   14) Setup Node.js dependencies"
    echo ""
    echo "    0) Exit"
    echo ""
}

# =============================================================================
# Main Script
# =============================================================================

main() {
    while true; do
        show_menu
        read -p "Enter your choice: " choice

        case $choice in
            1) run_docker_compose ;;
            2) run_docker_compose_detached ;;
            3) run_docker_compose "with-monitoring" ;;
            4) run_docker_compose "with-database" ;;
            5) run_docker_compose "with-nginx" ;;
            6) stop_docker_compose ;;
            7) run_backend_local ;;
            8) run_frontend_local ;;
            9) run_streamlit_local ;;
            10) run_full_local ;;
            11) check_ports_status ;;
            12) kill_all_platform_ports ;;
            13) check_python && setup_python_venv ;;
            14) check_node && setup_node_deps ;;
            0)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                sleep 2
                ;;
        esac

        if [ $? -eq 0 ]; then
            echo ""
            read -p "Press Enter to continue..."
        fi
    done
}

# Run main menu if no arguments provided
if [ $# -eq 0 ]; then
    main
else
    # Allow direct command execution
    case "$1" in
        docker) run_docker_compose "${2:-}" "${3:-}" ;;
        docker-detached) run_docker_compose_detached "${2:-}" "${3:-}" ;;
        backend) run_backend_local ;;
        frontend) run_frontend_local ;;
        streamlit) run_streamlit_local ;;
        full) run_full_local ;;
        stop) stop_docker_compose ;;
        check-ports) check_ports_status ;;
        kill-ports) kill_all_platform_ports ;;
        setup-python) check_python && setup_python_venv ;;
        setup-node) check_node && setup_node_deps ;;
        help|--help|-h)
            echo "Decentralized AI Simulation Platform - Run Script"
            echo ""
            echo "Usage: $0 [COMMAND] [OPTIONS]"
            echo ""
            echo "Commands:"
            echo "  docker [PROFILE] [--force]    Run with Docker Compose"
            echo "  docker-detached [PROFILE]     Run with Docker Compose (detached)"
            echo "  backend                       Run Backend only (FastAPI)"
            echo "  frontend                      Run Frontend only (React)"
            echo "  streamlit                     Run Streamlit UI only"
            echo "  full                          Run Full Stack locally"
            echo "  stop                          Stop Docker Compose services"
            echo "  check-ports                   Check port status"
            echo "  kill-ports                    Kill all platform processes"
            echo "  setup-python                  Setup Python environment"
            echo "  setup-node                    Setup Node.js dependencies"
            echo ""
            echo "Profiles:"
            echo "  with-monitoring               Include Prometheus + Grafana"
            echo "  with-database                 Include PostgreSQL"
            echo "  with-nginx                    Include Nginx reverse proxy"
            echo ""
            echo "Options:"
            echo "  --force, -f                   Force kill processes without confirmation"
            echo ""
            echo "Examples:"
            echo "  $0                            # Interactive menu"
            echo "  $0 docker                     # Run with Docker Compose"
            echo "  $0 docker with-monitoring -f  # Run with monitoring, force kill conflicts"
            echo "  $0 streamlit                  # Run Streamlit only"
            echo "  $0 check-ports                # Check which ports are in use"
            echo "  $0 kill-ports                 # Kill all platform processes"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown command: $1"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
fi

