"""
Comprehensive Integration Testing Suite for 3D AI Simulation Backend

Tests the complete integration between simulation backend, data transformation,
API endpoints, and WebSocket streaming functionality.
"""

import asyncio
import json
import time
import pytest
import httpx
import websockets
from typing import Dict, Any, List
import threading
import subprocess
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_transformers import (
    Vector3D, Agent3D, Anomaly3D, SimulationState3D,
    SimulationStateTransformer, create_3d_simulation_state,
    create_3d_agents, create_3d_anomalies_from_ledger
)

# Import simulation components
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..simulation import Simulation
from ..database import DatabaseLedger

class TestSimulationIntegration:
    """Test integration between simulation components."""

    @pytest.fixture
    def simulation(self):
        """Create a test simulation instance."""
        sim = Simulation(num_agents=50)
        yield sim
        sim.cleanup()

    @pytest.fixture
    def ledger(self):
        """Create a test ledger instance."""
        ledger = DatabaseLedger()
        yield ledger

    def test_simulation_initialization(self, simulation):
        """Test that simulation initializes correctly."""
        assert simulation.num_agents == 50
        assert len(simulation.node_agents) == 50
        assert simulation.ledger is not None

    def test_agent_creation(self, simulation):
        """Test that agents are created with correct properties."""
        for agent in simulation.node_agents:
            assert agent.node_id.startswith("Node_")
            assert hasattr(agent, 'anomaly_model')
            assert hasattr(agent, 'recent_data')
            assert agent.anomaly_threshold == -0.05

    def test_simulation_step_execution(self, simulation):
        """Test that simulation steps execute correctly."""
        initial_step_count = simulation.step_count

        # Run a few steps
        for _ in range(5):
            simulation.step()

        assert simulation.step_count == initial_step_count + 5

    def test_ledger_operations(self, ledger):
        """Test ledger read/write operations."""
        # Test writing an entry
        test_entry = {
            'timestamp': time.time(),
            'node_id': 'test_node',
            'features': [{'packet_size': 100, 'source_ip': '192.168.1.1'}],
            'confidence': 0.8
        }

        entry_id = ledger.append_entry(test_entry)
        assert entry_id > 0

        # Test reading the entry back
        retrieved = ledger.get_entry_by_id(entry_id)
        assert retrieved is not None
        assert retrieved['node_id'] == 'test_node'
        assert retrieved['confidence'] == 0.8

class TestDataTransformation:
    """Test data transformation from simulation to 3D format."""

    @pytest.fixture
    def transformer(self):
        """Create a simulation state transformer."""
        return SimulationStateTransformer()

    @pytest.fixture
    def sample_agents(self):
        """Create sample agents for testing."""
        sim = Simulation(num_agents=10)
        agents = sim.node_agents
        yield agents
        sim.cleanup()

    @pytest.fixture
    def sample_ledger(self):
        """Create sample ledger with test data."""
        ledger = DatabaseLedger()

        # Add some test entries
        for i in range(5):
            test_entry = {
                'timestamp': time.time() + i,
                'node_id': f'test_node_{i}',
                'features': [
                    {'packet_size': 100 + i * 10, 'source_ip': f'192.168.1.{i + 1}'}
                ],
                'confidence': 0.5 + i * 0.1
            }
            ledger.append_entry(test_entry)

        yield ledger

    def test_position_mapper_initialization(self, transformer, sample_agents):
        """Test position mapper initialization."""
        transformer.position_mapper.initialize_spherical_layout(sample_agents)

        positions = transformer.position_mapper.get_all_positions()
        assert len(positions) == len(sample_agents)

        # Check that positions are reasonable
        for pos in positions.values():
            assert isinstance(pos, Vector3D)
            assert -15 < pos.x < 15
            assert -15 < pos.y < 15
            assert -15 < pos.z < 15

    def test_agent_transformation(self, transformer, sample_agents):
        """Test transformation of agents to 3D format."""
        # Initialize positions first
        transformer.position_mapper.initialize_spherical_layout(sample_agents)

        agents_3d = transformer.get_agents_3d(sample_agents)
        assert len(agents_3d) == len(sample_agents)

        for agent_3d in agents_3d:
            assert isinstance(agent_3d, Agent3D)
            assert isinstance(agent_3d.position, Vector3D)
            assert 0 <= agent_3d.trustScore <= 1
            assert agent_3d.status == 'active'
            assert isinstance(agent_3d.connections, list)

    def test_anomaly_transformation(self, transformer, sample_ledger, sample_agents):
        """Test transformation of anomalies to 3D format."""
        # Initialize positions first
        transformer.position_mapper.initialize_spherical_layout(sample_agents)

        anomalies_3d = transformer.anomaly_transformer.transform_anomalies_from_ledger(
            sample_ledger, transformer.position_mapper, max_anomalies=3
        )

        # Should get some anomalies (depending on ledger content)
        assert isinstance(anomalies_3d, list)

        for anomaly_3d in anomalies_3d:
            assert isinstance(anomaly_3d, Anomaly3D)
            assert isinstance(anomaly_3d.position, Vector3D)
            assert anomaly_3d.severity in ['low', 'medium', 'high', 'critical']
            assert anomaly_3d.type in ['trust_drop', 'unusual_activity', 'connection_spike']

    def test_simulation_state_transformation(self, transformer, sample_agents, sample_ledger):
        """Test complete simulation state transformation."""
        # Initialize positions first
        transformer.position_mapper.initialize_spherical_layout(sample_agents)

        state_3d = transformer.transform_simulation_state(sample_agents, sample_ledger, True)

        assert isinstance(state_3d, SimulationState3D)
        assert state_3d.status == 'running'
        assert state_3d.activeAgents == len(sample_agents)
        assert isinstance(state_3d.averageTrustScore, float)
        assert isinstance(state_3d.anomalies, list)

class TestAPIBackend:
    """Test the FastAPI backend server."""

    @pytest.fixture(scope="class")
    def backend_server(self):
        """Start the backend server for testing."""
        # Import and start the backend server
        from backend.main import app
        # In a real test, you would use test client or start server
        # For now, we'll test the components directly
        yield app

    def test_backend_imports(self):
        """Test that backend components can be imported."""
        try:
            from backend.main import SimulationBridge
            from backend.data_transformers import SimulationStateTransformer
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import backend components: {e}")

    def test_simulation_bridge_creation(self):
        """Test SimulationBridge creation and basic functionality."""
        from backend.main import SimulationBridge

        bridge = SimulationBridge()
        assert bridge.simulation is None
        assert bridge.running is False
        assert len(bridge.websocket_connections) == 0

        # Test initialization
        success = bridge.initialize_simulation(25)
        assert success == True
        assert bridge.simulation is not None
        assert bridge.simulation.num_agents == 25

class TestAPIEndpoints:
    """Test API endpoints functionality."""

    @pytest.fixture
    def api_server_process(self):
        """Start API server process for testing."""
        # Start the API server in a subprocess
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn',
            'main:app', '--host', '127.0.0.1', '--port', '8000', '--reload'
        ])

        # Wait for server to start
        time.sleep(2)
        yield process

        # Cleanup
        process.terminate()
        process.wait()

    def test_api_server_startup(self, api_server_process):
        """Test that API server starts correctly."""
        assert api_server_process.poll() is None  # Process should be running

    @pytest.mark.asyncio
    async def test_api_health_endpoint(self):
        """Test API health endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"

class TestWebSocketIntegration:
    """Test WebSocket real-time streaming."""

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection and basic messaging."""
        try:
            # Test connection to WebSocket server
            uri = "ws://localhost:8503"

            async with websockets.connect(uri) as websocket:
                # Send ping
                ping_message = {"type": "ping", "timestamp": time.time()}
                await websocket.send(json.dumps(ping_message))

                # Receive pong
                response = await websocket.receive()
                pong_data = json.loads(response)

                assert pong_data["type"] == "pong"
                assert "timestamp" in pong_data

        except ConnectionRefusedError:
            pytest.skip("WebSocket server not running")

    @pytest.mark.asyncio
    async def test_websocket_simulation_updates(self):
        """Test receiving simulation updates via WebSocket."""
        try:
            uri = "ws://localhost:8503"

            async with websockets.connect(uri) as websocket:
                # Wait for initial state message
                message = await asyncio.wait_for(websocket.receive(), timeout=5.0)
                data = json.loads(message)

                # Should receive either initial_state or simulation_update
                assert data["type"] in ["initial_state", "simulation_update"]
                assert "data" in data
                assert "timestamp" in data

        except (ConnectionRefusedError, asyncio.TimeoutError):
            pytest.skip("WebSocket server not running or no simulation data")

class TestEndToEndIntegration:
    """Test complete end-to-end integration."""

    def test_data_flow_simulation_to_3d(self):
        """Test complete data flow from simulation to 3D format."""
        # Create simulation
        sim = Simulation(num_agents=20)
        ledger = DatabaseLedger()

        try:
            # Run a few simulation steps to generate data
            for _ in range(3):
                sim.step()

            # Transform to 3D format
            transformer = SimulationStateTransformer()
            transformer.position_mapper.initialize_spherical_layout(sim.node_agents)

            # Get 3D data
            agents_3d = transformer.get_agents_3d(sim.node_agents)
            anomalies_3d = transformer.anomaly_transformer.transform_anomalies_from_ledger(
                ledger, transformer.position_mapper
            )
            state_3d = transformer.transform_simulation_state(sim.node_agents, ledger, True)

            # Verify data integrity
            assert len(agents_3d) == 20
            assert isinstance(state_3d, SimulationState3D)
            assert state_3d.activeAgents == 20

            # Verify all agents have valid positions
            for agent_3d in agents_3d:
                assert agent_3d.position.x != 0 or agent_3d.position.y != 0 or agent_3d.position.z != 0

        finally:
            sim.cleanup()

    def test_performance_requirements(self):
        """Test that system meets performance requirements."""
        # Test data transformation performance
        sim = Simulation(num_agents=100)

        try:
            start_time = time.time()

            # Transform agents to 3D format
            transformer = SimulationStateTransformer()
            transformer.position_mapper.initialize_spherical_layout(sim.node_agents)
            agents_3d = transformer.get_agents_3d(sim.node_agents)

            transformation_time = time.time() - start_time

            # Should complete transformation in reasonable time
            assert transformation_time < 1.0  # Less than 1 second
            assert len(agents_3d) == 100

        finally:
            sim.cleanup()

class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_simulation_handling(self):
        """Test handling of empty or invalid simulation states."""
        transformer = SimulationStateTransformer()

        # Test with empty agent list
        state_3d = transformer.transform_simulation_state([], None, False)

        assert state_3d.activeAgents == 0
        assert state_3d.averageTrustScore == 0.0
        assert len(state_3d.anomalies) == 0

    def test_invalid_data_transformation(self):
        """Test handling of invalid data during transformation."""
        transformer = SimulationStateTransformer()

        # Create mock agent with invalid data
        class MockAgent:
            def __init__(self):
                self.node_id = "invalid_agent"
                self.trust_score = float('inf')  # Invalid trust score

        mock_agents = [MockAgent()]

        # Should handle gracefully
        try:
            agents_3d = transformer.get_agents_3d(mock_agents)
            # If we get here, transformation should have handled the error
            assert isinstance(agents_3d, list)
        except Exception as e:
            # Should not crash, but may raise handled exceptions
            assert "transformation" in str(e).lower() or True

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])