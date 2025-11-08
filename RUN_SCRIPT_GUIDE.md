# Run Script Guide - Decentralized AI Simulation Platform

## Overview

The `run.sh` script provides a comprehensive way to run the Decentralized AI Simulation Platform with automatic port conflict detection and resolution.

## Key Features

✅ **Automatic Port Conflict Detection** - Detects processes using required ports  
✅ **Automatic Port Conflict Resolution** - Kills conflicting processes (with confirmation)  
✅ **Multiple Deployment Modes** - Docker Compose or local development  
✅ **Interactive Menu** - User-friendly menu interface  
✅ **Command-Line Interface** - Direct command execution  
✅ **Port Status Monitoring** - Check which ports are in use  

## Quick Start

### Interactive Mode (Recommended)
```bash
cd build
./run.sh
```

This will display an interactive menu with all available options.

### Direct Commands

#### Docker Compose (Recommended for Production)
```bash
# Default services (backend + streamlit)
./run.sh docker

# Run in background (detached mode)
./run.sh docker-detached

# With monitoring (Prometheus + Grafana)
./run.sh docker with-monitoring

# With database (PostgreSQL)
./run.sh docker with-database

# Force kill port conflicts without confirmation
./run.sh docker --force
./run.sh docker with-monitoring --force

# Stop all services
./run.sh stop
```

#### Local Development
```bash
# Run backend only (FastAPI on port 8000)
./run.sh backend

# Run frontend only (React/Vite on port 3000)
./run.sh frontend

# Run Streamlit UI only (ports 8501, 8502, 8503)
./run.sh streamlit

# Run full stack locally
./run.sh full
```

#### Port Management
```bash
# Check which ports are in use
./run.sh check-ports

# Kill all platform processes
./run.sh kill-ports
```

#### Setup
```bash
# Setup Python virtual environment
./run.sh setup-python

# Setup Node.js dependencies
./run.sh setup-node
```

## Port Configuration

The platform uses the following ports:

| Port | Service | Description |
|------|---------|-------------|
| 8000 | Backend | FastAPI server |
| 8501 | Streamlit | Streamlit UI |
| 8502 | Streamlit | 3D API endpoints |
| 8503 | Streamlit | WebSocket server |
| 3000 | Frontend | React/Vite dev server |
| 3001 | Grafana | Monitoring dashboard (optional) |
| 5432 | PostgreSQL | Database (optional) |
| 6379 | Redis | Cache (optional) |
| 9090 | Prometheus | Metrics collection (optional) |
| 80/443 | Nginx | Reverse proxy (optional) |

## Port Conflict Handling

### Automatic Detection
When you start any service, the script automatically:
1. Checks if required ports are in use
2. Identifies the process using each port
3. Displays the conflicting processes
4. Asks for confirmation to kill them

### Example Output
```
⚠ Port conflicts detected:
  Port 8000: python (PID: 12345)
  Port 8501: streamlit (PID: 67890)

Kill all conflicting processes? (y/N):
```

### Force Mode
Use `--force` or `-f` flag to automatically kill processes without confirmation:
```bash
./run.sh docker --force
./run.sh docker with-monitoring -f
```

## Troubleshooting

### Port Already in Use Error
If you see "ERROR: [Errno 98] Address already in use":

1. **Check port status:**
   ```bash
   ./run.sh check-ports
   ```

2. **Kill conflicting processes:**
   ```bash
   ./run.sh kill-ports
   ```

3. **Or manually kill a specific process:**
   ```bash
   # Find the PID
   lsof -i :8501
   
   # Kill the process
   kill -9 <PID>
   ```

### Docker Compose Issues
If Docker Compose fails to start:

1. **Stop all services:**
   ```bash
   ./run.sh stop
   ```

2. **Check for orphaned containers:**
   ```bash
   docker ps -a
   docker rm -f <container_id>
   ```

3. **Try again with force:**
   ```bash
   ./run.sh docker --force
   ```

### Python Virtual Environment Issues
If Python dependencies are missing:

1. **Recreate virtual environment:**
   ```bash
   rm -rf venv
   ./run.sh setup-python
   ```

2. **Manually activate and install:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

### Node.js Dependencies Issues
If frontend fails to start:

1. **Reinstall dependencies:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   cd ..
   ```

2. **Or use the script:**
   ```bash
   ./run.sh setup-node
   ```

## Environment Variables

You can customize behavior with environment variables:

```bash
# Backend configuration
export BACKEND_HOST=0.0.0.0
export BACKEND_PORT=8000
export BACKEND_RELOAD=true

# Streamlit configuration
export STREAMLIT_SERVER_PORT=8501
export API_SERVER_PORT=8502
export WEBSOCKET_SERVER_PORT=8503

# Simulation configuration
export SIMULATION_NUM_AGENTS=100
export DATABASE_PATH=/data/simulation.db
```

## Advanced Usage

### Running Specific Docker Compose Profiles
```bash
# With monitoring
./run.sh docker with-monitoring

# With database
./run.sh docker with-database

# With Nginx reverse proxy
./run.sh docker with-nginx
```

### Combining Multiple Profiles
Edit `docker-compose.yml` to combine profiles, or use:
```bash
docker-compose --profile with-monitoring --profile with-database up
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f streamlit
```

### Accessing Services

Once running, access the services at:

- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501
- **3D API**: http://localhost:8502
- **Frontend**: http://localhost:3000
- **Grafana** (if enabled): http://localhost:3001
- **Prometheus** (if enabled): http://localhost:9090

## Getting Help

```bash
# Show help
./run.sh help
./run.sh --help
./run.sh -h
```

## Best Practices

1. **Use Docker Compose for production** - More reliable and easier to manage
2. **Use local development for debugging** - Faster iteration and easier debugging
3. **Check ports before starting** - Avoid conflicts with `./run.sh check-ports`
4. **Use force mode in CI/CD** - Automate deployments with `--force` flag
5. **Monitor logs** - Use `docker-compose logs -f` to watch for issues

## Common Workflows

### Development Workflow
```bash
# 1. Check port status
./run.sh check-ports

# 2. Kill any conflicts
./run.sh kill-ports

# 3. Run backend for API development
./run.sh backend

# Or run frontend for UI development
./run.sh frontend

# Or run Streamlit for visualization
./run.sh streamlit
```

### Production Deployment
```bash
# 1. Stop any running services
./run.sh stop

# 2. Start with monitoring
./run.sh docker with-monitoring --force

# 3. Check logs
docker-compose logs -f
```

### Testing Workflow
```bash
# 1. Clean environment
./run.sh stop
./run.sh kill-ports

# 2. Start fresh
./run.sh docker --force

# 3. Run tests
docker-compose exec backend pytest
```

## Support

For issues or questions:
1. Check this guide
2. Run `./run.sh check-ports` to diagnose port issues
3. Check Docker logs: `docker-compose logs -f`
4. Review the main documentation in the `build/` directory

