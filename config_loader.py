"""Configuration loader for decentralized AI simulation."""
import os
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Load and validate configuration from YAML file."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load_config()
    
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
        """Get configuration value by key with dot notation support."""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise KeyError(f"Configuration key '{key}' not found")
    
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.get('environment') == 'production'
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to the configuration."""
        for key_path in self._flatten_config(self.config):
            env_var = key_path.upper().replace('.', '_')
            if env_var in os.environ:
                value = os.environ[env_var]
                # Convert value to appropriate type based on existing config
                current_value = self.get(key_path, None)
                if current_value is not None:
                    if isinstance(current_value, bool):
                        value = value.lower() in ('true', '1', 'yes')
                    elif isinstance(current_value, int):
                        value = int(value)
                    elif isinstance(current_value, float):
                        value = float(value)
                    # For strings, no conversion needed
                else:
                    # If key doesn't exist in config, try to infer type
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            if value.lower() in ('true', 'false', '1', '0', 'yes', 'no'):
                                value = value.lower() in ('true', '1', 'yes')
                # Set the value using dot notation
                keys = key_path.split('.')
                config_dict = self.config
                for k in keys[:-1]:
                    config_dict = config_dict.setdefault(k, {})
                config_dict[keys[-1]] = value
                logger.info(f"Overridden config key '{key_path}' from environment variable {env_var}")

    def _flatten_config(self, config, parent_key='', sep='.'):
        """Flatten a nested configuration dictionary into dot-separated keys."""
        items = []
        for k, v in config.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_config(v, new_key, sep=sep))
            else:
                items.append(new_key)
        return items

    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.get('environment') == 'development'

# Global configuration instance
_config_loader: Optional[ConfigLoader] = None

def get_config_loader() -> ConfigLoader:
    """Get or create global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def get_config(key: str, default: Optional[Any] = None) -> Any:
    """Get configuration value by key."""
    return get_config_loader().get(key, default)