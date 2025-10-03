# Troubleshooting Guide (October 2025)

## Overview

This comprehensive troubleshooting guide provides solutions for common issues encountered when working with the Decentralized AI Simulation platform. The guide covers installation problems, configuration issues, performance bottlenecks, database connectivity problems, agent behavior issues, deployment challenges, and monitoring/alerting problems.

## Quick Reference

### Emergency Commands

```bash
# Stop all running processes
pkill -f "python.*simulation" || true
pkill -f "streamlit" || true

# Clear all logs and restart
./scripts/maintenance/cleanup.sh --verbose

# Quick health check
python -c "from monitoring import get_monitoring; print(get_monitoring().get_system_health())"
```

### Log Locations

- **Application Logs**: `logs/simulation.log`
- **Setup Logs**: `logs/setup.log`
- **Test Logs**: `logs/test_output.log`
- **System Health**: Real-time via monitoring system

## Installation and Setup Issues

### Python Environment Problems

#### Issue: Python Version Compatibility
**Error**: `Python 3.8 or higher is required`

**Symptoms**:
- Import errors during setup
- Module not found errors
- Version conflicts

**Solutions**:

1. **Check Python version**:
```bash
python --version
python3 --version
```

2. **Update Python** (Ubuntu/Debian):
```bash
# Add deadsnakes PPA for latest Python
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

3. **Update Python** (macOS):
```bash
# Using Homebrew
brew install python@3.11

# Add to PATH
echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

4. **Update Python** (Windows):
```cmd
# Download from Microsoft Store or python.org
# Ensure Python 3.11+ is installed and added to PATH
python --version
```

#### Issue: Virtual Environment Creation Fails
**Error**: `Module 'virtualenv' not found` or permission errors

**Solutions**:

1. **Install virtualenv**:
```bash
pip install virtualenv
python -m venv .venv
```

2. **Fix permission issues**:
```bash
# Linux/macOS
sudo chown -R $USER:$USER .venv/
chmod +x .venv/bin/activate

# Windows
# Run command prompt as Administrator
```

3. **Alternative environment creation**:
```bash
# Using virtualenv directly
virtualenv .venv --python=python3.11
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### Dependency Installation Issues

#### Issue: Package Installation Fails
**Error**: `ERROR: Failed building wheel for <package>`

**Symptoms**:
- Build errors during pip install
- Missing system dependencies
- Compiler errors

**Solutions**:

1. **Install system dependencies** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    python3.11-dev \
    libsqlite3-dev \
    libssl-dev \
    libffi-dev \
    cargo \
    pkg-config

# For Ray-specific dependencies
sudo apt install -y \
    libgomp1 \
    libopenmpi-dev \
    openmpi-bin
```

2. **Install system dependencies** (macOS):
```bash
# Using Homebrew
brew install openssl sqlite

# For Ray dependencies
brew install openmpi

# Install Rust (required for some packages)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

3. **Install system dependencies** (Windows):
```cmd
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install MPI for Ray (optional)
# Download from: https://www.microsoft.com/en-us/download/details.aspx?id=57467
```

4. **Alternative installation method**:
```bash
# Use conda instead of pip for complex dependencies
conda create -n simulation python=3.11
conda activate simulation
pip install -r requirements.txt
```

#### Issue: Ray Installation Problems
**Error**: `Ray installation failed` or `ImportError: No module named ray`

**Solutions**:

1. **Install Ray with minimal dependencies**:
```bash
pip uninstall ray -y
pip install ray[default]==2.45.0 --no-cache-dir

# Alternative: Install without full dependencies
pip install ray[tune]==2.45.0
```

2. **Fix Ray dashboard issues**:
```bash
# Set environment variables before Ray initialization
export RAY_ENABLE_WINDOWS_OR_OSX_CLUSTER=1  # macOS
export RAY_ADDRESS=auto

# Test Ray installation
python -c "import ray; ray.init(); print('Ray OK'); ray.shutdown()"
```

3. **Ray cluster troubleshooting**:
```bash
# Check Ray processes
ps aux | grep ray

# Check Ray logs
ray logs cluster

# Reset Ray cluster
ray stop
ray start --head --num-cpus=4
```

### Automated Setup Script Issues

#### Issue: Setup Script Fails
**Error**: `./setup.sh: Permission denied` or `Setup failed`

**Solutions**:

1. **Fix script permissions**:
```bash
chmod +x scripts/setup/setup.sh
chmod +x scripts/setup/setup.bat
chmod +x scripts/setup/setup.ps1
```

2. **Run setup with verbose output**:
```bash
# Linux/macOS
./scripts/setup/setup.sh --verbose --dev

# Windows PowerShell
.\scripts\setup\setup.ps1 -Verbose -DevMode
```

3. **Manual setup if automated fails**:
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r config/requirements.txt

# Initialize configuration
python -c "from config_loader import get_config; print('Config OK')"

# Test database
python -c "from database import DatabaseLedger; db = DatabaseLedger(); print('DB OK')"
```

4. **Debug setup issues**:
```bash
# Check setup logs
tail -f logs/setup.log

# Test individual components
python -c "import mesa; print('Mesa OK')"
python -c "import ray; print('Ray OK')"
python -c "import streamlit; print('Streamlit OK')"
```

## Configuration Problems

### Configuration File Issues

#### Issue: Configuration File Not Found
**Error**: `Config file not found` or `yaml.YAMLError`

**Solutions**:

1. **Check configuration file exists**:
```bash
ls -la config/config.yaml
ls -la config/.env.example
```

2. **Create default configuration**:
```bash
# Copy from example
cp config/.env.example .env

# Generate default config
python -c "
from config_loader import ConfigLoader
config = ConfigLoader()
config._create_default_config()
print('Default config created')
"
```

3. **Validate YAML syntax**:
```bash
# Install YAML validator
pip install yamllint

# Validate configuration
yamllint config/config.yaml

# Alternative: Python validation
python -c "
import yaml
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('YAML syntax OK')
"
```

4. **Fix common YAML issues**:
```yaml
# ❌ Wrong indentation (spaces instead of tabs)
# ✅ Correct indentation (2 spaces)
database:
  path: ledger.db
  connection_pool_size: 10

# ❌ Tab characters
# ✅ Space characters only
logging:
  level: INFO
  file: simulation.log
```

#### Issue: Environment Variable Override Issues
**Error**: Environment variables not taking effect

**Solutions**:

1. **Check environment variable format**:
```bash
# Correct format (no spaces around =)
export DATABASE_PATH=/custom/path/ledger.db
export LOGGING_LEVEL=DEBUG

# Verify variables are set
env | grep DATABASE
env | grep LOGGING
```

2. **Test configuration loading**:
```python
from config_loader import get_config, is_production, is_development

# Test configuration access
print(f"Database path: {get_config('database.path')}")
print(f"Environment: {'production' if is_production() else 'development'}")

# Test environment overrides
import os
os.environ['SIMULATION_DEFAULT_AGENTS'] = '200'
print(f"Agents: {get_config('simulation.default_agents')}")
```

3. **Fix environment variable precedence**:
```bash
# Set variables before running application
export SIMULATION_DEFAULT_AGENTS=200
export RAY_ENABLE=true
export LOGGING_LEVEL=DEBUG

# Run application with environment
env SIMULATION_DEFAULT_AGENTS=200 python decentralized_ai_simulation.py
```

### Database Configuration Issues

#### Issue: Database Connection Problems
**Error**: `sqlite3.OperationalError` or connection timeout

**Solutions**:

1. **Check database file permissions**:
```bash
# Check file exists and permissions
ls -la data/databases/ledger.db

# Fix permissions if needed
chmod 666 data/databases/ledger.db
chown $USER:$USER data/databases/ledger.db
```

2. **Test database connection**:
```python
from database import DatabaseLedger

# Test basic connection
try:
    db = DatabaseLedger()
    print("Database connection OK")
    db.close()
except Exception as e:
    print(f"Database error: {e}")
```

3. **Fix SQLite issues**:
```sql
-- Check database integrity
PRAGMA integrity_check;

-- Analyze database
PRAGMA analyze;

-- Check for locks
PRAGMA lock_status;
```

4. **Database migration issues**:
```bash
# Backup current database
cp data/databases/ledger.db data/databases/ledger.db.backup

# Run migration script
python scripts/migration/migrate_database.py
```

## Performance Issues

### High Memory Usage

#### Issue: Memory Usage Continuously Increasing
**Symptoms**: Memory usage grows over time, potential memory leaks

**Solutions**:

1. **Monitor memory usage**:
```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {memory_mb:.1f}MB")
```

2. **Enable memory profiling**:
```python
import tracemalloc

# Start tracing
tracemalloc.start()

# Run simulation
simulation.run(steps=100)

# Check top memory consumers
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

3. **Fix memory leaks**:
```python
import gc

# Force garbage collection
gc.collect()

# Check for uncollected objects
print(f"Objects: {len(gc.get_objects())}")

# Clear caches if needed
from utils.caching import clear_all_caches
clear_all_caches()
```

4. **Optimize agent memory usage**:
```python
# Reduce agent state storage
class MemoryOptimizedAgent(AnomalyAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self._recent_states = []  # Keep only recent states
        self._max_states = 10     # Limit state history

    def add_state(self, state):
        if len(self._recent_states) >= self._max_states:
            self._recent_states.pop(0)
        self._recent_states.append(state)
```

### Slow Performance

#### Issue: Simulation Running Slowly
**Symptoms**: Low steps per minute, high response times

**Solutions**:

1. **Enable Ray parallel processing**:
```yaml
# config/config.yaml
ray:
  enable: true
  num_cpus: 4
  object_store_memory: 2147483648  # 2GB

simulation:
  use_parallel_threshold: 50  # Use Ray for > 50 agents
```

2. **Optimize database queries**:
```python
# Use batch operations
from database import DatabaseLedger

db = DatabaseLedger()

# ❌ Slow: Individual inserts
for entry in entries:
    db.append_entry(entry)

# ✅ Fast: Batch inserts
db.batch_insert(entries)
```

3. **Enable caching**:
```yaml
# config/config.yaml
performance:
  enable_caching: true
  cache_size_mb: 500
  cache_ttl: 300
```

4. **Profile performance bottlenecks**:
```python
import cProfile
import pstats

# Profile simulation run
pr = cProfile.Profile()
pr.enable()

simulation.run(steps=100)

pr.disable()

# Show results
stats = pstats.Stats(pr)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### High CPU Usage

#### Issue: Excessive CPU Consumption
**Symptoms**: High CPU usage, system slowdown

**Solutions**:

1. **Monitor CPU usage**:
```bash
# Linux/macOS
top -p $(pgrep -f "python.*simulation")

# Python monitoring
import psutil
cpu_percent = psutil.cpu_percent(interval=1)
print(f"CPU Usage: {cpu_percent}%")
```

2. **Optimize agent processing**:
```python
# Reduce agent step frequency
class OptimizedSimulation(Simulation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_delay = 0.1  # Add delay between steps

    def step(self):
        # Process agents in batches
        agents = list(self.schedule.agents)
        batch_size = 10

        for i in range(0, len(agents), batch_size):
            batch = agents[i:i + batch_size]
            # Process batch concurrently
            # ... batch processing logic
```

3. **Configure Ray CPU allocation**:
```yaml
ray:
  num_cpus: 2  # Limit CPU usage
  object_store_memory: 1073741824  # 1GB
```

## Database Connectivity Problems

### Connection Pool Issues

#### Issue: Connection Pool Exhaustion
**Error**: `sqlite3.OperationalError: database is locked`

**Solutions**:

1. **Check connection pool configuration**:
```yaml
database:
  connection_pool:
    min_size: 5
    max_size: 20
    max_overflow: 10
    pool_timeout: 30
```

2. **Monitor connection usage**:
```python
from database import DatabaseLedger

db = DatabaseLedger()
print(f"Active connections: {db.get_connection_count()}")
print(f"Pool status: {db.get_pool_status()}")
```

3. **Fix connection leaks**:
```python
# ❌ Wrong: Not closing connections
conn = db.get_connection()
results = conn.execute("SELECT * FROM ledger")

# ✅ Correct: Use context manager
with db.get_connection() as conn:
    results = conn.execute("SELECT * FROM ledger")
    # Connection automatically closed
```

4. **Optimize connection usage**:
```python
# Use connection pooling efficiently
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_connection():
    async with db_pool.acquire() as conn:
        yield conn

# Use in async functions
async def process_data():
    async with get_db_connection() as conn:
        await conn.execute("INSERT INTO ledger VALUES (?, ?, ?)", data)
```

### Database Corruption Issues

#### Issue: Database File Corruption
**Error**: `sqlite3.DatabaseError: database disk image is malformed`

**Solutions**:

1. **Check database integrity**:
```bash
# SQLite integrity check
sqlite3 data/databases/ledger.db "PRAGMA integrity_check;"

# Quick integrity check
python -c "
import sqlite3
conn = sqlite3.connect('data/databases/ledger.db')
conn.execute('PRAGMA integrity_check')
print('Database integrity OK')
conn.close()
"
```

2. **Recover from backup**:
```bash
# Stop application
pkill -f "python.*simulation"

# Restore from backup
cp data/databases/ledger.db.backup data/databases/ledger.db

# Verify restoration
python -c "
import sqlite3
conn = sqlite3.connect('data/databases/ledger.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM ledger')
count = cursor.fetchone()[0]
print(f'Restored {count} records')
conn.close()
"
```

3. **Repair corrupted database**:
```bash
# Use SQLite recovery tools
sqlite3 data/databases/ledger.db ".recover" > recovered_ledger.sql

# Rebuild database from SQL
sqlite3 new_ledger.db < recovered_ledger.sql
mv new_ledger.db data/databases/ledger.db
```

## Agent Behavior Issues

### Agent Logic Problems

#### Issue: Agents Not Detecting Anomalies
**Symptoms**: No anomalies detected, agents behaving unexpectedly

**Solutions**:

1. **Check agent configuration**:
```python
from agents import AnomalyAgent

# Test anomaly detection
agent = AnomalyAgent(1, model)
test_data = {
    'source_ip': '192.168.1.100',
    'bytes_transferred': 2000000,  # Large transfer
    'protocol': 'UNKNOWN'
}

score = agent.detect_anomaly(test_data)
print(f"Anomaly score: {score}")
```

2. **Verify agent initialization**:
```python
# Check agent model
print(f"Agent model type: {type(agent.model)}")
print(f"Model features: {agent.model.n_features_}")

# Test with sample data
sample_data = generate_sample_traffic()
predictions = agent.model.predict(sample_data)
print(f"Predictions: {predictions}")
```

3. **Debug agent step logic**:
```python
# Add debug logging to agent
class DebugAnomalyAgent(AnomalyAgent):
    def step(self):
        print(f"Agent {self.unique_id} stepping")
        print(f"Position: {self.pos}")
        print(f"Anomaly score: {getattr(self, 'anomaly_score', 0)}")

        super().step()
```

### Agent Communication Issues

#### Issue: Agents Not Sharing Signatures
**Symptoms**: Signatures not propagating, consensus not reached

**Solutions**:

1. **Check network communication**:
```python
# Test signature broadcasting
from agents import AnomalyAgent

agent = AnomalyAgent(1, model)
signature = agent.generate_signature(anomaly_data)

# Test broadcast
try:
    broadcast_result = agent.broadcast_signature(signature)
    print(f"Broadcast result: {broadcast_result}")
except Exception as e:
    print(f"Broadcast error: {e}")
```

2. **Verify neighbor detection**:
```python
# Check agent neighbors
neighbors = model.grid.get_neighbors(agent.pos, moore=True)
print(f"Neighbors found: {len(neighbors)}")

for neighbor in neighbors:
    print(f"Neighbor {neighbor.unique_id} at {neighbor.pos}")
```

3. **Debug consensus mechanism**:
```python
# Test consensus resolution
from simulation import Simulation

sim = Simulation(num_agents=10)
all_validations = []

for agent in sim.schedule.agents:
    validation = agent.validate_signature(signature)
    all_validations.append(validation)

consensus = sim.resolve_consensus(all_validations)
print(f"Consensus reached: {consensus}")
```

## Deployment and Scaling Problems

### Docker Deployment Issues

#### Issue: Docker Container Fails to Start
**Error**: Container exits immediately or fails health checks

**Solutions**:

1. **Check Docker installation**:
```bash
docker --version
docker-compose --version
```

2. **Debug container startup**:
```bash
# Build with no cache
docker build --no-cache -t simulation-app .

# Run with interactive terminal
docker run -it --rm simulation-app /bin/bash

# Check container logs
docker run --rm simulation-app python -c "print('Container OK')"
```

3. **Fix Dockerfile issues**:
```dockerfile
# Use exec form for proper signal handling
CMD ["python", "-m", "uvicorn", "src.ui.streamlit_app:app", "--host", "0.0.0.0", "--port", "8501"]

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1
```

4. **Environment variable issues**:
```bash
# Set environment variables in docker-compose.yml
environment:
  - ENVIRONMENT=production
  - DATABASE_PATH=/app/data/ledger.db
  - LOGGING_LEVEL=WARNING
```

### Kubernetes Deployment Issues

#### Issue: Pods Failing to Start
**Error**: CrashLoopBackOff, ImagePullBackOff

**Solutions**:

1. **Check pod status**:
```bash
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

2. **Fix resource limits**:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

3. **Check image availability**:
```bash
# Pull image manually
docker pull your-registry/simulation-app:2.45.0

# Check image contents
docker run --rm your-registry/simulation-app:2.45.0 python --version
```

4. **Fix security context**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
  readOnlyRootFilesystem: true
```

### Scaling Issues

#### Issue: Performance Degradation Under Load
**Symptoms**: Response time increases, throughput decreases

**Solutions**:

1. **Monitor scaling metrics**:
```bash
# Check HPA status
kubectl get hpa

# Monitor resource usage
kubectl top pods
kubectl top nodes
```

2. **Optimize horizontal scaling**:
```yaml
# Adjust HPA thresholds
spec:
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Lower threshold
```

3. **Implement vertical scaling**:
```yaml
# Increase resource limits
resources:
  limits:
    memory: "4Gi"  # Increase memory
    cpu: "2000m"  # Increase CPU
```

4. **Database scaling optimization**:
```yaml
# Use read replicas for read-heavy workloads
database:
  read_replicas:
    enabled: true
    count: 2
```

## Monitoring and Alerting Issues

### Health Check Failures

#### Issue: Health Checks Failing
**Error**: Health check endpoints returning non-200 status

**Solutions**:

1. **Test health check endpoints**:
```bash
# Test Streamlit health
curl http://localhost:8501/health

# Test custom health checks
python -c "
from monitoring import get_monitoring
health = get_monitoring().get_system_health()
print(f'Health status: {health.status}')
"
```

2. **Debug health check logic**:
```python
# Check individual health checks
from monitoring import get_monitoring

monitoring = get_monitoring()

# Test database health
db_health = monitoring.check_database_health()
print(f"Database health: {db_health}")

# Test Ray health
ray_health = monitoring.check_ray_health()
print(f"Ray health: {ray_health}")
```

3. **Fix common health check issues**:
```python
# Increase health check timeout
monitoring:
  health_check_interval: 60  # Increase interval
  health_check_timeout: 30    # Increase timeout
```

### Alert Configuration Issues

#### Issue: Alerts Not Firing
**Symptoms**: No alerts received, monitoring data missing

**Solutions**:

1. **Check alert configuration**:
```yaml
monitoring:
  alerting:
    enable: true
    slack_webhook: "${SLACK_WEBHOOK_URL}"
    pagerduty_key: "${PAGERDUTY_ROUTING_KEY}"
```

2. **Test alert functionality**:
```python
from monitoring import get_monitoring

# Trigger test alert
monitoring.trigger_alert(
    'test_alert',
    'Testing alert functionality',
    'info'
)
```

3. **Verify external integrations**:
```bash
# Test Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert"}' \
  $SLACK_WEBHOOK_URL

# Test PagerDuty integration
curl -X POST $PAGERDUTY_EVENTS_API \
  -H 'Content-Type: application/json' \
  -d '{"routing_key": "$PAGERDUTY_KEY", "event_action": "trigger"}'
```

### Metrics Collection Issues

#### Issue: Metrics Not Being Collected
**Symptoms**: Empty dashboards, missing performance data

**Solutions**:

1. **Check Prometheus configuration**:
```bash
# Verify Prometheus is running
curl http://localhost:9090/-/healthy

# Check metrics endpoint
curl http://localhost:8501/metrics
```

2. **Debug metrics collection**:
```python
from monitoring import get_monitoring

# Check available metrics
metrics = get_monitoring().get_all_metrics()
print(f"Available metrics: {list(metrics.keys())}")

# Test metric recording
get_monitoring().record_metric('test_metric', 42.0, {'test': 'value'})
```

3. **Fix Grafana data source**:
```json
{
  "name": "Simulation Metrics",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "access": "proxy",
  "isDefault": true
}
```

## Common Error Messages and Solutions

### Import Errors

#### `ModuleNotFoundError: No module named 'mesa'`

**Solution**:
```bash
# Install missing dependency
pip install mesa==3.3.0

# Or reinstall all dependencies
pip install -r config/requirements.txt --force-reinstall
```

#### `ImportError: libgomp.so.1: cannot open shared object file`

**Solution**:
```bash
# Install OpenMP library
sudo apt install libgomp1

# For Ray-specific issues
sudo apt install libopenmpi-dev openmpi-bin
```

### Runtime Errors

#### `RuntimeError: Ray cluster is not initialized`

**Solution**:
```python
import ray

# Initialize Ray properly
ray.init(num_cpus=4, object_store_memory=2*1024*1024*1024)

# Or use auto-initialization
ray.init(address='auto')
```

#### `sqlite3.OperationalError: database is locked`

**Solution**:
```python
# Check for connection leaks
from database import DatabaseLedger

db = DatabaseLedger()

# Close connections properly
db.close()

# Or use connection pooling
with db.get_connection() as conn:
    # Use connection
    pass  # Automatically closed
```

### Configuration Errors

#### `yaml.YAMLError: ScannerError`

**Solution**:
```bash
# Validate YAML syntax
python -c "
import yaml
try:
    with open('config/config.yaml', 'r') as f:
        yaml.safe_load(f)
    print('YAML syntax OK')
except yaml.YAMLError as e:
    print(f'YAML error: {e}')
"
```

#### `KeyError: 'database'`

**Solution**:
```python
# Check configuration structure
from config_loader import get_config

try:
    db_path = get_config('database.path')
except KeyError:
    print("Configuration key missing - using defaults")
    db_path = "ledger.db"
```

## Diagnostic Commands

### System Diagnostics

```bash
# Comprehensive system check
python -c "
import sys
import psutil
import os

print(f'Python version: {sys.version}')
print(f'Platform: {sys.platform}')
print(f'CPU count: {os.cpu_count()}')
print(f'Memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}GB')

# Check disk space
disk = psutil.disk_usage('/')
print(f'Disk space: {disk.free / 1024 / 1024 / 1024:.1f}GB free')
"
```

### Application Diagnostics

```bash
# Full application health check
python -c "
from monitoring import get_monitoring
from database import DatabaseLedger
from config_loader import get_config
import ray

# Test configuration
print('✓ Configuration loaded')

# Test database
try:
    db = DatabaseLedger()
    db.close()
    print('✓ Database connection OK')
except Exception as e:
    print(f'✗ Database error: {e}')

# Test Ray
try:
    if not ray.is_initialized():
        ray.init(num_cpus=2, object_store_memory=1*1024*1024*1024)
    ray.shutdown()
    print('✓ Ray initialization OK')
except Exception as e:
    print(f'✗ Ray error: {e}')

# Test monitoring
try:
    health = get_monitoring().get_system_health()
    print(f'✓ System health: {health.status}')
except Exception as e:
    print(f'✗ Monitoring error: {e}')
"
```

### Performance Diagnostics

```bash
# Performance profiling script
python -c "
import cProfile
import pstats
import time
from simulation import Simulation

# Profile simulation run
pr = cProfile.Profile()
pr.enable()

# Run simulation
sim = Simulation(num_agents=50)
sim.run(steps=20)

pr.disable()

# Save results
stats = pstats.Stats(pr)
stats.sort_stats('cumulative')
stats.dump_stats('performance.prof')

print('Performance profile saved to performance.prof')
"
```

## Getting Help

### Support Request Template

When requesting support, please include:

1. **Environment Information**:
   - Operating system and version
   - Python version
   - Key dependency versions (Mesa, Ray, Streamlit)

2. **Error Details**:
   - Complete error message
   - Stack trace (if available)
   - Steps to reproduce

3. **Configuration**:
   - Relevant configuration file sections
   - Environment variables set
   - Recent changes

4. **Logs**:
   - Application logs (`logs/simulation.log`)
   - Setup logs (`logs/setup.log`)
   - System logs (if relevant)

5. **System Resources**:
   - Available memory and CPU
   - Disk space
   - Network connectivity

### Community Resources

- **Main Documentation**: [README.md](README.md) - Installation, usage, and general guidance
- **Best Practices**: [Best Practices Guide](BEST_PRACTICES.md) - Development and deployment standards
- **Performance**: [Performance Optimization Guide](PERFORMANCE_OPTIMIZATION.md) - Detailed performance tuning
- **Architecture**: [design.md](design.md) - Technical architecture and design decisions
- **API Reference**: [API Documentation Index](API_DOCUMENTATION_INDEX.md) - Complete API documentation
- **Migration**: [Migration Guide](MIGRATION_GUIDE.md) - Version upgrade procedures

### Reporting Issues

For bug reports and feature requests:

1. Check existing issues in the project repository
2. Create a new issue with detailed reproduction steps
3. Include environment information and error logs
4. Provide minimal code example if applicable

## Related Documentation and Cross-References

### 📚 Complete Documentation Suite

| Documentation | Purpose | Key Sections |
|---------------|---------|--------------|
| **[README.md](README.md)** | **Main Guide** | Installation, usage, FAQ, support |
| **[TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)** | **Problem Resolution** | Installation issues, configuration problems, performance troubleshooting |
| **[BEST_PRACTICES.md](BEST_PRACTICES.md)** | **Development Standards** | Code quality, configuration management, deployment best practices |
| **[PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)** | **Performance Tuning** | Database optimization, Ray configuration, monitoring setup |
| **[design.md](design.md)** | **Technical Architecture** | System design, component interactions, integration patterns |
| **[API Documentation Index](API_DOCUMENTATION_INDEX.md)** | **API Reference** | Complete API documentation for all components |

### 🔗 Quick Reference Links

#### **Troubleshooting by Category**
- **Installation Issues** → [Installation and Setup Issues](#installation-and-setup-issues)
- **Configuration Problems** → [Configuration Problems](#configuration-problems)
- **Performance Issues** → [Performance Issues](#performance-issues)
- **Database Issues** → [Database Connectivity Problems](#database-connectivity-problems)
- **Agent Behavior** → [Agent Behavior Issues](#agent-behavior-issues)
- **Deployment Issues** → [Deployment and Scaling Problems](#deployment-and-scaling-problems)
- **Monitoring Issues** → [Monitoring and Alerting Issues](#monitoring-and-alerting-issues)

#### **Technology-Specific Troubleshooting**
- **Mesa Issues** → [PERFORMANCE_OPTIMIZATION.md#mesa-330-agent-based-modeling](PERFORMANCE_OPTIMIZATION.md#mesa-330-agent-based-modeling)
- **Ray Issues** → [PERFORMANCE_OPTIMIZATION.md#ray-2450-distributed-computing](PERFORMANCE_OPTIMIZATION.md#ray-2450-distributed-computing)
- **Streamlit Issues** → [PERFORMANCE_OPTIMIZATION.md#streamlit-1390-dashboard](PERFORMANCE_OPTIMIZATION.md#streamlit-1390-dashboard)
- **Database Issues** → [API_DATABASE.md](API_DATABASE.md)

#### **Best Practices by Topic**
- **Code Quality** → [BEST_PRACTICES.md#code-quality-standards](BEST_PRACTICES.md#code-quality-standards)
- **Configuration Management** → [BEST_PRACTICES.md#configuration-management-best-practices](BEST_PRACTICES.md#configuration-management-best-practices)
- **Security** → [BEST_PRACTICES.md#security-best-practices](BEST_PRACTICES.md#security-best-practices)
- **Performance** → [BEST_PRACTICES.md#performance-best-practices](BEST_PRACTICES.md#performance-best-practices)

### 🔍 Diagnostic and Monitoring Tools

#### **Built-in Diagnostic Commands**
- **System Health Check** → [Diagnostic Commands](#diagnostic-commands)
- **Performance Profiling** → [Performance Diagnostics](#performance-diagnostics)
- **Application Diagnostics** → [Application Diagnostics](#application-diagnostics)

#### **External Monitoring Integration**
- **Prometheus Metrics** → [Monitoring and Alerting Issues](#monitoring-and-alerting-issues)
- **Grafana Dashboards** → [PERFORMANCE_OPTIMIZATION.md#monitoring-and-profiling-optimization](PERFORMANCE_OPTIMIZATION.md#monitoring-and-profiling-optimization)
- **Jaeger Tracing** → [BEST_PRACTICES.md#modern-observability-with-opentelemetry](BEST_PRACTICES.md#modern-observability-with-opentelemetry)

### 📖 Documentation Navigation Guide

#### **For New Users**
1. **Start Here**: [README.md](README.md) - Overview and installation
2. **Quick Start**: [README.md#quick-start-guide](README.md#quick-start-guide) - Get running quickly
3. **Common Questions**: [README.md#frequently-asked-questions-faq](README.md#frequently-asked-questions-faq) - FAQ section

#### **For Developers**
1. **Architecture**: [design.md](design.md) - Technical design and patterns
2. **Best Practices**: [BEST_PRACTICES.md](BEST_PRACTICES.md) - Development standards
3. **API Reference**: [API Documentation Index](API_DOCUMENTATION_INDEX.md) - API documentation

#### **For Operators**
1. **Troubleshooting**: [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) - Problem resolution
2. **Performance**: [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md) - Performance tuning
3. **Deployment**: [README.md#deployment](README.md#deployment) - Deployment guidance

#### **For Architects**
1. **System Design**: [design.md](design.md) - Architecture and design decisions
2. **Scalability**: [design.md#scalability-architecture](design.md#scalability-architecture) - Scaling strategies
3. **Security**: [design.md#security-architecture](design.md#security-architecture) - Security architecture

This troubleshooting guide is continuously updated based on user feedback and new issues discovered in the field. For the most current information, check the latest version in the project repository.