"""
Enhanced Monitoring and Logging Integration for 3D AI Simulation Platform

Provides comprehensive monitoring, metrics collection, alerting, and
structured logging for the complete 3D visualization system.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import json
import threading
from collections import defaultdict, deque
import psutil
import os

# Import existing monitoring components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from decentralized_ai_simulation.src.utils.monitoring import get_monitoring
    from decentralized_ai_simulation.src.utils.logging_setup import get_logger
    EXISTING_MONITORING_AVAILABLE = True
except ImportError:
    EXISTING_MONITORING_AVAILABLE = False

@dataclass
class MetricPoint:
    """Single metric data point."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str]
    unit: str = ""

@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    metric: str
    condition: str  # 'gt', 'lt', 'eq', 'ne'
    threshold: float
    duration: int  # seconds
    severity: str  # 'info', 'warning', 'error', 'critical'
    enabled: bool = True

@dataclass
class Alert:
    """Active alert."""
    rule_name: str
    message: str
    severity: str
    timestamp: float
    value: float
    threshold: float

class MetricsCollector:
    """Enhanced metrics collector for 3D platform."""

    def __init__(self):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.collectors: Dict[str, Callable] = {}
        self.collection_interval = 10.0  # seconds
        self.lock = threading.Lock()

    def register_collector(self, name: str, collector_func: Callable) -> None:
        """Register a metrics collector function."""
        self.collectors[name] = collector_func

    def collect_metric(self, name: str, value: float, tags: Dict[str, str] = None, unit: str = "") -> None:
        """Collect a single metric."""
        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            unit=unit
        )

        with self.lock:
            self.metrics[name].append(metric_point)

    def get_metrics(self, name: str = None, since: float = None) -> List[MetricPoint]:
        """Get collected metrics."""
        if name:
            metrics = self.metrics.get(name, [])
        else:
            metrics = []
            for metric_list in self.metrics.values():
                metrics.extend(metric_list)

        if since:
            metrics = [m for m in metrics if m.timestamp >= since]

        return sorted(metrics, key=lambda x: x.timestamp)

    def get_latest_value(self, name: str) -> Optional[float]:
        """Get latest value for a metric."""
        metrics = self.metrics.get(name, [])
        return metrics[-1].value if metrics else None

    def get_metric_stats(self, name: str, window: int = 60) -> Dict[str, float]:
        """Get statistics for a metric over a time window."""
        since = time.time() - window
        metrics = [m for m in self.metrics.get(name, []) if m.timestamp >= since]

        if not metrics:
            return {}

        values = [m.value for m in metrics]

        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'latest': values[-1],
            'oldest': values[0]
        }

class AlertManager:
    """Manages alerting rules and active alerts."""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.alert_callbacks: List[Callable] = []

    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self.rules[rule.name] = rule

    def check_alerts(self, metrics_collector: MetricsCollector) -> List[Alert]:
        """Check all alert rules and return new alerts."""
        new_alerts = []
        current_time = time.time()

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            # Get latest metric value
            latest_value = metrics_collector.get_latest_value(rule.metric)

            if latest_value is None:
                continue

            # Check if alert should trigger
            should_alert = self._evaluate_condition(
                latest_value, rule.condition, rule.threshold
            )

            alert_key = f"{rule.name}_{rule.metric}"

            if should_alert:
                # Check if alert is already active
                if alert_key not in self.active_alerts:
                    alert = Alert(
                        rule_name=rule.name,
                        message=f"{rule.metric} {rule.condition} {rule.threshold}",
                        severity=rule.severity,
                        timestamp=current_time,
                        value=latest_value,
                        threshold=rule.threshold
                    )

                    self.active_alerts[alert_key] = alert
                    new_alerts.append(alert)

                    # Trigger alert callbacks
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            logging.error(f"Alert callback error: {e}")

            else:
                # Clear resolved alert
                if alert_key in self.active_alerts:
                    resolved_alert = self.active_alerts.pop(alert_key)
                    resolved_alert.resolved_timestamp = current_time
                    self.alert_history.append(resolved_alert)

        return new_alerts

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition."""
        if condition == 'gt':
            return value > threshold
        elif condition == 'lt':
            return value < threshold
        elif condition == 'eq':
            return abs(value - threshold) < 0.001
        elif condition == 'ne':
            return abs(value - threshold) >= 0.001
        else:
            return False

class SystemMonitor:
    """Monitors system resources and performance."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = 0
        self.baseline_cpu = 0

    def get_system_metrics(self) -> Dict[str, float]:
        """Get comprehensive system metrics."""
        try:
            # Memory metrics
            memory = self.process.memory_info()
            cpu_times = self.process.cpu_times()

            # System-wide metrics
            system_cpu = psutil.cpu_percent(interval=1)
            system_memory = psutil.virtual_memory()

            return {
                'process_memory_rss_mb': memory.rss / 1024 / 1024,
                'process_memory_vms_mb': memory.vms / 1024 / 1024,
                'process_cpu_percent': self.process.cpu_percent(),
                'process_cpu_user_seconds': cpu_times.user,
                'process_cpu_system_seconds': cpu_times.system,
                'system_cpu_percent': system_cpu,
                'system_memory_percent': system_memory.percent,
                'system_memory_available_mb': system_memory.available / 1024 / 1024,
                'system_memory_used_mb': system_memory.used / 1024 / 1024,
                'timestamp': time.time()
            }

        except Exception as e:
            logging.error(f"Error collecting system metrics: {e}")
            return {}

class EnhancedMonitoring:
    """Enhanced monitoring system for 3D platform."""

    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.system_monitor = SystemMonitor()
        self.running = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # Set up default collectors
        self._setup_default_collectors()

        # Set up default alert rules
        self._setup_default_alert_rules()

    def _setup_default_collectors(self) -> None:
        """Set up default metrics collectors."""

        # System metrics collector
        def collect_system_metrics():
            metrics = self.system_monitor.get_system_metrics()
            for name, value in metrics.items():
                if name != 'timestamp':  # Skip timestamp
                    self.metrics_collector.collect_metric(
                        f"system.{name}",
                        value,
                        unit=self._get_unit_for_metric(name)
                    )

        self.metrics_collector.register_collector("system", collect_system_metrics)

        # Simulation metrics collector (placeholder)
        def collect_simulation_metrics():
            # This would collect simulation-specific metrics
            # For now, just collect a placeholder metric
            self.metrics_collector.collect_metric(
                "simulation.active_agents",
                100,  # Would get from actual simulation
                tags={"component": "simulation"},
                unit="count"
            )

        self.metrics_collector.register_collector("simulation", collect_simulation_metrics)

    def _setup_default_alert_rules(self) -> None:
        """Set up default alert rules."""

        # Memory usage alert
        memory_rule = AlertRule(
            name="high_memory_usage",
            metric="system.process_memory_rss_mb",
            condition="gt",
            threshold=512,  # 512 MB
            duration=60,    # Alert if high for 60 seconds
            severity="warning"
        )
        self.alert_manager.add_rule(memory_rule)

        # CPU usage alert
        cpu_rule = AlertRule(
            name="high_cpu_usage",
            metric="system.system_cpu_percent",
            condition="gt",
            threshold=80,   # 80%
            duration=30,    # Alert if high for 30 seconds
            severity="warning"
        )
        self.alert_manager.add_rule(cpu_rule)

    def _get_unit_for_metric(self, metric_name: str) -> str:
        """Get unit for metric name."""
        unit_map = {
            'mb': 'megabytes',
            'percent': 'percent',
            'seconds': 'seconds',
            'count': 'count',
            'bytes': 'bytes'
        }

        for key, unit in unit_map.items():
            if key in metric_name.lower():
                return unit

        return ""

    def start_monitoring(self) -> None:
        """Start the monitoring system."""
        if self.running:
            return

        self.running = True

        def monitoring_loop():
            """Main monitoring loop."""
            while self.running:
                try:
                    # Collect metrics from all collectors
                    for collector_name in self.metrics_collector.collectors:
                        try:
                            self.metrics_collector.collectors[collector_name]()
                        except Exception as e:
                            logging.error(f"Error in collector {collector_name}: {e}")

                    # Check alerts
                    new_alerts = self.alert_manager.check_alerts(self.metrics_collector)

                    if new_alerts:
                        for alert in new_alerts:
                            logging.warning(f"ALERT: {alert.message} (Severity: {alert.severity})")

                    # Sleep until next collection
                    time.sleep(self.metrics_collector.collection_interval)

                except Exception as e:
                    logging.error(f"Error in monitoring loop: {e}")
                    time.sleep(5)  # Brief pause before retrying

        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        logging.info("Enhanced monitoring system started")

    def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        self.running = False

        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)

        logging.info("Enhanced monitoring system stopped")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all collected metrics."""
        summary = {}

        for metric_name in self.metrics_collector.metrics.keys():
            stats = self.metrics_collector.get_metric_stats(metric_name)
            if stats:
                summary[metric_name] = stats

        return summary

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts."""
        return [asdict(alert) for alert in self.alert_manager.active_alerts.values()]

    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format."""
        all_metrics = self.metrics_collector.get_metrics()

        if format.lower() == 'json':
            return json.dumps([asdict(m) for m in all_metrics], indent=2)
        elif format.lower() == 'prometheus':
            # Export in Prometheus format
            lines = []
            for metric in all_metrics:
                # Convert metric name to Prometheus format
                prom_name = metric.name.replace('.', '_').replace('-', '_')
                lines.append(f"# HELP {prom_name} {metric.name}")
                lines.append(f"# TYPE {prom_name} gauge")
                labels = ','.join(f'{k}="{v}"' for k, v in metric.tags.items())
                if labels:
                    lines.append(f"{prom_name}{{{labels}}} {metric.value}")
                else:
                    lines.append(f"{prom_name} {metric.value}")
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Global monitoring instance
monitoring_instance: Optional[EnhancedMonitoring] = None

def get_enhanced_monitoring() -> EnhancedMonitoring:
    """Get or create global monitoring instance."""
    global monitoring_instance
    if monitoring_instance is None:
        monitoring_instance = EnhancedMonitoring()
    return monitoring_instance

@contextmanager
def monitor_performance(operation_name: str, tags: Dict[str, str] = None):
    """Context manager to monitor operation performance."""
    monitoring = get_enhanced_monitoring()

    start_time = time.time()
    start_memory = monitoring.system_monitor.get_memory_usage()

    try:
        yield
        success = True
    except Exception as e:
        success = False
        raise
    finally:
        end_time = time.time()
        end_memory = monitoring.system_monitor.get_memory_usage()

        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory

        # Record metrics
        monitoring.metrics_collector.collect_metric(
            f"operation.{operation_name}.duration",
            execution_time,
            tags=tags,
            unit="seconds"
        )

        monitoring.metrics_collector.collect_metric(
            f"operation.{operation_name}.memory_delta",
            memory_delta,
            tags=tags,
            unit="megabytes"
        )

        monitoring.metrics_collector.collect_metric(
            f"operation.{operation_name}.success",
            1.0 if success else 0.0,
            tags=tags,
            unit="boolean"
        )

def setup_enhanced_logging(log_level: str = 'INFO',
                          log_file: str = 'logs/enhanced_simulation.log') -> None:
    """Set up enhanced logging configuration."""

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Set specific log levels for noisy libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('websockets.protocol').setLevel(logging.WARNING)

    # Add structured logging for 3D platform
    def log_3d_event(event_type: str, data: Dict[str, Any]) -> None:
        """Log structured 3D platform events."""
        logger = logging.getLogger('simulation_3d')
        logger.info(f"EVENT:{event_type}", extra={
            'event_type': event_type,
            'event_data': json.dumps(data)
        })

    # Make function available globally
    import builtins
    builtins.log_3d_event = log_3d_event

def integrate_with_existing_monitoring() -> None:
    """Integrate with existing monitoring system if available."""
    if EXISTING_MONITORING_AVAILABLE:
        try:
            existing_monitor = get_monitoring()
            print("✅ Integrated with existing monitoring system")
        except Exception as e:
            print(f"⚠️  Could not integrate with existing monitoring: {e}")

# Initialize enhanced monitoring when module is imported
def initialize_monitoring() -> EnhancedMonitoring:
    """Initialize the enhanced monitoring system."""
    monitoring = get_enhanced_monitoring()

    # Set up enhanced logging
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/enhanced_simulation.log')
    setup_enhanced_logging(log_level, log_file)

    # Integrate with existing monitoring if available
    integrate_with_existing_monitoring()

    # Start monitoring
    monitoring.start_monitoring()

    return monitoring

if __name__ == "__main__":
    # Example usage and testing
    monitoring = initialize_monitoring()

    print("📊 Enhanced monitoring system initialized")
    print("Available metrics collectors:")
    for collector_name in monitoring.metrics_collector.collectors.keys():
        print(f"  - {collector_name}")

    print("\nActive alert rules:")
    for rule_name, rule in monitoring.alert_manager.rules.items():
        print(f"  - {rule_name}: {rule.metric} {rule.condition} {rule.threshold}")

    # Let it run for a bit to collect some metrics
    print("\nCollecting metrics for 30 seconds...")
    time.sleep(30)

    # Show collected metrics
    summary = monitoring.get_metrics_summary()
    print(f"\nCollected {len(summary)} metric types")

    for metric_name, stats in summary.items():
        print(f"  {metric_name}: avg={stats.get('avg', 0):.2f}")

    # Export metrics
    print("\nExporting metrics...")
    json_metrics = monitoring.export_metrics('json')
    print(f"Exported {len(json.loads(json_metrics))} metric points")

    monitoring.stop_monitoring()
    print("✅ Monitoring test completed")