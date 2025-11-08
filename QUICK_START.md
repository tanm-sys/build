# Quick Start Guide - Decentralized AI Simulation Platform

## 🚀 Getting Started in 3 Steps

### Step 1: Check Port Status
```bash
cd build
./run.sh check-ports
```

This shows which ports are currently in use.

### Step 2: Kill Conflicting Processes (if needed)
```bash
./run.sh kill-ports
```

This will ask for confirmation before killing processes using platform ports.

### Step 3: Start the Platform
```bash
# Option A: Docker Compose (Recommended)
./run.sh docker

# Option B: Interactive Menu
./run.sh

# Option C: Specific Component
./run.sh streamlit
./run.sh backend
./run.sh frontend
```

## 🎯 Common Commands

### Check What's Running
```bash
./run.sh check-ports
```

### Kill All Platform Processes
```bash
./run.sh kill-ports
```

### Start with Docker (Recommended)
```bash
# Basic
./run.sh docker

# With monitoring
./run.sh docker with-monitoring

# Force kill conflicts without asking
./run.sh docker --force
```

### Start Individual Components
```bash
# Backend only (port 8000)
./run.sh backend

# Frontend only (port 3000)
./run.sh frontend

# Streamlit only (ports 8501, 8502, 8503)
./run.sh streamlit

# Everything locally
./run.sh full
```

### Stop Everything
```bash
# Stop Docker Compose
./run.sh stop

# Or kill all processes
./run.sh kill-ports
```

## 🔧 Troubleshooting

### "Address already in use" Error

**Solution 1: Automatic (Recommended)**
```bash
./run.sh streamlit
# Script will detect conflicts and ask to kill them
```

**Solution 2: Manual Check**
```bash
# 1. Check what's using the ports
./run.sh check-ports

# 2. Kill all platform processes
./run.sh kill-ports

# 3. Try again
./run.sh streamlit
```

**Solution 3: Force Mode**
```bash
# Automatically kill conflicts without asking
./run.sh docker --force
```

### Port Status Shows Conflicts

Example output:
```
PORT       STATUS          PID        PROCESS             
8000       IN USE          618616     python              
8501       IN USE          657934     streamlit           
8502       IN USE          659458     streamlit           
```

**Fix:**
```bash
./run.sh kill-ports
```

### Docker Won't Start

```bash
# Stop all containers
./run.sh stop

# Check for orphaned containers
docker ps -a

# Remove if needed
docker rm -f <container_id>

# Try again with force
./run.sh docker --force
```

## 📊 Port Reference

| Port | Service | Required For |
|------|---------|--------------|
| 8000 | Backend | API server |
| 8501 | Streamlit | Main UI |
| 8502 | Streamlit | 3D API |
| 8503 | Streamlit | WebSocket |
| 3000 | Frontend | React UI |

## 🎨 Interactive Menu

Just run without arguments:
```bash
./run.sh
```

You'll see:
```
========================================
Decentralized AI Simulation Platform
========================================

Select run mode:

  Docker Compose (Recommended):
    1) Run with Docker Compose (default profile)
    2) Run with Docker Compose (detached mode)
    3) Run with monitoring (Prometheus + Grafana)
    4) Run with database (PostgreSQL)
    5) Run with all services (full stack)
    6) Stop Docker Compose services

  Local Development:
    7) Run Backend only (FastAPI)
    8) Run Frontend only (React)
    9) Run Streamlit UI only
   10) Run Full Stack locally

  Port Management:
   11) Check port status
   12) Kill all platform processes

  Setup:
   13) Setup Python environment
   14) Setup Node.js dependencies

    0) Exit
```

## 🌐 Access URLs

Once running, access services at:

- **Streamlit UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **3D API**: http://localhost:8502
- **Frontend**: http://localhost:3000

## 💡 Pro Tips

1. **Always check ports first**
   ```bash
   ./run.sh check-ports
   ```

2. **Use force mode in scripts**
   ```bash
   ./run.sh docker --force
   ```

3. **Run in background**
   ```bash
   ./run.sh docker-detached
   ```

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

5. **Clean restart**
   ```bash
   ./run.sh stop
   ./run.sh kill-ports
   ./run.sh docker --force
   ```

## 📚 More Information

- **Full Guide**: See `RUN_SCRIPT_GUIDE.md`
- **Port Handling**: See `PORT_CONFLICT_HANDLING.md`
- **Help**: Run `./run.sh help`

## 🆘 Need Help?

```bash
# Show all commands
./run.sh help

# Check port status
./run.sh check-ports

# View this guide
cat QUICK_START.md
```

## ✅ Verification

After starting, verify everything is working:

```bash
# Check ports are in use
./run.sh check-ports

# Should show:
# 8000  IN USE  <pid>  python
# 8501  IN USE  <pid>  streamlit
# 8502  IN USE  <pid>  streamlit

# Test backend
curl http://localhost:8000/health

# Open Streamlit in browser
# Visit: http://localhost:8501
```

## 🎉 You're Ready!

The platform is now running. Visit http://localhost:8501 to see the Streamlit UI!

