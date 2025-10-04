"""
Decentralized AI Simulation Package

This package contains the core simulation engine for decentralized AI agents
with 3D visualization capabilities.
"""

__version__ = "1.0.0"
__author__ = "Decentralized AI Simulation Team"

# Export main classes for easier importing
try:
    # Try relative imports (works when package is installed)
    from .src.core.simulation import Simulation
    from .src.core.agents import AnomalyAgent, AnomalySignature
    from .src.core.database import DatabaseLedger
except ImportError:
    # Fall back to absolute imports (works when running tests)
    from src.core.simulation import Simulation
    from src.core.agents import AnomalyAgent, AnomalySignature
    from src.core.database import DatabaseLedger

__all__ = [
    'Simulation',
    'AnomalyAgent',
    'AnomalySignature',
    'DatabaseLedger'
]