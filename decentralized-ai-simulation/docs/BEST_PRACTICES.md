# Best Practices Guide (October 2025)

## Overview

This document outlines best practices for developing, deploying, and maintaining the modernized Decentralized AI Simulation platform. Following these practices ensures optimal performance, security, maintainability, and scalability.

**Technology Stack Alignment:**
- **Python 3.11+** - Utilize modern Python features including enhanced type hints, structural pattern matching, and improved async support
- **Mesa 3.3.0** - Leverage latest agent-based modeling framework capabilities for complex system simulations
- **Ray 2.45.0** - Implement distributed computing patterns with current Ray ecosystem best practices
- **Streamlit 1.39.0** - Build modern, responsive user interfaces with latest Streamlit features

**Related Documentation:**
- See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for system architecture details
- See [design.md](design.md) for technical design specifications
- See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for upgrade procedures

## Development Best Practices

### Code Organization and Structure

#### Project Structure
```
decentralized-ai-simulation/
├── src/                    # Source code (if using src layout)
│   ├── core/              # Core business logic
│   ├── models/            # Data models and schemas
│   ├── utils/             # Utility functions
│   ├── api/               # API endpoints
│   └── config/            # Configuration management
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test data and fixtures
├── docs/                  # Documentation
├── scripts/              # Build and deployment scripts
├── config/               # Configuration files
└── requirements/         # Dependency files
```

#### Module Organization
```python
# Good: Single responsibility modules
# config_loader.py - Configuration management only
# logging_setup.py - Logging setup only
# monitoring.py - Monitoring and health checks only

# Avoid: Monolithic modules with mixed responsibilities
```

### Version Control Practices

#### Branching Strategy
```bash
# Feature development
git checkout -b feature/new-agent-type
git push origin feature/new-agent-type

# Bug fixes
git checkout -b bugfix/consensus-resolution
git push origin bugfix/consensus-resolution

# Release preparation
git checkout -b release/v2.45.0
git push origin release/v2.45.0
```

#### Commit Message Standards
```bash
# Good commit messages
feat: add new anomaly detection algorithm
fix: resolve database connection leak
docs: update API documentation for v2.45.0
perf: optimize signature validation by 40%
test: add integration tests for consensus mechanism
refactor: extract configuration validation logic
```

### Code Quality Standards

#### Modern Python 3.11+ Features and Type Hints
```python
from typing import Dict, List, Optional, Tuple, Union, Literal, Annotated
from datetime import datetime, UTC
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import asyncio
from contextlib import asynccontextmanager

# Modern data modeling with Pydantic (recommended for API schemas)
class TrafficRecord(BaseModel):
    """Modern data model with validation and serialization."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_ip: str = Field(pattern=r'^(\d{1,3}\.){3}\d{1,3}$')
    destination_ip: str = Field(pattern=r'^(\d{1,3}\.){3}\d{1,3}$')
    bytes_transferred: int = Field(gt=0, le=10**9)
    protocol: Literal["TCP", "UDP", "ICMP"] = "TCP"
    port: int = Field(ge=1, le=65535, default=80)

    class Config:
        validate_assignment = True
        use_enum_values = True

# Enhanced type hints with modern Python features
def detect_anomalies(
    traffic_data: List[TrafficRecord],
    threshold: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5,
    model_version: Optional[str] = None,
    use_ray: bool = True
) -> Tuple[List[TrafficRecord], Dict[str, float]]:
    """
    Detect anomalies in network traffic data using modern Python patterns.

    This function demonstrates:
    - Modern type hints with Annotated and Field constraints
    - Pydantic models for data validation
    - Structural pattern matching (Python 3.10+)
    - Async/await patterns for non-blocking operations

    Args:
        traffic_data: Validated list of traffic records
        threshold: Anomaly detection threshold with runtime validation
        model_version: Optional model version for A/B testing
        use_ray: Enable Ray distributed processing

    Returns:
        Tuple of (anomalies_list, confidence_scores) with enhanced type safety

    Raises:
        ValueError: If threshold is outside valid range or data is invalid
        RuntimeError: If model fails to load or Ray cluster unavailable
    """
    # Structural pattern matching (Python 3.10+)
    match model_version:
        case None:
            model = load_default_model()
        case str(version) if version.startswith("v2"):
            model = load_model_async(version)
        case _:
            raise ValueError(f"Unsupported model version: {model_version}")

    # Async processing with modern patterns
    if use_ray and len(traffic_data) > 1000:
        return asyncio.run(process_with_ray(traffic_data, threshold))
    else:
        return process_sequentially(traffic_data, threshold)
```

#### Modern Async/Await Patterns
```python
@dataclass
class AsyncAnomalyDetector:
    """Modern async-enabled detector with proper resource management."""
    model_version: str = "v2.45.0"
    ray_enabled: bool = True
    _ray_cluster: Optional[Any] = field(default=None, init=False)

    async def __aenter__(self):
        """Async context manager for proper resource initialization."""
        if self.ray_enabled:
            self._ray_cluster = await initialize_ray_cluster()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources asynchronously."""
        if self._ray_cluster:
            await cleanup_ray_cluster(self._ray_cluster)

    async def detect_anomalies_async(
        self,
        traffic_stream: AsyncIterator[TrafficRecord]
    ) -> AsyncIterator[TrafficRecord]:
        """Process traffic data as async stream for better performance."""
        async with self:
            batch = []
            async for record in traffic_stream:
                batch.append(record)

                if len(batch) >= 100:  # Process in batches
                    anomalies = await self._process_batch_async(batch)
                    for anomaly in anomalies:
                        yield anomaly
                    batch.clear()

            # Process remaining records
            if batch:
                anomalies = await self._process_batch_async(batch)
                for anomaly in anomalies:
                    yield anomaly

    async def _process_batch_async(self, batch: List[TrafficRecord]) -> List[TrafficRecord]:
        """Process a batch using Ray for distributed computing."""
        if self.ray_enabled and len(batch) > 50:
            # Use Ray for distributed processing
            futures = [process_record.remote(record) for record in batch]
            results = await asyncio.get_event_loop().run_in_executor(
                None, lambda: ray.get(futures)
            )
            return [r for r in results if r.is_anomaly]
        else:
            # Fallback to sequential processing
            return [r for r in batch if self._is_anomaly_sequential(r)]
```

#### Modern Error Handling and Resilience Patterns
```python
# Enhanced error handling with modern Python patterns
import asyncio
import traceback
from typing import TypeVar, Callable, Any, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import functools
from logging_setup import get_logger

logger = get_logger(__name__)

class ErrorSeverity(Enum):
    """Classify error severity for appropriate handling."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categorize errors for better handling and reporting."""
    VALIDATION = "validation"
    NETWORK = "network"
    DATABASE = "database"
    COMPUTATION = "computation"
    EXTERNAL_SERVICE = "external_service"

@dataclass
class ErrorContext:
    """Rich error context for better debugging and monitoring."""
    operation: str
    component: str
    severity: ErrorSeverity
    category: ErrorCategory
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_data: dict = None

    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}

class SimulationError(Exception):
    """Enhanced base exception with context and categorization."""
    def __init__(
        self,
        message: str,
        context: ErrorContext,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.context = context
        self.cause = cause
        self.error_id = f"ERR_{int(time.time()*1000)}"

class AnomalyDetectionError(SimulationError):
    """Specialized exception for anomaly detection failures."""
    pass

# Modern retry decorator with exponential backoff
def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for implementing retry logic with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        break

                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)

                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    await asyncio.sleep(delay)

            # All retries exhausted
            error_context = ErrorContext(
                operation=func.__name__,
                component="retry_mechanism",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.COMPUTATION
            )

            raise SimulationError(
                f"Operation failed after {max_attempts} attempts",
                error_context,
                last_exception
            )

        return async_wrapper
    return decorator

# Circuit breaker pattern for resilient systems
class CircuitBreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception

class CircuitBreaker:
    """Circuit breaker pattern for preventing cascade failures."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise SimulationError(
                    "Circuit breaker is OPEN",
                    ErrorContext(
                        operation=func.__name__,
                        component="circuit_breaker",
                        severity=ErrorSeverity.HIGH,
                        category=ErrorCategory.EXTERNAL_SERVICE
                    )
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Reset failure count on successful execution."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        """Increment failure count and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True

        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout

# Enhanced robust anomaly detection with modern patterns
@with_retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
async def robust_anomaly_detection(
    data: List[TrafficRecord],
    circuit_breaker: Optional[CircuitBreaker] = None
) -> List[TrafficRecord]:
    """
    Robust anomaly detection with modern resilience patterns.

    Features:
    - Retry logic with exponential backoff
    - Circuit breaker for external service protection
    - Comprehensive error context and logging
    - Async processing for better performance
    """
    error_context = ErrorContext(
        operation="anomaly_detection",
        component="detection_engine",
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.COMPUTATION,
        additional_data={
            "data_size": len(data),
            "timestamp": datetime.now(UTC).isoformat()
        }
    )

    try:
        # Validate input data
        if not data:
            raise ValueError("Empty dataset provided")

        # Use circuit breaker for external services if provided
        if circuit_breaker:
            result = await circuit_breaker.call(detect_anomalies, data)
        else:
            result = await detect_anomalies(data)

        logger.info(
            "Anomaly detection completed successfully",
            extra={
                "anomalies_found": len(result),
                "data_processed": len(data),
                "error_context": error_context
            }
        )

        return result

    except ValueError as e:
        logger.warning(
            f"Invalid input data: {e}",
            extra={"error_context": error_context}
        )
        raise AnomalyDetectionError(f"Invalid input: {e}", error_context)
    except Exception as e:
        logger.error(
            f"Unexpected error in anomaly detection: {e}",
            extra={
                "error_context": error_context,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        raise AnomalyDetectionError(f"Detection failed: {e}", error_context)
```

## Configuration Management Best Practices

### Modern Configuration Management with Pydantic and Environment Variables

#### Enhanced Development Configuration
```yaml
# config/development.yaml
environment: development
app_name: "decentralized-ai-simulation"
version: "2.45.0"

# Modern logging configuration with structured logging
logging:
  level: "DEBUG"
  format: "json"  # Use JSON for better log aggregation
  enable_console: true
  enable_file: true
  file_path: "logs/simulation.log"
  max_file_size_mb: 100
  backup_count: 5
  enable_remote: false
  remote_endpoint: null

# Enhanced database configuration
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
  check_same_thread: false  # SQLite specific

# Ray cluster configuration for distributed computing
ray:
  enabled: true
  address: "auto"  # auto, local, or specific cluster address
  object_store_memory: 1073741824  # 1GB
  num_cpus: null  # Auto-detect if null
  num_gpus: 0
  dashboard_host: "127.0.0.1"
  dashboard_port: 8265

# Mesa simulation configuration
mesa:
  enabled: true
  visualization: true
  server_port: 8521
  max_steps: 1000
  concurrent_simulations: 3

# Streamlit UI configuration
streamlit:
  enabled: true
  server_port: 8501
  server_address: "0.0.0.0"
  enable_cors: false
  enable_xsrf_protection: true
  max_message_size: 200
  enable_websocket_compression: false

# Development-specific settings
development:
  debug_mode: true
  enable_profiling: true
  show_tracebacks: true
  auto_reload: true
  hot_reload: true
  enable_swagger_ui: true
  enable_metrics_endpoint: true
```

#### Production Configuration
```yaml
# config/production.yaml
environment: production
app_name: "decentralized-ai-simulation"
version: "2.45.0"

# Production-optimized logging
logging:
  level: "WARNING"
  format: "json"
  enable_console: false
  enable_file: true
  file_path: "/var/log/simulation/simulation.log"
  max_file_size_mb: 500
  backup_count: 10
  enable_remote: true
  remote_endpoint: "https://logs.example.com/api/logs"
  remote_api_key: "${LOG_REMOTE_API_KEY}"

# Production-grade database configuration
database:
  type: "postgresql"
  host: "${DB_HOST}"
  port: 5432
  database: "simulation_prod"
  username: "${DB_USER}"
  password: "${DB_PASSWORD}"
  ssl_mode: "require"
  connection_pool:
    min_size: 10
    max_size: 100
    max_overflow: 20
  timeout: 60.0
  retry_attempts: 5
  retry_delay: 2.0

# Production Ray cluster configuration
ray:
  enabled: true
  address: "${RAY_HEAD_ADDRESS}"
  object_store_memory: 8589934592  # 8GB
  num_cpus: "${RAY_NUM_CPUS}"
  num_gpus: "${RAY_NUM_GPUS:-0}"
  dashboard_host: "0.0.0.0"
  dashboard_port: 8265
  redis_password: "${RAY_REDIS_PASSWORD}"

# Production Mesa configuration
mesa:
  enabled: true
  visualization: false  # Disable in production for security
  server_port: 8521
  max_steps: 10000
  concurrent_simulations: 10

# Production Streamlit configuration
streamlit:
  enabled: true
  server_port: 8501
  server_address: "0.0.0.0"
  enable_cors: true
  enable_xsrf_protection: true
  max_message_size: 200
  enable_websocket_compression: true

# Production security settings
security:
  enable_rate_limiting: true
  rate_limit_requests_per_minute: 1000
  enable_input_validation: true
  enable_https_redirect: true
  allowed_hosts:
    - "simulation.example.com"
    - "internal.example.com"
  max_request_size_mb: 10
  enable_helmet: true  # Security headers

# Production monitoring and alerting
monitoring:
  enable_prometheus: true
  prometheus_gateway: "https://prometheus.example.com"
  health_check_interval: 30
  enable_distributed_tracing: true
  tracing_endpoint: "https://jaeger.example.com/api/traces"
  alerting:
    enable_slack_notifications: true
    slack_webhook_url: "${SLACK_WEBHOOK_URL}"
    enable_pagerduty: true
    pagerduty_routing_key: "${PAGERDUTY_ROUTING_KEY}"
    critical_alerts_only: true
```

#### Modern Configuration with Pydantic Models
```python
# src/config/models.py
from typing import Optional, List, Union, Literal
from pydantic import BaseModel, Field, validator, root_validator
from pathlib import Path
import os

class LoggingConfig(BaseModel):
    """Modern logging configuration with validation."""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    format: Literal["text", "json"] = "text"
    enable_console: bool = True
    enable_file: bool = True
    file_path: str = "logs/simulation.log"
    max_file_size_mb: int = Field(gt=0, le=1000, default=100)
    backup_count: int = Field(gt=0, le=50, default=5)
    enable_remote: bool = False
    remote_endpoint: Optional[str] = None
    remote_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("LOG_REMOTE_API_KEY"))

    @validator("remote_endpoint")
    def validate_remote_endpoint(cls, v, values):
        if values.get("enable_remote") and not v:
            raise ValueError("remote_endpoint is required when enable_remote is True")
        return v

class DatabaseConfig(BaseModel):
    """Enhanced database configuration with connection pooling."""
    type: Literal["sqlite", "postgresql", "mysql"] = "sqlite"
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = "simulation"
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[Literal["disable", "require", "verify-ca", "verify-full"]] = None

    # Connection pooling settings
    connection_pool_min_size: int = Field(gt=0, default=5)
    connection_pool_max_size: int = Field(gt=0, default=20)
    connection_pool_max_overflow: int = Field(ge=0, default=10)

    timeout: float = Field(gt=0, default=30.0)
    retry_attempts: int = Field(gt=0, default=3)
    retry_delay: float = Field(gt=0, default=1.0)

    @root_validator
    def validate_connection_params(cls, values):
        db_type = values.get("type")
        if db_type in ["postgresql", "mysql"]:
            required_fields = ["host", "port", "username", "password"]
            for field in required_fields:
                if not values.get(field):
                    raise ValueError(f"{field} is required for {db_type} databases")
        return values

class RayConfig(BaseModel):
    """Ray distributed computing configuration."""
    enabled: bool = True
    address: str = "auto"
    object_store_memory: int = Field(gt=0, default=1073741824)  # 1GB
    num_cpus: Optional[int] = None
    num_gpus: Optional[int] = Field(ge=0, default=0)
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = Field(ge=1024, le=65535, default=8265)
    redis_password: Optional[str] = Field(default_factory=lambda: os.getenv("RAY_REDIS_PASSWORD"))

class MesaConfig(BaseModel):
    """Mesa agent-based modeling framework configuration."""
    enabled: bool = True
    visualization: bool = True
    server_port: int = Field(ge=1024, le=65535, default=8521)
    max_steps: int = Field(gt=0, default=1000)
    concurrent_simulations: int = Field(gt=0, default=3)

class StreamlitConfig(BaseModel):
    """Streamlit UI configuration."""
    enabled: bool = True
    server_port: int = Field(ge=1024, le=65535, default=8501)
    server_address: str = "0.0.0.0"
    enable_cors: bool = False
    enable_xsrf_protection: bool = True
    max_message_size: int = Field(gt=0, le=1000, default=200)
    enable_websocket_compression: bool = False

class SecurityConfig(BaseModel):
    """Production security configuration."""
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = Field(gt=0, default=1000)
    enable_input_validation: bool = True
    enable_https_redirect: bool = True
    allowed_hosts: List[str] = []
    max_request_size_mb: int = Field(gt=0, le=100, default=10)
    enable_helmet: bool = True

class MonitoringConfig(BaseModel):
    """Modern monitoring and alerting configuration."""
    enable_prometheus: bool = True
    prometheus_gateway: Optional[str] = None
    health_check_interval: int = Field(gt=0, default=30)
    enable_distributed_tracing: bool = True
    tracing_endpoint: Optional[str] = None

    alerting_slack_webhook_url: Optional[str] = None
    alerting_pagerduty_routing_key: Optional[str] = None
    critical_alerts_only: bool = True

class AppConfig(BaseModel):
    """Main application configuration with all components."""
    environment: Literal["development", "staging", "production"] = "development"
    app_name: str = "decentralized-ai-simulation"
    version: str = "2.45.0"

    logging: LoggingConfig = LoggingConfig()
    database: DatabaseConfig = DatabaseConfig()
    ray: RayConfig = RayConfig()
    mesa: MesaConfig = MesaConfig()
    streamlit: StreamlitConfig = StreamlitConfig()
    security: SecurityConfig = SecurityConfig()
    monitoring: MonitoringConfig = MonitoringConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        use_enum_values = True

# Configuration loading with modern patterns
async def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load and validate configuration with modern async patterns."""
    if config_path is None:
        # Determine config path based on environment
        env = os.getenv("ENVIRONMENT", "development")
        config_path = Path(f"config/{env}.yaml")

    # Load YAML configuration
    with open(config_path) as f:
        config_dict = yaml.safe_load(f)

    # Override with environment variables
    config_dict = override_with_env_vars(config_dict)

    # Validate with Pydantic
    return AppConfig(**config_dict)
```

### Configuration Validation

```python
# Implement configuration validation
from config_loader import get_config
import jsonschema

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "database": {
            "type": "object",
            "properties": {
                "connection_pool_size": {"type": "integer", "minimum": 1, "maximum": 100}
            }
        }
    }
}

def validate_configuration():
    config = get_config()
    try:
        jsonschema.validate(config, CONFIG_SCHEMA)
        logger.info("Configuration validation passed")
    except jsonschema.ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
```

## Testing Best Practices

### Test Organization

#### Unit Tests
```python
# tests/unit/test_anomaly_detection.py
import pytest
from unittest.mock import Mock, patch

class TestAnomalyDetection:
    def test_valid_anomaly_detection(self):
        # Test with valid input
        pass

    def test_invalid_threshold_raises_error(self):
        # Test error handling
        pass

    def test_empty_data_returns_empty_result(self):
        # Test edge cases
        pass
```

#### Integration Tests
```python
# tests/integration/test_simulation_workflow.py
import pytest
from simulation import Simulation

class TestSimulationWorkflow:
    def test_complete_simulation_run(self):
        # Test full workflow
        pass

    def test_database_persistence(self):
        # Test data persistence across runs
        pass

    def test_monitoring_integration(self):
        # Test monitoring system integration
        pass
```

### Test Data Management

```python
# tests/fixtures/traffic_data.py
import pytest
from typing import List, Dict

@pytest.fixture
def sample_traffic_data():
    """Generate sample traffic data for testing."""
    return [
        {
            "timestamp": "2025-01-01T00:00:00Z",
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.50",
            "bytes": 1500,
            "protocol": "TCP"
        }
    ]

@pytest.fixture
def anomalous_traffic_data():
    """Generate traffic data with known anomalies."""
    return [
        {
            "timestamp": "2025-01-01T00:00:00Z",
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.50",
            "bytes": 1000000,  # Unusually large
            "protocol": "TCP"
        }
    ]
```

## Deployment Best Practices

### Modern Containerization and Orchestration

#### Multi-Stage Dockerfile with Security and Performance Optimizations
```dockerfile
# Multi-stage build for optimal image size and security
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create build user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 builder

# Set up Python virtual environment for better isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies first (for better caching)
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Development dependencies in separate stage
FROM builder as development
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
RUN chown -R builder:builder /opt/venv
USER builder
EXPOSE 8501 8521 8265

# Production-optimized stage
FROM python:3.11-slim as production

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create runtime user with minimal privileges
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create application directories with proper permissions
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Copy application code with proper ownership
COPY --chown=appuser:appuser . /app

# Set working directory
WORKDIR /app

# Switch to non-root user
USER appuser

# Health check with detailed response
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "
import requests
import sys
try:
    # Check main application health
    response = requests.get('http://localhost:8501/health', timeout=5)
    if response.status_code != 200:
        sys.exit(1)
    print('Application is healthy')
except Exception as e:
    print(f'Health check failed: {e}')
    sys.exit(1)
" || exit 1

# Expose ports for different services
EXPOSE 8501 8521 8265

# Use exec form for proper signal handling
CMD ["uvicorn", "src.ui.streamlit_app:app", "--host", "0.0.0.0", "--port", "8501"]
```

#### Docker Compose for Local Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Main application service
  simulation-app:
    build:
      context: .
      target: development
    container_name: simulation-app
    volumes:
      - .:/app
      - /app/__pycache__
      - /app/.pytest_cache
    ports:
      - "8501:8501"  # Streamlit UI
      - "8521:8521"  # Mesa visualization
      - "8265:8265"  # Ray dashboard
    environment:
      - ENVIRONMENT=development
      - LOGGING_LEVEL=DEBUG
      - RAY_ADDRESS=ray://ray-head:10001
    depends_on:
      - ray-head
      - postgres
    networks:
      - simulation-network

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
      POSTGRES_DB: simulation_dev
      POSTGRES_USER: simulation_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-dev_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - simulation-network

  # Redis for caching and session storage
  redis:
    image: redis:7-alpine
    container_name: simulation-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-dev_redis}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - simulation-network

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

#### Kubernetes Deployment with Modern Patterns
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simulation-app
  labels:
    app: simulation
    version: "2.45.0"
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
        version: "2.45.0"
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8501"
        prometheus.io/path: "/metrics"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: simulation-app
        image: simulation-app:2.45.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8501
          name: streamlit
        - containerPort: 8521
          name: mesa
        - containerPort: 8265
          name: ray-dashboard
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: simulation-secrets
              key: database-host
        - name: RAY_HEAD_ADDRESS
          value: "ray-head-service:10001"
        livenessProbe:
          httpGet:
            path: /health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8501
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          capabilities:
            drop:
            - ALL

---
# Ray cluster deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ray-head
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: ray-head
        image: rayproject/ray:2.45.0-py311
        command: ["ray", "start", "--head", "--dashboard-host=0.0.0.0"]
        ports:
        - containerPort: 6379
        - containerPort: 8265
        - containerPort: 10001
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "8Gi"
            cpu: "2000m"

---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: simulation-hpa
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 120
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### Modern Environment Management

#### Production Environment Variables with Secrets Management
```bash
# .env.production
# Application Configuration
ENVIRONMENT=production
APP_VERSION=2.45.0
LOG_LEVEL=WARNING

# Database Configuration (PostgreSQL)
DB_HOST=simulation-db.example.com
DB_PORT=5432
DB_NAME=simulation_prod
DB_USER=simulation_user
DB_PASSWORD_FILE=/run/secrets/db_password

# Ray Cluster Configuration
RAY_HEAD_ADDRESS=ray://ray-head.example.com:10001
RAY_OBJECT_STORE_MEMORY=8589934592
RAY_REDIS_PASSWORD_FILE=/run/secrets/ray_redis_password

# Security Configuration
SECURITY_SECRET_KEY_FILE=/run/secrets/secret_key
SECURITY_ENABLE_HTTPS=true
SECURITY_RATE_LIMIT_RPM=1000

# Monitoring and Observability
PROMETHEUS_GATEWAY_URL=https://prometheus.example.com
JAEGER_ENDPOINT=https://jaeger.example.com/api/traces
SLACK_WEBHOOK_URL_FILE=/run/secrets/slack_webhook
PAGERDUTY_ROUTING_KEY_FILE=/run/secrets/pagerduty_key

# External Services
REDIS_URL=redis://simulation-redis.example.com:6379
REDIS_PASSWORD_FILE=/run/secrets/redis_password
```

#### Kubernetes Secrets Management
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: simulation-secrets
  namespace: production
type: Opaque
data:
  # Base64 encoded secrets
  database-password: <base64-encoded-password>
  ray-redis-password: <base64-encoded-password>
  redis-password: <base64-encoded-password>
  secret-key: <base64-encoded-secret>
  slack-webhook: <base64-encoded-webhook>
  pagerduty-key: <base64-encoded-key>

---
# External Secrets Operator for cloud provider integration
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secret-store
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: simulation-external-secrets
spec:
  secretStoreRef:
    name: aws-secret-store
    kind: SecretStore
  target:
    name: simulation-secrets
    creationPolicy: Owner
  data:
  - secretKey: database-password
    remoteRef:
      key: prod/simulation/database-password
  - secretKey: ray-redis-password
    remoteRef:
      key: prod/simulation/ray-redis-password
  - secretKey: slack-webhook
    remoteRef:
      key: prod/simulation/slack-webhook
```

#### Modern Deployment Scripts with Error Handling
```bash
#!/bin/bash
# scripts/deploy.sh - Modern deployment script with comprehensive error handling

set -euo pipefail  # Exit on error, undefined vars, pipe failures

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Configuration
ENVIRONMENT="${1:-production}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-myregistry.com}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD)}"

# Logging functions
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

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."

    # Check if required tools are installed
    command -v docker >/dev/null 2>&1 || error "Docker is required but not installed"
    command -v kubectl >/dev/null 2>&1 || error "kubectl is required but not installed"

    # Check if we're in git repository
    [[ -d .git ]] || error "Not in a git repository"

    # Check if required secrets exist
    kubectl get secret simulation-secrets -n "${ENVIRONMENT}" >/dev/null 2>&1 || \
        error "Required secrets not found in ${ENVIRONMENT} namespace"

    success "Pre-deployment checks passed"
}

# Build and push Docker image
build_and_push_image() {
    log "Building Docker image for ${ENVIRONMENT}..."

    local image_name="${DOCKER_REGISTRY}/simulation-app:${IMAGE_TAG}"

    docker build \
        --target production \
        --tag "${image_name}" \
        --label "version=${IMAGE_TAG}" \
        --label "environment=${ENVIRONMENT}" \
        . || error "Failed to build Docker image"

    log "Pushing image to registry..."
    docker push "${image_name}" || error "Failed to push Docker image"

    success "Image built and pushed: ${image_name}"
}

# Deploy to Kubernetes
deploy_to_kubernetes() {
    log "Deploying to Kubernetes ${ENVIRONMENT}..."

    # Update image tag in deployment
    sed -i.bak "s|image:.*|image: ${DOCKER_REGISTRY}/simulation-app:${IMAGE_TAG}|g" \
        k8s/deployment.yaml

    # Apply Kubernetes manifests
    kubectl apply -f k8s/namespace.yaml -n "${ENVIRONMENT}"
    kubectl apply -f k8s/secrets.yaml -n "${ENVIRONMENT}"
    kubectl apply -f k8s/deployment.yaml -n "${ENVIRONMENT}"
    kubectl apply -f k8s/service.yaml -n "${ENVIRONMENT}"
    kubectl apply -f k8s/hpa.yaml -n "${ENVIRONMENT}"

    # Wait for rollout to complete
    kubectl rollout status deployment/simulation-app -n "${ENVIRONMENT}" --timeout=300s || \
        error "Deployment rollout failed"

    success "Deployment completed successfully"
}

# Post-deployment verification
post_deployment_verification() {
    log "Running post-deployment verification..."

    # Check if application is responding
    local app_url="https://simulation-${ENVIRONMENT}.example.com/health"
    curl -f -k "${app_url}" >/dev/null 2>&1 || error "Application health check failed"

    # Check if all pods are running
    local running_pods=$(kubectl get pods -n "${ENVIRONMENT}" -l app=simulation \
        -o jsonpath='{.items[*].status.phase}' | grep -o Running | wc -l)
    local total_pods=$(kubectl get pods -n "${ENVIRONMENT}" -l app=simulation --no-headers | wc -l)

    [[ "${running_pods}" -eq "${total_pods}" ]] || error "Not all pods are running"

    success "Post-deployment verification passed"
}

# Main deployment flow
main() {
    log "Starting deployment to ${ENVIRONMENT}"

    pre_deployment_checks
    build_and_push_image
    deploy_to_kubernetes
    post_deployment_verification

    success "Deployment to ${ENVIRONMENT} completed successfully!"
    log "Application available at: https://simulation-${ENVIRONMENT}.example.com"
}

# Execute main function
main "$@"
```

## Security Best Practices

### Modern Security Architecture with Zero-Trust and Defense in Depth

#### Enhanced Input Validation with Pydantic and Runtime Security
```python
# Modern security with Pydantic models and runtime protection
from typing import Any, Dict, Optional, Union
import re
import ipaddress
from datetime import datetime, UTC
from pydantic import BaseModel, Field, validator, root_validator
from dataclasses import dataclass
import bleach
import json
from cryptography.fernet import Fernet
import secrets
import hashlib
import hmac
from security import SecurityError, RateLimiter, AuditLogger

# Security configuration
@dataclass
class SecurityConfig:
    """Comprehensive security configuration."""
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 1000
    enable_input_validation: bool = True
    enable_output_encoding: bool = True
    enable_csrf_protection: bool = True
    enable_https_enforcement: bool = True
    max_request_size_mb: int = 10
    allowed_hosts: list = None
    secret_key: str = None

    def __post_init__(self):
        if self.allowed_hosts is None:
            self.allowed_hosts = []
        if self.secret_key is None:
            self.secret_key = secrets.token_hex(32)

class SecureTrafficRecord(BaseModel):
    """Enhanced traffic record with comprehensive security validation."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_ip: str = Field(min_length=7, max_length=15)
    destination_ip: str = Field(min_length=7, max_length=15)
    bytes_transferred: int = Field(ge=0, le=10**9)
    protocol: str = Field(regex=r'^(TCP|UDP|ICMP)$')
    port: int = Field(ge=1, le=65535, default=80)
    payload: Optional[str] = Field(max_length=10000)

    # Enhanced validators with security focus
    @validator('source_ip', 'destination_ip')
    def validate_ip_address(cls, v):
        """Validate IP addresses with security considerations."""
        try:
            ip_obj = ipaddress.ip_address(v)

            # Block private IP ranges in production
            if ip_obj.is_private and not os.getenv('ALLOW_PRIVATE_IPS', 'false').lower() == 'true':
                raise ValueError(f"Private IP addresses not allowed: {v}")

            # Block reserved IP ranges
            if ip_obj.is_reserved:
                raise ValueError(f"Reserved IP addresses not allowed: {v}")

            return v
        except ValueError as e:
            if "not allowed" in str(e):
                raise e
            raise ValueError(f"Invalid IP address format: {v}")

    @validator('payload')
    def sanitize_payload(cls, v):
        """Sanitize payload content to prevent XSS and injection."""
        if v is None:
            return v

        # Remove potentially dangerous content
        sanitized = bleach.clean(
            v,
            tags=[],  # No HTML tags allowed
            attributes={},  # No attributes allowed
            strip=True
        )

        # Check for SQL injection patterns
        sql_patterns = [
            r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)',
            r'(\bor\b|\band\b)\s+\d+\s*=\s*\d+',
            r'(\-\-|\#|\/\*|\*\/)',
            r'(\bDROP\b|\bALTER\b|\bCREATE\b|\bEXEC\b|\bEXECUTE\b)'
        ]

        for pattern in sql_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError("Potentially malicious content detected in payload")

        return sanitized

    @root_validator
    def validate_traffic_logic(cls, values):
        """Validate business logic rules for traffic data."""
        source_ip = values.get('source_ip')
        dest_ip = values.get('destination_ip')

        if source_ip and dest_ip:
            # Prevent self-communication
            if source_ip == dest_ip:
                raise ValueError("Source and destination IPs cannot be the same")

            # Validate port usage based on protocol
            protocol = values.get('protocol', 'TCP')
            port = values.get('port', 80)

            if protocol == 'TCP' and port in [22, 3389] and not os.getenv('ALLOW_ADMIN_PORTS'):
                raise ValueError(f"Administrative port {port} not allowed for TCP traffic")

        return values

class SecureDataProcessor:
    """Modern secure data processor with comprehensive protection."""

    def __init__(self, security_config: SecurityConfig):
        self.config = security_config
        self.rate_limiter = RateLimiter(
            requests_per_minute=self.config.rate_limit_requests_per_minute
        )
        self.audit_logger = AuditLogger()
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

    async def process_traffic_data_securely(
        self,
        data: Any,
        client_ip: str,
        user_agent: str,
        request_id: str
    ) -> Dict:
        """
        Process traffic data with comprehensive security measures.

        Features:
        - Rate limiting and DDoS protection
        - Input validation and sanitization
        - Audit logging for compliance
        - Data encryption for sensitive information
        - Request correlation for traceability
        """

        # Rate limiting check
        if self.config.enable_rate_limiting:
            if not self.rate_limiter.is_allowed(client_ip):
                self.audit_logger.log_security_event(
                    event_type="RATE_LIMIT_EXCEEDED",
                    client_ip=client_ip,
                    request_id=request_id,
                    severity="HIGH"
                )
                raise SecurityError("Rate limit exceeded", client_ip=client_ip)

        # Input validation with Pydantic
        if self.config.enable_input_validation:
            try:
                validated_data = SecureTrafficRecord(**data)
                data = validated_data.dict()
            except Exception as e:
                self.audit_logger.log_security_event(
                    event_type="VALIDATION_ERROR",
                    client_ip=client_ip,
                    request_id=request_id,
                    details=str(e),
                    severity="MEDIUM"
                )
                raise SecurityError(f"Input validation failed: {e}")

        # Encrypt sensitive data if present
        if 'payload' in data and data['payload']:
            data['payload'] = self.fernet.encrypt(data['payload'].encode()).decode()

        # Log security-relevant events
        self.audit_logger.log_security_event(
            event_type="TRAFFIC_DATA_PROCESSED",
            client_ip=client_ip,
            request_id=request_id,
            data_size=len(str(data)),
            severity="LOW"
        )

        return data

    def generate_security_headers(self) -> Dict[str, str]:
        """Generate security headers for HTTP responses."""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'X-Request-ID': secrets.token_hex(8)
        }
```

#### Modern Secure Configuration with Secrets Management
```yaml
# config/security.yaml
security:
  # Core security settings
  enable_rate_limiting: true
  rate_limit_requests_per_minute: 1000
  rate_limit_burst: 100
  enable_input_validation: true
  enable_output_encoding: true
  enable_csrf_protection: true
  enable_https_enforcement: true
  max_request_size_mb: 10

  # Host and network security
  allowed_hosts:
    - "simulation.example.com"
    - "api.example.com"
    - "internal.example.com"
  trusted_proxies:
    - "10.0.0.0/8"
    - "172.16.0.0/12"
    - "192.168.0.0/16"

  # API security
  api_keys:
    enabled: true
    header_name: "X-API-Key"
    required_for_endpoints:
      - "/api/v1/simulation/*"
      - "/api/v1/admin/*"

  # Authentication and authorization
  authentication:
    enable_jwt: true
    jwt_secret_key: "${JWT_SECRET_KEY}"
    jwt_algorithm: "HS256"
    jwt_expiry_hours: 24
    enable_oauth2: true
    oauth2_providers:
      - name: "google"
        client_id: "${OAUTH_GOOGLE_CLIENT_ID}"
        client_secret: "${OAUTH_GOOGLE_CLIENT_SECRET}"

  # Data protection
  data_protection:
    enable_encryption_at_rest: true
    encryption_algorithm: "AES256"
    enable_encryption_in_transit: true
    tls_version: "1.3"
    enable_data_masking: true
    sensitive_fields:
      - "password"
      - "secret"
      - "api_key"
      - "payload"

  # Audit and compliance
  audit:
    enable_audit_logging: true
    audit_log_retention_days: 2555  # 7 years for compliance
    enable_security_events: true
    security_events_retention_days: 3650  # 10 years
    enable_compliance_reporting: true

  # Threat detection and prevention
  threat_detection:
    enable_anomaly_detection: true
    anomaly_detection_threshold: 0.8
    enable_intrusion_detection: true
    enable_ddos_protection: true
    ddos_threshold_requests_per_minute: 10000
    enable_bot_detection: true
    bot_detection_sensitivity: "high"

  # Supply chain security
  supply_chain:
    enable_software_bill_of_materials: true
    sbom_format: "SPDX"
    enable_dependency_scanning: true
    allowed_licenses:
      - "MIT"
      - "Apache-2.0"
      - "BSD-3-Clause"
    blocked_licenses:
      - "proprietary"
      - "unknown"
    enable_vulnerability_scanning: true
    vulnerability_severity_threshold: "medium"

  # Container and infrastructure security
  container_security:
    enable_security_context: true
    run_as_non_root: true
    read_only_root_filesystem: true
    enable_apparmor: true
    enable_selinux: true
    enable_seccomp: true
    allowed_capabilities: []
    blocked_capabilities:
      - "SYS_ADMIN"
      - "NET_ADMIN"
      - "SYS_PTRACE"

  # Monitoring and alerting
  security_monitoring:
    enable_security_metrics: true
    security_metrics_prefix: "security"
    enable_security_alerts: true
    alert_webhook_urls:
      - "${SECURITY_SLACK_WEBHOOK}"
      - "${SECURITY_PAGERDUTY_WEBHOOK}"
    critical_security_events:
      - "AUTHENTICATION_FAILURE"
      - "PRIVILEGE_ESCALATION"
      - "DATA_BREACH_ATTEMPT"
      - "DDoS_ATTACK"
```

#### Advanced Threat Mitigation Strategies
```python
# Modern threat detection and mitigation
import asyncio
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, UTC, timedelta
import statistics
import numpy as np
from collections import defaultdict, deque

@dataclass
class ThreatIntelligence:
    """Threat intelligence data for proactive defense."""
    known_malicious_ips: Set[str] = field(default_factory=set)
    suspicious_patterns: List[str] = field(default_factory=list)
    threat_feeds: Dict[str, str] = field(default_factory=dict)
    last_updated: Optional[datetime] = None

class AdvancedThreatDetector:
    """Advanced threat detection with ML and behavioral analysis."""

    def __init__(self):
        self.threat_intel = ThreatIntelligence()
        self.request_history = defaultdict(deque)
        self.anomaly_scores = defaultdict(list)
        self.ddos_threshold = 10000  # requests per minute

    async def analyze_request_pattern(
        self,
        client_ip: str,
        endpoint: str,
        user_agent: str,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """
        Analyze request patterns for threat detection.

        Detects:
        - DDoS attacks
        - Credential stuffing
        - API abuse
        - Bot behavior
        - Anomalous access patterns
        """

        # Update request history
        self.request_history[client_ip].append({
            'endpoint': endpoint,
            'timestamp': timestamp,
            'user_agent': user_agent
        })

        # Keep only last 1000 requests per IP
        if len(self.request_history[client_ip]) > 1000:
            self.request_history[client_ip].popleft()

        analysis = {
            'client_ip': client_ip,
            'threat_level': 'LOW',
            'risk_factors': [],
            'recommendations': []
        }

        # DDoS detection
        recent_requests = [
            req for req in self.request_history[client_ip]
            if req['timestamp'] > timestamp - timedelta(minutes=1)
        ]

        if len(recent_requests) > self.ddos_threshold:
            analysis['threat_level'] = 'CRITICAL'
            analysis['risk_factors'].append('DDoS_ATTACK_DETECTED')
            analysis['recommendations'].append('BLOCK_IP_IMMEDIATELY')

        # Bot detection based on user agent patterns
        if self._is_suspicious_user_agent(user_agent):
            analysis['threat_level'] = 'HIGH'
            analysis['risk_factors'].append('SUSPICIOUS_USER_AGENT')
            analysis['recommendations'].append('REQUIRE_CAPTCHA')

        # API abuse detection
        if self._detect_api_abuse(client_ip, endpoint):
            analysis['threat_level'] = 'MEDIUM'
            analysis['risk_factors'].append('API_ABUSE_DETECTED')
            analysis['recommendations'].append('RATE_LIMIT_ENDPOINT')

        # Anomalous behavior detection
        if self._detect_anomalous_behavior(client_ip, endpoint, timestamp):
            analysis['threat_level'] = 'MEDIUM'
            analysis['risk_factors'].append('ANOMALOUS_BEHAVIOR')
            analysis['recommendations'].append('INCREASE_MONITORING')

        return analysis

    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Detect suspicious user agent patterns."""
        suspicious_patterns = [
            r'bot|crawler|spider|scraper',
            r'python-requests/\d+\.\d+',
            r'curl/\d+\.\d+',
            r'wget/\d+\.\d+',
            r'^$',  # Empty user agent
        ]

        return any(
            re.search(pattern, user_agent, re.IGNORECASE)
            for pattern in suspicious_patterns
        )

    def _detect_api_abuse(self, client_ip: str, endpoint: str) -> bool:
        """Detect potential API abuse patterns."""
        if client_ip not in self.request_history:
            return False

        # Check for rapid successive requests to sensitive endpoints
        sensitive_endpoints = ['/api/v1/admin', '/api/v1/simulation/create']
        if endpoint in sensitive_endpoints:
            recent_requests = [
                req for req in self.request_history[client_ip]
                if req['timestamp'] > datetime.now(UTC) - timedelta(seconds=10)
            ]

            if len(recent_requests) > 5:
                return True

        return False

    def _detect_anomalous_behavior(self, client_ip: str, endpoint: str, timestamp: datetime) -> bool:
        """Detect anomalous access patterns using statistical analysis."""
        if client_ip not in self.request_history:
            return False

        # Calculate request frequency patterns
        timestamps = [
            req['timestamp'] for req in self.request_history[client_ip]
            if req['timestamp'] > timestamp - timedelta(hours=1)
        ]

        if len(timestamps) < 10:
            return False

        # Calculate time differences
        intervals = [
            (timestamps[i] - timestamps[i-1]).total_seconds()
            for i in range(1, len(timestamps))
        ]

        # Check for unusually regular intervals (bot-like behavior)
        if len(intervals) > 5:
            mean_interval = statistics.mean(intervals)
            std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

            # If standard deviation is very low, it might be bot behavior
            if std_interval < mean_interval * 0.1 and mean_interval < 5:
                return True

        return False

# Zero-trust security implementation
class ZeroTrustSecurity:
    """Implement zero-trust security model."""

    def __init__(self):
        self.authenticated_sessions = {}
        self.device_fingerprints = {}
        self.access_policies = {}

    async def validate_request(
        self,
        request_id: str,
        client_ip: str,
        user_context: Dict,
        resource: str
    ) -> bool:
        """
        Validate every request using zero-trust principles.

        Checks:
        - User authentication and authorization
        - Device security posture
        - Network location and risk
        - Resource-specific access policies
        - Behavioral analysis
        """

        # 1. Verify user identity and authentication
        if not self._verify_user_authentication(user_context):
            return False

        # 2. Check device security posture
        if not self._verify_device_security(client_ip, user_context):
            return False

        # 3. Validate network and location
        if not self._validate_network_context(client_ip, user_context):
            return False

        # 4. Apply resource-specific access policies
        if not self._check_resource_access(resource, user_context):
            return False

        # 5. Behavioral analysis and anomaly detection
        if not await self._analyze_behavior(request_id, user_context):
            return False

        return True

    def _verify_user_authentication(self, user_context: Dict) -> bool:
        """Verify user has valid authentication."""
        # Implementation would verify JWT tokens, certificates, etc.
        return True

    def _verify_device_security(self, client_ip: str, user_context: Dict) -> bool:
        """Verify device meets security requirements."""
        # Check device certificates, security posture, etc.
        return True

    def _validate_network_context(self, client_ip: str, user_context: Dict) -> bool:
        """Validate network location and risk."""
        # Check if IP is from trusted network, VPN, etc.
        return True

    def _check_resource_access(self, resource: str, user_context: Dict) -> bool:
        """Check if user has access to specific resource."""
        # Implement role-based access control (RBAC)
        return True

    async def _analyze_behavior(self, request_id: str, user_context: Dict) -> bool:
        """Analyze user behavior for anomalies."""
        # Use the threat detector for behavioral analysis
        return True
```

## Performance Best Practices

### Efficient Database Operations

```python
# Batch operations for better performance
def efficient_signature_processing(signatures):
    """Process signatures in batches for optimal performance."""

    batch_size = 100
    for i in range(0, len(signatures), batch_size):
        batch = signatures[i:i + batch_size]

        # Process batch
        results = process_signature_batch(batch)

        # Bulk insert results
        db.append_batch(results)

        # Clear batch from memory
        del batch
```

### Memory Management

```python
import gc
from typing import List, Dict, Any

class MemoryEfficientProcessor:
    def __init__(self, max_cache_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.max_cache_size = max_cache_size

    def add_to_cache(self, key: str, value: Any):
        """Add item to cache with size management."""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest 25% of items
            items_to_remove = list(self.cache.keys())[:self.max_cache_size // 4]
            for item_key in items_to_remove:
                del self.cache[item_key]

        self.cache[key] = value

    def process_with_memory_management(self, data: List[Dict]) -> List[Dict]:
        """Process data with memory management."""
        results = []

        for item in data:
            # Process in chunks to manage memory
            if len(results) > 1000:
                # Yield or save intermediate results
                self.save_intermediate_results(results)
                results = []

            result = self.process_item(item)
            results.append(result)

        # Final cleanup
        gc.collect()
        return results
```

## Monitoring and Observability Best Practices

### Modern Observability with OpenTelemetry and Distributed Tracing

#### Enhanced Health Checks with Dependency Monitoring
```python
# Modern health check system with comprehensive monitoring
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, UTC
import psutil
import GPUtil
from monitoring import get_monitoring, HealthStatus, HealthCheckResult
import ray
import requests

@dataclass
class SystemMetrics:
    """Comprehensive system metrics collection."""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    gpu_metrics: List[Dict] = field(default_factory=list)
    ray_cluster_metrics: Dict[str, Any] = field(default_factory=dict)

class ModernHealthChecker:
    """Modern health checker with dependency monitoring and detailed reporting."""

    def __init__(self):
        self.monitoring = get_monitoring()
        self.check_interval = 30  # seconds
        self.health_history = []

    async def comprehensive_health_check(self) -> HealthCheckResult:
        """
        Perform comprehensive health check including all system components.

        Checks:
        - Application health and responsiveness
        - Database connectivity and performance
        - Ray cluster status and resource usage
        - System resource utilization
        - External service dependencies
        - Custom business logic health
        """

        start_time = datetime.now(UTC)
        checks = []
        overall_status = "healthy"

        # Application health check
        app_check = await self._check_application_health()
        checks.append(app_check)
        if app_check.status != "healthy":
            overall_status = "degraded"

        # Database health check
        db_check = await self._check_database_health()
        checks.append(db_check)
        if db_check.status != "healthy":
            overall_status = "unhealthy"

        # Ray cluster health check
        ray_check = await self._check_ray_cluster_health()
        checks.append(ray_check)
        if ray_check.status != "healthy":
            overall_status = "degraded"

        # System resources check
        system_check = self._check_system_resources()
        checks.append(system_check)
        if system_check.status != "healthy":
            overall_status = "degraded"

        # External dependencies check
        deps_check = await self._check_external_dependencies()
        checks.append(deps_check)
        if deps_check.status != "healthy":
            overall_status = "degraded"

        # Custom business logic check
        business_check = await self._check_business_logic_health()
        checks.append(business_check)
        if business_check.status != "healthy":
            overall_status = "degraded"

        end_time = datetime.now(UTC)
        duration = (end_time - start_time).total_seconds()

        # Store health check history for trend analysis
        self._store_health_history(overall_status, duration, checks)

        return HealthCheckResult(
            status=overall_status,
            message=f"Health check completed in {duration:.2f}s",
            timestamp=end_time.timestamp(),
            checks=checks,
            metrics={
                "check_duration_seconds": duration,
                "total_checks": len(checks),
                "healthy_checks": len([c for c in checks if c.status == "healthy"]),
                "degraded_checks": len([c for c in checks if c.status == "degraded"]),
                "unhealthy_checks": len([c for c in checks if c.status == "unhealthy"])
            }
        )

    async def _check_application_health(self) -> HealthStatus:
        """Check main application health and responsiveness."""
        try:
            # Test critical application endpoints
            response = requests.get(
                "http://localhost:8501/health",
                timeout=5,
                headers={"User-Agent": "HealthChecker"}
            )

            if response.status_code == 200:
                return HealthStatus(
                    status="healthy",
                    message="Application responding normally",
                    timestamp=datetime.now(UTC).timestamp(),
                    response_time=response.elapsed.total_seconds()
                )
            else:
                return HealthStatus(
                    status="unhealthy",
                    message=f"Application returned status {response.status_code}",
                    timestamp=datetime.now(UTC).timestamp()
                )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                message=f"Application health check failed: {e}",
                timestamp=datetime.now(UTC).timestamp()
            )

    async def _check_database_health(self) -> HealthStatus:
        """Check database connectivity and performance."""
        try:
            from database import DatabaseLedger

            # Measure query performance
            start_time = datetime.now(UTC)
            db = DatabaseLedger()
            result = db.read_ledger(limit=1)
            query_time = (datetime.now(UTC) - start_time).total_seconds()

            # Check connection pool status
            pool_status = db.get_connection_pool_status()

            return HealthStatus(
                status="healthy",
                message=f"Database query completed in {query_time:.3f}s",
                timestamp=datetime.now(UTC).timestamp(),
                metrics={
                    "query_time_seconds": query_time,
                    "pool_active": pool_status.get("active", 0),
                    "pool_idle": pool_status.get("idle", 0)
                }
            )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                message=f"Database health check failed: {e}",
                timestamp=datetime.now(UTC).timestamp()
            )

    async def _check_ray_cluster_health(self) -> HealthStatus:
        """Check Ray cluster health and resource utilization."""
        try:
            if not ray.is_initialized():
                return HealthStatus(
                    status="unhealthy",
                    message="Ray cluster not initialized",
                    timestamp=datetime.now(UTC).timestamp()
                )

            # Get cluster resources
            cluster_resources = ray.cluster_resources()
            available_resources = ray.available_resources()

            # Check if Ray dashboard is accessible
            dashboard_url = "http://localhost:8265"
            response = requests.get(f"{dashboard_url}/api/cluster_status", timeout=3)

            return HealthStatus(
                status="healthy",
                message="Ray cluster operational",
                timestamp=datetime.now(UTC).timestamp(),
                metrics={
                    "total_cpus": cluster_resources.get("CPU", 0),
                    "available_cpus": available_resources.get("CPU", 0),
                    "total_memory_gb": cluster_resources.get("memory", 0) / (1024**3),
                    "available_memory_gb": available_resources.get("memory", 0) / (1024**3),
                    "dashboard_responsive": response.status_code == 200
                }
            )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                message=f"Ray cluster health check failed: {e}",
                timestamp=datetime.now(UTC).timestamp()
            )

    def _check_system_resources(self) -> HealthStatus:
        """Check system resource utilization."""
        try:
            # CPU and memory metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # GPU metrics if available
            gpu_metrics = []
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_metrics.append({
                        "id": gpu.id,
                        "name": gpu.name,
                        "memory_used_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100,
                        "temperature": gpu.temperature,
                        "utilization_percent": gpu.load * 100
                    })
            except:
                pass  # No GPU or GPUtil not available

            # Network I/O
            network = psutil.net_io_counters()

            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                network_io={
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                gpu_metrics=gpu_metrics
            )

            # Determine health based on thresholds
            status = "healthy"
            issues = []

            if cpu_percent > 90:
                status = "degraded"
                issues.append(f"High CPU usage: {cpu_percent}%")
            if memory.percent > 85:
                status = "degraded"
                issues.append(f"High memory usage: {memory.percent}%")
            if disk.percent > 80:
                status = "degraded"
                issues.append(f"High disk usage: {disk.percent}%")

            return HealthStatus(
                status=status,
                message=f"System resources: {', '.join(issues) if issues else 'Normal'}",
                timestamp=datetime.now(UTC).timestamp(),
                metrics=metrics.__dict__
            )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                message=f"System resource check failed: {e}",
                timestamp=datetime.now(UTC).timestamp()
            )

    async def _check_external_dependencies(self) -> HealthStatus:
        """Check health of external service dependencies."""
        dependencies = [
            {"name": "prometheus", "url": "http://localhost:9090/-/healthy"},
            {"name": "grafana", "url": "http://localhost:3000/api/health"},
            {"name": "redis", "url": "http://localhost:6379/ping"}
        ]

        results = []
        for dep in dependencies:
            try:
                response = requests.get(dep["url"], timeout=3)
                results.append(f"{dep['name']}: {'OK' if response.status_code < 400 else 'ERROR'}")
            except:
                results.append(f"{dep['name']}: UNAVAILABLE")

        all_healthy = all("OK" in result for result in results)

        return HealthStatus(
            status="healthy" if all_healthy else "degraded",
            message=f"External dependencies: {'All healthy' if all_healthy else ', '.join(results)}",
            timestamp=datetime.now(UTC).timestamp(),
            details=results
        )

    async def _check_business_logic_health(self) -> HealthStatus:
        """Check custom business logic health indicators."""
        try:
            # Example: Check if simulation can be created and run
            from simulation import Simulation

            start_time = datetime.now(UTC)
            sim = Simulation()
            test_result = sim.validate_configuration()
            validation_time = (datetime.now(UTC) - start_time).total_seconds()

            return HealthStatus(
                status="healthy",
                message=f"Business logic validation passed in {validation_time:.3f}s",
                timestamp=datetime.now(UTC).timestamp(),
                metrics={
                    "validation_time_seconds": validation_time,
                    "configuration_valid": test_result
                }
            )
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                message=f"Business logic health check failed: {e}",
                timestamp=datetime.now(UTC).timestamp()
            )

    def _store_health_history(self, status: str, duration: float, checks: List[HealthStatus]):
        """Store health check history for trend analysis."""
        self.health_history.append({
            "timestamp": datetime.now(UTC),
            "status": status,
            "duration": duration,
            "check_count": len(checks)
        })

        # Keep only last 1000 checks
        if len(self.health_history) > 1000:
            self.health_history.pop(0)

# Register modern health checker
health_checker = ModernHealthChecker()
get_monitoring().register_health_check('comprehensive', health_checker.comprehensive_health_check)
```

#### Advanced Structured Logging with OpenTelemetry
```python
# Modern observability with OpenTelemetry integration
import asyncio
import json
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.status import Status, StatusCode
from logging_setup import get_logger

# Initialize OpenTelemetry
resource = Resource.create({
    "service.name": "decentralized-ai-simulation",
    "service.version": "2.45.0",
    "deployment.environment": "production"
})

trace.set_tracer_provider(TracerProvider(resource=resource))

# Add Jaeger exporter for distributed tracing
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)
logger = get_logger(__name__)

class ObservabilityManager:
    """Modern observability manager with distributed tracing."""

    def __init__(self):
        self.meter = None  # OpenTelemetry meter for metrics
        self.logger = logger

    @asynccontextmanager
    async def traced_operation(
        self,
        operation_name: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Context manager for automatic tracing of operations."""
        with tracer.start_as_current_span(
            operation_name,
            attributes=attributes or {}
        ) as span:
            start_time = time.time()
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
                self.logger.info(
                    f"Operation {operation_name} completed successfully",
                    extra={
                        "operation": operation_name,
                        "duration_ms": (time.time() - start_time) * 1000,
                        "trace_id": span.get_span_context().trace_id,
                        "span_id": span.get_span_context().span_id
                    }
                )
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                self.logger.error(
                    f"Operation {operation_name} failed: {e}",
                    extra={
                        "operation": operation_name,
                        "duration_ms": (time.time() - start_time) * 1000,
                        "error": str(e),
                        "trace_id": span.get_span_context().trace_id,
                        "span_id": span.get_span_context().span_id
                    },
                    exc_info=True
                )
                raise

async def log_anomaly_detection_with_tracing(
    traffic_data: List[Dict],
    anomalies: List[Dict],
    processing_time: float,
    model_version: str = "v2.45.0"
):
    """
    Enhanced anomaly detection logging with distributed tracing.

    Features:
    - OpenTelemetry distributed tracing
    - Structured logging with correlation IDs
    - Performance metrics collection
    - Error tracking and context
    """

    obs_manager = ObservabilityManager()

    async with obs_manager.traced_operation(
        "anomaly_detection",
        attributes={
            "model.version": model_version,
            "data.records.count": len(traffic_data),
            "processing.time_ms": processing_time * 1000
        }
    ) as span:

        # Enhanced log data with comprehensive context
        log_data = {
            'event': 'anomaly_detection',
            'event_type': 'security_analysis',
            'traffic_records': len(traffic_data),
            'anomalies_detected': len(anomalies),
            'processing_time_ms': processing_time * 1000,
            'threshold_used': 0.5,
            'model_version': model_version,
            'timestamp': datetime.now(UTC).isoformat(),
            'trace_id': span.get_span_context().trace_id,
            'span_id': span.get_span_context().span_id,
            'severity': 'INFO'
        }

        # Add anomaly details if present
        if anomalies:
            log_data.update({
                'anomaly_details': {
                    'count': len(anomalies),
                    'severity_distribution': {},
                    'top_anomaly_types': []
                },
                'severity': 'WARNING' if len(anomalies) > 10 else 'INFO'
            })

            # Calculate severity distribution
            for anomaly in anomalies:
                severity = anomaly.get('severity', 'unknown')
                log_data['anomaly_details']['severity_distribution'][severity] = \
                    log_data['anomaly_details']['severity_distribution'].get(severity, 0) + 1

        # Structured logging with JSON format for better aggregation
        if get_config('logging.enable_json_logging', False):
            logger.info(
                "Anomaly detection completed",
                extra={
                    'json': json.dumps(log_data, default=str),
                    'trace_id': span.get_span_context().trace_id,
                    'span_id': span.get_span_context().span_id
                }
            )
        else:
            # Human-readable format for development
            logger.info(
                "Anomaly Detection Results: "
                f"{log_data['anomalies_detected']} anomalies detected from "
                f"{log_data['traffic_records']} traffic records in "
                f"{log_data['processing_time_ms']:.2f}ms "
                f"(Model: {log_data['model_version']})"
            )

        # Record additional span attributes
        span.set_attribute("anomalies.count", len(anomalies))
        span.set_attribute("data.quality.score", calculate_data_quality_score(traffic_data))

        # Add performance metrics
        if hasattr(obs_manager, 'meter') and obs_manager.meter:
            anomaly_counter = obs_manager.meter.create_counter(
                "anomalies_detected_total",
                description="Total number of anomalies detected"
            )
            processing_time_histogram = obs_manager.meter.create_histogram(
                "anomaly_detection_duration_seconds",
                description="Time spent detecting anomalies"
            )

            anomaly_counter.add(len(anomalies), {"model_version": model_version})
            processing_time_histogram.record(processing_time, {"model_version": model_version})

def calculate_data_quality_score(traffic_data: List[Dict]) -> float:
    """Calculate a simple data quality score for observability."""
    if not traffic_data:
        return 0.0

    # Simple scoring based on data completeness
    required_fields = ['source_ip', 'destination_ip', 'timestamp', 'bytes_transferred']
    total_score = 0.0

    for record in traffic_data:
        record_score = sum(1 for field in required_fields if field in record) / len(required_fields)
        total_score += record_score

    return total_score / len(traffic_data)
```

## Maintenance Best Practices

### Modern Automated Maintenance with Monitoring and Alerting

#### Intelligent Database Maintenance with Performance Monitoring
```bash
#!/bin/bash
# scripts/maintenance/intelligent_maintenance.sh
# Modern maintenance script with intelligent scheduling and monitoring

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/maintenance.log"

# Configuration
MAINTENANCE_WINDOW_START="02:00"
MAINTENANCE_WINDOW_END="04:00"
HEALTH_CHECK_THRESHOLD=95  # Minimum system health percentage
DRY_RUN="${DRY_RUN:-false}"

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

# Pre-maintenance health assessment
assess_system_health() {
    log "Assessing system health before maintenance..."

    # Check overall system health
    local health_response=$(curl -s http://localhost:8501/health || echo '{"status":"unknown"}')
    local health_score=$(echo "$health_response" | jq -r '.health_score // 0')

    if (( $(echo "$health_score < $HEALTH_CHECK_THRESHOLD" | bc -l) )); then
        error "System health too low for maintenance: ${health_score}%"
    fi

    # Check active connections and sessions
    local active_connections=$(ss -tuln | grep -E ':(8501|8521|8265)' | wc -l)
    if [ "$active_connections" -gt 50 ]; then
        log "WARNING: High number of active connections: $active_connections"
    fi

    success "System health assessment passed: ${health_score}%"
}

# Intelligent database maintenance
perform_database_maintenance() {
    log "Starting intelligent database maintenance..."

    # Analyze database performance before maintenance
    local db_stats_before=$(sqlite3 data/databases/ledger.db "
        SELECT COUNT(*) as total_records,
               COUNT(DISTINCT source_ip) as unique_sources,
               COUNT(DISTINCT destination_ip) as unique_destinations
        FROM traffic_data;
    ")

    log "Database stats before maintenance: $db_stats_before"

    # Perform maintenance based on database size and fragmentation
    local db_size=$(stat -c%s data/databases/ledger.db 2>/dev/null || echo "0")
    local db_size_mb=$((db_size / 1024 / 1024))

    if [ "$db_size_mb" -gt 1000 ]; then
        log "Large database detected (${db_size_mb}MB), performing extensive maintenance..."

        # Create maintenance backup before major operations
        local backup_file="data/databases/ledger_$(date +%Y%m%d_%H%M%S).bak"
        cp data/databases/ledger.db "$backup_file"

        # Perform VACUUM for space reclamation
        log "Running VACUUM to reclaim space..."
        sqlite3 data/databases/ledger.db "VACUUM;"

        # Rebuild indexes for better performance
        log "Rebuilding indexes..."
        sqlite3 data/databases/ledger.db "REINDEX;"

        # Analyze tables for query optimization
        sqlite3 data/databases/ledger.db "ANALYZE;"

    else
        log "Database size is manageable (${db_size_mb}MB), performing standard maintenance..."

        # Standard cleanup of old records (older than 90 days)
        local cutoff_date=$(date -d '90 days ago' +%Y-%m-%d)
        sqlite3 data/databases/ledger.db "
            DELETE FROM traffic_data WHERE timestamp < '$cutoff_date';
            DELETE FROM anomaly_data WHERE timestamp < '$cutoff_date';
        "

        # Optimize database
        sqlite3 data/databases/ledger.db "VACUUM;"
    fi

    # Verify maintenance results
    local db_stats_after=$(sqlite3 data/databases/ledger.db "
        SELECT COUNT(*) as total_records,
               COUNT(DISTINCT source_ip) as unique_sources,
               COUNT(DISTINCT destination_ip) as unique_destinations
        FROM traffic_data;
    ")

    log "Database stats after maintenance: $db_stats_after"
    success "Database maintenance completed"
}

# Intelligent log management with rotation and compression
manage_logs() {
    log "Managing log files..."

    # Find log files older than retention period
    local retention_days=${1:-30}
    local log_dirs=("/var/log/simulation" "logs")
    local total_cleaned=0

    for log_dir in "${log_dirs[@]}"; do
        if [ -d "$log_dir" ]; then
            while IFS= read -r -d '' log_file; do
                # Check if file is older than retention period
                if [ "$(find "$log_file" -mtime +$retention_days)" ]; then
                    log "Archiving old log file: $log_file"

                    # Compress log file before archiving
                    if command -v gzip >/dev/null 2>&1; then
                        gzip "$log_file"
                        log_file="${log_file}.gz"
                    fi

                    # Move to archive location
                    local archive_dir="${log_dir}/archive"
                    mkdir -p "$archive_dir"
                    mv "$log_file" "$archive_dir/"

                    ((total_cleaned++))
                fi
            done < <(find "$log_dir" -name "*.log" -type f -print0)
        fi
    done

    success "Log management completed. Cleaned up $total_cleaned files"
}

# Ray cluster maintenance
maintain_ray_cluster() {
    log "Maintaining Ray cluster..."

    if command -v ray >/dev/null 2>&1 && ray status >/dev/null 2>&1; then
        # Get current cluster status
        local cluster_status=$(ray status)

        # Clean up dead nodes
        log "Cleaning up dead Ray nodes..."
        ray stop --force || true

        # Restart Ray dashboard if needed
        if ! curl -s http://localhost:8265 >/dev/null; then
            log "Restarting Ray dashboard..."
            ray start --head --dashboard-host=0.0.0.0 --dashboard-port=8265
        fi

        # Clean up object store if memory usage is high
        local memory_usage=$(ray memory | grep "Object store" | awk '{print $3}' | tr -d '%')
        if [ "${memory_usage:-0}" -gt 80 ]; then
            log "High Ray memory usage detected (${memory_usage}%), triggering cleanup..."
            # Note: Ray doesn't have a direct cleanup command, but we can restart workers
            ray stop --force
            sleep 5
            ray start --head --dashboard-host=0.0.0.0 --dashboard-port=8265
        fi

        success "Ray cluster maintenance completed"
    else
        log "Ray cluster not running, skipping maintenance"
    fi
}

# Cache maintenance with intelligent cleanup
maintain_cache() {
    log "Maintaining application cache..."

    # Clean up Redis cache if running
    if command -v redis-cli >/dev/null 2>&1 && redis-cli ping >/dev/null 2>&1; then
        local cache_size=$(redis-cli DBSIZE)
        log "Current cache size: $cache_size keys"

        # Clean up expired keys
        local expired_keys=$(redis-cli --scan --pattern "*" | xargs redis-cli TTL | grep -c "^-1" || echo "0")
        if [ "$expired_keys" -gt 100 ]; then
            log "Cleaning up $expired_keys expired cache keys..."
            redis-cli FLUSHDB
        fi

        # Clean up old sessions (older than 24 hours)
        redis-cli --scan --pattern "session:*" | while read key; do
            local ttl=$(redis-cli TTL "$key")
            if [ "$ttl" -eq -1 ]; then
                redis-cli DEL "$key"
            fi
        done

        success "Cache maintenance completed"
    fi
}

# Post-maintenance verification
verify_maintenance() {
    log "Verifying maintenance results..."

    # Check application health after maintenance
    if curl -s http://localhost:8501/health >/dev/null; then
        success "Application health check passed after maintenance"
    else
        error "Application health check failed after maintenance"
    fi

    # Verify database integrity
    if sqlite3 data/databases/ledger.db "PRAGMA integrity_check;" | grep -q "ok"; then
        success "Database integrity check passed"
    else
        error "Database integrity check failed"
    fi

    # Check available disk space
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
    if [ "$disk_usage" -lt 90 ]; then
        success "Disk space is adequate: ${disk_usage}% used"
    else
        error "Low disk space after maintenance: ${disk_usage}% used"
    fi
}

# Main maintenance execution
main() {
    log "Starting intelligent maintenance process..."

    # Check if we're in maintenance window
    current_hour=$(date +%H)
    if [ "$current_hour" -lt "${MAINTENANCE_WINDOW_START%:*}" ] || [ "$current_hour" -gt "${MAINTENANCE_WINDOW_END%:*}" ]; then
        log "Outside maintenance window, skipping scheduled maintenance"
        exit 0
    fi

    # Run maintenance tasks
    assess_system_health
    perform_database_maintenance
    manage_logs 30
    maintain_ray_cluster
    maintain_cache
    verify_maintenance

    success "All maintenance tasks completed successfully"
}

# Execute main function
main "$@"
```

#### Modern Log Management with ELK Stack Integration
```python
# Enhanced log management with modern observability stack
import asyncio
import json
import gzip
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime, UTC, timedelta
from pathlib import Path
import logging.handlers
from dataclasses import dataclass
from logging_setup import get_logger

@dataclass
class LogMetrics:
    """Log analysis metrics for monitoring."""
    total_lines: int = 0
    error_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    unique_ips: set = None
    top_endpoints: Dict[str, int] = None

    def __post_init__(self):
        if self.unique_ips is None:
            self.unique_ips = set()
        if self.top_endpoints is None:
            self.top_endpoints = {}

class ModernLogManager:
    """Modern log manager with intelligent analysis and alerting."""

    def __init__(self, log_config: Dict[str, Any]):
        self.config = log_config
        self.logger = get_logger(__name__)
        self.log_file_path = Path(log_config.get('file_path', 'logs/simulation.log'))
        self.max_file_size_mb = log_config.get('max_file_size_mb', 100)
        self.backup_count = log_config.get('backup_count', 5)
        self.enable_remote_logging = log_config.get('enable_remote', False)
        self.remote_endpoint = log_config.get('remote_endpoint')

        # Setup log rotation handler
        self._setup_log_rotation()

    def _setup_log_rotation(self):
        """Setup automatic log rotation based on size and time."""
        # Create rotating file handler
        rotating_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_file_path,
            maxBytes=self.max_file_size_mb * 1024 * 1024,
            backupCount=self.backup_count
        )

        # Add compression for archived logs
        rotating_handler.rotator = self._compress_log_file

        # Add namer for better file naming
        rotating_handler.namer = lambda name: name.replace('.log', '') + '.log'

        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(rotating_handler)

    def _compress_log_file(self, source: str, dest: str):
        """Compress rotated log files."""
        try:
            with open(source, 'rb') as f_in:
                with gzip.open(dest + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            Path(source).unlink()  # Remove original file after compression
        except Exception as e:
            self.logger.error(f"Failed to compress log file {source}: {e}")

    async def analyze_logs_for_insights(
        self,
        time_window_hours: int = 24,
        analysis_types: List[str] = None
    ) -> LogMetrics:
        """
        Analyze logs for patterns, errors, and insights.

        Args:
            time_window_hours: Hours of logs to analyze
            analysis_types: Types of analysis to perform
                         ['errors', 'performance', 'security', 'usage']
        """
        if analysis_types is None:
            analysis_types = ['errors', 'performance', 'security', 'usage']

        metrics = LogMetrics()
        cutoff_time = datetime.now(UTC) - timedelta(hours=time_window_hours)

        try:
            # Analyze current log file
            await self._analyze_log_file(self.log_file_path, cutoff_time, metrics, analysis_types)

            # Analyze rotated log files
            log_dir = self.log_file_path.parent
            for log_file in log_dir.glob(f"{self.log_file_path.stem}.log.*"):
                if log_file.suffix == '.gz':
                    await self._analyze_compressed_log(log_file, cutoff_time, metrics, analysis_types)
                else:
                    await self._analyze_log_file(log_file, cutoff_time, metrics, analysis_types)

        except Exception as e:
            self.logger.error(f"Log analysis failed: {e}")

        return metrics

    async def _analyze_log_file(
        self,
        log_file: Path,
        cutoff_time: datetime,
        metrics: LogMetrics,
        analysis_types: List[str]
    ):
        """Analyze a single log file."""
        if not log_file.exists():
            return

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    # Parse log line (assuming JSON format)
                    if line.strip().startswith('{'):
                        log_entry = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(log_entry.get('timestamp', '').replace('Z', '+00:00'))

                        if timestamp < cutoff_time:
                            continue

                        await self._process_log_entry(log_entry, metrics, analysis_types)
                except json.JSONDecodeError:
                    # Handle non-JSON log lines
                    continue
                except Exception as e:
                    self.logger.debug(f"Error processing log line: {e}")

    async def _analyze_compressed_log(
        self,
        log_file: Path,
        cutoff_time: datetime,
        metrics: LogMetrics,
        analysis_types: List[str]
    ):
        """Analyze a compressed log file."""
        try:
            with gzip.open(log_file, 'rt', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    try:
                        if line.strip().startswith('{'):
                            log_entry = json.loads(line.strip())
                            timestamp = datetime.fromisoformat(log_entry.get('timestamp', '').replace('Z', '+00:00'))

                            if timestamp < cutoff_time:
                                continue

                            await self._process_log_entry(log_entry, metrics, analysis_types)
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception as e:
            self.logger.debug(f"Error processing compressed log {log_file}: {e}")

    async def _process_log_entry(
        self,
        log_entry: Dict[str, Any],
        metrics: LogMetrics,
        analysis_types: List[str]
    ):
        """Process individual log entry for analysis."""
        metrics.total_lines += 1

        # Extract common fields
        level = log_entry.get('level', 'INFO').upper()
        message = log_entry.get('message', '')
        client_ip = log_entry.get('client_ip')
        endpoint = log_entry.get('endpoint')
        response_time = log_entry.get('response_time_ms')

        # Count by severity
        if level == 'ERROR':
            metrics.error_count += 1
        elif level == 'WARNING':
            metrics.warning_count += 1
        elif level == 'CRITICAL':
            metrics.critical_count += 1

        # Track unique IPs if security analysis enabled
        if 'security' in analysis_types and client_ip:
            metrics.unique_ips.add(client_ip)

        # Track endpoint usage if usage analysis enabled
        if 'usage' in analysis_types and endpoint:
            metrics.top_endpoints[endpoint] = metrics.top_endpoints.get(endpoint, 0) + 1

        # Performance analysis
        if 'performance' in analysis_types and response_time:
            if 'response_times' not in metrics.__dict__:
                metrics.response_times = []
            metrics.response_times.append(response_time)

    async def generate_log_insights_report(self, metrics: LogMetrics) -> Dict[str, Any]:
        """Generate comprehensive insights report from log analysis."""
        report = {
            'generated_at': datetime.now(UTC).isoformat(),
            'summary': {
                'total_lines_analyzed': metrics.total_lines,
                'error_rate': (metrics.error_count / max(metrics.total_lines, 1)) * 100,
                'warning_rate': (metrics.warning_count / max(metrics.total_lines, 1)) * 100,
                'critical_rate': (metrics.critical_count / max(metrics.total_lines, 1)) * 100
            },
            'security_insights': {},
            'performance_insights': {},
            'usage_insights': {}
        }

        # Security insights
        if hasattr(metrics, 'unique_ips'):
            report['security_insights'] = {
                'unique_client_ips': len(metrics.unique_ips),
                'potential_security_events': metrics.error_count + metrics.critical_count
            }

        # Performance insights
        if hasattr(metrics, 'response_times') and metrics.response_times:
            response_times = metrics.response_times
            report['performance_insights'] = {
                'avg_response_time_ms': sum(response_times) / len(response_times),
                'max_response_time_ms': max(response_times),
                'min_response_time_ms': min(response_times),
                'response_time_std_dev': (sum((x - (sum(response_times) / len(response_times))) ** 2 for x in response_times) / len(response_times)) ** 0.5
            }

        # Usage insights
        if metrics.top_endpoints:
            sorted_endpoints = sorted(metrics.top_endpoints.items(), key=lambda x: x[1], reverse=True)
            report['usage_insights'] = {
                'most_accessed_endpoints': sorted_endpoints[:10],
                'total_endpoints_tracked': len(metrics.top_endpoints)
            }

        return report

    async def check_log_rotation_health(self) -> Dict[str, Any]:
        """Monitor log rotation and file health."""
        health_status = {
            'status': 'healthy',
            'issues': [],
            'recommendations': []
        }

        try:
            # Check current log file size
            if self.log_file_path.exists():
                file_size_mb = self.log_file_path.stat().st_size / (1024 * 1024)

                if file_size_mb > self.max_file_size_mb * 0.9:
                    health_status['issues'].append(f"Log file approaching max size: {file_size_mb:.2f}MB")
                    health_status['recommendations'].append("Consider increasing log rotation size or frequency")

                # Check if file is writable
                if not os.access(self.log_file_path, os.W_OK):
                    health_status['status'] = 'unhealthy'
                    health_status['issues'].append("Log file is not writable")

            # Check disk space
            disk_usage = shutil.disk_usage(self.log_file_path.parent)
            disk_usage_percent = (disk_usage.used / disk_usage.total) * 100

            if disk_usage_percent > 80:
                health_status['issues'].append(f"Low disk space: {disk_usage_percent:.1f}% used")
                health_status['recommendations'].append("Clean up old log files or increase disk space")

            # Check for corrupted log files
            log_dir = self.log_file_path.parent
            corrupted_files = 0

            for log_file in log_dir.glob(f"{self.log_file_path.stem}.log*"):
                try:
                    with open(log_file, 'r') as f:
                        # Try to read first and last few lines
                        lines = f.readlines()
                        if lines:
                            json.loads(lines[0])  # Test JSON parsing
                            json.loads(lines[-1])
                except (json.JSONDecodeError, IOError):
                    corrupted_files += 1

            if corrupted_files > 0:
                health_status['issues'].append(f"Found {corrupted_files} potentially corrupted log files")
                health_status['recommendations'].append("Review and clean up corrupted log files")

        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['issues'].append(f"Log rotation health check failed: {e}")

        return health_status
```

#### Modern Backup and Recovery with Multi-Destination Strategy
```yaml
# config/backup.yaml
backup:
  # Core backup settings
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  retention_days: 30
  enable_compression: true
  compression_algorithm: "gzip"
  encryption_enabled: true
  encryption_key_file: "/run/secrets/backup_encryption_key"

  # Multi-destination backup strategy
  destinations:
    - name: "local_primary"
      type: "local"
      path: "/var/backups/simulation"
      enabled: true
      retention_days: 30
      priority: 1

    - name: "local_secondary"
      type: "local"
      path: "/mnt/secondary-backups/simulation"
      enabled: true
      retention_days: 90
      priority: 2

    - name: "aws_s3"
      type: "s3"
      bucket: "simulation-backups-prod"
      region: "us-east-1"
      storage_class: "STANDARD_IA"  # Infrequent Access for older backups
      enabled: true
      retention_days: 2555  # 7 years for compliance
      priority: 3
      encryption:
        server_side: true
        kms_key_id: "alias/simulation-backup-key"

    - name: "azure_blob"
      type: "azure"
      container: "simulation-backups"
      account_name: "${AZURE_STORAGE_ACCOUNT}"
      account_key: "${AZURE_STORAGE_KEY}"
      enabled: false  # Enable when needed
      retention_days: 365

  # Backup content configuration
  include:
    - "data/databases/ledger.db"
    - "data/databases/*.db"
    - "config/*.yaml"
    - "config/*.json"
    - "logs/simulation.log*"
    - "src/**/*.py"
    - "scripts/**/*"
    - "tests/**/*"

  exclude:
    - "**/__pycache__/**"
    - "**/*.pyc"
    - "**/node_modules/**"
    - "**/.pytest_cache/**"
    - "**/*.tmp"
    - "**/test_*"
    - "logs/archive/*"
    - "data/temp/**"

  # Database-specific backup settings
  database_backups:
    sqlite:
      enable_consistency_check: true
      enable_optimization_before_backup: true
      custom_pre_backup_commands:
        - "sqlite3 data/databases/ledger.db 'VACUUM;'"
        - "sqlite3 data/databases/ledger.db 'REINDEX;'"

    postgresql:
      enable_logical_backup: true
      enable_base_backup: false
      custom_pre_backup_commands:
        - "psql -c 'CHECKPOINT;'"
        - "psql -c 'VACUUM FREEZE;'"

  # Verification and monitoring
  verification:
    enable_backup_verification: true
    verification_schedule: "0 6 * * *"  # 6 AM UTC
    verify_database_integrity: true
    verify_file_checksums: true
    max_verification_time_minutes: 30

  # Recovery configuration
  recovery:
    enable_automated_recovery: false  # Manual recovery for safety
    recovery_test_schedule: "0 1 1 * *"  # Monthly recovery testing
    recovery_point_objective_minutes: 60  # RPO: 1 hour
    recovery_time_objective_minutes: 120  # RTO: 2 hours

  # Monitoring and alerting
  monitoring:
    enable_backup_monitoring: true
    alert_on_backup_failure: true
    alert_on_verification_failure: true
    backup_size_threshold_gb: 10
    backup_duration_threshold_minutes: 60
    slack_webhook_url: "${BACKUP_SLACK_WEBHOOK}"
    pagerduty_routing_key: "${BACKUP_PAGERDUTY_KEY}"
```

## Documentation Best Practices

### Code Documentation

#### Docstring Standards
```python
def generate_threat_signature(
    anomaly_data: List[Dict[str, Any]],
    anomaly_ips: List[str],
    anomaly_scores: List[float],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a threat signature from detected anomalies.

    This function creates a standardized threat signature that can be shared
    across the decentralized network for consensus validation.

    Args:
        anomaly_data: List of anomaly records with full context
        anomaly_ips: Source IP addresses associated with anomalies
        anomaly_scores: Confidence scores for each anomaly (0.0 to 1.0)
        context: Additional context information for signature generation

    Returns:
        Dictionary containing:
        - signature_id: Unique identifier for the signature
        - threat_type: Classified type of threat
        - confidence: Overall confidence score
        - features: Key features used for detection
        - metadata: Additional metadata and timestamps

    Raises:
        ValueError: If input data is invalid or insufficient
        RuntimeError: If signature generation fails due to system issues

    Example:
        >>> anomalies = [{"source": "192.168.1.100", "score": 0.95}]
        >>> signature = generate_threat_signature(anomalies, ["192.168.1.100"], [0.95])
        >>> print(signature['threat_type'])
        'ddos_attack'
    """
    pass
```

### API Documentation

#### OpenAPI/Swagger Documentation
```yaml
# api_docs.yaml
openapi: 3.0.3
info:
  title: Decentralized AI Simulation API
  version: "2.45.0"
  description: API for managing and monitoring the decentralized AI simulation

paths:
  /health:
    get:
      summary: Get system health status
      responses:
        '200':
          description: System is healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthStatus'

components:
  schemas:
    HealthStatus:
      type: object
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        message:
          type: string
        timestamp:
          type: number
        checks:
          type: array
          items:
            $ref: '#/components/schemas/HealthCheck'
```

## Continuous Integration and Deployment

### CI/CD Pipeline Best Practices

#### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: ./scripts/deploy.sh production
```

## Troubleshooting Best Practices

### Systematic Debugging Approach

```python
def systematic_debugging(error, context):
    """Systematic approach to debugging issues."""

    # 1. Gather context
    logger.info(f"Debugging error: {error}", extra={'context': context})

    # 2. Reproduce the issue
    try:
        reproduce_issue(context)
    except Exception as e:
        logger.error(f"Failed to reproduce: {e}")

    # 3. Isolate the problem
    isolated_cause = isolate_problem(error, context)

    # 4. Implement fix
    fix = implement_fix(isolated_cause)

    # 5. Test fix
    test_fix(fix, context)

    # 6. Document solution
    document_solution(error, fix, context)

    return fix
```

### Log Analysis

```python
def analyze_logs_for_patterns(log_file, time_window_hours=24):
    """Analyze logs for error patterns and performance issues."""

    import re
    from datetime import datetime, timedelta

    patterns = {
        'errors': r'ERROR.*',
        'warnings': r'WARNING.*',
        'performance': r'Processing time: (\d+\.?\d*)ms',
        'memory': r'Memory usage: (\d+)MB'
    }

    insights = {}
    cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

    with open(log_file, 'r') as f:
        for line in f:
            # Parse timestamp and check if within window
            # Extract patterns and analyze
            pass

    return insights
```

## Technology Stack Integration

### Mesa 3.3.0 Integration Best Practices

#### Agent-Based Modeling with Modern Mesa Features
```python
# Modern Mesa agent implementation with enhanced features
import mesa
import asyncio
from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np

@dataclass
class SimulationConfig:
    """Mesa 3.3.0 compatible simulation configuration."""
    width: int = 50
    height: int = 50
    num_agents: int = 100
    max_steps: int = 1000
    enable_visualization: bool = True
    visualization_port: int = 8521

class TrafficAgent(mesa.Agent):
    """Enhanced traffic agent with Mesa 3.3.0 features."""

    def __init__(self, unique_id: int, model: mesa.Model, agent_type: str = "normal"):
        super().__init__(unique_id, model)
        self.agent_type = agent_type
        self.anomaly_score = 0.0
        self.connections = set()
        self.message_queue = asyncio.Queue()
        self.processed_messages = 0

        # Mesa 3.3.0 specific attributes
        self.pos = None  # Will be set when added to grid
        self.data_collector = None

    async def process_traffic_async(self):
        """Process traffic data asynchronously (Mesa 3.3.0 compatible)."""
        while not self.message_queue.empty():
            message = await self.message_queue.get()
            await self._analyze_traffic_message(message)
            self.processed_messages += 1

    async def _analyze_traffic_message(self, message: Dict[str, Any]):
        """Analyze individual traffic message for anomalies."""
        # Use Ray for distributed analysis if available
        if hasattr(self.model, 'ray_enabled') and self.model.ray_enabled:
            # Ray task for distributed processing
            future = analyze_traffic_distributed.remote(message, self.model.threshold)
            result = await asyncio.get_event_loop().run_in_executor(
                None, ray.get, future
            )
            self.anomaly_score = max(self.anomaly_score, result)
        else:
            # Local analysis
            self.anomaly_score = self._calculate_anomaly_score(message)

    def _calculate_anomaly_score(self, message: Dict[str, Any]) -> float:
        """Calculate anomaly score for traffic message."""
        # Simple anomaly detection based on message characteristics
        score = 0.0

        # Check for unusual packet sizes
        if message.get('bytes', 0) > 1000000:  # 1MB threshold
            score += 0.5

        # Check for unusual protocols
        if message.get('protocol') not in ['TCP', 'UDP', 'ICMP']:
            score += 0.3

        # Check for suspicious ports
        suspicious_ports = [22, 23, 3389]  # SSH, Telnet, RDP
        if message.get('port') in suspicious_ports:
            score += 0.4

        return min(score, 1.0)

    def step(self):
        """Mesa 3.3.0 step method - called each simulation step."""
        # Move to random adjacent cell
        if self.pos is not None:
            neighbors = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            if neighbors:
                new_position = self.random.choice(neighbors)
                self.model.grid.move_agent(self, new_position)

        # Process any pending messages
        if hasattr(self, 'model') and hasattr(self.model, 'ray_enabled'):
            # Use asyncio for message processing in Mesa 3.3.0
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    loop.run_until_complete(self.process_traffic_async())
            except RuntimeError:
                # Event loop not available, process synchronously
                pass

class TrafficSimulation(mesa.Model):
    """Enhanced traffic simulation model using Mesa 3.3.0."""

    def __init__(self, config: SimulationConfig):
        super().__init__()
        self.config = config
        self.schedule = SimultaneousActivation(self)
        self.grid = MultiGrid(config.width, config.height, torus=True)

        # Ray integration for distributed processing
        self.ray_enabled = config.enable_ray_integration if hasattr(config, 'enable_ray_integration') else False
        self.threshold = 0.7

        # Enhanced data collection (Mesa 3.3.0 feature)
        self.datacollector = DataCollector(
            model_reporters={
                "Total Agents": lambda m: m.schedule.get_agent_count(),
                "Anomalous Agents": lambda m: len([a for a in m.schedule.agents if a.anomaly_score > 0.5]),
                "Average Anomaly Score": lambda m: np.mean([a.anomaly_score for a in m.schedule.agents]) if m.schedule.agents else 0
            },
            agent_reporters={
                "Anomaly Score": lambda a: a.anomaly_score,
                "Processed Messages": lambda a: a.processed_messages,
                "Position": lambda a: a.pos
            }
        )

        # Create agents
        for i in range(config.num_agents):
            agent = TrafficAgent(i, self)
            self.schedule.add(agent)

            # Add to random grid position
            x = self.random.randrange(config.width)
            y = self.random.randrange(config.height)
            self.grid.place_agent(agent, (x, y))

    def step(self):
        """Advance the model by one step."""
        # Collect data before step (Mesa 3.3.0 best practice)
        self.datacollector.collect(self)

        # Execute agent steps
        self.schedule.step()

        # Process any inter-agent communication
        if self.ray_enabled:
            self._process_distributed_communication()

    def _process_distributed_communication(self):
        """Process communication using Ray for distributed computing."""
        # Implementation would use Ray for distributed message passing
        pass

# Mesa 3.3.0 visualization integration
def launch_mesa_visualization(model: TrafficSimulation):
    """Launch Mesa 3.3.0 visualization server."""
    from mesa.visualization.modules import CanvasGrid, ChartModule
    from mesa.visualization.ModularVisualization import ModularServer

    def agent_portrayal(agent):
        """Define how agents are portrayed in visualization."""
        portrayal = {
            "Shape": "circle",
            "Color": "blue",
            "Filled": "true",
            "Layer": 0,
            "r": 0.5
        }

        # Color based on anomaly score
        if agent.anomaly_score > 0.7:
            portrayal["Color"] = "red"
        elif agent.anomaly_score > 0.4:
            portrayal["Color"] = "orange"

        return portrayal

    # Create visualization elements
    grid = CanvasGrid(agent_portrayal, model.config.width, model.config.height, 500, 500)

    chart = ChartModule([
        {"Label": "Anomalous Agents", "Color": "Red"},
        {"Label": "Average Anomaly Score", "Color": "Blue"}
    ])

    # Launch server (Mesa 3.3.0 compatible)
    server = ModularServer(
        model,
        visualization_elements=[grid, chart],
        title="Decentralized AI Traffic Simulation",
        model_params={"config": model.config}
    )

    server.port = model.config.visualization_port
    server.launch()
```

### Ray 2.45.0 Distributed Computing Integration

#### Modern Ray Patterns for Distributed Simulation
```python
# Ray 2.45.0 integration with enhanced distributed computing
import ray
import asyncio
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from ray import serve
from ray.serve import Application

@ray.remote
class DistributedAnomalyDetector:
    """Ray actor for distributed anomaly detection."""

    def __init__(self, model_version: str = "v2.45.0"):
        self.model_version = model_version
        self.detection_history = []

    async def detect_anomalies_distributed(
        self,
        traffic_batch: List[Dict[str, Any]],
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Distributed anomaly detection using Ray 2.45.0 features.

        Features:
        - Ray Core for distributed computing
        - Ray Serve for scalable deployment
        - Enhanced async support
        - Automatic scaling and load balancing
        """
        anomalies = []

        for record in traffic_batch:
            # Use Ray's enhanced async capabilities
            anomaly_score = await self._analyze_record_async(record)

            if anomaly_score >= threshold:
                record['anomaly_score'] = anomaly_score
                record['detected_by'] = 'ray_distributed'
                record['model_version'] = self.model_version
                anomalies.append(record)

        self.detection_history.extend(anomalies)
        return anomalies

    async def _analyze_record_async(self, record: Dict[str, Any]) -> float:
        """Analyze single record asynchronously."""
        # Simulate async processing
        await asyncio.sleep(0.001)  # Simulate I/O or computation

        # Simple anomaly detection logic
        score = 0.0

        if record.get('bytes', 0) > 100000:
            score += 0.6
        if record.get('protocol') not in ['TCP', 'UDP']:
            score += 0.4

        return min(score, 1.0)

# Ray Serve deployment for scalable anomaly detection
@serve.deployment(num_replicas=3, ray_actor_options={"num_cpus": 0.5})
class AnomalyDetectionService:
    """Ray Serve deployment for scalable anomaly detection."""

    def __init__(self):
        self.detectors = [
            DistributedAnomalyDetector.remote(f"v2.45.0-{i}")
            for i in range(3)
        ]

    async def __call__(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming anomaly detection requests."""
        traffic_data = request.get('traffic_data', [])
        threshold = request.get('threshold', 0.7)

        # Distribute work across Ray actors
        batch_size = len(traffic_data) // len(self.detectors)
        batches = [
            traffic_data[i:i + batch_size]
            for i in range(0, len(traffic_data), batch_size)
        ]

        # Process batches in parallel
        futures = [
            detector.detect_anomalies_distributed.remote(batch, threshold)
            for detector, batch in zip(self.detectors, batches)
        ]

        # Collect results
        results = await asyncio.gather(*[f for f in futures])

        all_anomalies = []
        for result in results:
            all_anomalies.extend(result)

        return {
            'anomalies': all_anomalies,
            'total_processed': len(traffic_data),
            'anomalies_detected': len(all_anomalies),
            'processing_node': ray.get_runtime_context().node_id.hex()
        }

# Initialize Ray cluster with modern configuration
def initialize_ray_cluster():
    """Initialize Ray 2.45.0 cluster with optimal settings."""
    ray.init(
        address="auto",  # Auto-detect or start local cluster
        num_cpus=4,
        num_gpus=0,
        object_store_memory=1073741824,  # 1GB
        dashboard_host="0.0.0.0",
        dashboard_port=8265,
        include_dashboard=True,
        ignore_reinit_error=True
    )

    # Deploy Ray Serve application
    app = AnomalyDetectionService.bind()
    serve.run(app, host="0.0.0.0", port=8000)

# Ray workflow for complex distributed tasks
@ray.remote
def distributed_simulation_workflow(traffic_data: List[Dict], steps: int = 10):
    """Complex distributed workflow using Ray 2.45.0."""
    results = []

    for step in range(steps):
        # Parallel processing step
        futures = [
            process_traffic_batch.remote(data)
            for data in np.array_split(traffic_data, min(4, len(traffic_data)))
        ]

        step_results = ray.get(futures)
        results.extend(step_results)

    return results
```

### Streamlit 1.39.0 Modern UI Integration

#### Enhanced Streamlit Dashboard with Real-time Updates
```python
# Modern Streamlit 1.39.0 dashboard with enhanced features
import streamlit as st
import asyncio
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, UTC, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class ModernStreamlitDashboard:
    """Enhanced Streamlit dashboard with real-time capabilities."""

    def __init__(self):
        self.config = {
            'server_port': 8501,
            'refresh_interval_ms': 5000,
            'max_data_points': 1000,
            'enable_websocket_compression': True
        }

    def render_dashboard(self):
        """Render the main dashboard with Streamlit 1.39.0 features."""
        st.set_page_config(
            page_title="Decentralized AI Simulation Dashboard",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Enhanced sidebar with Streamlit 1.39.0 features
        with st.sidebar:
            st.title("🔍 Simulation Control")

            # Modern form handling
            with st.form("simulation_config"):
                st.subheader("Simulation Parameters")

                threshold = st.slider(
                    "Anomaly Detection Threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.05,
                    help="Adjust the sensitivity of anomaly detection"
                )

                enable_ray = st.checkbox(
                    "Enable Ray Distributed Processing",
                    value=True,
                    help="Use Ray for distributed computing"
                )

                max_steps = st.number_input(
                    "Maximum Simulation Steps",
                    min_value=100,
                    max_value=10000,
                    value=1000,
                    step=100
                )

                submitted = st.form_submit_button("Apply Configuration")

                if submitted:
                    st.success("Configuration updated!")
                    st.rerun()

        # Main content area
        st.title("🚀 Decentralized AI Simulation Platform")
        st.markdown("Real-time monitoring and control dashboard")

        # Real-time metrics with Streamlit 1.39.0
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            with st.container():
                st.metric(
                    label="Active Agents",
                    value=self.get_active_agents_count(),
                    delta=self.get_agents_delta()
                )

        with col2:
            with st.container():
                st.metric(
                    label="Anomalies Detected",
                    value=self.get_anomalies_count(),
                    delta=self.get_anomalies_delta(),
                    delta_color="inverse"
                )

        with col3:
            with st.container():
                st.metric(
                    label="System Health",
                    value=f"{self.get_system_health()}%",
                    delta=self.get_health_delta()
                )

        with col4:
            with st.container():
                st.metric(
                    label="Processing Rate",
                    value=f"{self.get_processing_rate()}/s",
                    delta=self.get_processing_delta()
                )

        # Enhanced charts with Plotly integration
        tab1, tab2, tab3 = st.tabs(["📊 Real-time Data", "🔍 Anomaly Analysis", "⚙️ System Status"])

        with tab1:
            self.render_realtime_charts()

        with tab2:
            self.render_anomaly_analysis()

        with tab3:
            self.render_system_status()

    def render_realtime_charts(self):
        """Render real-time data visualization."""
        st.subheader("Real-time Traffic Analysis")

        # Sample data for demonstration
        timestamps = pd.date_range(
            start=datetime.now(UTC) - timedelta(hours=1),
            end=datetime.now(UTC),
            freq='1min'
        )

        # Generate sample traffic data
        traffic_data = pd.DataFrame({
            'timestamp': timestamps,
            'traffic_volume': np.random.randint(100, 1000, len(timestamps)),
            'anomaly_score': np.random.random(len(timestamps)) * 0.3,
            'active_agents': np.random.randint(50, 200, len(timestamps))
        })

        # Modern Plotly chart with Streamlit 1.39.0
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=traffic_data['timestamp'],
            y=traffic_data['traffic_volume'],
            mode='lines+markers',
            name='Traffic Volume',
            line=dict(color='#2E86AB', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=traffic_data['timestamp'],
            y=traffic_data['anomaly_score'] * 1000,  # Scale for visibility
            mode='lines',
            name='Anomaly Score',
            line=dict(color='#A23B72', width=2),
            yaxis='y2'
        ))

        fig.update_layout(
            title='Real-time Traffic and Anomaly Analysis',
            xaxis_title='Time',
            yaxis_title='Traffic Volume',
            yaxis2=dict(title='Anomaly Score', overlaying='y', side='right'),
            hovermode='x unified',
            template='plotly_white'
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_anomaly_analysis(self):
        """Render detailed anomaly analysis."""
        st.subheader("Anomaly Detection Analysis")

        # Sample anomaly data
        anomalies = pd.DataFrame({
            'timestamp': pd.date_range(start=datetime.now(UTC) - timedelta(hours=2), periods=10),
            'source_ip': [f'192.168.1.{i}' for i in range(10, 20)],
            'anomaly_score': np.random.random(10) * 0.8 + 0.2,
            'threat_type': np.random.choice(['DDoS', 'Port Scan', 'Data Exfiltration'], 10),
            'severity': np.random.choice(['Low', 'Medium', 'High'], 10)
        })

        # Enhanced DataFrame display with Streamlit 1.39.0
        st.dataframe(
            anomalies,
            use_container_width=True,
            column_config={
                'anomaly_score': st.column_config.ProgressColumn(
                    'Anomaly Score',
                    min_value=0.0,
                    max_value=1.0,
                    format='%.2f'
                ),
                'severity': st.column_config.SelectboxColumn(
                    'Severity',
                    options=['Low', 'Medium', 'High']
                )
            }
        )

        # Anomaly distribution chart
        fig = px.pie(
            anomalies,
            names='threat_type',
            title='Anomaly Types Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_system_status(self):
        """Render comprehensive system status."""
        st.subheader("System Health and Performance")

        # System health indicators
        health_data = {
            'Component': ['Application', 'Database', 'Ray Cluster', 'Streamlit UI'],
            'Status': ['Healthy', 'Healthy', 'Healthy', 'Healthy'],
            'Response Time (ms)': [45, 23, 67, 12],
            'Uptime': ['99.9%', '99.8%', '99.7%', '99.9%']
        }

        status_df = pd.DataFrame(health_data)

        # Color coding for status
        def color_status(val):
            if val == 'Healthy':
                return '🟢'
            return '🔴'

        status_df['Status'] = status_df['Status'].apply(color_status) + ' ' + status_df['Status']

        st.dataframe(status_df, use_container_width=True, hide_index=True)

        # Resource utilization chart
        resources = pd.DataFrame({
            'Resource': ['CPU', 'Memory', 'Disk', 'Network'],
            'Utilization (%)': [45, 67, 23, 34]
        })

        fig = px.bar(
            resources,
            x='Resource',
            y='Utilization (%)',
            title='Resource Utilization',
            color='Utilization (%)',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Mock data methods (replace with actual data sources)
    def get_active_agents_count(self) -> int:
        return 156

    def get_agents_delta(self) -> str:
        return "+12"

    def get_anomalies_count(self) -> int:
        return 23

    def get_anomalies_delta(self) -> str:
        return "+5"

    def get_system_health(self) -> float:
        return 98.7

    def get_health_delta(self) -> str:
        return "+0.3%"

    def get_processing_rate(self) -> int:
        return 1247

    def get_processing_delta(self) -> str:
        return "+156"

# Launch the dashboard
dashboard = ModernStreamlitDashboard()
dashboard.render_dashboard()
```

## ❓ Best Practices FAQ

### Code Quality and Development

**Q: What Python version should I use for new development?**
```
A: Use Python 3.11+ for all new development to leverage:
   - Enhanced type hints and generic types
   - Structural pattern matching (match/case)
   - Improved async/await performance
   - Better error messages and debugging
```

**Q: How do I implement proper error handling?**
```python
# ✅ Good: Comprehensive error handling
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}", extra={"context": context})
    raise CustomError("User-friendly message", context) from e
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise

# ❌ Bad: Generic exception handling
try:
    result = risky_operation()
except:
    pass  # Silent failure - never do this!
```

**Q: What's the recommended commit message format?**
```
A: Use conventional commits format:
   feat: add new anomaly detection algorithm
   fix: resolve database connection leak
   docs: update API documentation for v2.45.0
   perf: optimize signature validation by 40%
   test: add integration tests for consensus mechanism
   refactor: extract configuration validation logic
```

### Configuration Management

**Q: How do I handle configuration in different environments?**
```yaml
# Development (config/development.yaml)
environment: development
logging:
  level: DEBUG
  enable_console: true

# Production (config/production.yaml)
environment: production
logging:
  level: WARNING
  enable_console: false
  enable_remote: true

# Override with environment variables
export ENVIRONMENT=production
export LOGGING_LEVEL=WARNING
```

**Q: What's the best way to validate configuration?**
```python
# ✅ Good: Pydantic model validation
from pydantic import BaseModel, Field, validator

class AppConfig(BaseModel):
    database_url: str = Field(..., regex=r'postgresql://.+')
    max_workers: int = Field(ge=1, le=100, default=4)

    @validator('database_url')
    def validate_db_url(cls, v):
        if 'localhost' in v and os.getenv('ENVIRONMENT') == 'production':
            raise ValueError('Cannot use localhost in production')
        return v

# ❌ Bad: Manual validation
def validate_config(config):
    if not isinstance(config.get('max_workers'), int):
        raise ValueError("max_workers must be int")
```

### Testing

**Q: What testing strategy should I follow?**
```
A: Implement a comprehensive testing strategy:
   1. Unit tests: Test individual functions/classes (70%+ coverage)
   2. Integration tests: Test component interactions
   3. Performance tests: Validate performance requirements
   4. End-to-end tests: Test complete workflows
   5. Security tests: Validate security controls
```

**Q: How do I write effective test fixtures?**
```python
# ✅ Good: Reusable, well-structured fixtures
@pytest.fixture
def sample_traffic_data():
    """Generate realistic traffic data for testing."""
    return [
        TrafficRecord(
            timestamp=datetime.now(UTC),
            source_ip="192.168.1.100",
            destination_ip="10.0.0.50",
            bytes_transferred=1500,
            protocol="TCP"
        )
    ]

@pytest.fixture
def mock_database():
    """Mock database with realistic behavior."""
    with patch('database.DatabaseLedger') as mock_db:
        mock_db.return_value.read_ledger.return_value = []
        yield mock_db

# ❌ Bad: Hardcoded test data
def test_something():
    data = {"ip": "192.168.1.1", "bytes": 100}
    # Test implementation
```

### Deployment

**Q: What's the recommended deployment strategy?**
```
A: Follow modern deployment best practices:
   1. Use multi-stage Docker builds for smaller images
   2. Implement proper health checks and readiness probes
   3. Use Kubernetes for production orchestration
   4. Implement blue-green or rolling deployments
   5. Set up comprehensive monitoring and alerting
```

**Q: How do I handle secrets securely?**
```yaml
# ✅ Good: External secret management
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secrets
spec:
  secretStoreRef:
    name: aws-secret-store
    kind: SecretStore
  data:
  - secretKey: database-password
    remoteRef:
      key: prod/simulation/database-password

# ❌ Bad: Plain text secrets
environment:
  - DB_PASSWORD=super-secret-password
```

### Performance

**Q: How do I optimize database performance?**
```python
# ✅ Good: Batch operations and connection pooling
async def bulk_insert_traffic_data(records):
    async with db_pool.acquire() as conn:
        await conn.executemany(
            "INSERT INTO traffic (timestamp, source_ip, bytes) VALUES ($1, $2, $3)",
            [(r.timestamp, r.source_ip, r.bytes) for r in records]
        )

# ❌ Bad: Individual inserts
for record in records:
    await conn.execute("INSERT INTO traffic ...", record.timestamp, ...)
```

**Q: What's the best approach for caching?**
```python
# ✅ Good: Multi-level caching strategy
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # Fast in-memory
        self.l2_cache = {}  # Compressed on-disk
        self.cache_stats = {'hits': 0, 'misses': 0}

    async def get(self, key):
        # Check L1 first, then L2
        # Implement LRU eviction
        # Track cache performance
        pass

# ❌ Bad: No caching strategy
def expensive_operation():
    # Recalculate every time
    return expensive_calculation()
```

### Security

**Q: How do I implement proper input validation?**
```python
# ✅ Good: Defense in depth validation
class SecureInputValidator:
    def __init__(self):
        self.sanitizer = bleach.Cleaner()
        self.ip_validator = ipaddress.ip_network

    def validate_traffic_record(self, data):
        # 1. Schema validation with Pydantic
        validated = TrafficRecord(**data)

        # 2. Business logic validation
        if validated.source_ip == validated.destination_ip:
            raise ValueError("Source and destination cannot be same")

        # 3. Security validation
        if self._is_malicious_content(data.get('payload', '')):
            raise SecurityError("Malicious content detected")

        return validated

# ❌ Bad: Minimal validation
def process_data(data):
    # Assume data is valid
    return data
```

**Q: What's the recommended authentication approach?**
```
A: Implement multi-layered authentication:
   1. JWT tokens for API access
   2. OAuth2/OIDC for user authentication
   3. API keys for service-to-service communication
   4. Certificate-based authentication for high security
   5. Multi-factor authentication for admin access
```

### Monitoring and Observability

**Q: What metrics should I monitor?**
```
A: Monitor these key metrics:
   - Application: Response time, error rate, throughput
   - System: CPU, memory, disk, network utilization
   - Business: Active users, conversion rates, feature usage
   - Security: Failed logins, suspicious activities, data access
   - Infrastructure: Container health, service dependencies
```

**Q: How do I implement structured logging?**
```python
# ✅ Good: Structured logging with context
logger.info(
    "Anomaly detected",
    extra={
        'event_type': 'security',
        'anomaly_score': 0.95,
        'source_ip': '192.168.1.100',
        'threat_type': 'ddos',
        'trace_id': request.trace_id,
        'user_id': user.id
    }
)

# ❌ Bad: Unstructured logging
logger.info(f"Anomaly detected for IP {ip}")
```

## Cross-References and Related Documentation

### Documentation Navigation

| Section | Related Files | Purpose |
|---------|---------------|---------|
| **Project Overview** | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | High-level system architecture and capabilities |
| **Technical Design** | [design.md](design.md) | Detailed technical specifications and architecture decisions |
| **Migration Guide** | [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Upgrade procedures and compatibility information |
| **Performance Optimization** | [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md) | Detailed performance tuning and optimization strategies |
| **Troubleshooting Guide** | [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md) | Common issues and solutions |
| **Scripts Documentation** | [SCRIPTS_README.md](SCRIPTS_README.md) | Usage instructions for deployment and maintenance scripts |

### Configuration File References

- **Application Configuration**: `config/config.yaml` - Main application settings
- **Development Configuration**: `config/development.yaml` - Development-specific overrides
- **Production Configuration**: `config/production.yaml` - Production-optimized settings
- **Security Configuration**: `config/security.yaml` - Security policies and settings
- **Backup Configuration**: `config/backup.yaml` - Backup and recovery settings
- **Prometheus Configuration**: `config/prometheus.yml` - Monitoring configuration

### API and Integration References

- **Mesa Visualization API**: `http://localhost:8521` - Agent-based simulation visualization
- **Ray Dashboard**: `http://localhost:8265` - Distributed computing cluster management
- **Streamlit Dashboard**: `http://localhost:8501` - Main application dashboard
- **Prometheus Metrics**: `http://localhost:9090` - System metrics and monitoring
- **Grafana Dashboards**: `http://localhost:3000` - Visualization and alerting

### Development and Testing Resources

- **Requirements Files**: `requirements.txt`, `requirements-dev.txt` - Python dependencies
- **Test Suites**: `tests/` directory - Unit and integration tests
- **CI/CD Configuration**: `.github/workflows/` - GitHub Actions workflows
- **Docker Configuration**: `Dockerfile`, `docker-compose.yml` - Container definitions
- **Kubernetes Manifests**: `k8s/` directory - Production deployment configuration

## Summary of Enhanced Best Practices

1. **Modern Python Development**: Leverage Python 3.11+ features, Pydantic models, and async/await patterns
2. **Enhanced Configuration Management**: Use structured configuration with validation and environment-specific settings
3. **Advanced Security**: Implement zero-trust architecture, comprehensive threat detection, and modern authentication
4. **Scalable Deployment**: Utilize modern containerization, Kubernetes orchestration, and intelligent autoscaling
5. **Comprehensive Monitoring**: Implement OpenTelemetry tracing, structured logging, and proactive alerting
6. **Technology Integration**: Seamlessly integrate Mesa 3.3.0, Ray 2.45.0, and Streamlit 1.39.0 capabilities
7. **Automated Maintenance**: Deploy intelligent maintenance with health monitoring and automated recovery
8. **Documentation Excellence**: Maintain comprehensive, cross-referenced documentation with practical examples

Following these enhanced best practices ensures a robust, maintainable, and scalable decentralized AI simulation platform that leverages modern technologies effectively while maintaining security, performance, and operational excellence.