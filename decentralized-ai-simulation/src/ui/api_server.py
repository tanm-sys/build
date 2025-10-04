"""
Simple HTTP API Server for 3D Data Integration with Streamlit App

This module provides REST API endpoints that serve 3D visualization data
from the simulation to the frontend, running alongside the Streamlit UI.
"""

import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Set
from dataclasses import asdict
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import logging
import websockets
from websockets import WebSocketServerProtocol

# Import simulation components
from src.core.simulation import Simulation
from src.core.database import DatabaseLedger

# Import 3D data transformers
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

try:
    from backend.data_transformers import (
        SimulationStateTransformer, create_3d_simulation_state,
        create_3d_agents, create_3d_anomalies_from_ledger,
        Agent3D, Anomaly3D, SimulationState3D
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Could not import 3D transformers: {e}")
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class SimulationStateManager:
    """Manages simulation state for API endpoints."""

    def __init__(self):
        self.simulation: Optional[Simulation] = None
        self.ledger: Optional[DatabaseLedger] = None
        self.state_transformer = SimulationStateTransformer() if TRANSFORMERS_AVAILABLE else None
        self.last_update: float = 0
        self.update_interval: float = 0.1

        # WebSocket connections for real-time streaming
        self.websocket_connections: Set[WebSocketServerProtocol] = set()
        self.websocket_update_interval: float = 0.05  # 20 Hz for smooth updates

    def initialize_simulation(self, num_agents: int = 100) -> bool:
        """Initialize simulation for API serving."""
        try:
            self.ledger = DatabaseLedger()
            self.simulation = Simulation(num_agents=num_agents)

            if self.simulation.node_agents and self.state_transformer:
                self.state_transformer.position_mapper.initialize_spherical_layout(
                    self.simulation.node_agents
                )

            self.last_update = time.time()
            logger.info(f"API simulation initialized with {num_agents} agents")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize API simulation: {e}")
            return False

    def update_simulation_state(self) -> None:
        """Update simulation state for real-time API data."""
        if not self.simulation or not self.ledger:
            return

        try:
            # Run simulation step if needed
            if self.simulation:
                self.simulation.step()

            # Update 3D transformation data
            if self.state_transformer:
                self.state_transformer.position_mapper.update_positions_from_simulation(
                    self.simulation.node_agents
                )
                self.state_transformer.position_mapper.calculate_connections(
                    self.simulation.node_agents
                )

            self.last_update = time.time()

        except Exception as e:
            logger.error(f"Error updating simulation state: {e}")

    def get_3d_agents(self) -> List[Dict[str, Any]]:
        """Get agents in 3D format."""
        if not self.simulation or not self.state_transformer:
            return []

        agents_3d = self.state_transformer.get_agents_3d(self.simulation.node_agents)
        return [asdict(agent) for agent in agents_3d]

    def get_3d_anomalies(self, max_anomalies: int = 10) -> List[Dict[str, Any]]:
        """Get anomalies in 3D format."""
        if not self.ledger or not self.simulation or not self.state_transformer:
            return []

        anomalies_3d = create_3d_anomalies_from_ledger(
            self.ledger, self.simulation.node_agents, max_anomalies
        )
        return [asdict(anomaly) for anomaly in anomalies_3d]

    def get_3d_simulation_state(self) -> Dict[str, Any]:
        """Get complete 3D simulation state."""
        if not self.simulation or not self.ledger or not self.state_transformer:
            return {
                "status": "not_initialized",
                "timestamp": time.time(),
                "activeAgents": 0,
                "totalConnections": 0,
                "averageTrustScore": 0.0,
                "anomalies": []
            }

        state_3d = self.state_transformer.transform_simulation_state(
            self.simulation.node_agents, self.ledger, True
        )
        return asdict(state_3d)

    def get_api_status(self) -> Dict[str, Any]:
        """Get API server status."""
        return {
            "status": "running",
            "simulation_initialized": self.simulation is not None,
            "ledger_initialized": self.ledger is not None,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "websocket_connections": len(self.websocket_connections),
            "last_update": self.last_update,
            "timestamp": time.time()
        }

    def add_websocket_connection(self, websocket: WebSocketServerProtocol) -> None:
        """Add WebSocket connection for real-time updates."""
        self.websocket_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.websocket_connections)}")

    def remove_websocket_connection(self, websocket: WebSocketServerProtocol) -> None:
        """Remove WebSocket connection."""
        self.websocket_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.websocket_connections)}")

    async def broadcast_simulation_update(self) -> None:
        """Broadcast simulation state to all connected WebSocket clients."""
        if not self.websocket_connections or not self.state_transformer:
            return

        try:
            # Get current 3D simulation state
            state_3d = self.state_transformer.transform_simulation_state(
                self.simulation.node_agents if self.simulation else [],
                self.ledger,
                self.simulation is not None
            )

            # Prepare update message
            update_message = {
                "type": "simulation_update",
                "data": asdict(state_3d),
                "timestamp": time.time()
            }

            # Send to all connected clients
            disconnected_clients = set()
            for websocket in self.websocket_connections:
                try:
                    await websocket.send(json.dumps(update_message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(websocket)
                except Exception as e:
                    logger.error(f"Error sending WebSocket update: {e}")
                    disconnected_clients.add(websocket)

            # Remove disconnected clients
            for websocket in disconnected_clients:
                self.remove_websocket_connection(websocket)

        except Exception as e:
            logger.error(f"Error broadcasting simulation update: {e}")

    def start_websocket_server(self, port: int = 8503) -> None:
        """Start WebSocket server for real-time updates."""
        async def websocket_handler(websocket: WebSocketServerProtocol, path: str):
            """Handle WebSocket connections."""
            # Add connection to manager
            self.add_websocket_connection(websocket)

            try:
                # Send initial state
                if self.state_transformer and self.simulation and self.ledger:
                    initial_state = self.state_transformer.transform_simulation_state(
                        self.simulation.node_agents, self.ledger, True
                    )
                    await websocket.send(json.dumps({
                        "type": "initial_state",
                        "data": asdict(initial_state),
                        "timestamp": time.time()
                    }))

                # Keep connection alive and handle messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("type") == "ping":
                            await websocket.send(json.dumps({
                                "type": "pong",
                                "timestamp": time.time()
                            }))
                    except json.JSONDecodeError:
                        logger.warning("Received invalid JSON from WebSocket client")
                    except Exception as e:
                        logger.error(f"Error handling WebSocket message: {e}")
                        break

            except websockets.exceptions.ConnectionClosed:
                pass
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                self.remove_websocket_connection(websocket)

        async def start_server():
            """Start the WebSocket server."""
            server = await websockets.serve(websocket_handler, "localhost", port)
            logger.info(f"WebSocket server started on port {port}")
            await server.wait_closed()

        # Start WebSocket server in background thread
        def run_websocket_server():
            asyncio.run(start_server())

        ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
        ws_thread.start()
        logger.info("WebSocket server thread started")

    def start_realtime_broadcast(self) -> None:
        """Start background thread for real-time broadcasting."""
        def broadcast_loop():
            """Main broadcast loop."""
            while True:
                try:
                    if self.websocket_connections:
                        asyncio.run(self.broadcast_simulation_update())
                    time.sleep(self.websocket_update_interval)
                except Exception as e:
                    logger.error(f"Error in broadcast loop: {e}")
                    time.sleep(1.0)

        broadcast_thread = threading.Thread(target=broadcast_loop, daemon=True)
        broadcast_thread.start()
        logger.info("Real-time broadcast loop started")

# Global simulation state manager
simulation_manager = SimulationStateManager()

class APIRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for 3D API endpoints."""

    def _set_cors_headers(self) -> None:
        """Set CORS headers for frontend integration."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests for 3D API endpoints."""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            query_params = urllib.parse.parse_qs(parsed_path.query)

            # Route requests to appropriate handlers
            if path == '/3d/agents':
                self._handle_get_agents()
            elif path == '/3d/anomalies':
                self._handle_get_anomalies(query_params)
            elif path == '/3d/simulation-state':
                self._handle_get_simulation_state()
            elif path == '/3d/positions':
                self._handle_get_positions()
            elif path == '/health':
                self._handle_health_check()
            elif path == '/':
                self._handle_root()
            else:
                self._handle_not_found()

        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self._send_error(500, f"Internal server error: {e}")

    def _handle_get_agents(self) -> None:
        """Handle request for 3D agents data."""
        try:
            agents_data = simulation_manager.get_3d_agents()
            self._send_json_response({
                "agents": agents_data,
                "count": len(agents_data),
                "timestamp": time.time()
            })
        except Exception as e:
            self._send_error(500, f"Error retrieving agents: {e}")

    def _handle_get_anomalies(self, query_params: Dict[str, List[str]]) -> None:
        """Handle request for 3D anomalies data."""
        try:
            max_anomalies = int(query_params.get('max', ['10'])[0])
            anomalies_data = simulation_manager.get_3d_anomalies(max_anomalies)
            self._send_json_response({
                "anomalies": anomalies_data,
                "count": len(anomalies_data),
                "timestamp": time.time()
            })
        except Exception as e:
            self._send_error(500, f"Error retrieving anomalies: {e}")

    def _handle_get_simulation_state(self) -> None:
        """Handle request for complete 3D simulation state."""
        try:
            state_data = simulation_manager.get_3d_simulation_state()
            self._send_json_response(state_data)
        except Exception as e:
            self._send_error(500, f"Error retrieving simulation state: {e}")

    def _handle_get_positions(self) -> None:
        """Handle request for agent positions."""
        try:
            if simulation_manager.state_transformer:
                positions = simulation_manager.state_transformer.position_mapper.get_all_positions()
                self._send_json_response({
                    "positions": {k: asdict(v) for k, v in positions.items()},
                    "count": len(positions),
                    "timestamp": time.time()
                })
            else:
                self._send_error(503, "Position mapper not available")
        except Exception as e:
            self._send_error(500, f"Error retrieving positions: {e}")

    def _handle_health_check(self) -> None:
        """Handle health check requests."""
        try:
            status = simulation_manager.get_api_status()
            status_code = 200 if status["simulation_initialized"] else 503
            self._send_json_response(status, status_code)
        except Exception as e:
            self._send_error(500, f"Health check failed: {e}")

    def _handle_root(self) -> None:
        """Handle root path requests."""
        self._send_json_response({
            "name": "3D AI Simulation API",
            "version": "1.0.0",
            "endpoints": [
                "/3d/agents",
                "/3d/anomalies",
                "/3d/simulation-state",
                "/3d/positions",
                "/health"
            ],
            "status": simulation_manager.get_api_status()
        })

    def _handle_not_found(self) -> None:
        """Handle 404 responses."""
        self._send_error(404, "Endpoint not found")

    def _send_json_response(self, data: Any, status_code: int = 200) -> None:
        """Send JSON response."""
        self.send_response(status_code)
        self._set_cors_headers()
        self.end_headers()

        json_data = json.dumps(data, indent=2, default=str)
        self.wfile.write(json_data.encode('utf-8'))

    def _send_error(self, status_code: int, message: str) -> None:
        """Send error response."""
        self.send_response(status_code)
        self._set_cors_headers()
        self.end_headers()

        error_data = {
            "error": message,
            "status_code": status_code,
            "timestamp": time.time()
        }
        self.wfile.write(json.dumps(error_data, indent=2).encode('utf-8'))

    def log_message(self, format: str, *args: Any) -> None:
        """Override to use our logger."""
        logger.info(f"API Request: {format % args}")

def start_api_server(port: int = 8502) -> HTTPServer:
    """
    Start the API server for 3D data endpoints.

    Args:
        port: Port number for the API server

    Returns:
        HTTPServer instance
    """
    try:
        server = HTTPServer(('localhost', port), APIRequestHandler)
        logger.info(f"3D API server started on port {port}")

        # Start background thread for periodic simulation updates
        def update_loop():
            while True:
                try:
                    simulation_manager.update_simulation_state()
                    time.sleep(0.1)  # 10 Hz updates
                except Exception as e:
                    logger.error(f"Error in update loop: {e}")
                    time.sleep(1.0)

        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
        logger.info("Background simulation update loop started")

        # Start WebSocket server for real-time streaming
        if TRANSFORMERS_AVAILABLE:
            simulation_manager.start_websocket_server(port + 1)  # Port 8503
            simulation_manager.start_realtime_broadcast()
            logger.info("WebSocket real-time streaming enabled")

        return server

    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        raise

def initialize_api_simulation(num_agents: int = 100) -> bool:
    """
    Initialize simulation for API serving.

    Args:
        num_agents: Number of agents to initialize

    Returns:
        True if successful, False otherwise
    """
    return simulation_manager.initialize_simulation(num_agents)

if __name__ == "__main__":
    # Start API server when run directly
    port = 8502
    logger.info(f"Starting 3D API server on port {port}")

    server = start_api_server(port)

    try:
        logger.info("3D API server running. Press Ctrl+C to stop.")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down 3D API server")
        server.shutdown()