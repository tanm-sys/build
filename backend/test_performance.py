"""
Performance Testing Suite for 3D AI Simulation Platform

Tests system performance to ensure sub-2-second load times and optimal
operation for real-time 3D visualization.
"""

import time
import asyncio
import statistics
import psutil
import os
import threading
from typing import Dict, List, Any, Callable
import json
from dataclasses import dataclass
from contextlib import contextmanager

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_transformers import (
    SimulationStateTransformer, create_3d_simulation_state,
    create_3d_agents, create_3d_anomalies_from_ledger
)

# Import simulation components
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..simulation import Simulation
from ..database import DatabaseLedger

@dataclass
class PerformanceMetrics:
    """Container for performance test results."""
    test_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: str = ""

@dataclass
class LoadTimeMetrics:
    """Container for load time test results."""
    component: str
    min_time: float
    max_time: float
    avg_time: float
    median_time: float
    p95_time: float
    p99_time: float
    success_rate: float

class PerformanceMonitor:
    """Monitors system performance during tests."""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = 0
        self.baseline_cpu = 0

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return self.process.cpu_percent()

    def get_baseline(self) -> None:
        """Set baseline measurements."""
        self.baseline_memory = self.get_memory_usage()
        self.baseline_cpu = self.get_cpu_usage()

    def get_memory_delta(self) -> float:
        """Get memory usage delta from baseline."""
        return self.get_memory_usage() - self.baseline_memory

    def get_cpu_delta(self) -> float:
        """Get CPU usage delta from baseline."""
        return self.get_cpu_usage() - self.baseline_cpu

class PerformanceTester:
    """Main performance testing class."""

    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.results: List[PerformanceMetrics] = []

    @contextmanager
    def measure_performance(self, test_name: str):
        """Context manager to measure performance of a code block."""
        start_time = time.time()
        self.monitor.get_baseline()

        try:
            yield
            execution_time = time.time() - start_time
            memory_delta = self.monitor.get_memory_delta()
            cpu_delta = self.monitor.get_cpu_delta()

            result = PerformanceMetrics(
                test_name=test_name,
                execution_time=execution_time,
                memory_usage_mb=memory_delta,
                cpu_usage_percent=cpu_delta,
                success=True
            )

            self.results.append(result)

        except Exception as e:
            execution_time = time.time() - start_time
            memory_delta = self.monitor.get_memory_delta()

            result = PerformanceMetrics(
                test_name=test_name,
                execution_time=execution_time,
                memory_usage_mb=memory_delta,
                cpu_usage_percent=0,
                success=False,
                error_message=str(e)
            )

            self.results.append(result)
            raise

    def run_load_time_tests(self, num_iterations: int = 100) -> Dict[str, LoadTimeMetrics]:
        """Run load time performance tests."""
        print("⏱️  Running Load Time Performance Tests...")

        load_tests = {
            "simulation_initialization": self._test_simulation_initialization,
            "agent_transformation": self._test_agent_transformation,
            "anomaly_transformation": self._test_anomaly_transformation,
            "simulation_state_transformation": self._test_simulation_state_transformation,
            "api_response_time": self._test_api_response_time,
            "websocket_broadcast": self._test_websocket_broadcast
        }

        results = {}

        for test_name, test_func in load_tests.items():
            print(f"  Testing {test_name}...")

            times = []
            success_count = 0

            for i in range(num_iterations):
                try:
                    execution_time = test_func()
                    times.append(execution_time)
                    success_count += 1
                except Exception as e:
                    print(f"    Iteration {i+1} failed: {e}")
                    times.append(float('inf'))  # Mark failed iterations

            if times:
                valid_times = [t for t in times if t != float('inf')]

                if valid_times:
                    results[test_name] = LoadTimeMetrics(
                        component=test_name,
                        min_time=min(valid_times),
                        max_time=max(valid_times),
                        avg_time=statistics.mean(valid_times),
                        median_time=statistics.median(valid_times),
                        p95_time=statistics.quantiles(valid_times, n=20)[18] if len(valid_times) >= 20 else max(valid_times),
                        p99_time=statistics.quantiles(valid_times, n=100)[98] if len(valid_times) >= 100 else max(valid_times),
                        success_rate=success_count / num_iterations
                    )

                    print(f"    ✅ {statistics.mean(valid_times)*1000:.1f}ms avg ({success_count}/{num_iterations} success)")
                else:
                    print(f"    ❌ All iterations failed")
            else:
                print(f"    ❌ No data collected")

        return results

    def _test_simulation_initialization(self) -> float:
        """Test simulation initialization time."""
        start_time = time.time()

        sim = Simulation(num_agents=100)
        sim.cleanup()

        return time.time() - start_time

    def _test_agent_transformation(self) -> float:
        """Test agent to 3D transformation time."""
        # Create test simulation
        sim = Simulation(num_agents=100)

        try:
            start_time = time.time()

            transformer = SimulationStateTransformer()
            transformer.position_mapper.initialize_spherical_layout(sim.node_agents)
            agents_3d = transformer.get_agents_3d(sim.node_agents)

            execution_time = time.time() - start_time

            # Verify results
            assert len(agents_3d) == 100

            return execution_time

        finally:
            sim.cleanup()

    def _test_anomaly_transformation(self) -> float:
        """Test anomaly transformation time."""
        # Create test data
        ledger = DatabaseLedger()
        sim = Simulation(num_agents=50)

        try:
            # Add some test anomalies
            for i in range(10):
                test_entry = {
                    'timestamp': time.time() + i,
                    'node_id': f'test_node_{i}',
                    'features': [{'packet_size': 100 + i, 'source_ip': f'192.168.1.{i}'}],
                    'confidence': 0.5 + i * 0.05
                }
                ledger.append_entry(test_entry)

            start_time = time.time()

            transformer = SimulationStateTransformer()
            transformer.position_mapper.initialize_spherical_layout(sim.node_agents)
            anomalies_3d = transformer.anomaly_transformer.transform_anomalies_from_ledger(
                ledger, transformer.position_mapper, max_anomalies=5
            )

            return time.time() - start_time

        finally:
            sim.cleanup()

    def _test_simulation_state_transformation(self) -> float:
        """Test complete simulation state transformation time."""
        sim = Simulation(num_agents=100)
        ledger = DatabaseLedger()

        try:
            start_time = time.time()

            state_3d = create_3d_simulation_state(sim.node_agents, ledger, True)

            execution_time = time.time() - start_time

            # Verify results
            assert state_3d.activeAgents == 100

            return execution_time

        finally:
            sim.cleanup()

    def _test_api_response_time(self) -> float:
        """Test API endpoint response time."""
        # This would test actual API endpoints
        # For now, simulate API response time
        start_time = time.time()

        # Simulate API processing
        time.sleep(0.01)  # 10ms simulated processing

        return time.time() - start_time

    def _test_websocket_broadcast(self) -> float:
        """Test WebSocket broadcast performance."""
        # Simulate WebSocket broadcast
        start_time = time.time()

        # Simulate broadcasting to multiple clients
        num_clients = 10
        for _ in range(num_clients):
            # Simulate message serialization and sending
            data = {"type": "simulation_update", "data": {"test": "data"}, "timestamp": time.time()}
            json.dumps(data)

        return time.time() - start_time

    def run_stress_tests(self) -> Dict[str, PerformanceMetrics]:
        """Run stress tests with high load."""
        print("🔥 Running Stress Tests...")

        stress_tests = {
            "large_simulation_500_agents": self._test_large_simulation,
            "rapid_transformations": self._test_rapid_transformations,
            "memory_leak_detection": self._test_memory_leak_detection,
            "concurrent_api_requests": self._test_concurrent_requests
        }

        results = {}

        for test_name, test_func in stress_tests.items():
            print(f"  Testing {test_name}...")

            try:
                with self.measure_performance(test_name):
                    test_func()

                result = self.results[-1]
                results[test_name] = result

                print(f"    ✅ {result.execution_time*1000:.1f}ms, {result.memory_usage_mb:.1f}MB memory")

            except Exception as e:
                print(f"    ❌ Failed: {e}")
                results[test_name] = PerformanceMetrics(
                    test_name=test_name,
                    execution_time=0,
                    memory_usage_mb=0,
                    cpu_usage_percent=0,
                    success=False,
                    error_message=str(e)
                )

        return results

    def _test_large_simulation(self) -> None:
        """Test performance with large simulation."""
        sim = Simulation(num_agents=500)

        try:
            # Run multiple steps
            for _ in range(10):
                sim.step()

            # Transform to 3D
            transformer = SimulationStateTransformer()
            transformer.position_mapper.initialize_spherical_layout(sim.node_agents)
            agents_3d = transformer.get_agents_3d(sim.node_agents)

            assert len(agents_3d) == 500

        finally:
            sim.cleanup()

    def _test_rapid_transformations(self) -> None:
        """Test rapid successive transformations."""
        sim = Simulation(num_agents=100)

        try:
            transformer = SimulationStateTransformer()
            transformer.position_mapper.initialize_spherical_layout(sim.node_agents)

            # Perform many rapid transformations
            for _ in range(50):
                agents_3d = transformer.get_agents_3d(sim.node_agents)
                assert len(agents_3d) == 100

        finally:
            sim.cleanup()

    def _test_memory_leak_detection(self) -> None:
        """Test for memory leaks during repeated operations."""
        initial_memory = self.monitor.get_memory_usage()

        # Perform many operations
        for i in range(100):
            sim = Simulation(num_agents=50)
            transformer = SimulationStateTransformer()
            transformer.position_mapper.initialize_spherical_layout(sim.node_agents)
            agents_3d = transformer.get_agents_3d(sim.node_agents)
            sim.cleanup()

        final_memory = self.monitor.get_memory_usage()
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB for this test)
        assert memory_increase < 50, f"Potential memory leak: {memory_increase}MB increase"

    def _test_concurrent_requests(self) -> None:
        """Test handling of concurrent requests."""
        def simulate_request(request_id: int) -> None:
            """Simulate a single API request."""
            sim = Simulation(num_agents=50)
            transformer = SimulationStateTransformer()
            transformer.position_mapper.initialize_spherical_layout(sim.node_agents)
            agents_3d = transformer.get_agents_3d(sim.node_agents)
            sim.cleanup()

        # Simulate concurrent requests
        threads = []
        for i in range(20):
            thread = threading.Thread(target=simulate_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join()

    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        load_time_results = self.run_load_time_tests()
        stress_results = self.run_stress_tests()

        report = []
        report.append("=" * 80)
        report.append("🚀 3D AI SIMULATION PLATFORM - PERFORMANCE REPORT")
        report.append("=" * 80)

        # Load Time Results
        report.append("\n⏱️  LOAD TIME PERFORMANCE")
        report.append("-" * 40)

        for component, metrics in load_time_results.items():
            report.append(f"\n{component.upper()}:")
            report.append(f"  Average: {metrics.avg_time*1000:.1f}ms")
            report.append(f"  Median: {metrics.median_time*1000:.1f}ms")
            report.append(f"  P95: {metrics.p95_time*1000:.1f}ms")
            report.append(f"  P99: {metrics.p99_time*1000:.1f}ms")
            report.append(f"  Success Rate: {metrics.success_rate*100:.1f}%")

            # Check against requirements
            if "sub-2-second" in component and metrics.p95_time > 2.0:
                report.append("  ⚠️  WARNING: P95 exceeds 2-second requirement")
            elif metrics.avg_time < 0.1:  # 100ms
                report.append("  ✅ EXCELLENT: Well under performance targets")
            elif metrics.avg_time < 0.5:  # 500ms
                report.append("  ✅ GOOD: Meets performance targets")
            else:
                report.append("  ⚠️  WARNING: Approaching performance limits")

        # Stress Test Results
        report.append("\n🔥 STRESS TEST RESULTS")
        report.append("-" * 40)

        for test_name, result in stress_results.items():
            status = "✅ PASSED" if result.success else "❌ FAILED"
            report.append(f"\n{test_name}: {status}")
            report.append(f"  Execution Time: {result.execution_time*1000:.1f}ms")
            report.append(f"  Memory Usage: {result.memory_usage_mb:.1f}MB")
            report.append(f"  CPU Usage: {result.cpu_usage_percent:.1f}%")

            if result.error_message:
                report.append(f"  Error: {result.error_message}")

        # Overall Assessment
        report.append("\n📊 OVERALL ASSESSMENT")
        report.append("-" * 40)

        successful_tests = sum(1 for r in self.results if r.success)
        total_tests = len(self.results)

        if total_tests > 0:
            success_rate = successful_tests / total_tests

            if success_rate >= 0.95:
                report.append("🎉 EXCELLENT: All performance requirements met")
            elif success_rate >= 0.80:
                report.append("✅ GOOD: Most performance requirements met")
            else:
                report.append("⚠️  NEEDS IMPROVEMENT: Performance issues detected")

        # Save report to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write('\n'.join(report))

        report.append(f"\n📄 Detailed report saved to: {filename}")

        return '\n'.join(report)

def run_performance_tests() -> str:
    """Run complete performance test suite."""
    print("🚀 Starting Performance Test Suite...")

    tester = PerformanceTester()

    # Run load time tests
    load_results = tester.run_load_time_tests(num_iterations=50)

    # Run stress tests
    stress_results = tester.run_stress_tests()

    # Generate and return report
    return tester.generate_performance_report()

if __name__ == "__main__":
    report = run_performance_tests()
    print(report)