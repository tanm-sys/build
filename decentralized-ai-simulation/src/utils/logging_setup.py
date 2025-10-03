"""Logging setup for decentralized AI simulation."""
import logging
import logging.handlers
from src.config.config_loader import get_config

def setup_logging() -> None:
    """Configure structured logging for the application."""
    # Get logging configuration
    log_level = get_config('logging.level', 'INFO')
    log_file = get_config('logging.file', 'simulation.log')
    max_bytes = get_config('logging.max_bytes', 10485760)
    backup_count = get_config('logging.backup_count', 5)
    log_format = get_config('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Convert log level string to logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log configuration loaded
    root_logger.info("Logging configured successfully")
    root_logger.info(f"Log level: {log_level}")
    root_logger.info(f"Log file: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

# Initialize logging when module is imported
setup_logging()