"""Monitoring and health checks for decentralized AI simulation."""
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)

@dataclass
class HealthStatus:
    """Health status data class."""
    status: str  # 'healthy', 'degraded', 'unhealthy'
    message: str
    timestamp: float
    details: Optional[Dict[str, Any]] = None

class Monitoring:
    """Monitoring class for collecting metrics and health checks."""
    
    def __init__(self):
        self.metrics = {}
        self.health_checks = {}
        self.start_time = time.time()
        
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric with optional labels."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        metric_data = {
            'value': value,
            'timestamp': time.time(),
            'labels': labels or {}
        }
        self.metrics[name].append(metric_data)
        
        # Keep only recent metrics to prevent memory issues
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metric_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if name not in self.metrics or not self.metrics[name]:
            return {}
        
        values = [m['value'] for m in self.metrics[name]]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'latest': values[-1]
        }
    
    def register_health_check(self, name: str, check_func) -> None:
        """Register a health check function."""
        self.health_checks[name] = check_func
    
    def perform_health_check(self, name: str) -> HealthStatus:
        """Perform a specific health check."""
        if name not in self.health_checks:
            return HealthStatus(
                status='unhealthy',
                message=f'Health check {name} not found',
                timestamp=time.time()
            )
        
        try:
            return self.health_checks[name]()
        except Exception as e:
            return HealthStatus(
                status='unhealthy',
                message=f'Health check {name} failed: {str(e)}',
                timestamp=time.time(),
                details={'error': str(e)}
            )
    
    def perform_all_health_checks(self) -> Dict[str, HealthStatus]:
        """Perform all registered health checks."""
        results = {}
        for name in self.health_checks:
            results[name] = self.perform_health_check(name)
        return results
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time
    
    def get_system_health(self) -> HealthStatus:
        """Get overall system health status."""
        all_checks = self.perform_all_health_checks()
        
        unhealthy_checks = [name for name, status in all_checks.items() if status.status == 'unhealthy']
        degraded_checks = [name for name, status in all_checks.items() if status.status == 'degraded']
        
        if unhealthy_checks:
            return HealthStatus(
                status='unhealthy',
                message=f'System unhealthy: {len(unhealthy_checks)} checks failed',
                timestamp=time.time(),
                details={'unhealthy_checks': unhealthy_checks, 'degraded_checks': degraded_checks}
            )
        elif degraded_checks:
            return HealthStatus(
                status='degraded',
                message=f'System degraded: {len(degraded_checks)} checks degraded',
                timestamp=time.time(),
                details={'degraded_checks': degraded_checks}
            )
        else:
            return HealthStatus(
                status='healthy',
                message='All systems operational',
                timestamp=time.time()
            )

# Default health checks
def database_health_check() -> HealthStatus:
    """Health check for database connectivity."""
    from database import DatabaseLedger
    try:
        db = DatabaseLedger()
        entries = db.read_ledger()
        return HealthStatus(
            status='healthy',
            message=f'Database connected with {len(entries)} entries',
            timestamp=time.time(),
            details={'entry_count': len(entries)}
        )
    except Exception as e:
        return HealthStatus(
            status='unhealthy',
            message=f'Database connection failed: {str(e)}',
            timestamp=time.time(),
            details={'error': str(e)}
        )

def simulation_health_check() -> HealthStatus:
    """Health check for simulation components."""
    try:
        from simulation import Simulation
        # Just test that we can import and instantiate
        _ = Simulation(num_agents=1)
        return HealthStatus(
            status='healthy',
            message='Simulation components operational',
            timestamp=time.time()
        )
    except Exception as e:
        return HealthStatus(
            status='unhealthy',
            message=f'Simulation components failed: {str(e)}',
            timestamp=time.time(),
            details={'error': str(e)}
        )

# Global monitoring instance
_monitoring_instance = None

def get_monitoring() -> Monitoring:
    """Get or create the global monitoring instance."""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = Monitoring()
        # Register default health checks
        _monitoring_instance.register_health_check('database', database_health_check)
        _monitoring_instance.register_health_check('simulation', simulation_health_check)
    return _monitoring_instance