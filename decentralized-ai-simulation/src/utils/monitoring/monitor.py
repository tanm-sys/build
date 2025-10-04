"""Monitoring and health checks for decentralized AI simulation."""
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable, Union, List

# Import with fallback to handle duplicate files
try:
    from src.utils.logging_setup import get_logger
except ImportError:
    # Fallback to root level imports
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
        """Record a metric with optional labels and memory management.

        Args:
            name: Name of the metric
            value: Numeric value of the metric
            labels: Optional dictionary of labels for the metric
        """
        if name not in self.metrics:
            self.metrics[name] = []

        metric_data = {
            'value': value,
            'timestamp': time.time(),
            'labels': labels or {}
        }
        self.metrics[name].append(metric_data)

        # Keep only recent metrics to prevent memory issues (configurable per metric)
        max_metrics = getattr(self, f'_max_metrics_{name}', 1000)
        if len(self.metrics[name]) > max_metrics:
            self.metrics[name] = self.metrics[name][-max_metrics:]

    def set_metric_retention(self, name: str, max_count: int) -> None:
        """Set maximum number of metrics to retain for a specific metric.

        Args:
            name: Name of the metric
            max_count: Maximum number of metric entries to retain

        Raises:
            ValueError: If max_count is not positive
        """
        if max_count <= 0:
            raise ValueError("max_count must be positive")
        setattr(self, f'_max_metrics_{name}', max_count)

        # Trim existing metrics if needed
        if name in self.metrics and len(self.metrics[name]) > max_count:
            self.metrics[name] = self.metrics[name][-max_count:]
    
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
        """Get application uptime in seconds.

        Returns:
            Number of seconds since monitoring started
        """
        return time.time() - self.start_time

    def get_memory_usage(self) -> Dict[str, Union[int, float, Dict[str, int]]]:
        """Get estimated memory usage of monitoring data.

        Returns:
            Dictionary containing memory usage statistics
        """
        total_memory = 0
        metric_sizes = {}

        for name, metrics_list in self.metrics.items():
            # Estimate memory per metric entry
            entry_size = 0
            for metric in metrics_list:
                entry_size += len(str(metric.get('value', 0)))  # value
                entry_size += len(str(metric.get('timestamp', 0)))  # timestamp
                entry_size += len(str(metric.get('labels', {})))  # labels

            metric_memory = entry_size * len(metrics_list)
            metric_sizes[name] = metric_memory
            total_memory += metric_memory

        return {
            'total_bytes': total_memory,
            'total_mb': total_memory / (1024 * 1024),
            'metric_breakdown': metric_sizes
        }

    def cleanup_old_metrics(self, max_age_seconds: float) -> int:
        """Remove metrics older than max_age_seconds.

        Args:
            max_age_seconds: Maximum age of metrics to keep in seconds

        Returns:
            Number of metrics removed
        """
        current_time = time.time()
        total_removed = 0

        for name in list(self.metrics.keys()):
            original_count = len(self.metrics[name])
            # Keep only recent metrics
            self.metrics[name] = [
                metric for metric in self.metrics[name]
                if current_time - metric['timestamp'] <= max_age_seconds
            ]
            total_removed += original_count - len(self.metrics[name])

        return total_removed
    
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
    from src.core.database import DatabaseLedger
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
        from src.core.simulation import Simulation
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

# Performance monitoring utilities
def performance_logger(metric_name: str):
    """Decorator to automatically log performance metrics for functions.

    Args:
        metric_name: Name of the metric to record

    Returns:
        Decorated function that logs performance metrics
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Record performance metric
                monitoring = get_monitoring()
                monitoring.record_metric(f'{metric_name}_duration', execution_time)
                monitoring.record_metric(f'{metric_name}_success', 1)

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                monitoring = get_monitoring()
                monitoring.record_metric(f'{metric_name}_duration', execution_time)
                monitoring.record_metric(f'{metric_name}_errors', 1)
                logger.error(f"Error in {metric_name}: {e}")
                raise
        return wrapper
    return decorator

def log_performance_summary() -> Dict[str, Any]:
    """Generate a comprehensive performance summary.

    Returns:
        Dictionary containing performance statistics
    """
    monitoring = get_monitoring()

    # Get memory usage
    memory_stats = monitoring.get_memory_usage()

    # Get uptime
    uptime = monitoring.get_uptime()

    # Get system health
    health_status = monitoring.get_system_health()

    # Compile summary
    summary = {
        'uptime_seconds': uptime,
        'memory_usage': memory_stats,
        'system_health': {
            'status': health_status.status,
            'message': health_status.message,
            'timestamp': health_status.timestamp
        },
        'performance_metrics': {}
    }

    # Add key performance metrics
    for metric_name in monitoring.metrics:
        stats = monitoring.get_metric_stats(metric_name)
        if stats:
            summary['performance_metrics'][metric_name] = stats

    return summary

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

class PerformanceMonitor:
    """Advanced performance monitoring with reporting capabilities."""

    def __init__(self, monitoring_instance: Optional[Monitoring] = None):
        """Initialize performance monitor.

        Args:
            monitoring_instance: Monitoring instance to use (creates new if None)
        """
        self.monitoring = monitoring_instance or get_monitoring()
        self._performance_baselines = {}
        self._alert_thresholds = {}

    def set_performance_baseline(self, metric_name: str, baseline_value: float) -> None:
        """Set a performance baseline for comparison.

        Args:
            metric_name: Name of the metric
            baseline_value: Baseline value for comparison
        """
        self._performance_baselines[metric_name] = baseline_value
        logger.info(f"Set performance baseline for {metric_name}: {baseline_value}")

    def set_alert_threshold(self, metric_name: str, threshold_value: float, condition: str = 'greater') -> None:
        """Set alert threshold for a metric.

        Args:
            metric_name: Name of the metric
            threshold_value: Threshold value
            condition: 'greater' or 'less' for threshold condition
        """
        self._alert_thresholds[metric_name] = {
            'threshold': threshold_value,
            'condition': condition
        }
        logger.info(f"Set alert threshold for {metric_name}: {condition} than {threshold_value}")

    def check_performance_alerts(self) -> List[str]:
        """Check for performance alerts based on thresholds.

        Returns:
            List of alert messages
        """
        alerts = []

        for metric_name, threshold_config in self._alert_thresholds.items():
            stats = self.monitoring.get_metric_stats(metric_name)

            if not stats:
                continue

            latest_value = stats.get('latest', 0)
            threshold = threshold_config['threshold']
            condition = threshold_config['condition']

            should_alert = (
                (condition == 'greater' and latest_value > threshold) or
                (condition == 'less' and latest_value < threshold)
            )

            if should_alert:
                alert_msg = f"Performance alert: {metric_name} = {latest_value:.4f} {condition} threshold {threshold}"
                alerts.append(alert_msg)
                logger.warning(alert_msg)

        return alerts

    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report.

        Returns:
            Formatted performance report string
        """
        summary = log_performance_summary()
        alerts = self.check_performance_alerts()

        report = []
        report.append("=" * 60)
        report.append("PERFORMANCE MONITORING REPORT")
        report.append("=" * 60)
        report.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # System overview
        report.append("SYSTEM OVERVIEW:")
        report.append(f"  Uptime: {summary['uptime_seconds']:.2f} seconds")
        report.append(f"  Memory Usage: {summary['memory_usage']['total_mb']:.2f} MB")
        report.append(f"  Health Status: {summary['system_health']['status'].upper()}")
        report.append(f"  Health Message: {summary['system_health']['message']}")
        report.append("")

        # Performance alerts
        if alerts:
            report.append("PERFORMANCE ALERTS:")
            for alert in alerts:
                report.append(f"  ⚠️  {alert}")
            report.append("")

        # Key metrics
        report.append("KEY PERFORMANCE METRICS:")
        for metric_name, stats in summary['performance_metrics'].items():
            if stats.get('count', 0) > 0:
                report.append(f"  {metric_name}:")
                report.append(f"    Count: {stats['count']}")
                report.append(f"    Latest: {stats['latest']:.4f}")
                report.append(f"    Average: {stats['avg']:.4f}")
                report.append(f"    Min: {stats['min']:.4f}")
                report.append(f"    Max: {stats['max']:.4f}")

                # Check against baseline if available
                if metric_name in self._performance_baselines:
                    baseline = self._performance_baselines[metric_name]
                    latest = stats['latest']
                    deviation = ((latest - baseline) / baseline) * 100
                    report.append(f"    Baseline: {baseline:.4f} ({deviation:+.1f}%)")
                report.append("")

        # Memory breakdown
        report.append("MEMORY BREAKDOWN:")
        for metric_name, memory_bytes in summary['memory_usage']['metric_breakdown'].items():
            memory_mb = memory_bytes / (1024 * 1024)
            report.append(f"  {metric_name}: {memory_mb:.2f} MB")
        report.append("")

        report.append("=" * 60)

        return "\n".join(report)

    def export_metrics(self, format: str = 'json') -> str:
        """Export performance metrics in specified format.

        Args:
            format: Export format ('json' or 'csv')

        Returns:
            Formatted metrics data
        """
        summary = log_performance_summary()

        if format.lower() == 'json':
            import json
            return json.dumps(summary, indent=2, default=str)
        elif format.lower() == 'csv':
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(['Metric', 'Count', 'Latest', 'Average', 'Min', 'Max'])

            # Write metrics
            for metric_name, stats in summary['performance_metrics'].items():
                if stats.get('count', 0) > 0:
                    writer.writerow([
                        metric_name,
                        stats['count'],
                        f"{stats['latest']:.4f}",
                        f"{stats['avg']:.4f}",
                        f"{stats['min']:.4f}",
                        f"{stats['max']:.4f}"
                    ])

            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")