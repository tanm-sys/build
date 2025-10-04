# Configuration Management Guide

## Overview

This guide provides comprehensive instructions for managing configuration across the decentralized AI simulation project. It covers configuration file organization, environment-specific settings, validation procedures, and template usage.

## Configuration File Organization

### Directory Structure

```
config/
├── 📄 config.yaml                 # Main configuration file
├── 📄 requirements.txt            # Python dependencies
├── 📄 .env.example               # Environment variables template
├── 📁 environments/              # Environment-specific configurations
│   ├── 📄 base.yaml             # Base configuration shared across environments
│   ├── 📄 development.env       # Development environment settings
│   └── 📄 production.env        # Production environment settings
└── 📁 templates/                 # Configuration templates
    └── 📄 .env.example          # Environment variables template
```

### Configuration Hierarchy

The configuration system follows a hierarchy of precedence:

1. **Environment Variables** (highest priority)
2. **Environment-specific files** (`development.env`, `production.env`)
3. **Main configuration file** (`config.yaml`)
4. **Base configuration** (`base.yaml`)
5. **Default values** (lowest priority)

## Main Configuration File (`config.yaml`)

### Structure Overview

```yaml
# Core application settings
environment: development
project:
  name: "Decentralized AI Simulation"
  version: "1.0.0"

# Database configuration
database:
  path: "data/databases/ledger.db"
  connection_pool_size: 5
  timeout: 30
  check_same_thread: false

# Simulation parameters
simulation:
  default_agents: 50
  default_steps: 100
  grid_width: 10
  grid_height: 10
  step_delay: 0.1
  anomaly_rate: 0.05
  use_parallel_threshold: 50

# Agent behavior settings
agent:
  initial_wealth: 1
  initial_trust_score: 100
  trust_increment: 10
  trust_decrement: 20
  blacklist_threshold: 50
  trade_probability: 0.1
  move_probability: 0.5

# Logging configuration
logging:
  level: "INFO"
  file: "logs/simulation.log"
  max_bytes: 10485760
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# User interface settings
streamlit:
  page_title: "Decentralized AI Simulation"
  layout: "wide"
  agent_slider_min: 10
  agent_slider_max: 200
  agent_slider_default: 50
  anomaly_slider_min: 0.0
  anomaly_slider_max: 0.1
  anomaly_slider_default: 0.05
  steps_slider_min: 10
  steps_slider_max: 100
  steps_slider_default: 50
  cache_ttl: 5

# Monitoring and health checks
monitoring:
  health_check_interval: 30
  metrics_port: 8000
  enable_prometheus: false

# Performance optimization
performance:
  enable_caching: true
  cache_size_mb: 100
  max_workers: 4

# Security settings
security:
  enable_rate_limiting: true
  rate_limit_requests_per_minute: 100
  cors_origins: ["http://localhost:8501"]

# Development settings (only used in development)
development:
  debug_mode: true
  enable_profiling: false
  show_tracebacks: true
```

## Environment-Specific Configuration

### Development Environment (`environments/development.env`)

```yaml
# Development-specific settings
environment: development

# Database settings for development
database:
  path: "data/databases/ledger.db"
  connection_pool_size: 5
  timeout: 15
  check_same_thread: false

# Logging optimized for development
logging:
  level: "DEBUG"
  file: "logs/simulation.log"
  max_bytes: 5242880  # 5MB
  backup_count: 3
  enable_console_output: true

# Development debugging features
development:
  debug_mode: true
  enable_profiling: false
  show_tracebacks: true
  hot_reload: true

# Reduced resource usage for development
simulation:
  default_agents: 25
  default_steps: 50
  use_parallel_threshold: 100

# Monitoring for development
monitoring:
  health_check_interval: 15
  enable_prometheus: false
  enable_detailed_metrics: true
```

### Production Environment (`environments/production.env`)

```yaml
# Production-specific settings
environment: production

# Production database settings
database:
  path: "/var/lib/simulation/ledger.db"
  connection_pool_size: 20
  timeout: 60
  check_same_thread: false
  retry_attempts: 3

# Production logging
logging:
  level: "WARNING"
  file: "/var/log/simulation/simulation.log"
  max_bytes: 104857600  # 100MB
  backup_count: 10
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Production monitoring
monitoring:
  health_check_interval: 30
  metrics_port: 8000
  enable_prometheus: true
  enable_detailed_metrics: true

# Production performance settings
performance:
  enable_caching: true
  cache_size_mb: 500
  max_workers: 8

# Production security
security:
  enable_rate_limiting: true
  rate_limit_requests_per_minute: 1000
  cors_origins: []
```

## Environment Variables

### Template File (`.env.example`)

```bash
# Project Configuration
PROJECT_NAME="Decentralized AI Simulation"
PROJECT_VERSION="1.0.0"
ENVIRONMENT="development"

# Database Configuration
DATABASE_PATH="data/databases/ledger.db"
DATABASE_CONNECTION_POOL_SIZE=5
DATABASE_TIMEOUT=30

# Simulation Parameters
SIMULATION_DEFAULT_AGENTS=50
SIMULATION_DEFAULT_STEPS=100
SIMULATION_ANOMALY_RATE=0.05

# Ray Distributed Computing
RAY_ENABLE=true
RAY_NUM_CPUS=4
RAY_OBJECT_STORE_MEMORY=2147483648

# Logging Configuration
LOGGING_LEVEL=INFO
LOGGING_FILE=logs/simulation.log
LOGGING_MAX_BYTES=10485760

# Streamlit Dashboard
STREAMLIT_SERVER_PORT=8501
STREAMLIT_PAGE_TITLE="Decentralized AI Simulation"

# Monitoring and Health Checks
MONITORING_HEALTH_CHECK_INTERVAL=30
MONITORING_ENABLE_PROMETHEUS=false
MONITORING_METRICS_PORT=8000

# Performance Optimization
PERFORMANCE_ENABLE_CACHING=true
PERFORMANCE_CACHE_SIZE_MB=100
PERFORMANCE_MAX_WORKERS=4

# Security Settings
SECURITY_ENABLE_RATE_LIMITING=true
SECURITY_RATE_LIMIT_REQUESTS_PER_MINUTE=100
```

### Usage Instructions

**Create environment file:**
```bash
cp .env.example .env
# Edit .env with your specific settings
```

**Override specific settings:**
```bash
export DATABASE_PATH="/custom/path/ledger.db"
export SIMULATION_DEFAULT_AGENTS=100
python decentralized_ai_simulation.py
```

## Configuration Access Patterns

### Basic Configuration Access

```python
from decentralized_ai_simulation.src.config.config_manager import get_config

# Get configuration values with dot notation
db_path = get_config('database.path')
agent_count = get_config('simulation.default_agents')
log_level = get_config('logging.level', 'INFO')  # With default

# Check environment
if get_config('environment') == 'production':
    print("Running in production mode")
```

### Type-Safe Configuration Access

```python
# Get with validation and type checking
port = get_config_loader().get_config_with_validation(
    key='monitoring.metrics_port',
    expected_type=int,
    default=8000,
    min_val=1024,
    max_val=65535
)

# Validate configuration values
is_valid = get_config_loader().validate_config_value(
    key='database.timeout',
    value=30,
    expected_type=int
)
```

### Environment-Specific Access

```python
from decentralized_ai_simulation.src.config.config_manager import ConfigLoader

# Load environment-specific configuration
if get_config('environment') == 'production':
    config = ConfigLoader('config/environments/production.env')
else:
    config = ConfigLoader('config/environments/development.env')

# Access environment-specific settings
db_path = config.get('database.path')
```

## Configuration Validation

### Validation Rules

**Define validation rules for configuration sections:**

```python
from decentralized_ai_simulation.src.utils.data_manager import DataValidationRule

# Database configuration validation rules
database_rules = [
    DataValidationRule(
        field="database.path",
        rule_type="required",
        message="Database path is required"
    ),
    DataValidationRule(
        field="database.connection_pool_size",
        rule_type="range",
        value=(1, 100),
        message="Connection pool size must be between 1 and 100"
    ),
    DataValidationRule(
        field="database.timeout",
        rule_type="range",
        value=(1, 300),
        message="Database timeout must be between 1 and 300 seconds"
    )
]

# Simulation configuration validation rules
simulation_rules = [
    DataValidationRule(
        field="simulation.default_agents",
        rule_type="range",
        value=(1, 1000),
        message="Agent count must be between 1 and 1000"
    ),
    DataValidationRule(
        field="simulation.anomaly_rate",
        rule_type="range",
        value=(0.0, 1.0),
        message="Anomaly rate must be between 0.0 and 1.0"
    )
]
```

### Validation Procedures

**Validate configuration before application startup:**

```python
def validate_configuration(config_path: str = "config.yaml") -> List[str]:
    """Validate configuration file for common issues."""
    errors = []

    try:
        # Load configuration
        config_loader = ConfigLoader(config_path)

        # Validate critical sections
        database_rules = [...]  # Define validation rules
        simulation_rules = [...]  # Define validation rules

        # Validate database configuration
        config_data = config_loader.config
        db_errors = data_manager.validate_data(
            config_data.get('database', {}),
            database_rules
        )
        errors.extend([f"Database: {error}" for error in db_errors])

        # Validate simulation configuration
        sim_errors = data_manager.validate_data(
            config_data.get('simulation', {}),
            simulation_rules
        )
        errors.extend([f"Simulation: {error}" for error in sim_errors])

    except Exception as e:
        errors.append(f"Configuration validation failed: {e}")

    return errors

# Use validation
errors = validate_configuration()
if errors:
    print(f"Configuration errors: {errors}")
    sys.exit(1)
```

## Template Usage Guidelines

### Creating New Configuration Templates

**For new deployment environments:**

```bash
# 1. Create environment-specific configuration
cp config/environments/development.env config/environments/staging.env

# 2. Modify for staging environment
# Edit config/environments/staging.env with staging-specific settings

# 3. Update .env.example if new variables are needed
# Add new environment variables to .env.example

# 4. Test the new configuration
ENVIRONMENT=staging python -c "from config.config_manager import get_config; print(get_config('environment'))"
```

### Using Configuration Templates

**Template for new projects:**

```yaml
# config/templates/project_template.yaml
# Template for new project configurations

project:
  name: "{{PROJECT_NAME}}"
  version: "{{PROJECT_VERSION}}"

database:
  path: "{{DATABASE_PATH}}"
  connection_pool_size: {{DATABASE_CONNECTION_POOL_SIZE}}

simulation:
  default_agents: {{SIMULATION_DEFAULT_AGENTS}}
  default_steps: {{SIMULATION_DEFAULT_STEPS}}

# Replace {{VARIABLE}} placeholders with actual values
```

## Best Practices

### Configuration Organization

**1. Environment Separation**
- Keep environment-specific settings in separate files
- Use `environments/` directory for environment configs
- Avoid hardcoding environment-specific values in main config

**2. Sensitive Data Handling**
- Never commit sensitive data (passwords, API keys) to version control
- Use environment variables for sensitive configuration
- Use `.env` files for local development only

**3. Validation and Testing**
- Validate configuration on application startup
- Test configuration changes in development before production
- Use type hints and validation for configuration values

### Environment Variable Management

**Naming Conventions:**
```bash
# Use UPPER_SNAKE_CASE for environment variables
DATABASE_CONNECTION_POOL_SIZE=10
SIMULATION_DEFAULT_AGENTS=50
LOGGING_LEVEL=INFO

# Use full configuration path as variable name
export SIMULATION_DEFAULT_AGENTS=100
export DATABASE_CONNECTION_POOL_SIZE=20
```

**Environment Variable Precedence:**
```python
# Environment variables override configuration file values
# 1. Set environment variables
export DATABASE_PATH="/custom/path.db"

# 2. Configuration file value is ignored
db_path = get_config('database.path')  # Returns "/custom/path.db"
```

## Advanced Configuration Patterns

### Dynamic Configuration Loading

**Load different configurations based on context:**

```python
def load_environment_config() -> ConfigLoader:
    """Load configuration based on current environment."""
    environment = os.getenv('ENVIRONMENT', 'development')

    if environment == 'production':
        return ConfigLoader('config/environments/production.env')
    elif environment == 'staging':
        return ConfigLoader('config/environments/staging.env')
    else:
        return ConfigLoader('config/environments/development.env')

# Usage
config = load_environment_config()
db_path = config.get('database.path')
```

### Configuration Hot Reloading

**For development environments:**

```python
def enable_config_hot_reload():
    """Enable hot reloading of configuration in development."""
    if get_config('development.debug_mode'):
        # Monitor configuration file for changes
        import time

        last_modified = os.path.getmtime('config/config.yaml')
        current_modified = last_modified

        while True:
            current_modified = os.path.getmtime('config/config.yaml')
            if current_modified > last_modified:
                # Reload configuration
                get_config_loader().clear_cache()
                logger.info("Configuration reloaded")
                last_modified = current_modified

            time.sleep(1)  # Check every second
```

### Configuration Profiles

**Support multiple configuration profiles:**

```python
class ConfigurationProfile:
    """Manage different configuration profiles."""

    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.config_loader = ConfigLoader(f'config/environments/{profile_name}.env')

    def get_config(self, key: str, default=None):
        """Get configuration value for this profile."""
        return self.config_loader.get(key, default)

# Usage
dev_profile = ConfigurationProfile('development')
prod_profile = ConfigurationProfile('production')

# Switch between profiles
current_profile = dev_profile if get_config('environment') == 'development' else prod_profile
db_path = current_profile.get_config('database.path')
```

## Troubleshooting Configuration Issues

### Common Issues and Solutions

**1. Configuration Not Loading**
```bash
# Check configuration file syntax
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Test configuration loading
python -c "from config.config_manager import get_config; print(get_config('database.path'))"
```

**2. Environment Variables Not Working**
```bash
# Check environment variable is set
echo $DATABASE_PATH

# Test in Python
import os
print(os.getenv('DATABASE_PATH'))

# Ensure variable is exported (not just set)
export DATABASE_PATH="/custom/path.db"
```

**3. Configuration Validation Errors**
```python
# Debug configuration validation
try:
    config_loader = ConfigLoader('config/config.yaml')
    value = config_loader.get('problematic.key')
except Exception as e:
    print(f"Error: {e}")
    # Check configuration file structure
```

### Debugging Configuration

**Create configuration debugging utility:**

```python
def debug_configuration():
    """Debug configuration loading and display all values."""
    config_loader = get_config_loader()

    print("=== Configuration Debug ===")
    print(f"Config file: {config_loader.config_path}")
    print(f"Environment: {get_config('environment')}")

    # Display key configuration sections
    sections = ['database', 'simulation', 'logging', 'monitoring']
    for section in sections:
        try:
            section_config = config_loader.get(section)
            print(f"{section}: {section_config}")
        except:
            print(f"{section}: ERROR")

    # Display environment variables used
    env_vars = [key for key in os.environ.keys() if any(
        config_key.upper() in key for config_key in [
            'database', 'simulation', 'logging', 'monitoring'
        ]
    )]
    print(f"Relevant env vars: {env_vars}")

# Use for debugging
debug_configuration()
```

## Configuration Management Workflow

### Adding New Configuration Options

**1. Define the configuration option:**
```python
# In config_manager.py
def get_config(key: str, default: Optional[Any] = None) -> Any:
    config_map = {
        'new_feature.enabled': True,
        'new_feature.setting': 'default_value',
        # ... existing config
    }
    return config_map.get(key, default)
```

**2. Update configuration files:**
```yaml
# config.yaml
new_feature:
  enabled: true
  setting: "default_value"
```

**3. Add environment variable support:**
```bash
# .env.example
NEW_FEATURE_ENABLED=true
NEW_FEATURE_SETTING=default_value
```

**4. Update validation rules:**
```python
# Add validation for new feature
new_feature_rules = [
    DataValidationRule(
        field="new_feature.enabled",
        rule_type="type",
        value=bool,
        message="new_feature.enabled must be a boolean"
    )
]
```

**5. Test the new configuration:**
```python
# Test configuration access
enabled = get_config('new_feature.enabled')
setting = get_config('new_feature.setting')

# Test environment variable override
export NEW_FEATURE_ENABLED=false
assert get_config('new_feature.enabled') == False
```

### Configuration Deployment

**For production deployments:**

```bash
# 1. Validate configuration
python -c "from config.config_manager import validate_configuration; errors = validate_configuration(); print('Errors:', errors)"

# 2. Test configuration loading
python -c "from config.config_manager import get_config; print('DB Path:', get_config('database.path'))"

# 3. Deploy with environment variables
ENVIRONMENT=production DATABASE_PATH=/prod/path/ledger.db ./run.sh

# 4. Verify in production
curl http://localhost:8000/health
```

## Security Considerations

### Secure Configuration Practices

**1. Sensitive Data Protection**
```bash
# Never commit secrets to version control
git add .env.example  # Template only
git add .env         # ❌ Never add actual .env file

# Use environment variables for secrets
export DATABASE_PASSWORD=secret_password
export API_KEY=secret_key
```

**2. Configuration Validation**
```python
# Validate configuration values for security
def validate_secure_config():
    """Validate configuration for security issues."""
    errors = []

    # Check for suspicious paths
    db_path = get_config('database.path')
    if '..' in db_path or db_path.startswith('/etc'):
        errors.append("Potentially unsafe database path")

    # Check for debug mode in production
    if (get_config('environment') == 'production' and
        get_config('development.debug_mode')):
        errors.append("Debug mode enabled in production")

    return errors
```

**3. Access Control**
```python
# Environment-based access control
def check_environment_access():
    """Check if current environment allows certain operations."""
    if get_config('environment') == 'production':
        # Restrict certain operations in production
        if get_config('security.restrict_modifications'):
            raise SecurityError("Modifications not allowed in production")
```

This comprehensive configuration management system ensures consistent, secure, and maintainable configuration across all deployment environments.

## Related Documentation

- **[File Structure Overview](../project/file-structure-overview.md)** - Understanding configuration file organization
- **[File Management Guidelines](../guides/file-management-guidelines.md)** - Managing configuration files with file utilities
- **[Developer File Guide](../guides/developer-file-guide.md)** - Working with configuration during development
- **[Migration Documentation](../guides/migration-documentation.md)** - How configuration was updated during reorganization