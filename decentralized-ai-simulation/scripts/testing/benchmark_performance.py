#!/usr/bin/env python3
"""
Performance benchmarking script for the optimized decentralized AI simulation.

This script measures and validates the performance improvements made to the codebase,
including memory usage, execution speed, and scalability metrics.
"""

import gc
import time
import psutil
import os
import sys
from typing import Dict, List, Any, Tuple
from contextlib import contextmanager
import json
import argparse

# Import with fallback to handle duplicate files
try:
    from src.core.agents import AnomalyAgent, AgentFactory
    from src.core.database import DatabaseLedger
    from src.core.simulation import Simulation
    from src.utils.monitoring import get_monitoring, PerformanceMonitor
    from src.config.config_loader import get_config
    from src.utils.logging_setup import get_logger
except ImportError:
    try:
        from src.core.agents import AnomalyAgent, AgentFactory
        from src.core.database import DatabaseLedger
        from src.core.simulation import Simulation
        from src.utils.monitoring import get_monitoring, PerformanceMonitor
        from src.config.config_loader import get_config
        from src.utils.logging_setup import get_logger
    except ImportError:
        print("Error: Could not import required modules")
        sys.exit(1)

logger = get_logger(__name__)

class PerformanceBenchmark:
    """Comprehensive performance benchmarking suite."""

    def __init__(self):
        self.process = psutil.Process()
        self.monitoring = get_monitoring()
        self.performance_monitor = PerformanceMonitor(self.monitoring)
        self.results = {}

    @contextmanager
    def measure_time(self, operation_name: str):
        """Context manager to measure operation execution time and resources."""
        start_time = time.time()
        start_memory = self.process.memory_info().rss

        # Force garbage collection before measurement
        gc.collect()

        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self.process.memory_info().rss

            execution_time = end_time - start_time
            memory_used = end_memory - start_memory

            # Record metrics
            self.monitoring.record_metric(f'{operation_name}_time', execution_time)
            self.monitoring.record_metric(f'{operation_name}_memory', memory_used)

            logger.info(f"{operation_name}: {execution_time:.4f}s, {memory_used / 1024:.1f} KB")

    def benchmark_agent_creation(self, num_agents_list: List[int] = None) -> Dict[str, Any]:
        """Benchmark agent creation performance."""
        if num_agents_list is None:
            num_agents_list = [10, 50, 100, 200]

        results = {}

        for num_agents in num_agents_list:
            logger.info(f"Benchmarking agent creation for {num_agents} agents")

            with self.measure_time(f'agent_creation_{num_agents}'):
                # Create mock model
                from unittest.mock import Mock
                mock_model = Mock()
                mock_ledger = Mock()
                mock_ledger.append_entry.return_value = 1
                mock_ledger.get_new_entries.return_value = []
                mock_ledger.read_ledger.return_value = []
                mock_model.ledger = mock_ledger

                # Create agents using factory
                agents = AgentFactory.create_agents_batch(mock_model, num_agents)

                # Test lazy loading
                for agent in agents[:5]:  # Test first 5 agents
                    _ = agent.anomaly_model  # Trigger lazy loading

            # Collect memory statistics
            results[num_agents] = {
                'creation_time': self.monitoring.get_metric_stats(f'agent_creation_{num_agents}_time').get('latest', 0),
                'memory_usage': self.monitoring.get_metric_stats(f'agent_creation_{num_agents}_memory').get('latest', 0),
                'agents_created': len(agents)
            }

        return results

    def benchmark_database_operations(self, num_operations: int = 1000) -> Dict[str, Any]:
        """Benchmark database operations performance."""
        logger.info(f"Benchmarking database operations for {num_operations} operations")

        # Create temporary database for testing
        test_db = f"benchmark_test_{int(time.time())}.db"

        try:
            with self.measure_time('database_operations'):
                with DatabaseLedger(test_db) as ledger:
                    # Benchmark writes
                    for i in range(num_operations):
                        entry = {
                            'timestamp': time.time(),
                            'node_id': f'benchmark_node_{i}',
                            'features': [{'packet_size': 100.0, 'source_ip': f'192.168.1.{i}'}],
                            'confidence': 0.5
                        }
                        ledger.append_entry(entry)

                    # Benchmark reads
                    entries = ledger.read_ledger()

                    # Benchmark cache performance
                    for i in range(min(100, len(entries))):
                        _ = ledger.get_entry_by_id(i + 1)

            # Collect database statistics
            from src.core.database import get_connection_stats, get_query_stats
            connection_stats = get_connection_stats()
            query_stats = get_query_stats()

            return {
                'operations_completed': num_operations,
                'entries_created': len(entries),
                'connection_stats': connection_stats,
                'query_stats': query_stats,
                'execution_time': self.monitoring.get_metric_stats('database_operations_time').get('latest', 0),
                'memory_usage': self.monitoring.get_metric_stats('database_operations_memory').get('latest', 0)
            }

        finally:
            # Cleanup test database
            if os.path.exists(test_db):
                os.remove(test_db)

    def benchmark_simulation_performance(self, num_agents: int = 50, num_steps: int = 10) -> Dict[str, Any]:
        """Benchmark simulation performance."""
        logger.info(f"Benchmarking simulation with {num_agents} agents for {num_steps} steps")

        with self.measure_time('simulation_run'):
            try:
                # Create temporary database for simulation
                test_db = f"simulation_benchmark_{int(time.time())}.db"

                with Simulation(num_agents=num_agents) as sim:
                    sim.run(steps=num_steps)

                    # Collect final statistics
                    final_entries = sim.ledger.read_ledger()

                # Get simulation metrics
                step_times = self.monitoring.get_metric_stats('step_duration')
                validation_counts = self.monitoring.get_metric_stats('validation_count')

                return {
                    'agents': num_agents,
                    'steps': num_steps,
                    'final_ledger_entries': len(final_entries),
                    'avg_step_time': step_times.get('avg', 0) if step_times else 0,
                    'total_execution_time': self.monitoring.get_metric_stats('simulation_run_time').get('latest', 0),
                    'memory_usage': self.monitoring.get_metric_stats('simulation_run_memory').get('latest', 0)
                }

            except Exception as e:
                logger.error(f"Simulation benchmark failed: {e}")
                return {
                    'agents': num_agents,
                    'steps': num_steps,
                    'error': str(e),
                    'execution_time': self.monitoring.get_metric_stats('simulation_run_time').get('latest', 0)
                }

    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage patterns."""
        logger.info("Benchmarking memory usage patterns")

        # Force garbage collection
        gc.collect()
        initial_memory = self.process.memory_info().rss

        # Create various objects to test memory management
        agents_data = []
        cache_data = []

        with self.measure_time('memory_benchmark'):
            # Test BoundedList memory efficiency
            from src.core.agents import BoundedList
            from src.core.database import BoundedCache

            # Create bounded lists with different sizes
            for size in [100, 1000, 10000]:
                bounded_list = BoundedList(max_size=size)
                for i in range(size * 2):  # Add more items than max_size
                    bounded_list.append(f"item_{i}")

                agents_data.append({
                    'max_size': size,
                    'actual_size': len(bounded_list),
                    'memory_usage': bounded_list.get_memory_usage(),
                    'stats': bounded_list.get_stats()
                })

            # Test cache memory efficiency
            for cache_size in [100, 500, 1000]:
                cache = BoundedCache(max_size=cache_size)
                for i in range(cache_size * 2):
                    cache.put(f"key_{i}", f"value_{i}")

                cache_data.append({
                    'max_size': cache_size,
                    'actual_size': cache.size(),
                    'memory_usage': cache.get_memory_usage(),
                    'stats': cache.get_stats()
                })

        final_memory = self.process.memory_info().rss
        total_memory_used = final_memory - initial_memory

        return {
            'initial_memory_mb': initial_memory / (1024 * 1024),
            'final_memory_mb': final_memory / (1024 * 1024),
            'total_memory_used_mb': total_memory_used / (1024 * 1024),
            'bounded_lists': agents_data,
            'caches': cache_data,
            'execution_time': self.monitoring.get_metric_stats('memory_benchmark_time').get('latest', 0)
        }

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run all benchmarks and return comprehensive results."""
        logger.info("Starting comprehensive performance benchmark")

        all_results = {
            'timestamp': time.time(),
            'system_info': self._get_system_info(),
            'agent_creation': {},
            'database_operations': {},
            'simulation_performance': {},
            'memory_usage': {},
            'summary': {}
        }

        try:
            # Run individual benchmarks
            all_results['agent_creation'] = self.benchmark_agent_creation()
            all_results['database_operations'] = self.benchmark_database_operations()
            all_results['simulation_performance'] = self.benchmark_simulation_performance()
            all_results['memory_usage'] = self.benchmark_memory_usage()

            # Generate summary
            all_results['summary'] = self._generate_summary(all_results)

            logger.info("Comprehensive benchmark completed successfully")
            return all_results

        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            all_results['error'] = str(e)
            return all_results

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmark context."""
        return {
            'python_version': sys.version,
            'cpu_count': os.cpu_count(),
            'total_memory_gb': psutil.virtual_memory().total / (1024**3),
            'available_memory_gb': psutil.virtual_memory().available / (1024**3)
        }

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of benchmark results."""
        summary = {
            'total_execution_time': 0,
            'total_memory_used_mb': 0,
            'benchmarks_run': 0,
            'performance_score': 0
        }

        # Calculate totals
        for benchmark_name in ['agent_creation', 'database_operations', 'simulation_performance', 'memory_usage']:
            if benchmark_name in results and 'execution_time' in results[benchmark_name]:
                summary['total_execution_time'] += results[benchmark_name]['execution_time']
                summary['benchmarks_run'] += 1

        if 'memory_usage' in results and 'total_memory_used_mb' in results['memory_usage']:
            summary['total_memory_used_mb'] = results['memory_usage']['total_memory_used_mb']

        # Calculate performance score (lower is better)
        if summary['total_execution_time'] > 0:
            summary['performance_score'] = summary['total_memory_used_mb'] / summary['total_execution_time']

        return summary

    def export_results(self, results: Dict[str, Any], format: str = 'json') -> str:
        """Export benchmark results in specified format."""
        if format.lower() == 'json':
            return json.dumps(results, indent=2, default=str)
        elif format.lower() == 'txt':
            return self._format_results_as_text(results)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _format_results_as_text(self, results: Dict[str, Any]) -> str:
        """Format results as human-readable text."""
        lines = []
        lines.append("=" * 60)
        lines.append("PERFORMANCE BENCHMARK RESULTS")
        lines.append("=" * 60)
        lines.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # System info
        lines.append("SYSTEM INFORMATION:")
        for key, value in results['system_info'].items():
            lines.append(f"  {key}: {value}")
        lines.append("")

        # Summary
        if 'summary' in results:
            lines.append("SUMMARY:")
            for key, value in results['summary'].items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        # Individual benchmarks
        for benchmark_name, data in results.items():
            if benchmark_name not in ['timestamp', 'system_info', 'summary', 'error']:
                lines.append(f"{benchmark_name.upper()}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            lines.append(f"  {key}:")
                            for sub_key, sub_value in value.items():
                                lines.append(f"    {sub_key}: {sub_value}")
                        else:
                            lines.append(f"  {key}: {value}")
                lines.append("")

        if 'error' in results:
            lines.append(f"ERROR: {results['error']}")

        lines.append("=" * 60)
        return "\n".join(str(line) for line in lines)


def main():
    """Main function to run benchmarks."""
    parser = argparse.ArgumentParser(description='Performance benchmarking for optimized simulation')
    parser.add_argument('--quick', action='store_true', help='Run quick benchmark suite')
    parser.add_argument('--full', action='store_true', help='Run full benchmark suite')
    parser.add_argument('--agents', action='store_true', help='Benchmark only agent creation')
    parser.add_argument('--database', action='store_true', help='Benchmark only database operations')
    parser.add_argument('--simulation', action='store_true', help='Benchmark only simulation performance')
    parser.add_argument('--memory', action='store_true', help='Benchmark only memory usage')
    parser.add_argument('--export', choices=['json', 'txt'], default='txt', help='Export format')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    # Determine which benchmarks to run
    if args.quick or not any([args.agents, args.database, args.simulation, args.memory]):
        # Default quick benchmark
        benchmark = PerformanceBenchmark()
        results = benchmark.run_comprehensive_benchmark()
    else:
        # Run specific benchmarks
        benchmark = PerformanceBenchmark()
        results = {'timestamp': time.time(), 'system_info': benchmark._get_system_info()}

        if args.agents:
            results['agent_creation'] = benchmark.benchmark_agent_creation([10, 50])
        if args.database:
            results['database_operations'] = benchmark.benchmark_database_operations(500)
        if args.simulation:
            results['simulation_performance'] = benchmark.benchmark_simulation_performance(25, 5)
        if args.memory:
            results['memory_usage'] = benchmark.memory_usage()

        results['summary'] = benchmark._generate_summary(results)

    # Export results
    output = benchmark.export_results(results, args.export)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        logger.info(f"Results exported to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()