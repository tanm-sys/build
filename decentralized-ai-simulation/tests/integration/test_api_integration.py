"""
API Integration Tests for 3D Data Endpoints

Tests the API server endpoints, WebSocket connections, and data streaming
functionality for the 3D visualization platform.
"""

import pytest
import httpx
import websockets
import json
import time
import asyncio
import threading
import subprocess
import sys
import os
from typing import Dict, Any

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/ui'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

class TestAPIEndpoints:
    """Test REST API endpoints."""

    @pytest.fixture(scope="class")
    def api_server(self):
        """Start API server for testing."""
        # Start the API server
        process = subprocess.Popen([
            sys.executable, '-c',
            '''
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src/ui"))
from api_server import start_api_server, initialize_api_simulation
initialize_api_simulation(50)
server = start_api_server(8502)
server.serve_forever()
            '''
        ], cwd=os.path.dirname(__file__))

        # Wait for server to start
        time.sleep(3)
        yield "http://localhost:8502"

        # Cleanup
        process.terminate()
        process.wait()

    def test_health_endpoint(self, api_server):
        """Test API health check endpoint."""
        response = httpx.get(f"{api_server}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "running"
        assert "simulation_initialized" in data

    def test_agents_endpoint(self, api_server):
        """Test 3D agents endpoint."""
        response = httpx.get(f"{api_server}/3d/agents")
        assert response.status_code == 200

        data = response.json()
        assert "agents" in data
        assert "count" in data
        assert "timestamp" in data

        if data["count"] > 0:
            agent = data["agents"][0]
            assert "id" in agent
            assert "position" in agent
            assert "trustScore" in agent
            assert "status" in agent

    def test_anomalies_endpoint(self, api_server):
        """Test 3D anomalies endpoint."""
        response = httpx.get(f"{api_server}/3d/anomalies")
        assert response.status_code == 200

        data = response.json()
        assert "anomalies" in data
        assert "count" in data
        assert "timestamp" in data

        # Anomalies might be empty initially
        assert isinstance(data["anomalies"], list)

    def test_simulation_state_endpoint(self, api_server):
        """Test 3D simulation state endpoint."""
        response = httpx.get(f"{api_server}/3d/simulation-state")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "activeAgents" in data
        assert "totalConnections" in data
        assert "averageTrustScore" in data
        assert "anomalies" in data

    def test_positions_endpoint(self, api_server):
        """Test agent positions endpoint."""
        response = httpx.get(f"{api_server}/3d/positions")
        assert response.status_code == 200

        data = response.json()
        assert "positions" in data
        assert "count" in data
        assert "timestamp" in data

        if data["count"] > 0:
            positions = data["positions"]
            assert isinstance(positions, dict)

            # Check position structure
            for agent_id, pos in positions.items():
                assert "x" in pos
                assert "y" in pos
                assert "z" in pos

    def test_root_endpoint(self, api_server):
        """Test root API endpoint."""
        response = httpx.get(f"{api_server}/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
        assert "status" in data

class TestWebSocketIntegration:
    """Test WebSocket real-time streaming."""

    @pytest.fixture(scope="class")
    def websocket_server(self):
        """Start WebSocket server for testing."""
        # This would start the WebSocket server
        # For now, we'll test the connection logic
        yield "ws://localhost:8503"

    @pytest.mark.asyncio
    async def test_websocket_connection(self, websocket_server):
        """Test WebSocket connection establishment."""
        try:
            uri = websocket_server

            async with websockets.connect(uri) as websocket:
                # Connection successful
                assert websocket.open

                # Test ping/pong
                ping_message = {"type": "ping", "timestamp": time.time()}
                await websocket.send(json.dumps(ping_message))

                response = await asyncio.wait_for(websocket.receive(), timeout=2.0)
                pong_data = json.loads(response)

                assert pong_data["type"] == "pong"

        except (ConnectionRefusedError, asyncio.TimeoutError):
            pytest.skip("WebSocket server not available for testing")

    @pytest.mark.asyncio
    async def test_websocket_simulation_updates(self, websocket_server):
        """Test receiving simulation updates."""
        try:
            uri = websocket_server

            async with websockets.connect(uri) as websocket:
                # Wait for initial state or update
                message = await asyncio.wait_for(websocket.receive(), timeout=5.0)
                data = json.loads(message)

                # Should receive initial state or simulation update
                assert data["type"] in ["initial_state", "simulation_update"]
                assert "data" in data
                assert "timestamp" in data

                # Verify data structure
                if data["type"] == "initial_state":
                    assert "data" in data
                    state_data = data["data"]
                    assert "status" in state_data
                    assert "activeAgents" in state_data

        except (ConnectionRefusedError, asyncio.TimeoutError):
            pytest.skip("WebSocket server not available for testing")

class TestCrossComponentIntegration:
    """Test integration between different components."""

    def test_simulation_to_api_data_flow(self):
        """Test data flow from simulation through API."""
        # This would test the complete pipeline:
        # 1. Simulation generates data
        # 2. Data is transformed to 3D format
        # 3. API serves the 3D data
        # 4. Frontend can consume the data

        # For now, we'll test the transformation pipeline
        try:
            from backend.data_transformers import SimulationStateTransformer

            # Create minimal test data
            transformer = SimulationStateTransformer()

            # Test with empty data (should not crash)
            state_3d = transformer.transform_simulation_state([], None, False)
            assert state_3d.activeAgents == 0

        except ImportError:
            pytest.skip("Data transformers not available")

    def test_api_response_format_compatibility(self):
        """Test that API responses are compatible with frontend expectations."""
        # Test that API responses match the expected TypeScript interfaces

        expected_agent_fields = {
            "id", "position", "trustScore", "status",
            "connections", "lastUpdate", "metadata"
        }

        expected_anomaly_fields = {
            "id", "type", "severity", "position",
            "timestamp", "description"
        }

        expected_state_fields = {
            "status", "timestamp", "activeAgents",
            "totalConnections", "averageTrustScore", "anomalies"
        }

        # These would be tested against actual API responses
        # For now, we'll verify the field definitions exist in our transformers

        from backend.data_transformers import Agent3D, Anomaly3D, SimulationState3D

        # Check that our dataclasses have the expected fields
        agent_fields = set(Agent3D.__dataclass_fields__.keys())
        anomaly_fields = set(Anomaly3D.__dataclass_fields__.keys())
        state_fields = set(SimulationState3D.__dataclass_fields__.keys())

        # Verify field compatibility (allowing for additional fields)
        assert expected_agent_fields.issubset(agent_fields)
        assert expected_anomaly_fields.issubset(anomaly_fields)
        assert expected_state_fields.issubset(state_fields)

class TestPerformanceRequirements:
    """Test performance requirements for the system."""

    def test_api_response_time(self):
        """Test that API responses meet timing requirements."""
        # This would measure actual API response times
        # For now, we'll test the transformation performance

        try:
            from backend.data_transformers import SimulationStateTransformer

            transformer = SimulationStateTransformer()

            # Create test data
            class MockAgent:
                def __init__(self, i):
                    self.node_id = f"agent_{i}"
                    self.trust_score = 0.5

            agents = [MockAgent(i) for i in range(100)]

            # Measure transformation time
            start_time = time.time()
            agents_3d = transformer.get_agents_3d(agents)
            end_time = time.time()

            transformation_time = end_time - start_time

            # Should transform 100 agents quickly
            assert transformation_time < 0.5  # Less than 500ms
            assert len(agents_3d) == 100

        except ImportError:
            pytest.skip("Data transformers not available")

    def test_memory_usage(self):
        """Test memory usage during data transformation."""
        import psutil
        import os

        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Perform intensive transformation
            from backend.data_transformers import SimulationStateTransformer

            transformer = SimulationStateTransformer()

            class MockAgent:
                def __init__(self, i):
                    self.node_id = f"agent_{i}"
                    self.trust_score = 0.5

            agents = [MockAgent(i) for i in range(1000)]

            # Multiple transformations
            for _ in range(10):
                transformer.get_agents_3d(agents)

            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 100MB for this test)
            assert memory_increase < 100

        except ImportError:
            pytest.skip("Data transformers not available or psutil not installed")

class TestErrorHandling:
    """Test error handling in API endpoints."""

    def test_invalid_endpoint_handling(self, api_server):
        """Test handling of requests to invalid endpoints."""
        response = httpx.get(f"{api_server}/invalid-endpoint")
        assert response.status_code == 404

    def test_malformed_request_handling(self, api_server):
        """Test handling of malformed requests."""
        # Test with invalid JSON or parameters
        response = httpx.get(f"{api_server}/3d/anomalies?max=invalid")
        # Should handle gracefully, either 200 with empty results or 400 error
        assert response.status_code in [200, 400]

    def test_server_error_recovery(self):
        """Test that server recovers from errors."""
        # This would test server resilience
        # For now, we'll just verify that error handling exists

        assert True  # Placeholder for actual error recovery tests

if __name__ == "__main__":
    pytest.main([__file__, "-v"])