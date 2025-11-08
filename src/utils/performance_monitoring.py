"""
Enterprise Performance Monitoring and Profiling Framework for AI Simulation Platform

Provides comprehensive performance monitoring, profiling, bottleneck identification,
capacity planning, and optimization recommendations for enterprise-grade operations.
"""

import asyncio
import time
import psutil
import threading
import json
import gc
import sys
import tracemalloc
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
from contextlib import contextmanager
import numpy as np
from datetime import datetime, timedelta
import logging
import statistics
from functools import wraps
import cProfile
import pstats
import io
import resource
import os

@dataclass
class PerformanceMetric:
    """Represents a single performance metric."""
    name: str
    value: float
    timestamp: float
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance at a point in time."""
    timestamp: float
    cpu_percent: float
    memory_usage: Dict[str, float]
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    process_metrics: Dict[str, Any]
    custom_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class PerformanceProfile:
    """Performance profile of an operation or component."""
    operation_name: str
    total_calls: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    p95_time: float = 0.0
    p99_time: float = 0.0
    memory_usage: Dict[str, float] = field(default_factory=dict)
    error_count: int = 0
    success_rate: float = 1.0
    throughput: float = 0.0  # calls per second

@dataclass
class BottleneckAnalysis:
    """Results of bottleneck analysis."""
    component: str
    severity: str  # critical, high, medium, low
    issue_type: str  # cpu, memory, io, network, algorithm
    description: str
    impact_score: float
    recommendations: List[str]
    evidence: Dict[str, Any]

@dataclass
class CapacityRecommendation:
    """Capacity planning recommendation."""
    resource_type: str  # cpu, memory, disk, network
    current_usage: float
    recommended_capacity: float
    projected_need: float
    time_horizon: str  # short_term, medium_term, long_term
    confidence_level: float
    reasoning: str
    actions: List[str]

class PerformanceProfiler:
    """Advanced performance profiler for AI simulation components."""
    
    def __init__(self):
        self.profiles: Dict[str, PerformanceProfile] = defaultdict(lambda: PerformanceProfile(operation_name=""))
        self.memory_traces: Dict[str, List] = defaultdict(list)
        self.call_counts: Dict[str, int] = defaultdict(int)
        self.active_traces: Dict[str, bool] = {}
        self._lock = threading.Lock()
    
    def start_memory_trace(self, operation_name: str) -> None:
        """Start memory tracing for an operation."""
        tracemalloc.start()
        self.active_traces[operation_name] = True
    
    def stop_memory_trace(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """Stop memory tracing and return results."""
        if not self.active_traces.get(operation_name, False):
            return None
        
        try:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            trace_info = {
                "operation": operation_name,
                "current_memory": current,
                "peak_memory": peak,
                "timestamp": time.time()
            }
            
            self.memory_traces[operation_name].append(trace_info)
            self.active_traces[operation_name] = False
            
            return trace_info
        except Exception as e:
            logging.error(f"Error stopping memory trace for {operation_name}: {e}")
            return None
    
    def profile_function(self, operation_name: str):
        """Decorator to profile function performance."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                profile = self.profiles[operation_name]
                
                # Start timing
                start_time = time.perf_counter()
                start_memory = self._get_memory_usage()
                
                try:
                    # Execute function
                    result = func(*args, **kwargs)
                    success = True
                except Exception as e:
                    success = False
                    profile.error_count += 1
                    raise
                finally:
                    # Record metrics
                    end_time = time.perf_counter()
                    end_memory = self._get_memory_usage()
                    
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    self._update_profile_stats(profile, execution_time, memory_delta, success)
                
                return result
            return wrapper
        return decorator
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def _update_profile_stats(self, profile: PerformanceProfile, execution_time: float, 
                            memory_delta: float, success: bool) -> None:
        """Update performance profile statistics."""
        with self._lock:
            profile.total_calls += 1
            profile.total_time += execution_time
            profile.avg_time = profile.total_time / profile.total_calls
            profile.min_time = min(profile.min_time, execution_time)
            profile.max_time = max(profile.max_time, execution_time)
            
            # Calculate percentiles
            if execution_time > 0:
                profile.memory_usage[f"call_{profile.total_calls}"] = memory_delta
            
            if profile.total_calls > 0:
                profile.success_rate = (profile.total_calls - profile.error_count) / profile.total_calls
            
            # Calculate throughput (calls per second over last minute)
            recent_calls = min(profile.total_calls, 60)
            if recent_calls > 0:
                profile.throughput = recent_calls / 60.0
    
    def get_operation_profile(self, operation_name: str) -> PerformanceProfile:
        """Get performance profile for an operation."""
        return self.profiles.get(operation_name, PerformanceProfile(operation_name=operation_name))
    
    def get_all_profiles(self) -> Dict[str, PerformanceProfile]:
        """Get all performance profiles."""
        return dict(self.profiles)
    
    def analyze_bottlenecks(self) -> List[BottleneckAnalysis]:
        """Analyze performance profiles to identify bottlenecks."""
        bottlenecks = []
        
        # Analyze CPU-intensive operations
        high_cpu_ops = [
            (name, profile) for name, profile in self.profiles.items()
            if profile.avg_time > 1.0 or profile.total_time > 60.0
        ]
        
        for name, profile in high_cpu_ops:
            if profile.avg_time > 5.0:
                severity = "critical"
            elif profile.avg_time > 2.0:
                severity = "high"
            elif profile.avg_time > 1.0:
                severity = "medium"
            else:
                severity = "low"
            
            recommendations = [
                "Consider algorithmic optimization",
                "Implement caching strategies",
                "Use async/await for I/O operations",
                "Profile database queries",
                "Consider parallel processing"
            ]
            
            bottlenecks.append(BottleneckAnalysis(
                component=name,
                severity=severity,
                issue_type="cpu",
                description=f"High CPU usage detected in {name} - avg time: {profile.avg_time:.2f}s",
                impact_score=profile.avg_time * profile.throughput,
                recommendations=recommendations,
                evidence={
                    "avg_execution_time": profile.avg_time,
                    "total_time": profile.total_time,
                    "throughput": profile.throughput,
                    "total_calls": profile.total_calls
                }
            ))
        
        # Analyze memory-intensive operations
        for name, traces in self.memory_traces.items():
            if traces:
                latest_trace = traces[-1]
                if latest_trace["peak_memory"] > 100 * 1024 * 1024:  # 100MB
                    bottlenecks.append(BottleneckAnalysis(
                        component=name,
                        severity="high",
                        issue_type="memory",
                        description=f"High memory usage detected in {name} - peak: {latest_trace['peak_memory'] / 1024 / 1024:.1f}MB",
                        impact_score=latest_trace["peak_memory"] / 1024 / 1024,
                        recommendations=[
                            "Optimize data structures",
                            "Implement object pooling",
                            "Use generators for large datasets",
                            "Clear references to free memory",
                            "Consider memory-mapped files"
                        ],
                        evidence={
                            "peak_memory_mb": latest_trace["peak_memory"] / 1024 / 1024,
                            "current_memory_mb": latest_trace["current_memory"] / 1024 / 1024
                        }
                    ))
        
        return sorted(bottlenecks, key=lambda x: x.impact_score, reverse=True)

class SystemResourceMonitor:
    """Monitors system resource utilization."""
    
    def __init__(self, collection_interval: float = 10.0):
        self.collection_interval = collection_interval
        self.snapshots: deque = deque(maxlen=1000)
        self.baseline_metrics: Dict[str, float] = {}
        self.thresholds = {
            "cpu_warning": 80.0,
            "cpu_critical": 95.0,
            "memory_warning": 85.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0
        }
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def start_monitoring(self) -> None:
        """Start system resource monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logging.info("System resource monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop system resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logging.info("System resource monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring:
            try:
                snapshot = self._collect_snapshot()
                self.snapshots.append(snapshot)
                
                # Check thresholds
                self._check_thresholds(snapshot)
                
                time.sleep(self.collection_interval)
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _collect_snapshot(self) -> PerformanceSnapshot:
        """Collect current system performance snapshot."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk_io = psutil.disk_io_counters()
        disk_usage = psutil.disk_usage('/')
        
        # Network metrics
        network_io = psutil.net_io_counters()
        
        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent()
        
        return PerformanceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_usage={
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent
            },
            disk_io={
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0,
                "read_count": disk_io.read_count if disk_io else 0,
                "write_count": disk_io.write_count if disk_io else 0
            },
            network_io={
                "bytes_sent": network_io.bytes_sent if network_io else 0,
                "bytes_recv": network_io.bytes_recv if network_io else 0,
                "packets_sent": network_io.packets_sent if network_io else 0,
                "packets_recv": network_io.packets_recv if network_io else 0
            },
            process_metrics={
                "cpu_percent": process_cpu,
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0
            }
        )
    
    def _check_thresholds(self, snapshot: PerformanceSnapshot) -> None:
        """Check performance thresholds and log alerts."""
        # CPU threshold checks
        if snapshot.cpu_percent > self.thresholds["cpu_critical"]:
            logging.critical(f"CPU usage critical: {snapshot.cpu_percent:.1f}%")
        elif snapshot.cpu_percent > self.thresholds["cpu_warning"]:
            logging.warning(f"CPU usage high: {snapshot.cpu_percent:.1f}%")
        
        # Memory threshold checks
        if snapshot.memory_usage["percent"] > self.thresholds["memory_critical"]:
            logging.critical(f"Memory usage critical: {snapshot.memory_usage['percent']:.1f}%")
        elif snapshot.memory_usage["percent"] > self.thresholds["memory_warning"]:
            logging.warning(f"Memory usage high: {snapshot.memory_usage['percent']:.1f}%")
    
    def get_current_metrics(self) -> Optional[PerformanceSnapshot]:
        """Get current system metrics."""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_metrics_history(self, duration_minutes: int = 60) -> List[PerformanceSnapshot]:
        """Get metrics history for specified duration."""
        cutoff_time = time.time() - (duration_minutes * 60)
        return [s for s in self.snapshots if s.timestamp >= cutoff_time]
    
    def calculate_trends(self, duration_minutes: int = 60) -> Dict[str, str]:
        """Calculate resource usage trends."""
        history = self.get_metrics_history(duration_minutes)
        if len(history) < 2:
            return {"cpu": "stable", "memory": "stable", "disk": "stable"}
        
        trends = {}
        
        # CPU trend
        cpu_values = [s.cpu_percent for s in history]
        trends["cpu"] = self._calculate_trend(cpu_values)
        
        # Memory trend
        memory_values = [s.memory_usage["percent"] for s in history]
        trends["memory"] = self._calculate_trend(memory_values)
        
        # Disk trend (based on usage percentage)
        disk_usage = psutil.disk_usage('/')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        disk_values = [disk_percent] * len(history)  # Simplified for demo
        trends["disk"] = self._calculate_trend(disk_values)
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 10:
            return "stable"
        
        # Simple linear regression to determine trend
        x = np.arange(len(values))
        y = np.array(values)
        
        try:
            slope = np.polyfit(x, y, 1)[0]
            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"
        except:
            return "stable"
    
    def generate_capacity_recommendations(self) -> List[CapacityRecommendation]:
        """Generate capacity planning recommendations."""
        recommendations = []
        current_metrics = self.get_current_metrics()
        
        if not current_metrics:
            return recommendations
        
        # CPU recommendations
        cpu_usage = current_metrics.cpu_percent
        if cpu_usage > 80:
            recommendations.append(CapacityRecommendation(
                resource_type="cpu",
                current_usage=cpu_usage,
                recommended_capacity=cpu_usage * 1.5,
                projected_need=cpu_usage * 2.0,
                time_horizon="medium_term",
                confidence_level=0.8,
                reasoning=f"Current CPU usage is {cpu_usage:.1f}%, indicating high utilization",
                actions=[
                    "Scale up CPU capacity",
                    "Optimize CPU-intensive operations",
                    "Implement load balancing",
                    "Consider horizontal scaling"
                ]
            ))
        
        # Memory recommendations
        memory_usage = current_metrics.memory_usage["percent"]
        if memory_usage > 85:
            recommendations.append(CapacityRecommendation(
                resource_type="memory",
                current_usage=memory_usage,
                recommended_capacity=memory_usage * 1.3,
                projected_need=memory_usage * 1.8,
                time_horizon="short_term",
                confidence_level=0.9,
                reasoning=f"Current memory usage is {memory_usage:.1f}%, risk of OOM",
                actions=[
                    "Increase memory allocation",
                    "Optimize memory usage patterns",
                    "Implement memory caching strategies",
                    "Review garbage collection settings"
                ]
            ))
        
        return recommendations

class SLAMonitor:
    """Monitors Service Level Agreements and compliance."""
    
    def __init__(self):
        self.sla_targets = {
            "api_response_time_p95": 1.0,  # seconds
            "api_response_time_p99": 2.0,  # seconds
            "api_availability": 99.9,      # percentage
            "error_rate": 0.1,             # percentage
            "throughput": 1000.0           # requests per minute
        }
        self.sla_metrics = defaultdict(list)
        self.violations = []
        self._lock = threading.Lock()
    
    def record_metric(self, metric_name: str, value: float, timestamp: float = None) -> None:
        """Record SLA metric."""
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            self.sla_metrics[metric_name].append((timestamp, value))
            
            # Check for SLA violations
            if metric_name in self.sla_targets:
                self._check_sla_violation(metric_name, value, timestamp)
    
    def _check_sla_violation(self, metric_name: str, value: float, timestamp: float) -> None:
        """Check if metric violates SLA target."""
        target = self.sla_targets[metric_name]
        violation = False
        
        if "response_time" in metric_name:
            # Response time should be below target
            violation = value > target
            violation_type = "high_response_time"
        elif "availability" in metric_name:
            # Availability should be above target
            violation = value < target
            violation_type = "low_availability"
        elif "error_rate" in metric_name:
            # Error rate should be below target
            violation = value > target
            violation_type = "high_error_rate"
        elif "throughput" in metric_name:
            # Throughput should be above target
            violation = value < target
            violation_type = "low_throughput"
        
        if violation:
            self.violations.append({
                "metric": metric_name,
                "value": value,
                "target": target,
                "timestamp": timestamp,
                "violation_type": violation_type,
                "severity": self._calculate_violation_severity(metric_name, value, target)
            })
    
    def _calculate_violation_severity(self, metric_name: str, value: float, target: float) -> str:
        """Calculate violation severity."""
        if "response_time" in metric_name:
            ratio = value / target
            if ratio > 2.0:
                return "critical"
            elif ratio > 1.5:
                return "high"
            else:
                return "medium"
        elif "availability" in metric_name:
            gap = target - value
            if gap > 1.0:
                return "critical"
            elif gap > 0.5:
                return "high"
            else:
                return "medium"
        else:
            gap = abs(value - target) / target
            if gap > 0.5:
                return "high"
            else:
                return "medium"
    
    def get_sla_status(self) -> Dict[str, Any]:
        """Get current SLA compliance status."""
        current_time = time.time()
        status = {}
        
        for metric_name, target in self.sla_targets.items():
            recent_values = [
                value for timestamp, value in self.sla_metrics[metric_name]
                if current_time - timestamp <= 3600  # Last hour
            ]
            
            if recent_values:
                avg_value = statistics.mean(recent_values)
                compliant = self._is_compliant(metric_name, avg_value, target)
                
                status[metric_name] = {
                    "current_value": avg_value,
                    "target": target,
                    "compliant": compliant,
                    "samples": len(recent_values)
                }
            else:
                status[metric_name] = {
                    "current_value": None,
                    "target": target,
                    "compliant": False,
                    "samples": 0
                }
        
        return status
    
    def _is_compliant(self, metric_name: str, value: float, target: float) -> bool:
        """Check if metric value is compliant with SLA target."""
        if "response_time" in metric_name or "error_rate" in metric_name:
            return value <= target
        elif "availability" in metric_name or "throughput" in metric_name:
            return value >= target
        else:
            return True
    
    def get_recent_violations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent SLA violations."""
        cutoff_time = time.time() - (hours * 3600)
        return [
            v for v in self.violations
            if v["timestamp"] >= cutoff_time
        ]
    
    def generate_sla_report(self) -> Dict[str, Any]:
        """Generate comprehensive SLA compliance report."""
        status = self.get_sla_status()
        recent_violations = self.get_recent_violations()
        
        overall_compliance = all(s["compliant"] for s in status.values() if s["current_value"] is not None)
        
        report = {
            "overall_compliance": overall_compliance,
            "generation_time": datetime.utcnow().isoformat(),
            "metrics_status": status,
            "recent_violations": recent_violations,
            "violation_summary": {
                "total_violations": len(recent_violations),
                "by_severity": {},
                "by_metric": {}
            }
        }
        
        # Summarize violations
        for violation in recent_violations:
            severity = violation["severity"]
            metric = violation["metric"]
            
            if severity not in report["violation_summary"]["by_severity"]:
                report["violation_summary"]["by_severity"][severity] = 0
            report["violation_summary"]["by_severity"][severity] += 1
            
            if metric not in report["violation_summary"]["by_metric"]:
                report["violation_summary"]["by_metric"][metric] = 0
            report["violation_summary"]["by_metric"][metric] += 1
        
        return report

class PerformanceBenchmarker:
    """Performs performance benchmarking and regression testing."""
    
    def __init__(self):
        self.benchmarks: Dict[str, Dict[str, Any]] = {}
        self.baseline_metrics: Dict[str, float] = {}
        self.regression_threshold = 0.1  # 10% performance regression threshold
    
    def run_benchmark(self, benchmark_name: str, test_function: Callable, 
                     iterations: int = 10, warmup: int = 3) -> Dict[str, Any]:
        """Run performance benchmark."""
        results = []
        
        # Warmup runs
        for _ in range(warmup):
            try:
                test_function()
            except Exception:
                pass
        
        # Actual benchmark runs
        for i in range(iterations):
            start_time = time.perf_counter()
            try:
                result = test_function()
                end_time = time.perf_counter()
                
                execution_time = end_time - start_time
                results.append({
                    "iteration": i + 1,
                    "execution_time": execution_time,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                end_time = time.perf_counter()
                results.append({
                    "iteration": i + 1,
                    "execution_time": end_time - start_time,
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            execution_times = [r["execution_time"] for r in successful_results]
            
            benchmark_result = {
                "name": benchmark_name,
                "timestamp": datetime.utcnow().isoformat(),
                "iterations": iterations,
                "successful_runs": len(successful_results),
                "failed_runs": len(results) - len(successful_results),
                "statistics": {
                    "mean": statistics.mean(execution_times),
                    "median": statistics.median(execution_times),
                    "min": min(execution_times),
                    "max": max(execution_times),
                    "stdev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                    "p95": np.percentile(execution_times, 95),
                    "p99": np.percentile(execution_times, 99)
                },
                "raw_results": results
            }
        else:
            benchmark_result = {
                "name": benchmark_name,
                "timestamp": datetime.utcnow().isoformat(),
                "iterations": iterations,
                "successful_runs": 0,
                "failed_runs": iterations,
                "error": "All benchmark runs failed"
            }
        
        self.benchmarks[benchmark_name] = benchmark_result
        return benchmark_result
    
    def set_baseline(self, benchmark_name: str, metrics: Dict[str, float]) -> None:
        """Set baseline performance metrics."""
        self.baseline_metrics[benchmark_name] = metrics
        logging.info(f"Set baseline for {benchmark_name}: {metrics}")
    
    def check_regression(self, benchmark_name: str, current_result: Dict[str, Any]) -> Dict[str, Any]:
        """Check for performance regression compared to baseline."""
        if benchmark_name not in self.baseline_metrics:
            return {"status": "no_baseline", "regression_detected": False}
        
        baseline = self.baseline_metrics[benchmark_name]
        current_stats = current_result.get("statistics", {})
        
        if not current_stats:
            return {"status": "no_current_stats", "regression_detected": False}
        
        regression_results = {}
        
        # Check mean execution time regression
        current_mean = current_stats.get("mean", 0)
        baseline_mean = baseline.get("mean", 0)
        
        if baseline_mean > 0:
            regression_ratio = (current_mean - baseline_mean) / baseline_mean
            regression_detected = regression_ratio > self.regression_threshold
            
            regression_results["mean_execution_time"] = {
                "baseline": baseline_mean,
                "current": current_mean,
                "regression_ratio": regression_ratio,
                "regression_detected": regression_detected,
                "threshold": self.regression_threshold
            }
        
        # Check P95 execution time regression
        current_p95 = current_stats.get("p95", 0)
        baseline_p95 = baseline.get("p95", 0)
        
        if baseline_p95 > 0:
            regression_ratio = (current_p95 - baseline_p95) / baseline_p95
            regression_detected = regression_ratio > self.regression_threshold
            
            regression_results["p95_execution_time"] = {
                "baseline": baseline_p95,
                "current": current_p95,
                "regression_ratio": regression_ratio,
                "regression_detected": regression_detected,
                "threshold": self.regression_threshold
            }
        
        # Overall regression status
        any_regression = any(
            result.get("regression_detected", False) 
            for result in regression_results.values()
        )
        
        return {
            "status": "analyzed",
            "regression_detected": any_regression,
            "detailed_results": regression_results,
            "recommendations": self._generate_regression_recommendations(regression_results)
        }
    
    def _generate_regression_recommendations(self, regression_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for performance regression."""
        recommendations = []
        
        for metric, result in regression_results.items():
            if result.get("regression_detected", False):
                if "execution_time" in metric:
                    recommendations.extend([
                        "Profile the code to identify performance bottlenecks",
                        "Optimize algorithms and data structures",
                        "Implement caching for expensive operations",
                        "Consider database query optimization",
                        "Review recent code changes for performance impacts"
                    ])
        
        return list(set(recommendations))  # Remove duplicates

class EnterprisePerformanceMonitor:
    """Main enterprise performance monitoring system."""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.resource_monitor = SystemResourceMonitor()
        self.sla_monitor = SLAMonitor()
        self.benchmarker = PerformanceBenchmarker()
        self.performance_metrics: deque = deque(maxlen=10000)
        self.monitoring_enabled = False
        
    def start_monitoring(self) -> None:
        """Start all monitoring components."""
        if self.monitoring_enabled:
            return
        
        self.resource_monitor.start_monitoring()
        self.monitoring_enabled = True
        logging.info("Enterprise performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop all monitoring components."""
        self.resource_monitor.stop_monitoring()
        self.monitoring_enabled = False
        logging.info("Enterprise performance monitoring stopped")
    
    def record_performance_metric(self, metric: PerformanceMetric) -> None:
        """Record a performance metric."""
        self.performance_metrics.append(metric)
        
        # Update SLA monitor if applicable
        if metric.name in self.sla_monitor.sla_targets:
            self.sla_monitor.record_metric(metric.name, metric.value, metric.timestamp)
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            "generation_time": datetime.utcnow().isoformat(),
            "monitoring_status": {
                "enabled": self.monitoring_enabled,
                "resource_monitoring": self.resource_monitor.monitoring,
                "total_metrics": len(self.performance_metrics)
            },
            "resource_utilization": self._get_resource_summary(),
            "performance_profiles": self._get_performance_profiles(),
            "bottleneck_analysis": self._get_bottleneck_analysis(),
            "capacity_recommendations": self._get_capacity_recommendations(),
            "sla_status": self.sla_monitor.get_sla_status(),
            "sla_violations": self.sla_monitor.get_recent_violations(),
            "trends": self.resource_monitor.calculate_trends()
        }
        
        return report
    
    def _get_resource_summary(self) -> Dict[str, Any]:
        """Get resource utilization summary."""
        current_metrics = self.resource_monitor.get_current_metrics()
        if not current_metrics:
            return {}
        
        return {
            "cpu_percent": current_metrics.cpu_percent,
            "memory_percent": current_metrics.memory_usage["percent"],
            "memory_available_gb": current_metrics.memory_usage["available"] / (1024**3),
            "memory_used_gb": current_metrics.memory_usage["used"] / (1024**3),
            "swap_percent": current_metrics.memory_usage["swap_percent"],
            "disk_usage_percent": self._calculate_disk_usage_percent(),
            "network_io": current_metrics.network_io
        }
    
    def _calculate_disk_usage_percent(self) -> float:
        """Calculate current disk usage percentage."""
        try:
            disk_usage = psutil.disk_usage('/')
            return (disk_usage.used / disk_usage.total) * 100
        except:
            return 0.0
    
    def _get_performance_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get performance profiles summary."""
        profiles = self.profiler.get_all_profiles()
        return {
            name: asdict(profile) for name, profile in profiles.items()
        }
    
    def _get_bottleneck_analysis(self) -> List[Dict[str, Any]]:
        """Get bottleneck analysis results."""
        bottlenecks = self.profiler.analyze_bottlenecks()
        return [asdict(bottleneck) for bottleneck in bottlenecks]
    
    def _get_capacity_recommendations(self) -> List[Dict[str, Any]]:
        """Get capacity planning recommendations."""
        recommendations = self.resource_monitor.generate_capacity_recommendations()
        return [asdict(rec) for rec in recommendations]
    
    @contextmanager
    def performance_monitor(self, operation_name: str, tags: Dict[str, str] = None):
        """Context manager for comprehensive performance monitoring."""
        tags = tags or {}
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            yield
            success = True
        except Exception as e:
            success = False
            raise
        finally:
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Record metrics
            self.record_performance_metric(PerformanceMetric(
                name=f"operation_{operation_name}_duration",
                value=execution_time,
                timestamp=time.time(),
                unit="seconds",
                tags=tags
            ))
            
            self.record_performance_metric(PerformanceMetric(
                name=f"operation_{operation_name}_memory_delta",
                value=memory_delta,
                timestamp=time.time(),
                unit="megabytes",
                tags=tags
            ))
            
            self.record_performance_metric(PerformanceMetric(
                name=f"operation_{operation_name}_success",
                value=1.0 if success else 0.0,
                timestamp=time.time(),
                unit="boolean",
                tags=tags
            ))

# Global performance monitor instance
performance_monitor: Optional[EnterprisePerformanceMonitor] = None

def get_performance_monitor() -> EnterprisePerformanceMonitor:
    """Get or create global performance monitor instance."""
    global performance_monitor
    if performance_monitor is None:
        performance_monitor = EnterprisePerformanceMonitor()
    return performance_monitor

def profile_performance(operation_name: str):
    """Decorator for automatic performance profiling."""
    def decorator(func):
        monitor = get_performance_monitor()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with monitor.performance_monitor(operation_name):
                result = func(*args, **kwargs)
            return result
        
        # Apply function-level profiling
        wrapper = monitor.profiler.profile_function(operation_name)(wrapper)
        
        return wrapper
    return decorator

# Initialize performance monitoring
def initialize_performance_monitoring():
    """Initialize the enterprise performance monitoring system."""
    monitor = get_performance_monitor()
    monitor.start_monitoring()
    logging.info("Enterprise performance monitoring initialized")
    return monitor

if __name__ == "__main__":
    # Example usage and testing
    initialize_performance_monitoring()
    
    monitor = get_performance_monitor()
    
    # Test performance monitoring
    print("Testing performance monitoring...")
    
    @profile_performance("test_operation")
    def test_operation():
        """Test operation for performance monitoring."""
        time.sleep(0.1)  # Simulate work
        return "success"
    
    # Run test operation multiple times
    for i in range(5):
        test_operation()
    
    # Generate comprehensive report
    report = monitor.get_comprehensive_report()
    print(f"Performance Report Generated:")
    print(f"- Total metrics collected: {report['monitoring_status']['total_metrics']}")
    print(f"- Active performance profiles: {len(report['performance_profiles'])}")
    print(f"- Bottlenecks detected: {len(report['bottleneck_analysis'])}")
    print(f"- Capacity recommendations: {len(report['capacity_recommendations'])}")
    
    # Run SLA monitoring test
    print("\nTesting SLA monitoring...")
    monitor.sla_monitor.record_metric("api_response_time_p95", 1.5)
    monitor.sla_monitor.record_metric("api_availability", 99.5)
    
    sla_status = monitor.sla_monitor.get_sla_status()
    print(f"SLA Status: {sla_status}")
    
    # Run benchmark test
    print("\nTesting performance benchmarking...")
    
    def benchmark_function():
        """Benchmark test function."""
        time.sleep(0.05)
        return sum(range(1000))
    
    benchmark_result = monitor.benchmarker.run_benchmark(
        "test_benchmark", 
        benchmark_function, 
        iterations=10
    )
    print(f"Benchmark Result: {benchmark_result['statistics']}")
    
    # Test regression detection
    monitor.benchmarker.set_baseline("test_benchmark", {
        "mean": 0.06,
        "p95": 0.08
    })
    
    regression_check = monitor.benchmarker.check_regression("test_benchmark", benchmark_result)
    print(f"Regression Check: {regression_check}")
    
    monitor.stop_monitoring()
    print("✅ Performance monitoring test completed")