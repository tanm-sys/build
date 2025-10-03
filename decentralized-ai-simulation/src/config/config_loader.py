"""Configuration loader for decentralized AI simulation with modern patterns."""
import os
import yaml
import time
from typing import Dict, Any, Optional, Union, TypeVar, Generic, Type, List
from dataclasses import dataclass, field
from pathlib import Path
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    path: str = 'ledger.db'
    connection_pool_size: int = 5
    timeout: int = 30
    check_same_thread: bool = False


@dataclass
class SimulationConfig:
    """Simulation configuration settings."""
    default_agents: int = 50
    default_steps: int = 100
    grid_width: int = 10
    grid_height: int = 10
    step_delay: float = 0.1
    anomaly_rate: float = 0.05
    use_parallel_threshold: int = 50


@dataclass
class AgentConfig:
    """Agent configuration settings."""
    initial_wealth: int = 1
    initial_trust_score: int = 100
    trust_increment: int = 10
    trust_decrement: int = 20
    blacklist_threshold: int = 50
    trade_probability: float = 0.1
    move_probability: float = 0.5


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = 'INFO'
    file: str = 'simulation.log'
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


@dataclass
class StreamlitConfig:
    """Streamlit UI configuration settings."""
    page_title: str = 'Decentralized AI Simulation'
    layout: str = 'wide'
    agent_slider_min: int = 10
    agent_slider_max: int = 200
    agent_slider_default: int = 50
    anomaly_slider_min: float = 0.0
    anomaly_slider_max: float = 0.1
    anomaly_slider_default: float = 0.05
    steps_slider_min: int = 10
    steps_slider_max: int = 100
    steps_slider_default: int = 50
    cache_ttl: int = 5


@dataclass
class MonitoringConfig:
    """Monitoring configuration settings."""
    health_check_interval: int = 30
    metrics_port: int = 8000
    enable_prometheus: bool = False


@dataclass
class APIConfig:
    """API configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    request_timeout: int = 30
    max_concurrent_requests: int = 100


@dataclass
class RayConfig:
    """Ray configuration settings."""
    enable: bool = True
    address: str = "auto"
    num_cpus: Optional[int] = None
    num_gpus: Optional[int] = None
    object_store_memory: Optional[int] = None
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8265
    include_dashboard: bool = True
    log_to_driver: bool = True
    logging_level: str = "INFO"
    ignore_reinit_error: bool = True


@dataclass
class PerformanceConfig:
    """Performance configuration settings."""
    enable_multiprocessing: bool = True
    max_workers: int = 4
    memory_limit_mb: int = 1024
    gc_threshold: int = 1000
    enable_caching: bool = True
    cache_size_mb: int = 100
    enable_async_processing: bool = False
    thread_pool_size: int = 10
    enable_memory_profiling: bool = False


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    enable_input_validation: bool = True
    max_request_size_mb: int = 10
    rate_limit_requests_per_minute: int = 100
    enable_rate_limiting: bool = True
    allowed_hosts: List[str] = field(default_factory=list)
    enable_https_redirect: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    secret_key: Optional[str] = None
    enable_csrf_protection: bool = True


@dataclass
class DevelopmentConfig:
    """Development configuration settings."""
    debug_mode: bool = False
    enable_profiling: bool = False
    log_sql_queries: bool = False
    auto_reload: bool = False
    enable_hot_reload: bool = False
    show_tracebacks: bool = True
    enable_debug_toolbar: bool = False


@dataclass
class AppConfig:
    """Main application configuration with all sections."""
    environment: str = 'development'
    api: APIConfig = field(default_factory=APIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ray: RayConfig = field(default_factory=RayConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    streamlit: StreamlitConfig = field(default_factory=StreamlitConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    development: DevelopmentConfig = field(default_factory=DevelopmentConfig)

class ConfigLoader:
    """Enhanced configuration loader with validation and modern patterns."""

    def __init__(self, config_path: str = "config.yaml") -> None:
        """
        Initialize configuration loader with enhanced validation.

        Args:
            config_path: Path to the YAML configuration file.
        """
        self.config_path: str = config_path
        self.config: AppConfig = AppConfig()
        self._config_cache: Optional[Dict[str, Any]] = None
        self._load_config()

    def _load_config(self) -> None:
        """Load and validate configuration with enhanced error handling."""
        try:
            config_data = self._read_config_file()
            if config_data:
                self._validate_and_merge_config(config_data)
                logger.info(f"Configuration loaded and validated from {self.config_path}")
            else:
                logger.info("Using default configuration")
                self._create_and_save_default_config()

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def _read_config_file(self) -> Optional[Dict[str, Any]]:
        """Read and parse YAML configuration file."""
        if not Path(self.config_path).exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return None

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {self.config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading config file {self.config_path}: {e}")
            raise

    def _validate_and_merge_config(self, config_data: Dict[str, Any]) -> None:
        """Validate configuration data and merge with defaults."""
        try:
            # Validate top-level structure
            if not isinstance(config_data, dict):
                raise ValueError("Configuration must be a dictionary")

            # Update configuration sections with validation
            for section_name in ['api', 'database', 'ray', 'simulation', 'agent', 'logging', 'streamlit', 'monitoring', 'performance', 'security', 'development']:
                if section_name in config_data:
                    section_data = config_data[section_name]
                    if isinstance(section_data, dict):
                        self._update_config_section(section_name, section_data)

            # Update top-level settings
            if 'environment' in config_data:
                self.config.environment = str(config_data['environment'])

            # Apply environment variable overrides
            self._apply_env_overrides()

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

    def _update_config_section(self, section_name: str, section_data: Dict[str, Any]) -> None:
        """Update a specific configuration section with validation."""
        try:
            current_section = getattr(self.config, section_name)

            for key, value in section_data.items():
                if hasattr(current_section, key):
                    # Validate type matches expected type
                    expected_type = type(getattr(current_section, key))
                    if isinstance(value, expected_type):
                        setattr(current_section, key, value)
                    else:
                        logger.warning(f"Type mismatch for {section_name}.{key}: expected {expected_type.__name__}, got {type(value).__name__}")
                else:
                    logger.warning(f"Unknown configuration key: {section_name}.{key}")

        except Exception as e:
            logger.error(f"Error updating config section {section_name}: {e}")
            raise

    def _create_and_save_default_config(self) -> None:
        """Create and save default configuration."""
        try:
            # Ensure directory exists
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)

            # Convert config to dictionary for YAML serialization
            config_dict = self._config_to_dict()

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Created default configuration at {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to create default configuration: {e}")
            raise

    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert AppConfig dataclass to dictionary for serialization."""
        return {
            'environment': self.config.environment,
            'api': {
                'host': self.config.api.host,
                'port': self.config.api.port,
                'debug': self.config.api.debug,
                'cors_origins': self.config.api.cors_origins,
                'cors_methods': self.config.api.cors_methods,
                'cors_headers': self.config.api.cors_headers,
                'request_timeout': self.config.api.request_timeout,
                'max_concurrent_requests': self.config.api.max_concurrent_requests
            },
            'database': {
                'path': self.config.database.path,
                'connection_pool_size': self.config.database.connection_pool_size,
                'timeout': self.config.database.timeout,
                'check_same_thread': self.config.database.check_same_thread
            },
            'ray': {
                'enable': self.config.ray.enable,
                'address': self.config.ray.address,
                'num_cpus': self.config.ray.num_cpus,
                'num_gpus': self.config.ray.num_gpus,
                'object_store_memory': self.config.ray.object_store_memory,
                'dashboard_host': self.config.ray.dashboard_host,
                'dashboard_port': self.config.ray.dashboard_port,
                'include_dashboard': self.config.ray.include_dashboard,
                'log_to_driver': self.config.ray.log_to_driver,
                'logging_level': self.config.ray.logging_level,
                'ignore_reinit_error': self.config.ray.ignore_reinit_error
            },
            'simulation': {
                'default_agents': self.config.simulation.default_agents,
                'default_steps': self.config.simulation.default_steps,
                'grid_width': self.config.simulation.grid_width,
                'grid_height': self.config.simulation.grid_height,
                'step_delay': self.config.simulation.step_delay,
                'anomaly_rate': self.config.simulation.anomaly_rate,
                'use_parallel_threshold': self.config.simulation.use_parallel_threshold
            },
            'agent': {
                'initial_wealth': self.config.agent.initial_wealth,
                'initial_trust_score': self.config.agent.initial_trust_score,
                'trust_increment': self.config.agent.trust_increment,
                'trust_decrement': self.config.agent.trust_decrement,
                'blacklist_threshold': self.config.agent.blacklist_threshold,
                'trade_probability': self.config.agent.trade_probability,
                'move_probability': self.config.agent.move_probability
            },
            'logging': {
                'level': self.config.logging.level,
                'file': self.config.logging.file,
                'max_bytes': self.config.logging.max_bytes,
                'backup_count': self.config.logging.backup_count,
                'format': self.config.logging.format
            },
            'streamlit': {
                'page_title': self.config.streamlit.page_title,
                'layout': self.config.streamlit.layout,
                'agent_slider_min': self.config.streamlit.agent_slider_min,
                'agent_slider_max': self.config.streamlit.agent_slider_max,
                'agent_slider_default': self.config.streamlit.agent_slider_default,
                'anomaly_slider_min': self.config.streamlit.anomaly_slider_min,
                'anomaly_slider_max': self.config.streamlit.anomaly_slider_max,
                'anomaly_slider_default': self.config.streamlit.anomaly_slider_default,
                'steps_slider_min': self.config.streamlit.steps_slider_min,
                'steps_slider_max': self.config.streamlit.steps_slider_max,
                'steps_slider_default': self.config.streamlit.steps_slider_default,
                'cache_ttl': self.config.streamlit.cache_ttl
            },
            'monitoring': {
                'health_check_interval': self.config.monitoring.health_check_interval,
                'metrics_port': self.config.monitoring.metrics_port,
                'enable_prometheus': self.config.monitoring.enable_prometheus
            },
            'performance': {
                'enable_multiprocessing': self.config.performance.enable_multiprocessing,
                'max_workers': self.config.performance.max_workers,
                'memory_limit_mb': self.config.performance.memory_limit_mb,
                'gc_threshold': self.config.performance.gc_threshold,
                'enable_caching': self.config.performance.enable_caching,
                'cache_size_mb': self.config.performance.cache_size_mb,
                'enable_async_processing': self.config.performance.enable_async_processing,
                'thread_pool_size': self.config.performance.thread_pool_size,
                'enable_memory_profiling': self.config.performance.enable_memory_profiling
            },
            'security': {
                'enable_input_validation': self.config.security.enable_input_validation,
                'max_request_size_mb': self.config.security.max_request_size_mb,
                'rate_limit_requests_per_minute': self.config.security.rate_limit_requests_per_minute,
                'enable_rate_limiting': self.config.security.enable_rate_limiting,
                'allowed_hosts': self.config.security.allowed_hosts,
                'enable_https_redirect': self.config.security.enable_https_redirect,
                'ssl_cert_file': self.config.security.ssl_cert_file,
                'ssl_key_file': self.config.security.ssl_key_file,
                'secret_key': self.config.security.secret_key,
                'enable_csrf_protection': self.config.security.enable_csrf_protection
            },
            'development': {
                'debug_mode': self.config.development.debug_mode,
                'enable_profiling': self.config.development.enable_profiling,
                'log_sql_queries': self.config.development.log_sql_queries,
                'auto_reload': self.config.development.auto_reload,
                'enable_hot_reload': self.config.development.enable_hot_reload,
                'show_tracebacks': self.config.development.show_tracebacks,
                'enable_debug_toolbar': self.config.development.enable_debug_toolbar
            }
        }
    
    def _load_config(self) -> None:
        """Load configuration from YAML file and apply environment overrides."""
        try:
            if not os.path.exists(self.config_path):
                logger.warning("Config file not found, using default configuration")
                self._create_default_config()
                return
            
            with open(self.config_path, 'r') as f:
                loaded_config = yaml.safe_load(f)
            
            if loaded_config is None:
                logger.warning("Config file is empty, using default configuration")
                self._create_default_config()
                return
                
            self.config = loaded_config
            logger.info(f"Configuration loaded from {self.config_path}")
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config file: {e}")
            logger.warning("Using default configuration due to YAML error")
            self._create_default_config()
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise
    
    def _create_default_config(self) -> None:
        """Create default configuration if config file doesn't exist."""
        default_config = {
            'environment': 'development',
            'database': {
                'path': 'ledger.db',
                'connection_pool_size': 5,
                'timeout': 30,
                'check_same_thread': False
            },
            'simulation': {
                'default_agents': 50,
                'default_steps': 100,
                'grid_width': 10,
                'grid_height': 10,
                'step_delay': 0.1,
                'anomaly_rate': 0.05,
                'use_parallel_threshold': 50
            },
            'agent': {
                'initial_wealth': 1,
                'initial_trust_score': 100,
                'trust_increment': 10,
                'trust_decrement': 20,
                'blacklist_threshold': 50,
                'trade_probability': 0.1,
                'move_probability': 0.5
            },
            'logging': {
                'level': 'INFO',
                'file': 'simulation.log',
                'max_bytes': 10485760,
                'backup_count': 5,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'streamlit': {
                'page_title': 'Decentralized AI Simulation',
                'layout': 'wide',
                'agent_slider_min': 10,
                'agent_slider_max': 200,
                'agent_slider_default': 50,
                'anomaly_slider_min': 0.0,
                'anomaly_slider_max': 0.1,
                'anomaly_slider_default': 0.05,
                'steps_slider_min': 10,
                'steps_slider_max': 100,
                'steps_slider_default': 50,
                'cache_ttl': 5
            },
            'monitoring': {
                'health_check_interval': 30,
                'metrics_port': 8000,
                'enable_prometheus': False
            }
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        logger.info(f"Created default configuration at {self.config_path}")
        self.config = default_config
        # Apply environment variable overrides to default config
        self._apply_env_overrides()
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get configuration value by key with enhanced dot notation support.

        Args:
            key: Configuration key with dot notation (e.g., 'database.timeout')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Raises:
            KeyError: If key not found and no default provided
        """
        try:
            return self._get_nested_value(self._config_to_dict(), key.split('.'))
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise KeyError(f"Configuration key '{key}' not found")

    def _get_nested_value(self, config_dict: Dict[str, Any], keys: List[str]) -> Any:
        """Get nested value from dictionary using list of keys."""
        value = config_dict
        for key in keys:
            if isinstance(value, dict):
                value = value[key]
            else:
                raise KeyError(f"Key '{key}' not found in configuration")
        return value

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """
        Get entire configuration section as dictionary.

        Args:
            section_name: Name of the configuration section

        Returns:
            Section configuration as dictionary
        """
        if hasattr(self.config, section_name):
            section = getattr(self.config, section_name)
            if hasattr(section, '__dict__'):
                return section.__dict__
        raise KeyError(f"Configuration section '{section_name}' not found")

    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.config.environment == 'production'

    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.config.environment == 'development'

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides with enhanced type conversion."""
        config_dict = self._config_to_dict()

        for key_path in self._flatten_config(config_dict):
            env_var = key_path.upper().replace('.', '_')

            if env_var in os.environ:
                raw_value = os.environ[env_var]
                converted_value = self._convert_env_value(raw_value, key_path, config_dict)

                if converted_value is not None:
                    self._set_nested_value(config_dict, key_path.split('.'), converted_value)
                    logger.info(f"Overridden '{key_path}' from environment variable {env_var}")

        # Update internal config from modified dictionary
        self._validate_and_merge_config(config_dict)

    def _convert_env_value(self, value: str, key_path: str, config_dict: Dict[str, Any]) -> Any:
        """Convert environment variable string to appropriate type."""
        try:
            # Get current value to determine target type
            current_value = self._get_nested_value(config_dict, key_path.split('.'))

            if isinstance(current_value, bool):
                return value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(current_value, int):
                return int(value)
            elif isinstance(current_value, float):
                return float(value)
            else:
                return value  # Keep as string

        except (KeyError, ValueError, TypeError):
            # Try to infer type if current value not available
            try:
                # Try integer first
                if '.' not in value:
                    return int(value)
                # Try float
                return float(value)
            except ValueError:
                # Check for boolean values
                if value.lower() in ('true', 'false', '1', '0', 'yes', 'no'):
                    return value.lower() in ('true', '1', 'yes')
                # Return as string
                return value

    def _set_nested_value(self, config_dict: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set nested value in dictionary using list of keys."""
        for key in keys[:-1]:
            if key not in config_dict:
                config_dict[key] = {}
            config_dict = config_dict[key]

        config_dict[keys[-1]] = value

    def _flatten_config(self, config: Dict[str, Any], parent_key: str = '', sep: str = '.') -> List[str]:
        """Flatten nested configuration dictionary into dot-separated keys."""
        items = []
        for k, v in config.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(self._flatten_config(v, new_key, sep=sep))
            else:
                items.append(new_key)

        return items

    def reload_config(self) -> None:
        """Reload configuration from file."""
        logger.info("Reloading configuration from file")
        self._load_config()

    def validate_config(self) -> bool:
        """Validate current configuration."""
        try:
            # Basic validation - ensure all sections are properly typed
            required_sections = ['api', 'database', 'ray', 'simulation', 'agent', 'logging', 'streamlit', 'monitoring', 'performance', 'security', 'development']
            for section in required_sections:
                if not hasattr(self.config, section):
                    logger.error(f"Missing required configuration section: {section}")
                    return False

            # Validate specific constraints
            if self.config.simulation.default_agents <= 0:
                logger.error("Simulation default_agents must be positive")
                return False

            if not 0 <= self.config.simulation.anomaly_rate <= 1:
                logger.error("Simulation anomaly_rate must be between 0 and 1")
                return False

            if self.config.api.port <= 0 or self.config.api.port > 65535:
                logger.error("API port must be between 1 and 65535")
                return False

            if self.config.database.timeout <= 0:
                logger.error("Database timeout must be positive")
                return False

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False

# Global configuration instance with enhanced caching
_config_loader: Optional[ConfigLoader] = None
_config_cache: Optional[Dict[str, Any]] = None
_cache_timestamp: float = 0
_cache_ttl: float = 300  # 5 minutes


@lru_cache(maxsize=128)
def get_config_loader() -> ConfigLoader:
    """Get or create global configuration loader instance with caching."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def get_config(key: str, default: Optional[Any] = None) -> Any:
    """
    Get configuration value by key with enhanced caching.

    Args:
        key: Configuration key with dot notation
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    global _config_cache, _cache_timestamp

    # Use cached value if still valid
    if (_config_cache is not None and
        (time.time() - _cache_timestamp) < _cache_ttl and
        key in _config_cache):
        return _config_cache[key]

    # Get fresh value from loader
    try:
        loader = get_config_loader()
        value = loader.get(key, default)

        # Update cache
        if _config_cache is None:
            _config_cache = {}
        _config_cache[key] = value
        _cache_timestamp = time.time()

        return value

    except Exception as e:
        logger.error(f"Error getting configuration key '{key}': {e}")
        return default


def reload_global_config() -> None:
    """Reload global configuration and clear caches."""
    global _config_cache, _cache_timestamp, _config_loader

    logger.info("Reloading global configuration")

    # Clear caches
    _config_cache = None
    _cache_timestamp = 0
    get_config_loader.cache_clear()

    # Force recreation of loader
    _config_loader = None

    # Test that new configuration loads correctly
    loader = get_config_loader()
    if not loader.validate_config():
        raise RuntimeError("New configuration failed validation")


def get_config_summary() -> Dict[str, Any]:
    """Get a summary of current configuration for debugging."""
    try:
        loader = get_config_loader()
        return {
            'environment': loader.config.environment,
            'database_path': loader.config.database.path,
            'default_agents': loader.config.simulation.default_agents,
            'config_file': loader.config_path,
            'cache_enabled': _config_cache is not None
        }
    except Exception as e:
        logger.error(f"Error getting configuration summary: {e}")
        return {'error': str(e)}