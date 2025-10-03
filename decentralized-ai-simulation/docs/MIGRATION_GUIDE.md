# Migration Guide: Dependency Updates and Modernization (October 2025)

## Overview

This guide provides comprehensive instructions for migrating from the previous version to the modernized Decentralized AI Simulation platform with updated dependencies and enhanced features.

## Dependency Changes

### Major Version Updates

| Package | Previous Version | Current Version | Impact |
|---------|------------------|-----------------|---------|
| **mesa** | 2.x | **3.3.0** | Enhanced agent-based modeling, improved scheduling |
| **ray** | 2.x | **2.45.0** | Advanced distributed computing, better dashboard |
| **numpy** | 1.x | **2.1.3** | Performance improvements, new array functions |
| **streamlit** | 1.28.x | **1.39.0** | Enhanced UI components, better performance |
| **scikit-learn** | 1.3.x | **1.7.2** | Improved ML algorithms, bug fixes |
| **pandas** | 2.0.x | **2.2.3** | Enhanced data manipulation capabilities |
| **pytest** | 7.x | **8.4.2** | Better testing framework, improved assertions |
| **networkx** | 3.1 | **3.5** | Enhanced graph algorithms |
| **plotly** | 5.x | **6.3.1** | Advanced visualization features |
| **PyYAML** | 6.0 | **6.0.3** | Security patches, stability improvements |

### Installation Migration

#### Before (Previous Version)
```bash
pip install mesa==2.x ray==2.x numpy==1.x
```

#### After (Current Version)
```bash
pip install -r requirements.txt
# or manually:
pip install mesa==3.3.0 ray[default]==2.45.0 numpy==2.1.3 scikit-learn==1.7.2 streamlit==1.39.0
```

## Configuration Changes

### New Configuration Structure

The configuration system has been significantly enhanced with new sections and options.

#### Previous Structure
```yaml
# Old config.yaml
environment: development
database:
  path: ledger.db
logging:
  level: INFO
simulation:
  default_agents: 50
```

#### Current Structure
```yaml
# New config.yaml (October 2025)
environment: development

# API Configuration (NEW)
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  request_timeout: 30
  max_concurrent_requests: 100

# Enhanced Database Configuration
database:
  path: ledger.db
  connection_pool_size: 5
  timeout: 30
  retry_attempts: 3
  max_overflow: 20
  pool_recycle: 3600

# Ray Configuration (NEW)
ray:
  enable: true
  num_cpus: 4
  object_store_memory: 1073741824
  dashboard_port: 8265

# Enhanced Logging
logging:
  level: DEBUG
  file: simulation.log
  max_bytes: 5242880
  backup_count: 5
  enable_console_output: true

# Monitoring Configuration (ENHANCED)
monitoring:
  health_check_interval: 30
  enable_prometheus: false
  enable_detailed_metrics: true

# Performance Configuration (NEW)
performance:
  enable_caching: true
  cache_size_mb: 100
  max_workers: 4

# Security Configuration (NEW)
security:
  enable_input_validation: true
  rate_limit_requests_per_minute: 100
  enable_rate_limiting: true

# Development Configuration (NEW)
development:
  debug_mode: true
  enable_profiling: true
  show_tracebacks: true
```

## Environment Variable Migration

### New Environment Variables

The system now supports many more environment variable overrides for flexible configuration.

#### Previous Variables
```bash
export SIMULATION_DEFAULT_AGENTS=100
export LOGGING_LEVEL=DEBUG
export DATABASE_PATH=ledger.db
```

#### Current Variables (Comprehensive)
```bash
# Simulation parameters
export SIMULATION_DEFAULT_AGENTS=100
export SIMULATION_DEFAULT_STEPS=200
export SIMULATION_ANOMALY_RATE=0.05
export SIMULATION_USE_PARALLEL_THRESHOLD=50

# Database settings
export DATABASE_PATH=custom_ledger.db
export DATABASE_CONNECTION_POOL_SIZE=20
export DATABASE_TIMEOUT=60

# Ray distributed computing
export RAY_ENABLE=true
export RAY_NUM_CPUS=8
export RAY_OBJECT_STORE_MEMORY=2147483648

# Logging configuration
export LOGGING_LEVEL=DEBUG
export LOGGING_FILE=logs/custom.log
export LOGGING_MAX_BYTES=10485760

# Streamlit dashboard
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"

# Monitoring settings
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

## Code Migration

### Import Changes

#### Previous Imports
```python
# Old imports (may still work but deprecated)
import mesa
from ray import tune
import numpy as np
```

#### Current Imports (Recommended)
```python
# New imports with version-specific features
import mesa  # v3.3.0
import ray  # v2.45.0
import numpy as np  # v2.1.3
from sklearn.ensemble import IsolationForest  # v1.7.2
import streamlit as st  # v1.39.0
```

### API Changes

#### Configuration Access
```python
# Previous (still supported)
from config_loader import get_config
agents = get_config('simulation.default_agents')

# Current (enhanced with validation)
from config_loader import get_config, is_production, is_development
agents = get_config('simulation.default_agents', 50)  # With default
if is_production():
    # Production-specific logic
    pass
```

#### Database Operations
```python
# Previous (basic)
from database import DatabaseLedger
db = DatabaseLedger()
entries = db.read_ledger()

# Current (enhanced with caching and pooling)
from database import DatabaseLedger
db = DatabaseLedger()  # Now uses connection pooling
entries = db.read_ledger()  # Cached for better performance
new_entries = db.get_new_entries(last_id)  # Efficient incremental queries
```

## Performance Migration

### Optimization Settings

#### Previous Performance Settings
```yaml
# Limited performance configuration
database:
  connection_pool_size: 5
logging:
  level: INFO
```

#### Current Performance Settings
```yaml
# Comprehensive performance configuration
database:
  connection_pool_size: 10
  timeout: 30
  retry_attempts: 3
  max_overflow: 20

performance:
  enable_caching: true
  cache_size_mb: 100
  max_workers: 4
  memory_limit_mb: 1024
  enable_async_processing: false

ray:
  enable: true
  num_cpus: 4
  object_store_memory: 1073741824
```

## Testing Migration

### Test Framework Updates

#### Previous Testing
```bash
# Basic testing
python -m pytest tests/
```

#### Current Testing (Enhanced)
```bash
# Comprehensive testing with coverage
pytest tests/ --cov=. --cov-report=html --verbose

# Performance testing
pytest tests/ -k "performance" --durations=10

# Integration testing
pytest tests/ -k "integration" --tb=short
```

## Deployment Migration

### Docker Migration (if applicable)

#### Previous Dockerfile
```dockerfile
FROM python:3.8-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
```

#### Current Dockerfile (Optimized)
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Add health check, security, and optimization layers
```

### Production Deployment

#### Previous Deployment
```bash
# Basic deployment
python decentralized_ai_simulation.py
```

#### Current Deployment (Production-Ready)
```bash
# Production deployment with monitoring
SIMULATION_DEFAULT_AGENTS=100 \
LOGGING_LEVEL=WARNING \
MONITORING_ENABLE_PROMETHEUS=true \
python decentralized_ai_simulation.py --production
```

## Troubleshooting Migration Issues

### Common Issues and Solutions

#### Issue 1: Import Errors
```bash
# Problem: ImportError: No module named 'mesa'
# Solution: Update requirements and reinstall
pip install -r requirements.txt --upgrade
```

#### Issue 2: Configuration Errors
```bash
# Problem: Configuration key not found
# Solution: Check new configuration structure
python -c "from config_loader import get_config; print(get_config('ray.enable', False))"
```

#### Issue 3: Performance Issues
```bash
# Problem: High memory usage
# Solution: Adjust performance settings
export PERFORMANCE_CACHE_SIZE_MB=50
export RAY_OBJECT_STORE_MEMORY=1073741824
```

## Rollback Plan

If you encounter issues with the migration:

1. **Backup Current State**: Save your current configuration and data
2. **Downgrade Dependencies**: Use previous versions if needed
3. **Gradual Migration**: Update components one at a time
4. **Test Thoroughly**: Use the comprehensive test suite

## Support and Resources

### Documentation
- [README.md](README.md) - Updated user documentation
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Technical overview
- [design.md](design.md) - Architecture and design details
- [SCRIPTS_README.md](SCRIPTS_README.md) - Script documentation

### Testing
- Run `pytest tests/` to verify all functionality
- Use `pytest tests/ --cov=.` for coverage analysis
- Check `pytest tests/ -k "integration"` for integration tests

### Monitoring
- Monitor system health with the new monitoring system
- Check logs for any migration-related errors
- Use the Streamlit dashboard for visual monitoring

## Modern Deployment Migration Scenarios

### Kubernetes Deployment Migration

#### Migration from Docker Compose to Kubernetes

**Scenario**: Migrate from local Docker Compose deployment to production Kubernetes cluster.

**Prerequisites**:
- Kubernetes cluster (v1.24+)
- kubectl configured
- Docker registry access
- Secrets management (Sealed Secrets or External Secrets Operator)

**Migration Steps**:

1. **Pre-Migration Assessment**
```bash
# Check current Docker Compose setup
docker-compose ps
docker stats

# Assess resource requirements
kubectl cluster-info
kubectl get nodes
kubectl describe nodes | grep -A 10 "Capacity"
```

2. **Create Kubernetes Namespace**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: simulation-production
  labels:
    name: simulation-production
    environment: production
```

3. **Migrate Configuration to Kubernetes Secrets**
```bash
# Create secrets from existing environment variables
kubectl create secret generic simulation-secrets \
  --from-env-file=.env.production \
  --namespace=simulation-production

# Or use individual secrets for better security
kubectl create secret generic db-secret \
  --from-literal=username=simulation_user \
  --from-literal=password=$(openssl rand -base64 32) \
  --namespace=simulation-production
```

4. **Deploy PostgreSQL Database**
```yaml
# k8s/postgresql.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: simulation-postgres
  namespace: simulation-production
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 50Gi
```

5. **Deploy Ray Cluster**
```yaml
# k8s/ray-cluster.yaml
apiVersion: ray.io/v1alpha1
kind: RayCluster
metadata:
  name: simulation-ray-cluster
  namespace: simulation-production
spec:
  rayVersion: '2.45.0'
  headGroupSpec:
    replicas: 1
    serviceType: ClusterIP
    rayStartParams:
      dashboard-host: '0.0.0.0'
      block: 'true'
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:2.45.0-py311
          ports:
          - containerPort: 6379
          - containerPort: 8265
          - containerPort: 10001
          resources:
            requests:
              cpu: "2"
              memory: "4Gi"
            limits:
              cpu: "4"
              memory: "8Gi"
  workerGroupSpecs:
  - replicas: 3
    minReplicas: 1
    maxReplicas: 10
    groupName: worker-group
    rayStartParams:
      block: 'true'
    template:
      spec:
        containers:
        - name: ray-worker
          image: rayproject/ray:2.45.0-py311
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
            limits:
              cpu: "2"
              memory: "4Gi"
```

6. **Deploy Application with Horizontal Pod Autoscaler**
```yaml
# k8s/application.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simulation-app
  namespace: simulation-production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: simulation
  template:
    metadata:
      labels:
        app: simulation
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8501"
    spec:
      containers:
      - name: simulation-app
        image: simulation-app:2.45.0
        ports:
        - containerPort: 8501
        - containerPort: 8521
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DB_HOST
          value: "simulation-postgres"
        - name: RAY_HEAD_ADDRESS
          value: "simulation-ray-cluster-head-svc:10001"
        livenessProbe:
          httpGet:
            path: /health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8501
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: simulation-hpa
  namespace: simulation-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: simulation-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

7. **Migration Validation**
```bash
# Verify deployment
kubectl get all -n simulation-production
kubectl get hpa -n simulation-production

# Check application health
kubectl port-forward svc/simulation-app 8501:8501 -n simulation-production
curl http://localhost:8501/health

# Verify Ray cluster
kubectl exec -it deployment/simulation-ray-cluster-head -n simulation-production -- ray status
```

**Rollback Procedure**:
```bash
# Scale down new deployment
kubectl scale deployment simulation-app --replicas=0 -n simulation-production

# Restore from backup if needed
kubectl apply -f k8s/docker-compose-backup.yaml -n simulation-production

# Verify rollback
kubectl get pods -n simulation-production
```

### Enhanced Docker Compose Migration

#### Multi-Service Docker Compose Setup

**Scenario**: Migrate from single-container deployment to multi-service Docker Compose orchestration.

**Migration Steps**:

1. **Create Enhanced docker-compose.yml**
```yaml
# docker-compose.migrated.yml
version: '3.8'

services:
  # Main application service
  simulation-app:
    build:
      context: .
      target: production
    container_name: simulation-app
    restart: unless-stopped
    ports:
      - "8501:8501"  # Streamlit UI
      - "8521:8521"  # Mesa visualization
    environment:
      - ENVIRONMENT=production
      - LOGGING_LEVEL=WARNING
      - RAY_ADDRESS=ray://ray-head:10001
    depends_on:
      - ray-head
      - postgres
    networks:
      - simulation-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Ray cluster for distributed computing
  ray-head:
    image: rayproject/ray:2.45.0-py311
    container_name: ray-head
    command: ray start --head --port=6379 --dashboard-host=0.0.0.0
    ports:
      - "6379:6379"
      - "8265:8265"
      - "10001:10001"
    volumes:
      - ray_data:/tmp/ray
    networks:
      - simulation-network
    healthcheck:
      test: ["CMD", "ray", "status"]
      interval: 30s
      timeout: 10s
      retries: 3

  ray-worker:
    image: rayproject/ray:2.45.0-py311
    container_name: ray-worker
    command: ray start --address=ray-head:6379 --num-cpus=2
    depends_on:
      - ray-head
    volumes:
      - ray_data:/tmp/ray
    networks:
      - simulation-network
    deploy:
      replicas: 2

  # PostgreSQL database
  postgres:
    image: postgres:15-alpine
    container_name: simulation-db
    environment:
      POSTGRES_DB: simulation_prod
      POSTGRES_USER: simulation_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - simulation-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U simulation_user -d simulation_prod"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis for caching and session storage
  redis:
    image: redis:7-alpine
    container_name: simulation-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-dev_redis}
    secrets:
      - redis_password
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - simulation-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s

  # Prometheus for monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: simulation-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - simulation-network

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    container_name: simulation-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - simulation-network

secrets:
  db_password:
    file: ./secrets/db_password.txt
  redis_password:
    file: ./secrets/redis_password.txt

volumes:
  postgres_data:
  redis_data:
  ray_data:
  prometheus_data:
  grafana_data:

networks:
  simulation-network:
    driver: bridge
```

2. **Migrate Data and Configuration**
```bash
# Backup existing data
cp data/databases/ledger.db backup/
cp config/config.yaml backup/

# Update configuration for multi-service setup
cat > config/production.yaml << EOF
environment: production
app_name: "decentralized-ai-simulation"
version: "2.45.0"

database:
  type: "postgresql"
  host: "postgres"
  port: 5432
  database: "simulation_prod"
  username: "simulation_user"
  password: "/run/secrets/db_password"
  ssl_mode: "disable"

ray:
  enabled: true
  address: "ray://ray-head:10001"
  object_store_memory: 2147483648
  num_cpus: 4

monitoring:
  enable_prometheus: true
  prometheus_gateway: "http://prometheus:9090"
EOF
```

3. **Deploy with Migration**
```bash
# Stop existing deployment
docker-compose down

# Deploy new multi-service setup
docker-compose -f docker-compose.migrated.yml up -d

# Wait for services to be ready
docker-compose -f docker-compose.migrated.yml ps

# Run database migration script
docker-compose -f docker-compose.migrated.yml exec -T postgres psql -U simulation_user -d simulation_prod < scripts/migrate_to_postgres.sql
```

## Enhanced Database Migration Procedures

### SQLite to PostgreSQL Migration

#### Migration Strategy

**Scenario**: Migrate from SQLite to PostgreSQL for production scalability.

**Pre-Migration Steps**:

1. **Assess Database Size and Complexity**
```bash
# Analyze current SQLite database
sqlite3 data/databases/ledger.db ".schema"
sqlite3 data/databases/ledger.db "SELECT COUNT(*) FROM traffic_data;"
sqlite3 data/databases/ledger.db "SELECT COUNT(*) FROM anomaly_data;"
```

2. **Create PostgreSQL Migration Schema**
```sql
-- scripts/migrate_to_postgres.sql
-- Create tables matching SQLite schema
CREATE TABLE IF NOT EXISTS traffic_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    source_ip VARCHAR(45) NOT NULL,
    destination_ip VARCHAR(45) NOT NULL,
    bytes_transferred BIGINT NOT NULL,
    protocol VARCHAR(10) NOT NULL,
    port INTEGER NOT NULL,
    payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_traffic_data_timestamp ON traffic_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_data_source_ip ON traffic_data(source_ip);
CREATE INDEX IF NOT EXISTS idx_traffic_data_destination_ip ON traffic_data(destination_ip);

-- Create anomaly_data table
CREATE TABLE IF NOT EXISTS anomaly_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    source_ip VARCHAR(45) NOT NULL,
    anomaly_score FLOAT NOT NULL,
    threat_type VARCHAR(50),
    severity VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_anomaly_data_timestamp ON anomaly_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomaly_data_score ON anomaly_data(anomaly_score);
```

3. **Export Data from SQLite**
```bash
# Export data with proper formatting
sqlite3 data/databases/ledger.db << EOF
.mode csv
.headers on
.output traffic_data.csv
SELECT id, timestamp, source_ip, destination_ip, bytes_transferred, protocol, port, payload FROM traffic_data;
EOF

sqlite3 data/databases/ledger.db << EOF
.mode csv
.headers on
.output anomaly_data.csv
SELECT id, timestamp, source_ip, anomaly_score, threat_type, severity, description FROM anomaly_data;
EOF
```

4. **Import Data to PostgreSQL**
```bash
# Import traffic data
docker-compose exec -T postgres psql -U simulation_user -d simulation_prod -c "
\\copy traffic_data(id, timestamp, source_ip, destination_ip, bytes_transferred, protocol, port, payload) FROM 'traffic_data.csv' WITH CSV HEADER;
"

# Import anomaly data
docker-compose exec -T postgres psql -U simulation_user -d simulation_prod -c "
\\copy anomaly_data(id, timestamp, source_ip, anomaly_score, threat_type, severity, description) FROM 'anomaly_data.csv' WITH CSV HEADER;
"
```

5. **Verify Migration**
```sql
-- Verify data integrity
SELECT COUNT(*) as traffic_records FROM traffic_data;
SELECT COUNT(*) as anomaly_records FROM anomaly_data;

-- Check for data consistency
SELECT COUNT(*) FROM traffic_data WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours';
```

**Rollback Procedure**:
```bash
# If PostgreSQL migration fails, rollback to SQLite
docker-compose down postgres
cp backup/ledger.db data/databases/ledger.db
docker-compose up -d simulation-app
```

### Database Performance Migration

#### Connection Pool Optimization

**Migration Steps**:

1. **Update Database Configuration**
```yaml
# Enhanced database configuration
database:
  type: "postgresql"
  host: "${DB_HOST:-localhost}"
  port: 5432
  database: "simulation_prod"
  username: "${DB_USER}"
  password: "${DB_PASSWORD}"
  ssl_mode: "require"

  # Enhanced connection pooling
  connection_pool:
    min_size: 5
    max_size: 20
    max_overflow: 10
    timeout: 30.0
    retry_attempts: 3
    retry_delay: 1.0

  # Performance settings
  query_timeout: 60
  enable_statement_cache: true
  enable_connection_health_checks: true
```

2. **Migrate Connection Pool Settings**
```python
# Update database connection configuration
from config_loader import get_config

db_config = get_config('database')
pool_config = db_config.get('connection_pool', {})

# Apply new pooling configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_config['database'],
        'USER': db_config['username'],
        'PASSWORD': db_config['password'],
        'HOST': db_config['host'],
        'PORT': db_config['port'],
        'OPTIONS': {
            'sslmode': db_config.get('ssl_mode', 'require'),
        },
        'CONN_MAX_AGE': pool_config.get('max_age', 0),
        'CONN_HEALTH_CHECKS': pool_config.get('enable_connection_health_checks', True),
    }
}
```

## Configuration Migration Procedures

### YAML Structure Migration

#### Enhanced Configuration Migration

**Migration Steps**:

1. **Backup Existing Configuration**
```bash
# Backup current configuration
cp config/config.yaml backup/config.yaml.backup
cp .env backup/.env.backup.$(date +%Y%m%d_%H%M%S)
```

2. **Migrate to New YAML Structure**
```bash
# Create new configuration structure
cat > config/config.yaml << EOF
# Enhanced Configuration Structure (October 2025)
environment: development
app_name: "decentralized-ai-simulation"
version: "2.45.0"

# API Configuration
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  request_timeout: 30
  max_concurrent_requests: 100
  cors_origins: ["*"]

# Enhanced Database Configuration
database:
  type: "sqlite"  # sqlite, postgresql, mysql
  path: "data/databases/ledger.db"
  connection_pool:
    min_size: 5
    max_size: 20
    max_overflow: 10
  timeout: 30.0
  retry_attempts: 3
  retry_delay: 1.0

# Ray Configuration
ray:
  enabled: true
  address: "auto"
  object_store_memory: 1073741824  # 1GB
  num_cpus: null  # Auto-detect
  num_gpus: 0
  dashboard_host: "127.0.0.1"
  dashboard_port: 8265

# Mesa Configuration
mesa:
  enabled: true
  visualization: true
  server_port: 8521
  max_steps: 1000
  concurrent_simulations: 3

# Streamlit Configuration
streamlit:
  enabled: true
  server_port: 8501
  server_address: "0.0.0.0"
  enable_cors: false
  enable_xsrf_protection: true
  max_message_size: 200

# Enhanced Logging
logging:
  level: "DEBUG"
  format: "json"
  enable_console: true
  enable_file: true
  file_path: "logs/simulation.log"
  max_file_size_mb: 100
  backup_count: 5

# Monitoring Configuration
monitoring:
  enable_prometheus: true
  prometheus_gateway: "http://localhost:9090"
  health_check_interval: 30
  enable_distributed_tracing: true

# Performance Configuration
performance:
  enable_caching: true
  cache_size_mb: 100
  max_workers: 4
  memory_limit_mb: 1024
  enable_async_processing: false

# Security Configuration
security:
  enable_rate_limiting: true
  rate_limit_requests_per_minute: 1000
  enable_input_validation: true
  enable_https_redirect: true
  allowed_hosts: []
  max_request_size_mb: 10

# Development Configuration
development:
  debug_mode: true
  enable_profiling: true
  show_tracebacks: true
  auto_reload: true
  hot_reload: true
EOF
```

3. **Migrate Environment Variables**
```bash
# Create new .env file with enhanced variables
cat > .env << EOF
# Application Configuration
ENVIRONMENT=development
APP_VERSION=2.45.0
LOG_LEVEL=DEBUG

# Database Configuration
DB_TYPE=sqlite
DB_PATH=data/databases/ledger.db
DB_CONNECTION_POOL_MIN=5
DB_CONNECTION_POOL_MAX=20

# Ray Configuration
RAY_ENABLED=true
RAY_OBJECT_STORE_MEMORY=1073741824
RAY_DASHBOARD_PORT=8265

# Monitoring
MONITORING_PROMETHEUS_ENABLED=true
MONITORING_HEALTH_CHECK_INTERVAL=30

# Performance
PERFORMANCE_CACHE_ENABLED=true
PERFORMANCE_CACHE_SIZE_MB=100
PERFORMANCE_MAX_WORKERS=4

# Security
SECURITY_RATE_LIMIT_RPM=1000
SECURITY_ENABLE_VALIDATION=true
EOF
```

4. **Validate Configuration Migration**
```python
# Validate new configuration structure
from config_loader import get_config, validate_config

try:
    config = get_config()
    validate_config(config)
    print("Configuration migration successful")
except Exception as e:
    print(f"Configuration migration failed: {e}")
    # Rollback to backup configuration
    shutil.copy('backup/config.yaml.backup', 'config/config.yaml')
```

## Comprehensive Rollback Procedures

### Automated Rollback Scripts

#### Rollback Script for Failed Migrations

**Create Rollback Script**:
```bash
#!/bin/bash
# scripts/rollback_migration.sh
# Automated rollback script for failed migrations

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_TYPE="${1:-all}"
BACKUP_DIR="${BACKUP_DIR:-backup/$(date +%Y%m%d_%H%M%S)}"

log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%Z')] $*"
}

error() {
    log "ERROR: $*" >&2
    exit 1
}

success() {
    log "SUCCESS: $*"
}

# Create backup before rollback
create_backup() {
    log "Creating backup before rollback..."
    mkdir -p "$BACKUP_DIR"

    # Backup current state
    cp -r config/ "$BACKUP_DIR/config/"
    cp -r data/ "$BACKUP_DIR/data/"
    cp .env "$BACKUP_DIR/.env.$(date +%Y%m%d_%H%M%S)"

    success "Backup created at $BACKUP_DIR"
}

# Rollback configuration
rollback_configuration() {
    log "Rolling back configuration..."

    if [ -d "backup/config" ]; then
        cp -r backup/config/* config/
        success "Configuration rolled back"
    else
        error "No configuration backup found"
    fi
}

# Rollback database
rollback_database() {
    log "Rolling back database..."

    # Stop application
    docker-compose down

    # Restore database from backup
    if [ -f "backup/data/databases/ledger.db" ]; then
        cp backup/data/databases/ledger.db data/databases/ledger.db
        success "Database rolled back"
    else
        error "No database backup found"
    fi

    # Restart application
    docker-compose up -d
}

# Rollback deployment
rollback_deployment() {
    log "Rolling back deployment..."

    case "$MIGRATION_TYPE" in
        "kubernetes")
            kubectl rollout undo deployment/simulation-app -n simulation-production
            kubectl rollout status deployment/simulation-app -n simulation-production
            ;;
        "docker-compose")
            docker-compose down
            docker-compose -f docker-compose.backup.yml up -d
            ;;
        *)
            error "Unknown deployment type: $MIGRATION_TYPE"
            ;;
    esac

    success "Deployment rolled back"
}

# Main rollback function
main() {
    log "Starting rollback process for migration type: $MIGRATION_TYPE"

    create_backup

    case "$MIGRATION_TYPE" in
        "configuration")
            rollback_configuration
            ;;
        "database")
            rollback_database
            ;;
        "deployment")
            rollback_deployment
            ;;
        "all")
            rollback_configuration
            rollback_database
            rollback_deployment
            ;;
        *)
            error "Unknown migration type: $MIGRATION_TYPE"
            ;;
    esac

    success "Rollback completed successfully"
    log "Backup available at: $BACKUP_DIR"
}

# Execute main function
main "$@"
```

### Migration-Specific Rollback Procedures

#### Kubernetes Migration Rollback

**Immediate Rollback**:
```bash
# Scale down new deployment
kubectl scale deployment simulation-app --replicas=0 -n simulation-production

# Restore previous deployment
kubectl apply -f k8s/previous-deployment.yaml -n simulation-production

# Verify rollback
kubectl get pods -n simulation-production
kubectl get services -n simulation-production
```

**Gradual Rollback**:
```bash
# Rollback one replica at a time
kubectl patch deployment simulation-app -n simulation-production -p '{"spec":{"replicas":2}}'
sleep 60
kubectl patch deployment simulation-app -n simulation-production -p '{"spec":{"replicas":1}}'
sleep 60
kubectl patch deployment simulation-app -n simulation-production -p '{"spec":{"replicas":0}}'

# Deploy previous version
kubectl apply -f k8s/previous-version.yaml -n simulation-production
```

#### Database Migration Rollback

**SQLite Rollback**:
```bash
# Stop PostgreSQL containers
docker-compose down postgres

# Restore SQLite database
cp backup/ledger.db data/databases/ledger.db

# Update configuration back to SQLite
sed -i 's/type: "postgresql"/type: "sqlite"/' config/config.yaml
sed -i 's/host: "postgres"/path: "data\/databases\/ledger.db"/' config/config.yaml

# Restart application
docker-compose up -d simulation-app
```

**PostgreSQL Rollback**:
```bash
# Drop migrated data
docker-compose exec postgres psql -U simulation_user -d simulation_prod -c "
DROP TABLE IF EXISTS traffic_data CASCADE;
DROP TABLE IF EXISTS anomaly_data CASCADE;
"

# Restore from PostgreSQL backup
docker-compose exec postgres psql -U simulation_user -d simulation_prod < backup/postgres_backup.sql

# Verify data integrity
docker-compose exec postgres psql -U simulation_user -d simulation_prod -c "
SELECT COUNT(*) FROM traffic_data;
SELECT COUNT(*) FROM anomaly_data;
"
```

## Automated Migration Scripts

### Migration Automation Framework

#### Automated Migration Script

**Create Migration Script**:
```bash
#!/bin/bash
# scripts/automated_migration.sh
# Automated migration script with validation and rollback

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_TARGET="${1:-kubernetes}"
DRY_RUN="${DRY_RUN:-false}"

log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%Z')] $*"
}

success() {
    log "SUCCESS: $*"
}

# Pre-migration validation
validate_environment() {
    log "Validating environment for migration..."

    # Check required tools
    local required_tools=("docker" "kubectl" "python3")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            error "Required tool not found: $tool"
        fi
    done

    # Check current deployment status
    if kubectl get namespace simulation-production >/dev/null 2>&1; then
        log "Found existing Kubernetes namespace"
    fi

    success "Environment validation passed"
}

# Backup current state
create_migration_backup() {
    log "Creating comprehensive backup..."

    local backup_dir="backup/migration_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # Backup configuration and data
    tar -czf "$backup_dir/config_data.tar.gz" config/ data/ .env

    # Backup current deployment state
    if kubectl get namespace simulation-production >/dev/null 2>&1; then
        kubectl get all,secrets,configmaps,ingress -n simulation-production -o yaml > "$backup_dir/k8s_resources.yaml"
    fi

    success "Backup created at $backup_dir"
}

# Migrate to Kubernetes
migrate_to_kubernetes() {
    log "Starting Kubernetes migration..."

    # Create namespace
    kubectl apply -f k8s/namespace.yaml

    # Create secrets
    kubectl apply -f k8s/secrets.yaml -n simulation-production

    # Deploy in order
    kubectl apply -f k8s/postgresql.yaml -n simulation-production
    kubectl apply -f k8s/ray-cluster.yaml -n simulation-production
    kubectl apply -f k8s/application.yaml -n simulation-production

    # Wait for deployment
    kubectl wait --for=condition=available --timeout=300s deployment/simulation-app -n simulation-production

    success "Kubernetes migration completed"
}

# Migrate to Docker Compose
migrate_to_docker_compose() {
    log "Starting Docker Compose migration..."

    # Stop existing deployment
    docker-compose down

    # Update configuration
    cp config/production.yaml config/config.yaml

    # Start new deployment
    docker-compose -f docker-compose.migrated.yml up -d

    # Wait for services
    docker-compose -f docker-compose.migrated.yml ps

    success "Docker Compose migration completed"
}

# Post-migration validation
validate_migration() {
    log "Validating migration..."

    # Health checks
    if curl -f http://localhost:8501/health >/dev/null 2>&1; then
        success "Application health check passed"
    else
        error "Application health check failed"
    fi

    # Database connectivity
    if kubectl exec -n simulation-production deployment/simulation-postgres -- pg_isready >/dev/null 2>&1; then
        success "Database connectivity check passed"
    else
        error "Database connectivity check failed"
    fi

    # Ray cluster status
    if kubectl exec -n simulation-production deployment/simulation-ray-cluster-head -- ray status >/dev/null 2>&1; then
        success "Ray cluster status check passed"
    else
        error "Ray cluster status check failed"
    fi

    success "Migration validation completed"
}

# Main migration function
main() {
    log "Starting automated migration to $MIGRATION_TARGET"

    if [ "$DRY_RUN" = "true" ]; then
        log "DRY RUN: No actual changes will be made"
    fi

    validate_environment
    create_migration_backup

    case "$MIGRATION_TARGET" in
        "kubernetes")
            migrate_to_kubernetes
            ;;
        "docker-compose")
            migrate_to_docker_compose
            ;;
        *)
            error "Unknown migration target: $MIGRATION_TARGET"
            ;;
    esac

    validate_migration

    success "Migration completed successfully!"
    log "Run 'scripts/rollback_migration.sh $MIGRATION_TARGET' if rollback is needed"
}

# Execute main function
main "$@"
```

### Migration Validation Scripts

#### Post-Migration Validation

**Create Validation Script**:
```python
#!/usr/bin/env python3
# scripts/validate_migration.py
# Comprehensive post-migration validation

import requests
import psycopg2
import sqlite3
import subprocess
import time
import sys
from datetime import datetime, UTC
from config_loader import get_config

class MigrationValidator:
    """Comprehensive migration validation framework."""

    def __init__(self):
        self.config = get_config()
        self.issues = []
        self.successes = []

    def log_success(self, message: str):
        """Log successful validation."""
        print(f"✅ {message}")
        self.successes.append(message)

    def log_issue(self, message: str, severity: str = "ERROR"):
        """Log validation issue."""
        print(f"❌ {severity}: {message}")
        self.issues.append({"message": message, "severity": severity})

    def validate_application_health(self) -> bool:
        """Validate application health endpoints."""
        try:
            response = requests.get("http://localhost:8501/health", timeout=10)
            if response.status_code == 200:
                self.log_success("Application health endpoint responding")
                return True
            else:
                self.log_issue(f"Application health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_issue(f"Application health check error: {e}")
            return False

    def validate_database_connectivity(self) -> bool:
        """Validate database connectivity and data integrity."""
        db_config = self.config.get('database', {})

        try:
            if db_config.get('type') == 'postgresql':
                return self._validate_postgresql(db_config)
            elif db_config.get('type') == 'sqlite':
                return self._validate_sqlite(db_config)
            else:
                self.log_issue(f"Unknown database type: {db_config.get('type')}")
                return False
        except Exception as e:
            self.log_issue(f"Database validation error: {e}")
            return False

    def _validate_postgresql(self, db_config: dict) -> bool:
        """Validate PostgreSQL connectivity."""
        try:
            conn = psycopg2.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                database=db_config.get('database', 'simulation_prod'),
                user=db_config.get('username', 'simulation_user'),
                password=db_config.get('password', ''),
                connect_timeout=10
            )

            # Test basic queries
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM traffic_data LIMIT 1;")
                count = cursor.fetchone()[0]

            conn.close()
            self.log_success(f"PostgreSQL connectivity validated (found {count} traffic records)")
            return True

        except Exception as e:
            self.log_issue(f"PostgreSQL validation failed: {e}")
            return False

    def _validate_sqlite(self, db_config: dict) -> bool:
        """Validate SQLite database."""
        try:
            db_path = db_config.get('path', 'data/databases/ledger.db')
            conn = sqlite3.connect(db_path)

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM traffic_data;")
            count = cursor.fetchone()[0]

            conn.close()
            self.log_success(f"SQLite database validated (found {count} traffic records)")
            return True

        except Exception as e:
            self.log_issue(f"SQLite validation failed: {e}")
            return False

    def validate_ray_cluster(self) -> bool:
        """Validate Ray cluster functionality."""
        try:
            # Check if Ray is initialized
            result = subprocess.run(['ray', 'status'], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.log_success("Ray cluster status validated")
                return True
            else:
                self.log_issue("Ray cluster status check failed")
                return False

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.log_issue(f"Ray cluster validation failed: {e}")
            return False

    def validate_configuration_loading(self) -> bool:
        """Validate configuration loading and structure."""
        try:
            # Test configuration access
            db_type = get_config('database.type', 'sqlite')
            ray_enabled = get_config('ray.enabled', True)
            api_port = get_config('api.port', 8000)

            self.log_success(f"Configuration loaded successfully (DB: {db_type}, Ray: {ray_enabled}, API: {api_port})")
            return True

        except Exception as e:
            self.log_issue(f"Configuration validation failed: {e}")
            return False

    def validate_performance_metrics(self) -> bool:
        """Validate performance metrics collection."""
        try:
            # Check if Prometheus metrics are available
            response = requests.get("http://localhost:9090/-/healthy", timeout=5)

            if response.status_code == 200:
                self.log_success("Performance metrics collection validated")
                return True
            else:
                self.log_issue("Performance metrics not available")
                return False

        except Exception:
            self.log_issue("Performance metrics validation failed")
            return False

    def generate_validation_report(self) -> dict:
        """Generate comprehensive validation report."""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "validation_status": "PASSED" if not self.issues else "FAILED",
            "total_checks": len(self.successes) + len(self.issues),
            "successful_checks": len(self.successes),
            "failed_checks": len(self.issues),
            "successes": self.successes,
            "issues": self.issues
        }

    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting comprehensive migration validation...\n")

        # Run all validation checks
        checks = [
            self.validate_configuration_loading,
            self.validate_application_health,
            self.validate_database_connectivity,
            self.validate_ray_cluster,
            self.validate_performance_metrics
        ]

        results = []
        for check in checks:
            results.append(check())

        # Generate report
        report = self.generate_validation_report()

        print(f"\n📊 Validation Report ({report['timestamp']})")
        print(f"Status: {report['validation_status']}")
        print(f"Checks: {report['successful_checks']}/{report['total_checks']} passed")

        if report['issues']:
            print("\n❌ Issues Found:")
            for issue in report['issues']:
                print(f"  - {issue['severity']}: {issue['message']}")

        return len(self.issues) == 0

def main():
    """Main validation function."""
    validator = MigrationValidator()
    success = validator.run_all_validations()

    if not success:
        print("\n❌ Migration validation failed!")
        sys.exit(1)
    else:
        print("\n✅ Migration validation successful!")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

## Enhanced Troubleshooting Section

### Migration-Specific Troubleshooting

#### Kubernetes Migration Issues

**Issue**: Pods stuck in Pending state
```bash
# Diagnose pending pods
kubectl describe pod <pod-name> -n simulation-production
kubectl get events -n simulation-production

# Common solutions:
# 1. Check resource quotas
kubectl describe resourcequota -n simulation-production

# 2. Check node resources
kubectl describe nodes | grep -A 5 "Capacity"

# 3. Check persistent volume claims
kubectl get pvc -n simulation-production
```

**Issue**: Services not accessible
```bash
# Check service endpoints
kubectl get endpoints -n simulation-production

# Check service configuration
kubectl describe service simulation-app -n simulation-production

# Test service connectivity
kubectl run test-pod --image=curlimages/curl --rm -i --tty -- bash
curl http://simulation-app:8501/health
```

**Issue**: Ray cluster connection failures
```bash
# Check Ray cluster status
kubectl exec -it deployment/simulation-ray-cluster-head -n simulation-production -- ray status

# Check Ray dashboard
kubectl port-forward svc/simulation-ray-cluster-dashboard 8265:8265 -n simulation-production
# Visit http://localhost:8265

# Common fixes:
# 1. Restart Ray cluster
kubectl rollout restart deployment/simulation-ray-cluster -n simulation-production

# 2. Check Redis connectivity
kubectl exec -it deployment/simulation-ray-cluster-head -n simulation-production -- redis-cli ping
```

#### Database Migration Issues

**Issue**: PostgreSQL connection failures
```bash
# Test database connectivity
kubectl exec -it deployment/simulation-postgres -n simulation-production -- pg_isready -U simulation_user

# Check database logs
kubectl logs deployment/simulation-postgres -n simulation-production

# Common solutions:
# 1. Verify secrets
kubectl get secret db-secret -n simulation-production -o yaml

# 2. Check database initialization
kubectl exec -it deployment/simulation-postgres -n simulation-production -- psql -U simulation_user -d simulation_prod -c "\l"
```

**Issue**: Data migration failures
```bash
# Check data integrity
kubectl exec -it deployment/simulation-postgres -n simulation-production -- psql -U simulation_user -d simulation_prod -c "
SELECT COUNT(*) FROM traffic_data;
SELECT COUNT(*) FROM anomaly_data;
"

# Verify table structure
kubectl exec -it deployment/simulation-postgres -n simulation-production -- psql -U simulation_user -d simulation_prod -c "\d traffic_data"
```

#### Configuration Migration Issues

**Issue**: Configuration validation failures
```python
# Test configuration loading
python3 -c "
from config_loader import get_config, validate_config
try:
    config = get_config()
    validate_config(config)
    print('Configuration valid')
except Exception as e:
    print(f'Configuration error: {e}')
    import traceback
    traceback.print_exc()
"
```

**Issue**: Environment variable conflicts
```bash
# Check for conflicting environment variables
env | grep -E "(DB_|RAY_|SIMULATION_)" | sort

# Validate environment variable precedence
python3 -c "
import os
from config_loader import get_config

# Check environment variable loading
db_host = get_config('database.host')
env_db_host = os.getenv('DB_HOST')
print(f'Config DB host: {db_host}')
print(f'Env DB host: {env_db_host}')
"
```

### Performance Troubleshooting

#### Memory Usage Issues

**High Memory Consumption**:
```bash
# Check application memory usage
kubectl top pods -n simulation-production

# Analyze memory patterns
kubectl logs deployment/simulation-app -n simulation-production | grep -i memory

# Solutions:
# 1. Adjust resource limits
kubectl patch deployment simulation-app -n simulation-production -p '{"spec":{"template":{"spec":{"containers":[{"name":"simulation-app","resources":{"limits":{"memory":"4Gi"}}}]}}}}}'

# 2. Enable memory optimization
export PERFORMANCE_CACHE_SIZE_MB=50
export RAY_OBJECT_STORE_MEMORY=536870912
```

#### CPU Performance Issues

**High CPU Usage**:
```bash
# Monitor CPU usage
kubectl top nodes

# Check for CPU-intensive operations
kubectl logs deployment/simulation-app -n simulation-production --previous | grep -i "cpu\|performance"

# Solutions:
# 1. Scale horizontally
kubectl scale deployment simulation-app --replicas=5 -n simulation-production

# 2. Optimize Ray configuration
export RAY_NUM_CPUS=2
export PERFORMANCE_MAX_WORKERS=2
```

## Next Steps

After successful migration:

1. **Update Scripts**: Modify any custom scripts to use new configuration options
2. **Performance Tuning**: Adjust performance settings based on your hardware
3. **Security Review**: Review and customize security settings
4. **Backup Strategy**: Implement backup for the new database configuration
5. **Training**: Train team members on new features and configuration options
6. **Monitoring Setup**: Configure comprehensive monitoring and alerting
7. **Documentation Update**: Update internal documentation with migration learnings

## Version Compatibility

The modernized system maintains backward compatibility for:
- Basic simulation functionality
- Core agent behaviors
- Database operations (both SQLite and PostgreSQL)
- Configuration access patterns
- Existing API endpoints

New features are opt-in and don't affect existing deployments unless explicitly enabled.

## Migration Support and Resources

### Documentation
- [README.md](README.md) - Updated user documentation
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Technical overview
- [design.md](design.md) - Architecture and design details
- [BEST_PRACTICES.md](BEST_PRACTICES.md) - Enhanced best practices guide
- [SCRIPTS_README.md](SCRIPTS_README.md) - Script documentation

### Testing
- Run `pytest tests/` to verify all functionality
- Use `pytest tests/ --cov=.` for coverage analysis
- Check `pytest tests/ -k "integration"` for integration tests
- Run `python scripts/validate_migration.py` for migration validation

### Monitoring
- Monitor system health with the new monitoring system
- Check logs for any migration-related errors
- Use the Streamlit dashboard for visual monitoring
- Set up alerts for critical migration issues

### Support Channels
- GitHub Issues for bug reports and feature requests
- Documentation updates for community contributions
- Migration validation scripts for self-service troubleshooting