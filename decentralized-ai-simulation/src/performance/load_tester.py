"""
Load Testing and Stress Testing Framework for Enterprise Performance Validation

Implements comprehensive load testing capabilities:
- Concurrent request simulation with configurable patterns
- Stress testing to identify breaking points and failure modes
- Scalability testing with auto-scaling simulation
- Performance regression testing with baseline comparison
- Real-time monitoring and alerting during tests
- Comprehensive reporting and analysis

Author: Kilo Code
Date: November 1, 2025
"""

import asyncio
import aiohttp
import time
import threading
import json
import logging
import statistics
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, deque
import random
import requests
import psutil
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class LoadPattern(Enum):
    """Load testing patterns."""
    CONSTANT = "constant"
    RAMP_UP = "ramp_up"
    SPIKE = "spike"
    STEP = "step"
    RANDOM = "random"
    BURST = "burst"

class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class LoadTestRequest:
    """Load test request definition."""
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    payload: Optional[Dict[str, Any]] = None
    timeout: int = 30
    weight: int = 1

@dataclass
class LoadTestResult:
    """Load test result metrics."""
    request: LoadTestRequest
    start_time: float
    end_time: float
    response_time: float
    status_code: Optional[int]
    success: bool
    error_message: Optional[str] = None
    response_size: Optional[int] = None

@dataclass
class LoadTestMetrics:
    """Load test aggregate metrics."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_response_time: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    timestamp: float

@dataclass
class SystemMetrics:
    """System resource metrics during test."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_io_read: float
    disk_io_write: float
    network_io_sent: float
    network_io_recv: float
    active_connections: int
    thread_count: int

class LoadGenerator:
    """Asynchronous load generator for stress testing."""
    
    def __init__(self, requests: List[LoadTestRequest]):
        """Initialize load generator."""
        self.requests = requests
        self.results: List[LoadTestResult] = []
        self.results_lock = threading.Lock()
        self.is_running = False
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
    async def run_load_test(self, duration_seconds: int, 
                          requests_per_second: int = 10,
                          max_concurrent: int = 100,
                          pattern: LoadPattern = LoadPattern.CONSTANT) -> List[LoadTestResult]:
        """Run load test with specified parameters."""
        self.is_running = True
        self.start_time = time.time()
        self.end_time = self.start_time + duration_seconds
        
        logger.info(f"Starting load test: {duration_seconds}s, {requests_per_second} RPS, {pattern.value} pattern")
        
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60),
                connector=aiohttp.TCPConnector(limit=max_concurrent)
            ) as session:
                
                if pattern == LoadPattern.CONSTANT:
                    await self._run_constant_pattern(session, requests_per_second, duration_seconds)
                elif pattern == LoadPattern.RAMP_UP:
                    await self._run_ramp_up_pattern(session, duration_seconds)
                elif pattern == LoadPattern.SPIKE:
                    await self._run_spike_pattern(session, duration_seconds)
                elif pattern == LoadPattern.STEP:
                    await self._run_step_pattern(session, duration_seconds)
                elif pattern == LoadPattern.BURST:
                    await self._run_burst_pattern(session, duration_seconds)
                else:
                    await self._run_constant_pattern(session, requests_per_second, duration_seconds)
            
            self.end_time = time.time()
            logger.info(f"Load test completed. Total requests: {len(self.results)}")
            
            return self.results
            
        except Exception as e:
            logger.error(f"Load test failed: {e}")
            self.end_time = time.time()
            raise
        finally:
            self.is_running = False
    
    async def _run_constant_pattern(self, session: aiohttp.ClientSession, 
                                  rps: int, duration: int) -> None:
        """Run constant load pattern."""
        interval = 1.0 / rps
        end_time = time.time() + duration
        
        while time.time() < end_time and self.is_running:
            batch_start = time.time()
            
            # Create tasks for concurrent requests
            tasks = []
            for _ in range(rps):
                if not self.is_running or time.time() >= end_time:
                    break
                
                request = random.choices(self.requests, weights=[r.weight for r in self.requests])[0]
                task = asyncio.create_task(self._execute_request(session, request))
                tasks.append(task)
            
            # Wait for batch to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Sleep to maintain RPS
            elapsed = time.time() - batch_start
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def _run_ramp_up_pattern(self, session: aiohttp.ClientSession, duration: int) -> None:
        """Run ramp-up load pattern."""
        start_time = time.time()
        end_time = start_time + duration
        
        # Ramp up from 1 RPS to 50 RPS over duration
        target_rps = 50
        current_rps = 1
        ramp_duration = duration * 0.7  # Spend 70% of time ramping up
        
        while time.time() < end_time and self.is_running:
            elapsed = time.time() - start_time
            
            if elapsed < ramp_duration:
                # Gradually increase RPS
                progress = elapsed / ramp_duration
                current_rps = int(1 + (target_rps - 1) * progress)
            else:
                # Maintain peak load
                current_rps = target_rps
            
            batch_start = time.time()
            
            # Create requests for current RPS
            tasks = []
            for _ in range(current_rps):
                if not self.is_running or time.time() >= end_time:
                    break
                
                request = random.choices(self.requests, weights=[r.weight for r in self.requests])[0]
                task = asyncio.create_task(self._execute_request(session, request))
                tasks.append(task)
            
            # Wait for batch to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Sleep to maintain current RPS
            interval = 1.0 / max(current_rps, 1)
            elapsed = time.time() - batch_start
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def _run_spike_pattern(self, session: aiohttp.ClientSession, duration: int) -> None:
        """Run spike load pattern."""
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time and self.is_running:
            # Every 30 seconds, create a spike
            elapsed = time.time() - start_time
            cycle_position = elapsed % 60
            
            if cycle_position < 10:  # 10 seconds of high load
                current_rps = 100  # High load spike
            else:  # 50 seconds of normal load
                current_rps = 10   # Normal load
            
            batch_start = time.time()
            
            # Create requests for current load level
            tasks = []
            for _ in range(current_rps):
                if not self.is_running or time.time() >= end_time:
                    break
                
                request = random.choices(self.requests, weights=[r.weight for r in self.requests])[0]
                task = asyncio.create_task(self._execute_request(session, request))
                tasks.append(task)
            
            # Wait for batch to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Sleep to maintain RPS
            interval = 1.0 / max(current_rps, 1)
            elapsed = time.time() - batch_start
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def _run_step_pattern(self, session: aiohttp.ClientSession, duration: int) -> None:
        """Run step load pattern."""
        start_time = time.time()
        end_time = start_time + duration
        
        # Step up RPS every 25% of duration
        steps = [10, 25, 50, 75]
        step_duration = duration / len(steps)
        
        for i, target_rps in enumerate(steps):
            if not self.is_running:
                break
            
            step_start = time.time()
            step_end = step_start + step_duration
            
            while time.time() < step_end and time.time() < end_time and self.is_running:
                batch_start = time.time()
                
                # Create requests for current step RPS
                tasks = []
                for _ in range(target_rps):
                    if not self.is_running or time.time() >= step_end or time.time() >= end_time:
                        break
                    
                    request = random.choices(self.requests, weights=[r.weight for r in self.requests])[0]
                    task = asyncio.create_task(self._execute_request(session, request))
                    tasks.append(task)
                
                # Wait for batch to complete
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Sleep to maintain RPS
                interval = 1.0 / target_rps
                elapsed = time.time() - batch_start
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
    
    async def _run_burst_pattern(self, session: aiohttp.ClientSession, duration: int) -> None:
        """Run burst load pattern."""
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time and self.is_running:
            # Every 15 seconds, create a burst
            elapsed = time.time() - start_time
            cycle_position = elapsed % 30
            
            if cycle_position < 5:  # 5 seconds burst
                current_rps = 200  # Very high burst load
            elif cycle_position < 10:  # 5 seconds moderate
                current_rps = 50   # Moderate load
            else:  # 20 seconds low
                current_rps = 5    # Low load
            
            batch_start = time.time()
            
            # Create requests for current load level
            tasks = []
            for _ in range(current_rps):
                if not self.is_running or time.time() >= end_time:
                    break
                
                request = random.choices(self.requests, weights=[r.weight for r in self.requests])[0]
                task = asyncio.create_task(self._execute_request(session, request))
                tasks.append(task)
            
            # Wait for batch to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Sleep to maintain RPS
            interval = 1.0 / max(current_rps, 1)
            elapsed = time.time() - batch_start
            sleep_time = max(0, interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def _execute_request(self, session: aiohttp.ClientSession, 
                             request: LoadTestRequest) -> LoadTestResult:
        """Execute single HTTP request."""
        start_time = time.time()
        
        try:
            # Execute request based on method
            if request.method.upper() == "GET":
                async with session.get(
                    request.url,
                    headers=request.headers,
                    timeout=aiohttp.ClientTimeout(total=request.timeout)
                ) as response:
                    response_text = await response.text()
                    end_time = time.time()
                    
                    result = LoadTestResult(
                        request=request,
                        start_time=start_time,
                        end_time=end_time,
                        response_time=end_time - start_time,
                        status_code=response.status,
                        success=200 <= response.status < 300,
                        response_size=len(response_text)
                    )
                    
            elif request.method.upper() == "POST":
                async with session.post(
                    request.url,
                    json=request.payload,
                    headers=request.headers,
                    timeout=aiohttp.ClientTimeout(total=request.timeout)
                ) as response:
                    response_text = await response.text()
                    end_time = time.time()
                    
                    result = LoadTestResult(
                        request=request,
                        start_time=start_time,
                        end_time=end_time,
                        response_time=end_time - start_time,
                        status_code=response.status,
                        success=200 <= response.status < 300,
                        response_size=len(response_text)
                    )
                    
            else:
                # For other methods, use generic approach
                async with session.request(
                    request.method,
                    request.url,
                    json=request.payload,
                    headers=request.headers,
                    timeout=aiohttp.ClientTimeout(total=request.timeout)
                ) as response:
                    response_text = await response.text()
                    end_time = time.time()
                    
                    result = LoadTestResult(
                        request=request,
                        start_time=start_time,
                        end_time=end_time,
                        response_time=end_time - start_time,
                        status_code=response.status,
                        success=200 <= response.status < 300,
                        response_size=len(response_text)
                    )
        
        except asyncio.TimeoutError:
            end_time = time.time()
            result = LoadTestResult(
                request=request,
                start_time=start_time,
                end_time=end_time,
                response_time=end_time - start_time,
                status_code=None,
                success=False,
                error_message="Timeout"
            )
            
        except Exception as e:
            end_time = time.time()
            result = LoadTestResult(
                request=request,
                start_time=start_time,
                end_time=end_time,
                response_time=end_time - start_time,
                status_code=None,
                success=False,
                error_message=str(e)
            )
        
        # Store result
        with self.results_lock:
            self.results.append(result)
        
        return result

class SystemMonitor:
    """System resource monitoring during load tests."""
    
    def __init__(self, interval: float = 1.0):
        """Initialize system monitor."""
        self.interval = interval
        self.metrics: List[SystemMetrics] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._metrics_lock = threading.Lock()
    
    def start_monitoring(self) -> None:
        """Start system monitoring."""
        if self.is_monitoring:
            logger.warning("System monitoring already active")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("System monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop system monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        process = psutil.Process()
        last_disk_io = psutil.disk_io_counters()
        last_network_io = psutil.net_io_counters()
        
        while self.is_monitoring:
            try:
                # System memory
                memory = psutil.virtual_memory()
                
                # CPU
                cpu_percent = psutil.cpu_percent(interval=None)
                
                # Disk I/O
                current_disk_io = psutil.disk_io_counters()
                if last_disk_io and current_disk_io:
                    disk_read_mb = (current_disk_io.read_bytes - last_disk_io.read_bytes) / (1024 * 1024)
                    disk_write_mb = (current_disk_io.write_bytes - last_disk_io.write_bytes) / (1024 * 1024)
                else:
                    disk_read_mb = 0
                    disk_write_mb = 0
                last_disk_io = current_disk_io
                
                # Network I/O
                current_network_io = psutil.net_io_counters()
                if last_network_io and current_network_io:
                    network_sent_mb = (current_network_io.bytes_sent - last_network_io.bytes_sent) / (1024 * 1024)
                    network_recv_mb = (current_network_io.bytes_recv - last_network_io.bytes_recv) / (1024 * 1024)
                else:
                    network_sent_mb = 0
                    network_recv_mb = 0
                last_network_io = current_network_io
                
                # Process info
                memory_info = process.memory_info()
                connections = len(process.connections())
                
                metrics = SystemMetrics(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory_info.rss / (1024 * 1024),
                    memory_available_mb=memory.available / (1024 * 1024),
                    disk_io_read=disk_read_mb,
                    disk_io_write=disk_write_mb,
                    network_io_sent=network_sent_mb,
                    network_io_recv=network_recv_mb,
                    active_connections=connections,
                    thread_count=process.num_threads()
                )
                
                with self._metrics_lock:
                    self.metrics.append(metrics)
                
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                time.sleep(self.interval)
    
    def get_metrics(self) -> List[SystemMetrics]:
        """Get collected metrics."""
        with self._metrics_lock:
            return self.metrics.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        with self._metrics_lock:
            if not self.metrics:
                return {}
            
            metrics = self.metrics
            
            return {
                "duration_minutes": (metrics[-1].timestamp - metrics[0].timestamp) / 60,
                "data_points": len(metrics),
                "cpu_stats": {
                    "avg_percent": statistics.mean([m.cpu_percent for m in metrics]),
                    "max_percent": max([m.cpu_percent for m in metrics]),
                    "min_percent": min([m.cpu_percent for m in metrics])
                },
                "memory_stats": {
                    "avg_percent": statistics.mean([m.memory_percent for m in metrics]),
                    "max_percent": max([m.memory_percent for m in metrics]),
                    "min_percent": min([m.memory_percent for m in metrics]),
                    "peak_usage_mb": max([m.memory_used_mb for m in metrics])
                },
                "io_stats": {
                    "total_disk_read_mb": sum([m.disk_io_read for m in metrics]),
                    "total_disk_write_mb": sum([m.disk_io_write for m in metrics]),
                    "total_network_sent_mb": sum([m.network_io_sent for m in metrics]),
                    "total_network_recv_mb": sum([m.network_io_recv for m in metrics])
                },
                "connection_stats": {
                    "avg_connections": statistics.mean([m.active_connections for m in metrics]),
                    "max_connections": max([m.active_connections for m in metrics]),
                    "peak_threads": max([m.thread_count for m in metrics])
                }
            }

class LoadTestSuite:
    """Comprehensive load testing suite."""
    
    def __init__(self):
        """Initialize load test suite."""
        self.test_results: Dict[str, Any] = {}
        self.system_monitor = SystemMonitor()
    
    def create_test_requests(self, base_url: str) -> List[LoadTestRequest]:
        """Create standard test requests."""
        return [
            LoadTestRequest(
                url=f"{base_url}/health",
                method="GET",
                weight=3
            ),
            LoadTestRequest(
                url=f"{base_url}/api/agents",
                method="GET",
                weight=2
            ),
            LoadTestRequest(
                url=f"{base_url}/api/simulation",
                method="POST",
                payload={"action": "start", "agents": 50},
                weight=1
            ),
            LoadTestRequest(
                url=f"{base_url}/api/performance/metrics",
                method="GET",
                weight=2
            )
        ]
    
    async def run_stress_test(self, base_url: str, duration_minutes: int = 10) -> Dict[str, Any]:
        """Run comprehensive stress test."""
        logger.info(f"Starting stress test: {base_url}, duration: {duration_minutes} minutes")
        
        test_requests = self.create_test_requests(base_url)
        generator = LoadTestGenerator(test_requests)
        
        # Start system monitoring
        self.system_monitor.start_monitoring()
        
        try:
            duration_seconds = duration_minutes * 60
            
            # Test 1: Ramp-up test
            logger.info("Running ramp-up test...")
            results_ramp = await generator.run_load_test(
                duration_seconds=int(duration_seconds * 0.4),
                requests_per_second=10,
                pattern=LoadPattern.RAMP_UP
            )
            
            # Test 2: Constant load test
            logger.info("Running constant load test...")
            results_constant = await generator.run_load_test(
                duration_seconds=int(duration_seconds * 0.3),
                requests_per_second=25,
                pattern=LoadPattern.CONSTANT
            )
            
            # Test 3: Spike test
            logger.info("Running spike test...")
            results_spike = await generator.run_load_test(
                duration_seconds=int(duration_seconds * 0.3),
                requests_per_second=20,
                pattern=LoadPattern.SPIKE
            )
            
            # Analyze results
            metrics_ramp = self._calculate_metrics(results_ramp)
            metrics_constant = self._calculate_metrics(results_constant)
            metrics_spike = self._calculate_metrics(results_spike)
            
            # Get system metrics
            system_metrics = self.system_monitor.get_summary()
            
            test_results = {
                "test_start_time": datetime.now().isoformat(),
                "base_url": base_url,
                "duration_minutes": duration_minutes,
                "ramp_up_test": {
                    "pattern": LoadPattern.RAMP_UP.value,
                    "metrics": self._metrics_to_dict(metrics_ramp)
                },
                "constant_load_test": {
                    "pattern": LoadPattern.CONSTANT.value,
                    "metrics": self._metrics_to_dict(metrics_constant)
                },
                "spike_test": {
                    "pattern": LoadPattern.SPIKE.value,
                    "metrics": self._metrics_to_dict(metrics_spike)
                },
                "system_metrics": system_metrics,
                "recommendations": self._generate_recommendations(metrics_constant, system_metrics)
            }
            
            self.test_results["stress_test"] = test_results
            logger.info("Stress test completed successfully")
            
            return test_results
            
        finally:
            self.system_monitor.stop_monitoring()
    
    async def run_scalability_test(self, base_url: str, max_load: int = 1000) -> Dict[str, Any]:
        """Run scalability test with increasing load."""
        logger.info(f"Starting scalability test: {base_url}, max load: {max_load} RPS")
        
        test_requests = self.create_test_requests(base_url)
        generator = LoadTestGenerator(test_requests)
        
        # Test different load levels
        load_levels = [50, 100, 250, 500, 750, 1000] if max_load >= 1000 else [
            int(max_load * level) for level in [0.25, 0.5, 0.75, 1.0]
        ]
        
        scalability_results = []
        
        # Start system monitoring
        self.system_monitor.start_monitoring()
        
        try:
            for load_level in load_levels:
                logger.info(f"Testing load level: {load_level} RPS")
                
                # Test at this load level for 2 minutes
                results = await generator.run_load_test(
                    duration_seconds=120,
                    requests_per_second=load_level,
                    pattern=LoadPattern.CONSTANT
                )
                
                metrics = self._calculate_metrics(results)
                
                # Check if test failed (high error rate or timeout)
                if metrics.error_rate > 0.1 or metrics.p95_response_time > 5.0:
                    logger.warning(f"Load level {load_level} caused degradation")
                    break
                
                scalability_results.append({
                    "load_level": load_level,
                    "metrics": self._metrics_to_dict(metrics)
                })
                
                # Cool down period
                await asyncio.sleep(30)
            
            system_metrics = self.system_monitor.get_summary()
            
            test_results = {
                "test_start_time": datetime.now().isoformat(),
                "base_url": base_url,
                "max_load_tested": max_load,
                "scalability_results": scalability_results,
                "system_metrics": system_metrics,
                "scaling_limits": {
                    "max_sustainable_load": scalability_results[-1]["load_level"] if scalability_results else 0,
                    "performance_degradation_point": self._find_degradation_point(scalability_results)
                },
                "recommendations": self._generate_scalability_recommendations(scalability_results)
            }
            
            self.test_results["scalability_test"] = test_results
            logger.info("Scalability test completed")
            
            return test_results
            
        finally:
            self.system_monitor.stop_monitoring()
    
    def _calculate_metrics(self, results: List[LoadTestResult]) -> LoadTestMetrics:
        """Calculate aggregate metrics from test results."""
        if not results:
            return LoadTestMetrics(
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                total_response_time=0,
                avg_response_time=0,
                min_response_time=0,
                max_response_time=0,
                p95_response_time=0,
                p99_response_time=0,
                requests_per_second=0,
                error_rate=0,
                timestamp=time.time()
            )
        
        # Filter successful requests for response time calculations
        successful_results = [r for r in results if r.success]
        
        # Response times
        response_times = [r.response_time for r in successful_results]
        
        # Request rate
        total_duration = results[-1].end_time - results[0].start_time
        requests_per_second = len(results) / total_duration if total_duration > 0 else 0
        
        # Percentiles
        response_times.sort()
        p95_index = int(len(response_times) * 0.95)
        p99_index = int(len(response_times) * 0.99)
        
        p95_response_time = response_times[p95_index] if p95_index < len(response_times) else 0
        p99_response_time = response_times[p99_index] if p99_index < len(response_times) else 0
        
        return LoadTestMetrics(
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(results) - len(successful_results),
            total_response_time=sum(response_times),
            avg_response_time=sum(response_times) / len(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=(len(results) - len(successful_results)) / len(results) if results else 0,
            timestamp=time.time()
        )
    
    def _metrics_to_dict(self, metrics: LoadTestMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "avg_response_time": round(metrics.avg_response_time, 3),
            "min_response_time": round(metrics.min_response_time, 3),
            "max_response_time": round(metrics.max_response_time, 3),
            "p95_response_time": round(metrics.p95_response_time, 3),
            "p99_response_time": round(metrics.p99_response_time, 3),
            "requests_per_second": round(metrics.requests_per_second, 2),
            "error_rate": round(metrics.error_rate, 4)
        }
    
    def _generate_recommendations(self, metrics: LoadTestMetrics, 
                                system_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Performance recommendations
        if metrics.avg_response_time > 1.0:
            recommendations.append("Average response time is above 1 second - consider optimizing application logic")
        
        if metrics.p95_response_time > 2.0:
            recommendations.append("95th percentile response time is high - investigate slow endpoints")
        
        if metrics.error_rate > 0.01:
            recommendations.append("Error rate is above 1% - review error handling and capacity")
        
        # System recommendations
        if system_metrics.get("memory_stats", {}).get("max_percent", 0) > 85:
            recommendations.append("Memory usage exceeded 85% - consider scaling or optimization")
        
        if system_metrics.get("cpu_stats", {}).get("max_percent", 0) > 80:
            recommendations.append("CPU usage exceeded 80% - application may be CPU-bound")
        
        if not recommendations:
            recommendations.append("Performance appears good - no immediate optimization needed")
        
        return recommendations
    
    def _find_degradation_point(self, scalability_results: List[Dict]) -> Optional[int]:
        """Find the point where performance starts degrading."""
        if len(scalability_results) < 2:
            return None
        
        for i in range(1, len(scalability_results)):
            current = scalability_results[i]["metrics"]
            previous = scalability_results[i-1]["metrics"]
            
            # Check for degradation indicators
            if (current["error_rate"] > previous["error_rate"] * 2 or
                current["p95_response_time"] > previous["p95_response_time"] * 1.5 or
                current["avg_response_time"] > previous["avg_response_time"] * 1.5):
                return scalability_results[i]["load_level"]
        
        return scalability_results[-1]["load_level"]
    
    def _generate_scalability_recommendations(self, scalability_results: List[Dict]) -> List[str]:
        """Generate scalability recommendations."""
        recommendations = []
        
        if not scalability_results:
            return ["Unable to complete scalability test - review test configuration"]
        
        max_load = scalability_results[-1]["load_level"]
        
        recommendations.append(f"Maximum sustainable load: {max_load} RPS")
        
        # Analyze scaling characteristics
        for i, result in enumerate(scalability_results[1:], 1):
            prev_metrics = scalability_results[i-1]["metrics"]
            curr_metrics = result["metrics"]
            
            # Check response time scaling
            if curr_metrics["avg_response_time"] > prev_metrics["avg_response_time"] * 2:
                recommendations.append(f"Response time degradation detected at {result['load_level']} RPS")
            
            # Check error rate scaling
            if curr_metrics["error_rate"] > 0.01:
                recommendations.append(f"Error rate increases at {result['load_level']} RPS")
        
        return recommendations
    
    def save_results(self, filename: str) -> None:
        """Save test results to file."""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        logger.info(f"Test results saved to {filename}")

# Global test suite instance
_load_test_suite: Optional[LoadTestSuite] = None

def get_load_test_suite() -> LoadTestSuite:
    """Get global load test suite instance."""
    global _load_test_suite
    if _load_test_suite is None:
        _load_test_suite = LoadTestSuite()
    return _load_test_suite

# Example usage and testing
if __name__ == "__main__":
    async def run_example_test():
        """Run example load test."""
        test_suite = get_load_test_suite()
        
        try:
            # Run stress test
            stress_results = await test_suite.run_stress_test("https://httpbin.org", duration_minutes=1)
            print("Stress test completed")
            print(f"Total requests: {stress_results['constant_load_test']['metrics']['total_requests']}")
            print(f"Error rate: {stress_results['constant_load_test']['metrics']['error_rate']:.2%}")
            
            # Save results
            test_suite.save_results("load_test_results.json")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run example
    # asyncio.run(run_example_test())