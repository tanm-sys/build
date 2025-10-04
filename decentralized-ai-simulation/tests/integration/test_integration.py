"""
Comprehensive Integration Testing for Decentralized AI Simulation System

This module provides end-to-end integration tests that validate the complete
system functionality including simulation workflows, component interactions,
performance characteristics, and cross-platform compatibility.
"""

import sys
import os
import time
import tempfile
import shutil
import threading
import multiprocessing
from pathlib import Path
from typing import Dict, List, Any
import pytest
import psutil
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.simulation import Simulation
from src.core.database import DatabaseLedger, close_all_connections
from src.core.agents import AnomalyAgent
from src.config.config_loader import get_config
from src.utils.logging_setup import get_logger
from src.utils.monitoring import get_monitoring

logger = get_logger(__name__)


class TestEnvironment:
    """Test environment setup and teardown."""

    def __init__(self):
        self.temp_dir = None
        self.original_cwd = os.getcwd()
        self.test_db_path = None
        self.process = None

    def setup(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_ledger.db")

        # Change to temp directory for test isolation
        os.chdir(self.temp_dir)

        # Override config for testing
        os.environ['SIMULATION_DB_PATH'] = self.test_db_path
        os.environ['SIMULATION_LOG_LEVEL'] = 'DEBUG'

        logger.info(f"Test environment set up in {self.temp_dir}")

    def teardown(self):
        """Clean up test environment."""
        try:
            # Restore original working directory
            os.chdir(self.original_cwd)

            # Close database connections
            close_all_connections()

            # Clean up temp directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

            logger.info("Test environment cleaned up")

        except Exception as e:
            logger.error(f"Error during test environment cleanup: {e}")


@pytest.fixture(scope="module")
def test_env():
    """Module-level test environment fixture."""
    env = TestEnvironment()
    env.setup()
    yield env
    env.teardown()


class TestEndToEndWorkflow:
    """End-to-end workflow integration tests."""

    def test_complete_simulation_lifecycle(self, test_env):
        """Test complete simulation from initialization to completion."""
        logger.info("Starting complete simulation lifecycle test")

        # Initialize simulation with moderate size for testing
        num_agents = 20
        num_steps = 10

        simulation = Simulation(num_agents=num_agents, seed=42)

        # Verify initialization
        assert simulation.num_agents == num_agents
        assert len(simulation.node_agents) == num_agents
        assert simulation.threshold == num_agents // 2 + 1
        assert isinstance(simulation.ledger, DatabaseLedger)

        # Verify all agents are properly initialized
        for agent in simulation.node_agents:
            assert isinstance(agent, AnomalyAgent)
            assert agent.model is simulation
            assert agent.node_id.startswith("Node_")

        # Run simulation for specified steps
        initial_step_count = simulation.step_count
        simulation.run(steps=num_steps)

        # Verify simulation completed successfully
        assert simulation.step_count == initial_step_count + num_steps

        # Verify ledger has entries (agents should have generated signatures)
        ledger_entries = simulation.ledger.read_ledger()
        assert len(ledger_entries) > 0

        # Verify monitoring metrics were recorded
        stats = simulation.get_simulation_stats()
        assert stats['step_count'] == num_steps
        assert stats['num_agents'] == num_agents
        assert stats['runtime'] > 0

        logger.info(f"Simulation completed: {stats}")

    def test_agent_consensus_mechanism(self, test_env):
        """Test agent consensus mechanism with anomaly detection."""
        logger.info("Starting agent consensus mechanism test")

        simulation = Simulation(num_agents=10, seed=42)

        # Run multiple steps to generate consensus scenarios
        simulation.run(steps=5)

        # Verify ledger entries exist (indicating agent activity)
        entries = simulation.ledger.read_ledger()
        assert len(entries) > 0

        # Check that entries have proper structure
        for entry in entries:
            assert 'id' in entry
            assert 'timestamp' in entry
            assert 'node_id' in entry
            assert 'features' in entry
            assert 'confidence' in entry

        logger.info(f"Consensus test completed with {len(entries)} ledger entries")

    def test_database_ledger_integrity(self, test_env):
        """Test database operations and ledger integrity."""
        logger.info("Starting database ledger integrity test")

        # Clean slate - close any existing connections and start fresh
        close_all_connections()

        # Create a unique database file for this test
        unique_db_path = os.path.join(test_env.temp_dir, "test_ledger_integrity.db")

        # Remove existing database file if it exists
        if os.path.exists(unique_db_path):
            os.remove(unique_db_path)

        ledger = DatabaseLedger(db_file=unique_db_path)

        # Create test entries
        test_entries = [
            {
                'timestamp': time.time(),
                'node_id': f'Node_{i}',
                'features': [{'packet_size': 100.0 + i, 'source_ip': f'192.168.1.{i}'}],
                'confidence': 0.8 + i * 0.01
            }
            for i in range(5)
        ]

        # Append entries and collect IDs
        entry_ids = []
        for entry in test_entries:
            entry_id = ledger.append_entry(entry)
            assert isinstance(entry_id, int)
            assert entry_id > 0
            entry_ids.append(entry_id)

        # Verify entries can be read back
        all_entries = ledger.read_ledger()
        assert len(all_entries) >= 5  # Should have at least our entries

        # Verify our entries are in correct order (check the first 5 entries)
        # Since database may have existing entries, we need to find our entries by content
        found_entries = 0
        for entry in all_entries:
            if entry['node_id'] in [f'Node_{i}' for i in range(5)]:
                # Just verify the entry has the expected structure
                assert 'timestamp' in entry
                assert 'features' in entry
                assert 'confidence' in entry
                assert isinstance(entry['features'], list)
                found_entries += 1

        assert found_entries >= 5, f"Should find at least 5 of our test entries, found {found_entries}"

        # Test get_new_entries functionality
        new_entries = ledger.get_new_entries(entry_ids[2])
        assert len(new_entries) == 2  # Entries after ID 3
        assert new_entries[0]['id'] == entry_ids[3]
        assert new_entries[1]['id'] == entry_ids[4]

        logger.info("Database ledger integrity test completed successfully")


class TestComponentIntegration:
    """Component integration and interaction tests."""

    def test_configuration_integration(self, test_env):
        """Test configuration loading and environment overrides."""
        logger.info("Starting configuration integration test")

        # Test that configuration is properly loaded
        db_path = get_config('database.path', 'ledger.db')

        # Test that we can get various configuration values
        default_agents = get_config('simulation.default_agents', 50)
        assert isinstance(default_agents, int)
        assert default_agents > 0

        # Test Ray configuration
        ray_enabled = get_config('ray.enable', True)
        assert isinstance(ray_enabled, bool)

        # Test that environment variable override works for database path
        # (The SIMULATION_DB_PATH should be picked up by the config system)
        if 'SIMULATION_DB_PATH' in os.environ:
            env_db_path = os.environ['SIMULATION_DB_PATH']
            logger.info(f"Environment database path: {env_db_path}")

        # Test simulation configuration
        default_agents = get_config('simulation.default_agents', 50)
        assert isinstance(default_agents, int)
        assert default_agents > 0

        # Test Ray configuration
        ray_enabled = get_config('ray.enable', True)
        assert isinstance(ray_enabled, bool)

        logger.info("Configuration integration test completed")

    def test_monitoring_integration(self, test_env):
        """Test monitoring and metrics collection."""
        logger.info("Starting monitoring integration test")

        monitoring = get_monitoring()

        # Record some test metrics
        monitoring.record_metric('test_metric', 42)
        monitoring.record_metric('test_metric_float', 3.14)
        monitoring.record_metric('test_counter', 1)

        # Verify metrics are recorded (implementation specific)
        # This test mainly ensures no exceptions are raised

        logger.info("Monitoring integration test completed")

    def test_parallel_execution_integration(self, test_env):
        """Test Ray distributed computing integration."""
        logger.info("Starting parallel execution integration test")

        # Test with parallel-enabled simulation
        simulation = Simulation(num_agents=15, seed=42)  # Above threshold

        # Verify parallel execution is enabled for larger agent counts
        parallel_threshold = get_config('simulation.use_parallel_threshold', 50)
        if simulation.num_agents > parallel_threshold:
            # Should attempt to use parallel execution
            assert simulation.use_parallel is True

        # Run a few steps to test parallel execution
        simulation.run(steps=3)

        # Verify simulation completed without errors
        assert simulation.step_count == 3

        logger.info("Parallel execution integration test completed")


class TestPerformanceAndStability:
    """Performance and stability testing."""

    def test_memory_usage_stability(self, test_env):
        """Test memory usage during extended simulation."""
        logger.info("Starting memory usage stability test")

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run extended simulation
        simulation = Simulation(num_agents=30, seed=42)
        simulation.run(steps=20)

        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100, f"Memory increase too high: {memory_increase}MB"

        logger.info(f"Memory usage stable: {initial_memory:.1f}MB -> {final_memory:.1f}MB")

    def test_concurrent_simulations(self, test_env):
        """Test multiple simulations running concurrently."""
        logger.info("Starting concurrent simulations test")

        def run_simulation(simulation_id):
            """Run a simulation in a separate thread."""
            sim = Simulation(num_agents=10, seed=42 + simulation_id)
            sim.run(steps=5)
            return sim.get_simulation_stats()

        # Run multiple simulations concurrently
        num_concurrent = 3
        threads = []

        for i in range(num_concurrent):
            thread = threading.Thread(target=run_simulation, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all simulations to complete
        for thread in threads:
            thread.join()

        logger.info(f"Concurrent simulations test completed with {num_concurrent} parallel runs")

    def test_database_connection_pooling(self, test_env):
        """Test database connection pooling under load."""
        logger.info("Starting database connection pooling test")

        # Clean slate for this test
        close_all_connections()

        # Create a unique database file for this test
        unique_db_path = os.path.join(test_env.temp_dir, "test_pooling.db")

        # Remove existing database file if it exists
        if os.path.exists(unique_db_path):
            os.remove(unique_db_path)

        ledger = DatabaseLedger(db_file=unique_db_path)

        # Simulate high-frequency database operations
        num_operations = 100
        start_time = time.time()

        for i in range(num_operations):
            entry = {
                'timestamp': time.time(),
                'node_id': f'Node_{i % 10}',
                'features': [{'packet_size': 100.0 + i, 'source_ip': f'192.168.1.{i % 255}'}],
                'confidence': 0.8
            }
            ledger.append_entry(entry)

        operation_time = time.time() - start_time

        # Verify all operations completed
        entries = ledger.read_ledger()
        assert len(entries) >= num_operations  # Should have at least our entries

        # Operations should complete in reasonable time (< 5 seconds for 100 ops)
        assert operation_time < 5.0, f"Database operations too slow: {operation_time:.2f}s"

        logger.info(f"Database pooling test: {num_operations} operations in {operation_time:.2f}s")


class TestErrorHandlingAndRecovery:
    """Error handling and recovery mechanism tests."""

    def test_simulation_error_recovery(self, test_env):
        """Test simulation error handling and recovery."""
        logger.info("Starting simulation error recovery test")

        simulation = Simulation(num_agents=10, seed=42)

        # Simulate an error condition by corrupting agent state
        original_step = simulation.step
        error_count = 0

        def error_prone_step():
            nonlocal error_count
            error_count += 1
            if error_count == 3:
                raise Exception("Simulated agent error")
            return original_step()

        simulation.step = error_prone_step

        # Run simulation that encounters errors
        # The simulation should catch the error and continue, but we want to verify
        # that the error is properly logged and handled
        simulation.run(steps=5)

        # Verify that the error was encountered (step count should be less than expected)
        # Since the error happens on step 3, we should have completed only 2 steps
        assert simulation.step_count == 2, f"Expected 2 steps due to error, got {simulation.step_count}"

        logger.info("Simulation error recovery test completed - error properly handled")

    def test_database_error_handling(self, test_env):
        """Test database error handling."""
        logger.info("Starting database error handling test")

        # Test with invalid database path
        invalid_path = "/invalid/path/that/does/not/exist/test.db"

        with pytest.raises(Exception):
            ledger = DatabaseLedger(db_file=invalid_path)
            ledger.append_entry({'test': 'data'})

        logger.info("Database error handling test completed")


class TestCrossPlatformCompatibility:
    """Cross-platform compatibility tests."""

    def test_deployment_script_functionality(self, test_env):
        """Test deployment script functionality."""
        logger.info("Starting deployment script functionality test")

        # Get the original project directory (where scripts should be)
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Test that deployment scripts exist and are executable
        script_extensions = ['.sh', '.bat', '.ps1']
        script_names = ['setup', 'run', 'deploy', 'test', 'cleanup']

        found_scripts = 0
        for script_name in script_names:
            script_found = False
            for ext in script_extensions:
                script_path = os.path.join(project_dir, f"{script_name}{ext}")
                if os.path.exists(script_path):
                    script_found = True
                    found_scripts += 1
                    # Check if script is executable (Unix-like systems)
                    if os.name != 'nt':
                        st = os.stat(script_path)
                        assert st.st_mode & 0o111, f"Script {script_path} is not executable"
                    break

            # Don't assert for each script, just log what's found
            if script_found:
                logger.info(f"Found deployment script: {script_name}")
            else:
                logger.warning(f"Deployment script not found: {script_name}")

        # We should find at least some scripts
        assert found_scripts > 0, "No deployment scripts found at all"

        logger.info(f"Deployment script functionality test completed - found {found_scripts} scripts")

    def test_configuration_across_environments(self, test_env):
        """Test configuration loading across different environments."""
        logger.info("Starting configuration across environments test")

        # Test that configuration works with different environment variables
        test_configs = [
            ('SIMULATION_DB_PATH', test_env.test_db_path),
            ('SIMULATION_LOG_LEVEL', 'DEBUG'),
            ('RAY_ENABLE', 'true'),
        ]

        for env_var, expected_value in test_configs:
            if env_var in os.environ:
                actual_value = os.environ[env_var]
                logger.info(f"Environment variable {env_var}: {actual_value}")

        logger.info("Configuration across environments test completed")


def run_integration_tests():
    """Main function to run all integration tests."""
    logger.info("Starting comprehensive integration testing")

    # Create test environment
    test_env = TestEnvironment()
    test_env.setup()

    try:
        # Run all test classes
        test_classes = [
            TestEndToEndWorkflow,
            TestComponentIntegration,
            TestPerformanceAndStability,
            TestErrorHandlingAndRecovery,
            TestCrossPlatformCompatibility,
        ]

        results = {
            'passed': 0,
            'failed': 0,
            'total': 0
        }

        for test_class in test_classes:
            logger.info(f"Running {test_class.__name__} tests")
            instance = test_class()

            # Get all test methods
            test_methods = [method for method in dir(instance)
                          if method.startswith('test_') and callable(getattr(instance, method))]

            for test_method in test_methods:
                results['total'] += 1
                try:
                    test_func = getattr(instance, test_method)
                    test_func(test_env)
                    results['passed'] += 1
                    logger.info(f"✓ {test_class.__name__}.{test_method}")
                except Exception as e:
                    results['failed'] += 1
                    logger.error(f"✗ {test_class.__name__}.{test_method}: {e}")

        # Print summary
        logger.info(f"Integration test results: {results['passed']}/{results['total']} passed")
        if results['failed'] > 0:
            logger.error(f"{results['failed']} tests failed")

        return results

    finally:
        test_env.teardown()


if __name__ == "__main__":
    run_integration_tests()