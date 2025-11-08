# Port Conflict Handling - Implementation Summary

## Problem Statement

The Streamlit application (and other services) were failing to start with:
```
ERROR: [Errno 98] Address already in use
```

This occurred when ports 8501, 8502, 8503, 8000, or 3000 were already occupied by other processes.

## Solution Implemented

The `run.sh` script has been enhanced with comprehensive port conflict detection and automatic resolution.

## New Features Added

### 1. Port Detection Functions

#### `is_port_in_use(port)`
- Checks if a port is currently in use
- Uses `lsof`, `netstat`, or `ss` (in order of preference)
- Returns 0 if port is in use, 1 if available

#### `get_port_pid(port)`
- Returns the PID of the process using a port
- Works with multiple tools for compatibility

#### `get_port_process(port)`
- Returns the name of the process using a port
- Helps identify what needs to be killed

### 2. Port Management Functions

#### `kill_port_process(port, force)`
- Kills the process using a specific port
- If `force=false`: Asks for user confirmation
- If `force=true`: Kills immediately without asking
- Displays process name and PID before killing
- Verifies the port is freed after killing

#### `check_and_free_ports(force, ports...)`
- Checks multiple ports at once
- Displays all conflicts in a formatted table
- Asks once to kill all (if not forced)
- Kills all conflicting processes
- Returns success/failure status

### 3. Port Status Monitoring

#### `check_ports_status()`
- Displays status of all platform ports
- Shows which ports are in use
- Shows PID and process name for occupied ports
- Color-coded output (red=in use, green=available)

#### `kill_all_platform_ports()`
- Kills all processes using platform ports
- Covers ports: 8000, 8501, 8502, 8503, 3000, 3001
- Asks for confirmation before killing

### 4. Integration with Run Functions

All run functions now check ports before starting:

#### `run_docker_compose()`
- Checks ports: 8000, 8501, 8502, 8503
- Adds profile-specific ports (9090, 3001, 5432, 80, 443)
- Supports `--force` flag

#### `run_docker_compose_detached()`
- Same port checking as `run_docker_compose()`
- Supports `--force` flag

#### `run_backend_local()`
- Checks port 8000
- Asks for confirmation before killing

#### `run_frontend_local()`
- Checks port 3000
- Warns if port is in use (Vite can auto-select next port)

#### `run_streamlit_local()`
- Checks ports 8501, 8502, 8503
- Must free all three ports before starting
- Sets explicit port environment variables

#### `run_full_local()`
- Checks all required ports at once
- Prevents partial startup with conflicts

### 5. Enhanced Menu System

New menu options:
- **Option 11**: Check port status
- **Option 12**: Kill all platform processes
- **Option 13**: Setup Python environment (moved from 11)
- **Option 14**: Setup Node.js dependencies (moved from 12)

### 6. Enhanced CLI

New commands:
```bash
./run.sh check-ports          # Check port status
./run.sh kill-ports            # Kill all platform processes
./run.sh docker --force        # Force kill conflicts
./run.sh help                  # Show detailed help
```

## Usage Examples

### Check Which Ports Are In Use
```bash
./run.sh check-ports
```

Output:
```
PORT       STATUS          PID        PROCESS             
----       ------          ---        -------             
8000       IN USE          618616     python              
8501       IN USE          657934     streamlit           
8502       IN USE          659458     streamlit           
8503       AVAILABLE       -          -                   
3000       IN USE          630258     node                
```

### Kill All Platform Processes
```bash
./run.sh kill-ports
```

Output:
```
⚠ Port conflicts detected:
  Port 8000: python (PID: 618616)
  Port 8501: streamlit (PID: 657934)
  Port 8502: streamlit (PID: 659458)
  Port 3000: node (PID: 630258)

Kill all conflicting processes? (y/N): y
✓ Process on port 8000 killed
✓ Process on port 8501 killed
✓ Process on port 8502 killed
✓ Process on port 3000 killed
✓ All ports freed successfully
```

### Start Streamlit with Automatic Conflict Resolution
```bash
./run.sh streamlit
```

Output:
```
========================================
Running Streamlit UI Locally
========================================
ℹ Checking ports: 8501 8502 8503

⚠ Port conflicts detected:
  Port 8501: streamlit (PID: 657934)
  Port 8502: streamlit (PID: 659458)

Kill all conflicting processes? (y/N): y
✓ Process on port 8501 killed
✓ Process on port 8502 killed
✓ All ports freed successfully
ℹ Starting Streamlit application...
```

### Start Docker Compose with Force Mode
```bash
./run.sh docker --force
```

This will automatically kill all conflicting processes without asking for confirmation.

## Technical Details

### Port Detection Priority
1. **lsof** (most reliable, works on most systems)
2. **netstat** (fallback, widely available)
3. **ss** (modern alternative to netstat)

### Process Killing Strategy
1. Identify all conflicts first
2. Display all conflicts to user
3. Ask once for confirmation (unless forced)
4. Kill all processes with `kill -9`
5. Verify each port is freed
6. Report success/failure

### Error Handling
- Graceful fallback if port detection tools are unavailable
- Clear error messages if ports cannot be freed
- Prevents service startup if conflicts remain
- Returns proper exit codes for scripting

## Benefits

✅ **No More Manual Port Cleanup** - Automatic detection and resolution  
✅ **Clear Visibility** - See exactly what's using each port  
✅ **Safe Operation** - Asks for confirmation before killing  
✅ **Batch Operations** - Kill all conflicts at once  
✅ **Force Mode** - Automation-friendly with `--force` flag  
✅ **Comprehensive Coverage** - Works for Docker and local modes  
✅ **User-Friendly** - Color-coded output and clear messages  

## Compatibility

- ✅ Linux (tested)
- ✅ macOS (should work with lsof)
- ⚠️ Windows (requires WSL or Git Bash)

## Future Enhancements

Potential improvements:
- [ ] Automatic port selection if default is occupied
- [ ] Port conflict prevention (reserve ports)
- [ ] Integration with systemd for service management
- [ ] Windows native support (PowerShell version)
- [ ] Port usage history and analytics
- [ ] Graceful shutdown before killing (SIGTERM then SIGKILL)

## Files Modified

1. **build/run.sh** - Main run script with port handling
2. **build/RUN_SCRIPT_GUIDE.md** - Comprehensive usage guide
3. **build/PORT_CONFLICT_HANDLING.md** - This document

## Testing

The implementation has been tested with:
- ✅ Port detection (lsof)
- ✅ Process identification
- ✅ Port status display
- ✅ Multiple ports in use simultaneously
- ✅ Interactive menu
- ✅ Command-line interface

## Conclusion

The enhanced `run.sh` script now provides robust port conflict handling, making it much easier to run the Decentralized AI Simulation Platform without manual intervention for port conflicts.

The "Address already in use" error is now automatically detected and resolved, with clear user feedback throughout the process.

