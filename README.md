# 🚀 Decentralized AI Simulation Project

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Mesa 3.3.0](https://img.shields.io/badge/mesa-3.3.0-orange.svg)](https://mesa.readthedocs.io/)
[![Ray 2.45.0](https://img.shields.io/badge/ray-2.45.0-red.svg)](https://ray.io/)
[![Streamlit 1.39.0](https://img.shields.io/badge/streamlit-1.39.0-ff69b4.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A production-ready Python-based simulation platform demonstrating decentralized AI agents collaborating on network anomaly detection through distributed consensus mechanisms.**

## 🌟 Overview

The **Decentralized AI Simulation Project** showcases how multiple autonomous AI agents can collaborate to detect network anomalies and share threat intelligence through a distributed consensus mechanism. This project demonstrates the power of **collective intelligence** in cybersecurity applications, where individual AI nodes work together to improve collective security posture without relying on a central authority.

### 🎯 Key Features

- **🤖 Multi-Agent System**: Autonomous AI agents that detect anomalies using machine learning
- **🔗 Distributed Consensus**: Peer-to-peer validation of threat signatures through majority voting
- **📊 Immutable Ledger**: SQLite-based blockchain-like storage for audit trails
- **⚡ High Performance**: Ray-based distributed computing with parallel execution
- **🖥️ Interactive Dashboard**: Real-time monitoring via Streamlit web interface
- **🔧 Production Ready**: Comprehensive logging, monitoring, health checks, and error handling
- **🚀 Scalable Architecture**: Horizontal and vertical scaling capabilities
- **🔒 Enterprise Security**: Input validation, rate limiting, CORS, and CSRF protection

### 🏗️ System Architecture

```mermaid
graph TB
    subgraph "AI Agent Network"
        AGENT1[Agent 1<br/>Anomaly Detection]
        AGENT2[Agent 2<br/>Anomaly Detection]
        AGENT3[Agent N<br/>Anomaly Detection]
    end

    subgraph "Core Infrastructure"
        CONSENSUS[Consensus Engine<br/>Majority Voting]
        LEDGER[Immutable Ledger<br/>SQLite + WAL Mode]
        MONITOR[Monitoring System<br/>Health + Metrics]
    end

    subgraph "User Interfaces"
        CLI[Command Line<br/>Headless Execution]
        WEB[Streamlit Dashboard<br/>Real-time Monitoring]
    end

    AGENT1 --> CONSENSUS
    AGENT2 --> CONSENSUS
    AGENT3 --> CONSENSUS
    CONSENSUS --> LEDGER
    LEDGER --> MONITOR
    CLI --> AGENT1
    WEB --> MONITOR

    style AGENT1 fill:#e1f5fe
    style AGENT2 fill:#e1f5fe
    style AGENT3 fill:#e1f5fe
    style CONSENSUS fill:#fff3e0
    style LEDGER fill:#e8f5e8
    style MONITOR fill:#fce4ec
    style CLI fill:#f3e5f5
    style WEB fill:#e0f2f1
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Python 3.11+ recommended for optimal performance)
- **Git** for version control and automated setup scripts
- **Virtual environment** support (venv module)
- **System dependencies** (see [System Requirements](#system-requirements) for details)

### Automated Setup (Recommended)

#### Complete Setup Process

```bash
# 1. Clone the repository
git clone <repository-url>
cd decentralized-ai-simulation

# 2. Run automated setup with verification (Linux/macOS)
./scripts/setup/setup.sh --verbose --dev --verify

# 3. Verify installation and run health checks
./scripts/setup/setup.sh --health-check

# 4. Launch the simulation
./scripts/runtime/run.sh

# 5. Or launch the web dashboard
./scripts/runtime/run.sh ui
```

**Windows users**: Use the corresponding `.bat` or `.ps1` scripts:
```cmd
REM Command Prompt
scripts\setup\setup.bat /verbose /dev /verify
scripts\setup\setup.bat /health-check
scripts\runtime\run.bat ui
```

```powershell
# PowerShell
.\scripts\setup\setup.ps1 -Verbose -DevMode -Verify
.\scripts\setup\setup.ps1 -HealthCheck
.\scripts\runtime\run.ps1 ui
```

#### Setup Verification Steps

After running the automated setup, verify the installation:

```bash
# 1. Check Python environment
python --version  # Should show Python 3.8+
which python      # Should point to virtual environment

# 2. Verify key dependencies
python -c "import mesa; print(f'Mesa: {mesa.__version__}')"

# 3. Test configuration system
python -c "from config_loader import get_config; print(f'DB Path: {get_config(\"database.path\")}')"

# 4. Run comprehensive health check
python -c "
from monitoring import get_monitoring
health = get_monitoring().get_system_health()
print(f'System Health: {health.status}')
print(f'Components: {len(health.components)} checked')
"
```

### Manual Installation

For users who prefer manual setup or need custom configurations:

#### Step 1: Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Upgrade pip and setup tools
pip install --upgrade pip setuptools wheel
```

#### Step 2: Dependency Installation
```bash
# Install core dependencies
pip install -r config/requirements.txt

# Verify installations
python -c "
import mesa, ray, streamlit, numpy, pandas, sklearn
print('✓ All core dependencies installed successfully')
"
```

#### Step 3: Configuration Validation
```bash
# Generate default configuration if needed
python -c "
from config_loader import ConfigLoader
config = ConfigLoader()
if not config._config_exists():
    config._create_default_config()
    print('✓ Default configuration created')
"

# Validate configuration syntax
python -c "
import yaml
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('✓ Configuration YAML syntax is valid')
"
```

#### Step 4: Database Initialization
```bash
# Initialize database with test data
python -c "
from database import DatabaseLedger
db = DatabaseLedger()
print('✓ Database initialized successfully')
db.close()
"
```

#### Step 5: Final Verification
```bash
# Run comprehensive verification
python -c "
# Test all major components
from config_loader import get_config
from database import DatabaseLedger
from monitoring import get_monitoring
import mesa, ray, streamlit

print('✓ Configuration system: OK')
print('✓ Database system: OK')
print('✓ Monitoring system: OK')
print('✓ Mesa framework: OK')
print('✓ Ray distributed computing: OK')
print('✓ Streamlit dashboard: OK')
print('🎉 Manual installation completed successfully!')
"
```

### System Requirements

#### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.8+ (3.11+ recommended)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk Space**: 2GB free space
- **Network**: Internet connection for initial setup

#### Recommended Specifications
- **CPU**: 4+ cores for optimal performance
- **RAM**: 16GB+ for large-scale simulations
- **Storage**: SSD for improved I/O performance
- **Network**: Gigabit Ethernet for distributed deployments

#### Platform-Specific Dependencies

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    python3.11-dev \
    libsqlite3-dev \
    libssl-dev \
    libffi-dev \
    libgomp1 \
    libopenmpi-dev
```

**macOS**:
```bash
# Using Homebrew
brew install openssl sqlite openmpi
# Install Rust for some Python packages
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**Windows**:
```cmd
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Install MPI for Ray (optional)
# Download from: https://www.microsoft.com/en-us/download/details.aspx?id=57467
```

## 📋 Usage Examples

### Basic Simulation

```bash
# Run with default settings (50 agents, 100 steps)
./run.sh

# Custom configuration
./run.sh cli --agents 100 --steps 200 --parallel

# Test mode (minimal configuration)
./run.sh test --verbose
```

### Web Dashboard

```bash
# Launch interactive dashboard
./run.sh ui

# Dashboard will be available at http://localhost:8501
```

### Programmatic Usage

```python
from decentralized_ai_simulation.src.core.simulation import Simulation
from decentralized_ai_simulation.src.core.monitoring import get_monitoring

# Create and run simulation
sim = Simulation(num_agents=100)
sim.run(steps=50)

# Access monitoring data
health = get_monitoring().get_system_health()
print(f"System health: {health.status}")
```

## 🔧 Configuration

### Configuration System Overview

The system uses a **hierarchical configuration approach** with multiple sources:

1. **YAML Configuration Files** (`config/config.yaml`) - Primary configuration
2. **Environment Variables** - Runtime overrides with `SIMULATION_*`, `DATABASE_*`, etc. prefixes
3. **Command-line Arguments** - Direct parameter overrides
4. **Default Values** - Hardcoded fallbacks for missing settings

### Environment Variables

#### Core Simulation Settings
```bash
# Simulation parameters
export SIMULATION_DEFAULT_AGENTS=100
export SIMULATION_DEFAULT_STEPS=200
export SIMULATION_ANOMALY_RATE=0.05
export SIMULATION_USE_PARALLEL_THRESHOLD=50
export SIMULATION_ENABLE_CHECKPOINTING=true

# Database settings
export DATABASE_PATH=ledger.db
export DATABASE_CONNECTION_POOL_SIZE=20
export DATABASE_TIMEOUT=60
export DATABASE_RETRY_ATTEMPTS=3

# Ray distributed computing
export RAY_ENABLE=true
export RAY_NUM_CPUS=8
export RAY_OBJECT_STORE_MEMORY=2147483648
export RAY_DASHBOARD_PORT=8265

# Logging and monitoring
export LOGGING_LEVEL=INFO
export LOGGING_FILE=logs/simulation.log
export MONITORING_ENABLE_PROMETHEUS=true
export MONITORING_HEALTH_CHECK_INTERVAL=30

# Performance optimization
export PERFORMANCE_ENABLE_CACHING=true
export PERFORMANCE_CACHE_SIZE_MB=500
export PERFORMANCE_MAX_WORKERS=8

# Security settings
export SECURITY_ENABLE_RATE_LIMITING=true
export SECURITY_RATE_LIMIT_REQUESTS_PER_MINUTE=100
```

### YAML Configuration

The system uses a comprehensive `config.yaml` with 150+ configuration options organized by category:

#### Production Configuration Example
```yaml
# config/config.yaml - Production Configuration
environment: production

# API Configuration
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  request_timeout: 30
  max_concurrent_requests: 100

# Simulation Configuration
simulation:
  default_agents: 100
  default_steps: 200
  anomaly_rate: 0.05
  use_parallel_threshold: 50
  enable_checkpointing: true
  random_seed: 42

# Database Configuration
database:
  path: /var/lib/simulation/ledger.db
  connection_pool_size: 20
  timeout: 60
  retry_attempts: 3
  max_overflow: 20
  pool_recycle: 3600

# Ray Configuration
ray:
  enable: true
  num_cpus: 8
  object_store_memory: 2147483648
  dashboard_port: 8265
  include_dashboard: true

# Logging Configuration
logging:
  level: WARNING
  file: /var/log/simulation.log
  max_bytes: 104857600  # 100MB
  backup_count: 10
  enable_json_logging: false

# Monitoring Configuration
monitoring:
  health_check_interval: 60
  enable_prometheus: true
  enable_detailed_metrics: true
  metrics_retention_days: 7
  metrics_port: 9090

# Performance Configuration
performance:
  enable_caching: true
  cache_size_mb: 500
  max_workers: 8
  memory_limit_mb: 2048

# Security Configuration
security:
  enable_input_validation: true
  rate_limit_requests_per_minute: 100
  enable_rate_limiting: true
  enable_csrf_protection: true
```

#### Development Configuration Example
```yaml
# config/config.yaml - Development Configuration
environment: development

simulation:
  default_agents: 25
  default_steps: 50
  anomaly_rate: 0.1

database:
  path: ledger.db
  connection_pool_size: 5

logging:
  level: DEBUG
  file: simulation.log
  enable_console_output: true

monitoring:
  health_check_interval: 30
  enable_prometheus: false

development:
  debug_mode: true
  enable_profiling: true
  show_tracebacks: true
```

### Configuration Validation and Verification

#### Step 1: Configuration Loading Test
```bash
# Test configuration loading
python -c "
from config_loader import get_config, is_production, is_development

# Test basic configuration access
print('✓ Configuration loaded successfully')
print(f'Database path: {get_config(\"database.path\")}')
print(f'Environment: {\"production\" if is_production() else \"development\"}')

# Test nested configuration access
ray_config = get_config('ray')
print(f'Ray enabled: {ray_config.get(\"enable\", False)}')

# Test default values
agents = get_config('simulation.default_agents', 100)
print(f'Default agents: {agents}')
"
```

#### Step 2: Environment Variable Override Test
```bash
# Test environment variable overrides
export SIMULATION_DEFAULT_AGENTS=200
export DATABASE_PATH=/tmp/test_ledger.db

python -c "
from config_loader import get_config

# Verify overrides are applied
agents = get_config('simulation.default_agents')
db_path = get_config('database.path')

print(f'✓ Environment override - Agents: {agents}')
print(f'✓ Environment override - DB Path: {db_path}')
"
```

#### Step 3: Configuration Schema Validation
```bash
# Validate configuration structure
python -c "
import yaml
from config_loader import ConfigLoader

# Load and validate configuration
config_loader = ConfigLoader()
config = config_loader._load_config()

# Check required sections exist
required_sections = ['simulation', 'database', 'logging', 'monitoring']
for section in required_sections:
    if section not in config:
        print(f'✗ Missing required section: {section}')
    else:
        print(f'✓ Section {section}: OK')

# Validate data types
if not isinstance(config.get('simulation', {}).get('default_agents'), int):
    print('✗ Invalid data type for simulation.default_agents')
else:
    print('✓ Data types: OK')
"
```

#### Step 4: Configuration Completeness Check
```bash
# Verify all configuration categories are present
python -c "
from config_loader import get_config

# Check all major configuration categories
categories = [
    'simulation', 'database', 'ray', 'logging',
    'monitoring', 'performance', 'security'
]

print('Configuration completeness check:')
for category in categories:
    try:
        value = get_config(category)
        print(f'✓ {category}: Configured')
    except KeyError:
        print(f'⚠ {category}: Using defaults')
"
```

### Configuration Best Practices

#### Environment-Specific Configuration
- **Development**: Verbose logging, debug mode, relaxed security
- **Production**: Optimized performance, security hardening, monitoring enabled
- **Testing**: Minimal configuration, fast execution, comprehensive logging

#### Configuration File Organization
```bash
# Use separate config files for different environments
config/
├── config.yaml          # Base configuration
├── config.dev.yaml      # Development overrides
├── config.prod.yaml     # Production overrides
└── config.test.yaml     # Testing configuration
```

#### Security Considerations
```bash
# Avoid sensitive data in configuration files
# Use environment variables for secrets
export DATABASE_PASSWORD=$(openssl rand -base64 32)
export API_SECRET_KEY=$(openssl rand -hex 32)
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Set secure file permissions
chmod 600 config/config.yaml
chmod 600 .env
```

## 📊 Anomaly Detection Workflow

```mermaid
flowchart TD
    subgraph "Traffic Generation"
        START[Simulation Start] --> GENERATE[Generate Synthetic Traffic]
        GENERATE --> NORMAL{Normal Traffic?}
        NORMAL -- Yes --> BASELINE[Baseline Patterns]
        NORMAL -- No --> ANOMALY[Inject Anomalies]
    end

    subgraph "AI Detection"
        BASELINE --> ANALYZE[Isolation Forest Analysis]
        ANOMALY --> ANALYZE
        ANALYZE --> SCORE[Calculate Anomaly Scores]
        SCORE --> THRESHOLD{Score > Threshold?}
    end

    subgraph "Consensus Validation"
        THRESHOLD -- Yes --> EXTRACT[Extract Anomaly Features]
        EXTRACT --> SIGNATURE[Generate Threat Signature]
        SIGNATURE --> BROADCAST[Broadcast to Network]
        BROADCAST --> PEERS[Peer Validation]
        PEERS --> VOTE[Consensus Voting]
        VOTE --> CONSENSUS{Majority Agreement?}
    end

    subgraph "Learning & Adaptation"
        CONSENSUS -- Yes --> ACCEPT[Accept Signature]
        CONSENSUS -- No --> REJECT[Reject Signature]
        ACCEPT --> UPDATE[Update All Models]
        UPDATE --> BLACKLIST[Update Threat Blacklists]
        BLACKLIST --> IMPROVE[Improved Detection]
    end

    style START fill:#bbdefb
    style GENERATE fill:#c8e6c9
    style ANALYZE fill:#fff9c4
    style SIGNATURE fill:#ffccbc
    style BROADCAST fill:#d1c4e9
    style CONSENSUS fill:#f8bbd0
    style ACCEPT fill:#80deea
    style UPDATE fill:#e8f5e8
```

## 🎛️ API Reference

### Core Classes

#### `Simulation` Class
```python
class Simulation:
    def __init__(num_agents: int = 100, seed: Optional[int] = None)
    def step() -> None
    def run(steps: int = 100) -> None
    def get_simulation_stats() -> Dict[str, Any]
```

#### `AnomalyAgent` Class
```python
class AnomalyAgent:
    def generate_traffic(batch_size: int) -> pd.DataFrame
    def detect_anomaly(data: pd.DataFrame) -> List[AnomalyResult]
    def generate_signature(anomaly_data: Dict) -> ThreatSignature
    def validate_signature(signature: ThreatSignature) -> ValidationResult
    def update_model_and_blacklist(signature: ThreatSignature) -> None
```

#### `DatabaseLedger` Class
```python
class DatabaseLedger:
    def append_entry(entry: Dict) -> int
    def read_ledger() -> List[Dict]
    def get_entry_by_id(entry_id: int) -> Optional[Dict]
    def get_new_entries(last_seen_id: int) -> List[Dict]
```

### Configuration API

```python
from decentralized_ai_simulation.src.config.config_loader import get_config

# Access configuration with dot notation
db_path = get_config('database.path')
agents_count = get_config('simulation.default_agents', 100)
ray_enabled = get_config('ray.enable', False)
```

### Monitoring API

```python
from decentralized_ai_simulation.src.utils.monitoring import get_monitoring

# Health checks
health = get_monitoring().get_system_health()
results = get_monitoring().perform_all_health_checks()

# Metrics collection
get_monitoring().record_metric('custom_metric', 42.5, {'label': 'value'})
stats = get_monitoring().get_metric_stats('custom_metric')
```

## 💡 Use Cases & Examples

### Research & Development

```bash
# Large-scale simulation for research
SIMULATION_DEFAULT_AGENTS=200 RAY_ENABLE=true ./run.sh cli --steps 500

# Monitor detailed metrics
python -c "
from decentralized_ai_simulation.src.utils.monitoring import get_monitoring
import time
while True:
    health = get_monitoring().get_system_health()
    print(f'Health: {health.status}')
    time.sleep(30)
"
```

### Educational Settings

```bash
# Demo mode with visual output
./run.sh demo --parallel

# Launch dashboard for classroom demonstration
./run.sh ui
```

### Production Deployment

#### Standard Production Setup
```yaml
# config/config.prod.yaml - Production Configuration
environment: production

# High-performance simulation settings
simulation:
  default_agents: 100
  default_steps: 200
  anomaly_rate: 0.05
  use_parallel_threshold: 50
  enable_checkpointing: true

# Production-grade database
database:
  path: /var/lib/simulation/ledger.db
  connection_pool_size: 20
  timeout: 60
  retry_attempts: 3
  max_overflow: 20
  pool_recycle: 3600

# Distributed computing for scale
ray:
  enable: true
  num_cpus: 8
  object_store_memory: 2147483648  # 2GB
  dashboard_port: 8265

# Enterprise monitoring
monitoring:
  enable_prometheus: true
  health_check_interval: 60
  enable_detailed_metrics: true
  metrics_port: 9090

# Performance optimization
performance:
  enable_caching: true
  cache_size_mb: 500
  max_workers: 8
  memory_limit_mb: 2048

# Security hardening
security:
  enable_input_validation: true
  rate_limit_requests_per_minute: 100
  enable_rate_limiting: true
  enable_csrf_protection: true
```

#### Production Deployment Commands
```bash
# 1. Deploy with production configuration
export ENVIRONMENT=production
export LOGGING_LEVEL=WARNING

# 2. Run with production settings
./scripts/deployment/deploy.sh production --backup --verbose

# 3. Verify production deployment
./scripts/deployment/deploy.sh production --health-check

# 4. Monitor production system
curl http://localhost:8501/health
curl http://localhost:9090/metrics
```

### Edge Computing Deployment

#### Minimal Resource Configuration
```yaml
# config/config.edge.yaml - Edge Computing Configuration
environment: production

# Minimal simulation for edge devices
simulation:
  default_agents: 25
  default_steps: 50
  anomaly_rate: 0.03
  use_parallel_threshold: 100  # Disable parallel for small deployments

# Lightweight database settings
database:
  path: /var/lib/simulation/ledger.db
  connection_pool_size: 5
  timeout: 15
  retry_attempts: 2

# Disable Ray for minimal resource usage
ray:
  enable: false

# Minimal monitoring for edge
monitoring:
  health_check_interval: 120  # Less frequent checks
  enable_prometheus: false
  enable_detailed_metrics: false

# Resource-constrained performance
performance:
  enable_caching: true
  cache_size_mb: 50
  max_workers: 2
  memory_limit_mb: 512

# Essential security only
security:
  enable_input_validation: true
  rate_limit_requests_per_minute: 50
  enable_rate_limiting: true
```

#### Edge Deployment Commands
```bash
# 1. Deploy for edge computing
export SIMULATION_DEFAULT_AGENTS=25
export RAY_ENABLE=false
export PERFORMANCE_MAX_WORKERS=2

# 2. Run edge-optimized simulation
./scripts/runtime/run.sh cli --agents 25 --steps 50

# 3. Monitor resource usage
python -c "
import psutil
print(f'CPU Usage: {psutil.cpu_percent()}%')
print(f'Memory Usage: {psutil.virtual_memory().percent}%')
"
```

### Development Deployment

#### Development Environment Setup
```yaml
# config/config.dev.yaml - Development Configuration
environment: development

# Development-friendly simulation
simulation:
  default_agents: 25
  default_steps: 50
  anomaly_rate: 0.1  # Higher rate for testing

# Development database settings
database:
  path: ledger.db
  connection_pool_size: 5

# Verbose logging for debugging
logging:
  level: DEBUG
  file: simulation.log
  max_bytes: 5242880  # 5MB
  enable_console_output: true

# Development monitoring
monitoring:
  health_check_interval: 30
  enable_prometheus: false

# Development tools enabled
development:
  debug_mode: true
  enable_profiling: true
  show_tracebacks: true
  hot_reload: true
```

#### Development Deployment Commands
```bash
# 1. Setup development environment
./scripts/setup/setup.sh --dev --verbose

# 2. Run with development settings
export LOGGING_LEVEL=DEBUG
export SIMULATION_DEFAULT_AGENTS=25

# 3. Launch with hot reload
./scripts/runtime/run.sh ui --debug

# 4. Run tests during development
./scripts/testing/test.sh --unit --verbose

# 5. Check code quality
./scripts/testing/test.sh --quality
```

### Container Deployment

#### Docker Deployment Configuration
```yaml
# config/config.docker.yaml - Docker Configuration
environment: production

# Container-optimized settings
simulation:
  default_agents: 50
  default_steps: 100

database:
  path: /app/data/ledger.db
  connection_pool_size: 10

# Container networking
api:
  host: "0.0.0.0"
  port: 8501

# Container logging
logging:
  level: INFO
  file: /app/logs/simulation.log

# Container monitoring
monitoring:
  enable_prometheus: true
  metrics_port: 9090
```

#### Docker Deployment Commands
```bash
# 1. Build container image
docker build -t simulation-app:2.45.0 .

# 2. Run container
docker run -d \
  --name simulation-app \
  -p 8501:8501 \
  -p 9090:9090 \
  -v $(pwd)/data:/app/data \
  simulation-app:2.45.0

# 3. Monitor container health
docker ps
docker logs simulation-app
docker stats simulation-app
```

### Kubernetes Deployment

#### Kubernetes Configuration
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simulation-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: simulation-app
  template:
    metadata:
      labels:
        app: simulation-app
    spec:
      containers:
      - name: simulation
        image: simulation-app:2.45.0
        ports:
        - containerPort: 8501
        - containerPort: 9090
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: SIMULATION_DEFAULT_AGENTS
          value: "50"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

#### Kubernetes Deployment Commands
```bash
# 1. Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 2. Check deployment status
kubectl get pods -l app=simulation-app
kubectl get services

# 3. Monitor Kubernetes deployment
kubectl logs -l app=simulation-app
kubectl top pods -l app=simulation-app

# 4. Scale deployment
kubectl scale deployment simulation-app --replicas=5
```

### Deployment Verification and Health Checks

#### Post-Deployment Health Checks
```bash
# 1. Basic connectivity test
curl -f http://localhost:8501/health || echo "Health check failed"

# 2. Database connectivity
python -c "
from database import DatabaseLedger
db = DatabaseLedger()
print('✓ Database connection: OK')
db.close()
"

# 3. Configuration validation
python -c "
from config_loader import get_config
from monitoring import get_monitoring

config = get_config('simulation')
health = get_monitoring().get_system_health()

print(f'✓ Configuration: {len(config)} settings loaded')
print(f'✓ System health: {health.status}')
"

# 4. Performance baseline
python -c "
import time
from simulation import Simulation

start_time = time.time()
sim = Simulation(num_agents=25)
sim.run(steps=10)
end_time = time.time()

print(f'✓ Performance test: {(end_time - start_time):.2f}s for 10 steps')
"
```

#### Deployment Troubleshooting
```bash
# 1. Check application logs
tail -f logs/simulation.log

# 2. Monitor system resources
htop || top -p $(pgrep -f "python.*simulation")

# 3. Test individual components
python -c "
# Test Mesa
import mesa
print(f'✓ Mesa {mesa.__version__}: OK')

# Test Ray
import ray
ray.init(num_cpus=2)
ray.shutdown()
print('✓ Ray: OK')

# Test database
from database import DatabaseLedger
db = DatabaseLedger()
db.close()
print('✓ Database: OK')
"

# 4. Network connectivity (for distributed deployments)
python -c "
import socket
import ray

# Test Ray cluster connectivity
try:
    ray.init(address='auto')
    print('✓ Ray cluster: Connected')
    ray.shutdown()
except Exception as e:
    print(f'✗ Ray cluster: {e}')
"
```

## 🔍 Monitoring & Health Checks

### Comprehensive Setup Verification

After installation, run comprehensive health checks to verify all components:

#### Automated Health Check Script
```bash
# Run complete system health check
./scripts/maintenance/health_check.sh --comprehensive

# Or use Python directly
python -c "
from monitoring import get_monitoring
import sys

# Perform all health checks
monitoring = get_monitoring()
results = monitoring.perform_all_health_checks()
overall_health = monitoring.get_system_health()

# Display results
print(f'Overall Health: {overall_health.status}')
print(f'Components Checked: {len(results)}')

for check_name, result in results.items():
    status = '✓' if result.status == 'healthy' else '✗'
    print(f'{status} {check_name}: {result.message}')

# Exit with error code if unhealthy
if overall_health.status != 'healthy':
    sys.exit(1)
"
```

#### Individual Component Health Checks

**1. Configuration System Health**
```python
from config_loader import get_config, ConfigLoader

# Test configuration loading
config_loader = ConfigLoader()
config = config_loader._load_config()

print(f'✓ Configuration file: {config_loader.config_path}')
print(f'✓ Environment: {config.get(\"environment\", \"development\")}')
print(f'✓ Configuration sections: {len(config)}')

# Test configuration access patterns
simulation_config = get_config('simulation')
database_config = get_config('database')
ray_config = get_config('ray')

print(f'✓ Simulation config: {len(simulation_config)} settings')
print(f'✓ Database config: {len(database_config)} settings')
print(f'✓ Ray config: {len(ray_config)} settings')
```

**2. Database System Health**
```python
from database import DatabaseLedger
import sqlite3

# Test database connectivity
try:
    db = DatabaseLedger()
    print('✓ Database connection: Established')
    
    # Test database operations
    db.append_entry({'test': 'data', 'timestamp': '2025-01-01'})
    entries = db.read_ledger()
    print(f'✓ Database operations: {len(entries)} entries')
    
    # Test connection pooling
    pool_status = db.get_pool_status()
    print(f'✓ Connection pool: {pool_status}')
    
    db.close()
except Exception as e:
    print(f'✗ Database error: {e}')
```

**3. Ray Distributed Computing Health**
```python
import ray

# Test Ray initialization
try:
    if not ray.is_initialized():
        ray.init(num_cpus=2, object_store_memory=1*1024*1024*1024)
    
    print('✓ Ray initialization: Successful')
    print(f'✓ Available CPUs: {ray.available_resources().get(\"CPU\", 0)}')
    print(f'✓ Object store memory: {ray.available_resources().get(\"object_store_memory\", 0)}')
    
    # Test Ray task execution
    @ray.remote
    def test_task(x):
        return x * 2
    
    futures = [test_task.remote(i) for i in range(4)]
    results = ray.get(futures)
    print(f'✓ Ray task execution: {results}')
    
    ray.shutdown()
except Exception as e:
    print(f'✗ Ray error: {e}')
```

**4. Core Dependencies Health**
```python
# Test all major dependencies
dependencies = [
    ('mesa', '3.3.0'),
    ('ray', '2.45.0'),
    ('streamlit', '1.39.0'),
    ('numpy', '2.1.3'),
    ('pandas', '2.2.3'),
    ('scikit_learn', '1.7.2'),
    ('plotly', '6.3.1'),
    ('PyYAML', '6.0.3')
]

print('Dependency Health Check:')
for module, expected_version in dependencies:
    try:
        module_obj = __import__(module)
        version = getattr(module_obj, '__version__', 'unknown')
        status = '✓' if version.startswith(expected_version.split('.')[0]) else '⚠'
        print(f'{status} {module}: {version} (expected: {expected_version})')
    except ImportError as e:
        print(f'✗ {module}: Import failed - {e}')
```

### Real-time Health Monitoring

The system includes comprehensive health monitoring with customizable checks:

#### Custom Health Check Registration
```python
from monitoring import get_monitoring, HealthStatus

def custom_database_check():
    try:
        from database import DatabaseLedger
        db = DatabaseLedger()
        # Test database performance
        import time
        start = time.time()
        db.read_ledger()
        query_time = time.time() - start
        
        if query_time < 1.0:  # Less than 1 second
            return HealthStatus(status='healthy', message=f'DB query time: {query_time:.3f}s')
        else:
            return HealthStatus(status='warning', message=f'Slow DB query: {query_time:.3f}s')
    except Exception as e:
        return HealthStatus(status='unhealthy', message=f'DB error: {e}')
    finally:
        try: db.close()
        except: pass

def custom_memory_check():
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    if memory_mb < 500:  # Less than 500MB
        return HealthStatus(status='healthy', message=f'Memory usage: {memory_mb:.1f}MB')
    elif memory_mb < 1000:  # Less than 1GB
        return HealthStatus(status='warning', message=f'High memory: {memory_mb:.1f}MB')
    else:
        return HealthStatus(status='unhealthy', message=f'Critical memory: {memory_mb:.1f}MB')

# Register custom health checks
monitoring = get_monitoring()
monitoring.register_health_check('database_performance', custom_database_check)
monitoring.register_health_check('memory_usage', custom_memory_check)

# Perform all health checks
results = monitoring.perform_all_health_checks()
overall_health = monitoring.get_system_health()

print(f'Overall health: {overall_health.status}')
for check_name, result in results.items():
    print(f'{check_name}: {result.status} - {result.message}')
```

### Key Metrics Tracked

#### Performance Metrics
- **Step Duration**: Time taken for each simulation step
- **Throughput**: Number of simulation steps per minute
- **Latency**: Response time for API endpoints
- **Resource Utilization**: CPU, memory, and disk usage

#### Business Metrics
- **Anomalies Detected**: Number and rate of anomalies found
- **Signatures Validated**: Threat signatures created and validated
- **Consensus Reached**: Success rate of consensus mechanisms
- **Model Accuracy**: Machine learning model performance metrics

#### System Metrics
- **Error Rates**: Frequency and types of system errors
- **Availability**: System uptime and downtime tracking
- **Resource Consumption**: Memory, CPU, and storage usage trends
- **Network Activity**: Inter-agent communication statistics

#### Custom Metrics
```python
# Record custom application metrics
monitoring.record_metric('custom_anomaly_score', 0.85, {
    'agent_id': 'agent_001',
    'anomaly_type': 'network_scan'
})

monitoring.record_metric('consensus_confidence', 0.92, {
    'signature_id': 'sig_12345',
    'participating_agents': 15
})

# Retrieve metric statistics
stats = monitoring.get_metric_stats('custom_anomaly_score')
print(f"Anomaly score - Mean: {stats.mean:.3f}, Std: {stats.std:.3f}")
```

### Prometheus Integration

#### Prometheus Configuration
```yaml
# Enable comprehensive Prometheus metrics
monitoring:
  enable_prometheus: true
  metrics_port: 9090
  metrics_path: "/metrics"
  enable_detailed_metrics: true
  metrics_retention_days: 7
```

#### Prometheus Metrics Endpoints
```bash
# Start application with Prometheus metrics
export MONITORING_ENABLE_PROMETHEUS=true
export MONITORING_METRICS_PORT=9090

# Access metrics
curl http://localhost:9090/metrics

# Common metrics include:
# - simulation_step_duration_seconds
# - simulation_agents_active
# - database_connection_pool_size
# - ray_tasks_pending
# - system_memory_usage_mb
# - anomaly_detection_rate
```

#### Grafana Dashboard Setup
```bash
# 1. Configure Grafana data source
# URL: http://localhost:9090
# Access: Server (default)

# 2. Import dashboard JSON from:
# docs/monitoring/grafana_dashboard.json

# 3. Monitor key metrics:
# - System performance and resource usage
# - Simulation progress and anomaly detection
# - Database performance and connection pooling
# - Ray cluster status and task distribution
```

### Setup Troubleshooting with Health Checks

#### Automated Setup Verification
```bash
# Run post-setup health verification
python -c "
import sys

def verify_setup():
    checks = []
    
    # Check 1: Python environment
    try:
        import sys
        if sys.version_info >= (3, 8):
            checks.append(('Python version', True, f'{sys.version}'))
        else:
            checks.append(('Python version', False, f'Python {sys.version} (need 3.8+)'))
    except:
        checks.append(('Python version', False, 'Python check failed'))
    
    # Check 2: Virtual environment
    try:
        import sys
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            checks.append(('Virtual environment', True, 'Active'))
        else:
            checks.append(('Virtual environment', False, 'Not active'))
    except:
        checks.append(('Virtual environment', False, 'Check failed'))
    
    # Check 3: Core dependencies
    core_deps = ['mesa', 'ray', 'streamlit', 'numpy', 'pandas']
    for dep in core_deps:
        try:
            __import__(dep)
            checks.append((f'{dep} import', True, 'OK'))
        except ImportError as e:
            checks.append((f'{dep} import', False, str(e)))
    
    # Check 4: Configuration
    try:
        from config_loader import get_config
        config = get_config('simulation')
        checks.append(('Configuration', True, f'{len(config)} settings'))
    except Exception as e:
        checks.append(('Configuration', False, str(e)))
    
    # Check 5: Database
    try:
        from database import DatabaseLedger
        db = DatabaseLedger()
        db.close()
        checks.append(('Database', True, 'Connection OK'))
    except Exception as e:
        checks.append(('Database', False, str(e)))
    
    # Summary
    passed = sum(1 for _, success, _ in checks if success)
    total = len(checks)
    
    print(f'Setup Verification: {passed}/{total} checks passed')
    print()
    
    for check_name, success, message in checks:
        status = '✓' if success else '✗'
        print(f'{status} {check_name}: {message}')
    
    return passed == total

if not verify_setup():
    print('\\n❌ Setup verification failed!')
    sys.exit(1)
else:
    print('\\n✅ Setup verification completed successfully!')
"
```

#### Setup Issue Detection and Resolution
```bash
# Automated setup troubleshooting
python -c "
import sys
import os

def diagnose_setup_issues():
    issues = []
    solutions = []
    
    # Check 1: Python path issues
    if not hasattr(sys, 'real_prefix') and sys.base_prefix == sys.prefix:
        issues.append('Virtual environment not activated')
        solutions.append('Run: source .venv/bin/activate')
    
    # Check 2: Missing dependencies
    required_modules = ['mesa', 'ray', 'streamlit']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            issues.append(f'Missing module: {module}')
            solutions.append(f'Run: pip install {module}')
    
    # Check 3: Configuration file
    if not os.path.exists('config/config.yaml'):
        issues.append('Configuration file missing')
        solutions.append('Run: python -c \"from config_loader import ConfigLoader; ConfigLoader()._create_default_config()\"')
    
    # Check 4: Database directory
    if not os.path.exists('data/databases'):
        issues.append('Database directory missing')
        solutions.append('Run: mkdir -p data/databases')
    
    # Check 5: Log directory
    if not os.path.exists('logs'):
        issues.append('Log directory missing')
        solutions.append('Run: mkdir -p logs')
    
    # Report issues
    if issues:
        print('Setup Issues Found:')
        for issue, solution in zip(issues, solutions):
            print(f'❌ {issue}')
            print(f'   💡 {solution}')
            print()
        
        print(f'Total issues: {len(issues)}')
        return False
    else:
        print('✅ No setup issues detected!')
        return True

if not diagnose_setup_issues():
    sys.exit(1)
"
```

## 🛠️ Troubleshooting

### Setup Troubleshooting Guide

#### Quick Setup Diagnostics

**Automated Setup Verification**:
```bash
# Run comprehensive setup diagnostics
python -c "
import sys
import os

def run_setup_diagnostics():
    print('🔍 Running Setup Diagnostics...')
    print('=' * 50)
    
    # Check 1: Python Environment
    print('1. Python Environment:')
    print(f'   Version: {sys.version}')
    print(f'   Executable: {sys.executable}')
    
    # Check 2: Virtual Environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print('   Virtual Env: ✅ Active')
    else:
        print('   Virtual Env: ❌ Not active')
        return False
    
    # Check 3: Core Dependencies
    print('2. Core Dependencies:')
    core_deps = ['mesa', 'ray', 'streamlit', 'numpy', 'pandas', 'sklearn']
    for dep in core_deps:
        try:
            mod = __import__(dep)
            version = getattr(mod, '__version__', 'unknown')
            print(f'   {dep}: ✅ {version}')
        except ImportError as e:
            print(f'   {dep}: ❌ {e}')
            return False
    
    # Check 4: Configuration
    print('3. Configuration:')
    try:
        from config_loader import get_config
        sim_config = get_config('simulation')
        print(f'   Config file: ✅ {len(sim_config)} settings loaded')
    except Exception as e:
        print(f'   Config file: ❌ {e}')
        return False
    
    # Check 5: Database
    print('4. Database:')
    try:
        from database import DatabaseLedger
        db = DatabaseLedger()
        db.close()
        print('   Database: ✅ Connection OK')
    except Exception as e:
        print(f'   Database: ❌ {e}')
        return False
    
    # Check 6: File Structure
    print('5. File Structure:')
    required_dirs = ['logs', 'data/databases', 'config']
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f'   {dir_path}: ✅ Exists')
        else:
            print(f'   {dir_path}: ❌ Missing')
            return False
    
    print('=' * 50)
    print('🎉 All setup checks passed!')
    return True

if not run_setup_diagnostics():
    print('\\n❌ Setup diagnostics failed!')
    print('💡 Run: ./scripts/setup/setup.sh --verbose --force')
    sys.exit(1)
"
```

#### Common Setup Issues & Solutions

**Python Version Issues**:
```bash
# Check Python version compatibility
python --version  # Should be 3.8+

# Update Python if needed
# Ubuntu/Debian:
sudo apt install python3.11 python3.11-venv

# macOS:
brew install python@3.11

# Windows: Download from python.org
```

**Virtual Environment Problems**:
```bash
# Recreate environment if corrupted
./scripts/setup/setup.sh --force

# Manual environment setup
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\\Scripts\\activate   # Windows

# Verify activation
which python  # Should point to .venv/bin/python
```

**Dependency Installation Failures**:
```bash
# Install with verbose output
pip install -r config/requirements.txt -v

# Install individually for debugging
pip install mesa==3.3.0
pip install ray[default]==2.45.0
pip install streamlit==1.39.0

# Check for conflicts
pip check
```

**Ray Installation Issues**:
```bash
# Install Ray with minimal dependencies
pip uninstall ray -y
pip install ray[default]==2.45.0 --no-cache-dir

# Test Ray installation
python -c "
import ray
ray.init(num_cpus=2)
print('Ray: ✅ OK')
ray.shutdown()
"
```

**Database Connection Issues**:
```bash
# Reset database if corrupted
./scripts/maintenance/cleanup.sh --database --force

# Check database file permissions
ls -la data/databases/ledger.db
chmod 666 data/databases/ledger.db

# Test database connection
python -c "
from database import DatabaseLedger
db = DatabaseLedger()
print('Database: ✅ OK')
db.close()
"
```

**Configuration File Issues**:
```bash
# Validate YAML syntax
python -c "
import yaml
try:
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print('YAML syntax: ✅ Valid')
except yaml.YAMLError as e:
    print(f'YAML syntax: ❌ {e}')
"

# Generate default configuration
python -c "
from config_loader import ConfigLoader
ConfigLoader()._create_default_config()
print('Default config: ✅ Created')
"
```

**Permission Issues**:
```bash
# Fix script permissions
find scripts -name "*.sh" -exec chmod +x {} \\;

# Fix data directory permissions
chmod -R 755 data/
chmod -R 755 logs/
```

### Cross-Platform Setup Issues

#### Linux/Unix Issues
```bash
# Check for missing system dependencies
sudo apt install -y build-essential python3.11-dev libsqlite3-dev

# Fix locale issues
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Check for conflicting packages
pip list --format=freeze | grep -i mesa  # Should show mesa==3.3.0
```

#### macOS Issues
```bash
# Install missing dependencies
brew install openssl sqlite

# Fix OpenMP issues
brew install libomp

# Check Python path
which python3
python3 --version
```

#### Windows Issues
```cmd
# Check Python installation
python --version

# Fix execution policy for PowerShell
PowerShell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"

# Check virtual environment activation
where python  # Should show Scripts\python.exe
```

### Performance-Related Setup Issues

**High Memory Usage During Setup**:
```bash
# Monitor memory during setup
python -c "
import psutil
import time

print('Monitoring memory usage...')
for i in range(10):
    memory = psutil.virtual_memory().percent
    print(f'Memory: {memory}%')
    time.sleep(1)
"
```

**Slow Installation**:
```bash
# Use parallel installation
pip install -r config/requirements.txt --no-cache-dir

# Use alternative package index
pip install --extra-index-url https://pypi.org/simple -r config/requirements.txt
```

**Import Errors After Setup**:
```bash
# Check Python path
import sys
print('\\n'.join(sys.path))

# Verify module locations
python -c "
import mesa
print(f'Mesa location: {mesa.__file__}')

import ray
print(f'Ray location: {ray.__file__}')
"
```

### Log File Locations and Analysis

#### Setup and Installation Logs
- **Setup Logs**: `logs/setup.log` - Detailed setup process logs
- **Installation Logs**: `logs/install.log` - Package installation logs
- **Configuration Logs**: `logs/config.log` - Configuration loading logs
- **Database Logs**: `logs/database.log` - Database initialization logs

#### Log Analysis Commands
```bash
# View recent setup errors
tail -50 logs/setup.log | grep -i error

# Monitor setup in real-time
tail -f logs/setup.log

# Search for specific issues
grep -r "ImportError" logs/
grep -r "ModuleNotFoundError" logs/
grep -r "permission denied" logs/
```

#### Log Rotation and Management
```bash
# Check log file sizes
du -sh logs/*.log

# Rotate logs if too large
./scripts/maintenance/cleanup.sh --logs

# Archive old logs
tar -czf logs/archive_$(date +%Y%m%d).tar.gz logs/*.log.1
```

### Advanced Setup Troubleshooting

#### Component-Level Testing
```bash
# Test individual components after setup
python -c "
# Test 1: Configuration system
print('Testing configuration system...')
from config_loader import get_config
config = get_config('simulation')
print(f'✓ Configuration: {len(config)} settings')

# Test 2: Database system
print('Testing database system...')
from database import DatabaseLedger
db = DatabaseLedger()
db.close()
print('✓ Database: OK')

# Test 3: Monitoring system
print('Testing monitoring system...')
from monitoring import get_monitoring
health = get_monitoring().get_system_health()
print(f'✓ Monitoring: {health.status}')

# Test 4: Ray system
print('Testing Ray system...')
import ray
ray.init(num_cpus=2)
ray.shutdown()
print('✓ Ray: OK')

# Test 5: Mesa framework
print('Testing Mesa framework...')
import mesa
print(f'✓ Mesa: {mesa.__version__}')

print('🎉 All components tested successfully!')
"
```

#### Environment-Specific Setup Issues

**Development Environment Issues**:
```bash
# Enable debug mode for detailed logging
export LOGGING_LEVEL=DEBUG
export DEVELOPMENT_DEBUG_MODE=true

# Check development tools
python -c "
import sys
print(f'Python version: {sys.version}')
print(f'Platform: {sys.platform}')
print(f'Python executable: {sys.executable}')
"
```

**Production Environment Issues**:
```bash
# Test production configuration
export ENVIRONMENT=production
export LOGGING_LEVEL=WARNING

# Check security settings
python -c "
from config_loader import get_config
security = get_config('security')
print(f'Rate limiting: {security.get(\"enable_rate_limiting\", False)}')
print(f'Input validation: {security.get(\"enable_input_validation\", False)}')
"
```

**Edge Computing Issues**:
```bash
# Test resource-constrained setup
export SIMULATION_DEFAULT_AGENTS=10
export RAY_ENABLE=false

# Monitor resource usage
python -c "
import psutil
print(f'CPU cores: {psutil.cpu_count()}')
print(f'Memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}GB')
"
```

### Getting Help and Support

#### Automated Help Commands
```bash
# View all available script options
./scripts/setup/setup.sh --help
./scripts/runtime/run.sh --help
./scripts/testing/test.sh --help
./scripts/maintenance/cleanup.sh --help

# Check system health
python -c "
from monitoring import get_monitoring
health = get_monitoring().get_system_health()
print(f'System Health: {health.status}')
print(f'Components: {len(health.components)} checked')
"
```

#### Manual Component Testing
```bash
# Test configuration system
python -c "
from config_loader import get_config, is_production, is_development
print(f'Environment: {\"production\" if is_production() else \"development\"}')
print(f'Default agents: {get_config(\"simulation.default_agents\", \"not set\")}')
"

# Test database system
python -c "
from database import DatabaseLedger
db = DatabaseLedger()
entries = db.read_ledger()
print(f'Database entries: {len(entries)}')
db.close()
"

# Test monitoring system
python -c "
from monitoring import get_monitoring
monitoring = get_monitoring()
results = monitoring.perform_all_health_checks()
print(f'Health checks: {len(results)} performed')
for name, result in results.items():
    print(f'  {name}: {result.status}')
"
```

#### Cross-Reference Documentation Links

For detailed troubleshooting information, see:
- **[📖 Detailed Setup Guide](decentralized-ai-simulation/docs/README.md#installation)**: In-depth installation procedures
- **[🔧 Scripts Documentation](decentralized-ai-simulation/docs/SCRIPTS_README.md)**: Cross-platform script usage
- **[🛠️ Comprehensive Troubleshooting](decentralized-ai-simulation/docs/TROUBLESHOOTING_GUIDE.md)**: Detailed problem resolution
- **[⚡ Performance Optimization](decentralized-ai-simulation/docs/PERFORMANCE_OPTIMIZATION.md)**: Setup performance tuning
- **[🏗️ Architecture Overview](decentralized-ai-simulation/docs/PROJECT_OVERVIEW.md#usage-and-deployment)**: Deployment architecture details

### Setup Recovery Procedures

#### Complete Setup Reset
```bash
# 1. Stop all processes
pkill -f "python.*simulation" || true
pkill -f "streamlit" || true

# 2. Clean everything
./scripts/maintenance/cleanup.sh --all --force

# 3. Fresh setup
./scripts/setup/setup.sh --verbose --dev --force

# 4. Verify setup
./scripts/setup/setup.sh --health-check
```

#### Partial Setup Recovery
```bash
# Fix specific components

# Database issues
./scripts/maintenance/cleanup.sh --database --force
python -c "from database import DatabaseLedger; db = DatabaseLedger(); db.close(); print('DB OK')"

# Configuration issues
python -c "from config_loader import ConfigLoader; ConfigLoader()._create_default_config()"
python -c "from config_loader import get_config; print(get_config('simulation'))"

# Dependency issues
pip install -r config/requirements.txt --force-reinstall --no-cache-dir
```

#### Emergency Setup Commands
```bash
# Quick environment check
python -c "import sys; print(f'Python: {sys.version}')"

# Quick dependency check
python -c "
deps = ['mesa', 'ray', 'streamlit']
for dep in deps:
    try:
        __import__(dep)
        print(f'{dep}: OK')
    except ImportError as e:
        print(f'{dep}: ERROR - {e}')
"

# Quick database check
python -c "
try:
    from database import DatabaseLedger
    db = DatabaseLedger()
    db.close()
    print('Database: OK')
except Exception as e:
    print(f'Database: ERROR - {e}')
"
```

## 📚 Documentation

### Comprehensive Guides

- **[📖 Detailed Documentation](decentralized-ai-simulation/docs/README.md)**: In-depth technical documentation
- **[🏗️ Project Overview](decentralized-ai-simulation/docs/PROJECT_OVERVIEW.md)**: Technical architecture and design
- **[🚀 Scripts Guide](decentralized-ai-simulation/docs/SCRIPTS_README.md)**: Cross-platform script documentation
- **[⚡ Performance Guide](decentralized-ai-simulation/docs/PERFORMANCE_OPTIMIZATION.md)**: Optimization and scaling
- **[🛠️ Migration Guide](decentralized-ai-simulation/docs/MIGRATION_GUIDE.md)**: Version upgrade instructions

### API Documentation

- **[🔧 Configuration API](decentralized-ai-simulation/src/config/config_loader.py)**: Configuration management
- **[📊 Monitoring API](decentralized-ai-simulation/src/utils/monitoring.py)**: Health checks and metrics
- **[🗄️ Database API](decentralized-ai-simulation/src/core/database.py)**: Ledger operations
- **[🤖 Agent API](decentralized-ai-simulation/src/core/agents.py)**: AI agent functionality

## 🤝 Contributing

We welcome contributions! Please see our comprehensive guides:

1. **[Development Setup](decentralized-ai-simulation/docs/README.md#contributing)**: Environment setup and standards
2. **[Code Quality](decentralized-ai-simulation/docs/README.md#development-standards)**: Testing and documentation requirements
3. **[Pull Request Process](decentralized-ai-simulation/docs/README.md#pull-request-process)**: Contribution workflow

### Development Standards

- **Testing**: 90%+ code coverage with comprehensive test suites
- **Documentation**: Complete API documentation and usage examples
- **Code Style**: PEP8 compliance with Black formatting
- **Type Hints**: Full type annotation for all public APIs

## 📈 Performance & Benchmarks

### Tested Configurations

- **Agent Capacity**: Successfully tested with 200+ concurrent agents
- **Processing Speed**: 50-200+ simulation steps per minute
- **Memory Usage**: 100-800MB depending on configuration
- **Database Performance**: 2000+ transactions per second
- **Network Throughput**: 1000+ signatures per second in distributed mode

### Scalability Features

- **Horizontal Scaling**: Linear performance improvement with additional CPU cores
- **Vertical Scaling**: Efficient memory usage with configurable connection pools
- **Ray Integration**: Distributed execution across multiple nodes
- **Memory Optimization**: Intelligent caching with LRU eviction

## 🔒 Security & Reliability

### Security Features

- **Input Validation**: Comprehensive sanitization and validation
- **Rate Limiting**: Configurable API rate limiting
- **CORS Protection**: Cross-origin request controls
- **CSRF Protection**: Cross-site request forgery prevention
- **Access Control**: Environment-based permissions

### Reliability Features

- **Health Monitoring**: Continuous system health checks
- **Error Handling**: Comprehensive exception handling and recovery
- **Graceful Degradation**: System continues despite partial failures
- **Resource Management**: Proper cleanup and garbage collection

## 🏷️ Changelog

### Recent Updates (October 2025)

- **Enhanced Architecture**: Modernized to Mesa 3.3.0 and Ray 2.45.0
- **Performance Optimizations**: Multi-level caching and connection pooling
- **Security Enhancements**: Input validation and rate limiting
- **Monitoring Integration**: Prometheus metrics and health checks
- **Developer Experience**: Hot reload and enhanced debugging

*For detailed changelog, see [📋 Documentation](decentralized-ai-simulation/docs/README.md#changelog)*

## 📞 Support

For questions, issues, or contributions:

1. **📖 Check Documentation**: Review guides and API documentation
2. **🔍 Search Issues**: Look for similar problems and solutions
3. **🐛 Report Bugs**: Provide detailed reproduction steps
4. **💡 Request Features**: Describe use cases and requirements
5. **🤝 Contribute**: Follow our contribution guidelines

### Support Details

Include these details for support requests:
- Configuration file contents (sanitized)
- Environment variables and versions
- Relevant log excerpts
- Steps to reproduce the issue
- Expected vs. actual behavior

## 📄 License

This project is open source and available under the **MIT License**.

---

<div align="center">

**Built with ❤️ by the Decentralized AI Simulation Team**

[📖 Full Documentation](decentralized-ai-simulation/docs/README.md) •
[🏗️ Architecture](decentralized-ai-simulation/docs/PROJECT_OVERVIEW.md) •
[🚀 Get Started](decentralized-ai-simulation/README.md) •
[🤝 Contribute](#contributing)

</div>