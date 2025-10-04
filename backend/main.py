"""
FastAPI Backend Server for 3D AI Simulation Visualization Platform

This server bridges the existing Python simulation backend with the 3D frontend,
providing real-time data streaming and API endpoints for seamless integration.
"""

import asyncio
import json
import time
import threading
from typing import Dict, List, Any, Optional, Set
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from datetime import datetime

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np

# Import existing simulation components
import sys
import os

# Add the parent directory to Python path for proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Add the decentralized-ai-simulation directory to Python path
simulation_dir = os.path.join(parent_dir, 'decentralized-ai-simulation')
sys.path.insert(0, simulation_dir)

try:
    # Try importing from the package structure
    from src.core.simulation import Simulation
    from src.core.agents import AnomalyAgent, AnomalySignature
    from src.core.database import DatabaseLedger
    from src.config.config_loader import get_config
    from src.utils.logging_setup import get_logger
    from src.utils.monitoring import get_monitoring
except ImportError as e:
    # Fallback to direct imports if package structure is different
    print(f"Warning: Could not import from package structure: {e}")
    print("Attempting direct imports...")
    from simulation import Simulation
    from agents import AnomalyAgent, AnomalySignature
    from database import DatabaseLedger
    from config_loader import get_config
    from logging_setup import get_logger
    from monitoring import get_monitoring

# Import data transformation module
from data_transformers import (
    Vector3D, Agent3D, Anomaly3D, SimulationState3D,
    SimulationStateTransformer, create_3d_simulation_state,
    create_3d_agents, create_3d_anomalies_from_ledger
)

logger = get_logger(__name__)

class SimulationBridge:
    """
    Bridge class that connects the existing simulation to the 3D frontend.

    Handles data transformation, real-time updates, and state management.
    """

    def __init__(self):
        self.simulation: Optional[Simulation] = None
        self.ledger: Optional[DatabaseLedger] = None
        self.running: bool = False
        self.simulation_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.websocket_connections: Set[WebSocket] = set()
        self.last_update_time: float = 0
        self.update_interval: float = 0.1  # 100ms for smooth updates
        self.monitoring = get_monitoring()

        # Data transformation components
        self.state_transformer = SimulationStateTransformer()

        logger.info("SimulationBridge initialized")

    def initialize_simulation(self, num_agents: int = 100) -> bool:
        """Initialize the simulation with specified number of agents."""
        try:
            if self.simulation is not None:
                self.cleanup()

            self.ledger = DatabaseLedger()
            self.simulation = Simulation(num_agents=num_agents)

            # Initialize 3D data transformation
            if self.simulation.node_agents:
                self.state_transformer.position_mapper.initialize_spherical_layout(
                    self.simulation.node_agents
                )

            logger.info(f"Simulation initialized with {num_agents} agents")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize simulation: {e}")
            return False

    def start_simulation(self, steps: int = 100) -> bool:
        """Start the simulation in a background thread."""
        if self.running or not self.simulation:
            return False

        try:
            self.stop_event.clear()
            self.running = True

            self.simulation_thread = threading.Thread(
                target=self._run_simulation_loop,
                args=(steps,),
                daemon=True
            )
            self.simulation_thread.start()

            logger.info(f"Simulation started with {steps} steps")
            return True

        except Exception as e:
            logger.error(f"Failed to start simulation: {e}")
            self.running = False
            return False

    def stop_simulation(self) -> None:
        """Stop the simulation and cleanup resources."""
        self.running = False
        self.stop_event.set()

        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2.0)

        logger.info("Simulation stopped")

    def _run_simulation_loop(self, steps: int) -> None:
        """Main simulation loop running in background thread."""
        try:
            step_count = 0
            while self.running and step_count < steps and not self.stop_event.is_set():
                if self.simulation:
                    # Run one simulation step
                    start_time = time.time()
                    self.simulation.step()
                    step_duration = time.time() - start_time

                    step_count += 1

                    # Update 3D visualization data
                    self._update_3d_data()

                    # Send real-time updates to connected clients
                    asyncio.run(self._broadcast_simulation_update())

                    # Record performance metrics
                    self.monitoring.record_metric('simulation_step_duration', step_duration)
                    self.monitoring.record_metric('simulation_step_count', step_count)

                    # Control update frequency for smooth visualization
                    time.sleep(max(0, self.update_interval - step_duration))

                else:
                    break

        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
        finally:
            self.running = False

    def _update_3d_data(self) -> None:
        """Update 3D visualization data from simulation state."""
        if not self.simulation or not self.ledger:
            return

        try:
            # Update position mapping and connections
            self.state_transformer.position_mapper.update_positions_from_simulation(
                self.simulation.node_agents
            )
            self.state_transformer.position_mapper.calculate_connections(
                self.simulation.node_agents
            )

            # Update agent trust scores based on simulation state
            self._update_agent_trust_scores()

        except Exception as e:
            logger.error(f"Error updating 3D data: {e}")

    def _update_agent_trust_scores(self) -> None:
        """Update agent trust scores based on simulation state."""
        if not self.simulation or not self.ledger:
            return

        # Simulate trust score evolution based on agent activity
        for agent in self.simulation.node_agents:
            # Trust score influenced by recent validations and anomalies
            base_trust = 0.5

            # Get recent entries for this agent
            recent_entries = self.ledger.get_entries_by_node(agent.node_id, limit=5)

            if recent_entries:
                # Calculate trust based on recent confidence scores
                avg_confidence = np.mean([entry['confidence'] for entry in recent_entries])
                base_trust = min(1.0, max(0.0, avg_confidence + 0.3))

            # Add some temporal variation for dynamic visualization
            time_factor = np.sin(time.time() * 0.1) * 0.1
            agent.trust_score = base_trust + time_factor

    async def _broadcast_simulation_update(self) -> None:
        """Broadcast simulation state to all connected WebSocket clients."""
        if not self.websocket_connections:
            return

        try:
            # Create 3D simulation state
            simulation_state = self._create_3d_simulation_state()

            # Send to all connected clients
            disconnected_clients = set()
            for websocket in self.websocket_connections:
                try:
                    await websocket.send_json({
                        "type": "simulation_update",
                        "data": asdict(simulation_state),
                        "timestamp": time.time()
                    })
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    disconnected_clients.add(websocket)

            # Remove disconnected clients
            self.websocket_connections -= disconnected_clients

        except Exception as e:
            logger.error(f"Error broadcasting simulation update: {e}")

    def _create_3d_simulation_state(self) -> SimulationState3D:
        """Create 3D simulation state from current simulation data."""
        if not self.simulation or not self.ledger:
            return SimulationState3D(
                status="stopped",
                timestamp=time.time(),
                activeAgents=0,
                totalConnections=0,
                averageTrustScore=0.0,
                anomalies=[]
            )

        # Use the data transformation module
        return self.state_transformer.transform_simulation_state(
            self.simulation.node_agents, self.ledger, self.running
        )

    def get_agents_3d(self) -> List[Agent3D]:
        """Get all agents in 3D format for frontend."""
        if not self.simulation:
            return []

        # Use the data transformation module
        return self.state_transformer.get_agents_3d(self.simulation.node_agents)

    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get comprehensive simulation statistics."""
        if not self.simulation:
            return {"status": "not_initialized"}

        stats = self.simulation.get_simulation_stats()
        stats.update({
            "running": self.running,
            "websocket_connections": len(self.websocket_connections),
            "last_update": self.last_update_time,
            "agent_positions_count": len(self.agent_positions),
            "total_connections": sum(len(connections) for connections in self.agent_connections.values())
        })

        return stats

    def cleanup(self) -> None:
        """Cleanup simulation resources."""
        self.stop_simulation()

        if self.simulation:
            self.simulation.cleanup()
            self.simulation = None

        # Clear data transformation state
        self.state_transformer = SimulationStateTransformer()

        logger.info("SimulationBridge cleanup completed")

# Global simulation bridge instance
simulation_bridge = SimulationBridge()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting FastAPI backend server")
    yield
    # Shutdown
    logger.info("Shutting down FastAPI backend server")
    simulation_bridge.cleanup()

# Create FastAPI application
app = FastAPI(
    title="3D AI Simulation Backend",
    description="Backend API for 3D AI Simulation Visualization Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_config('backend.cors_origins', ["http://localhost:3000", "http://localhost:3001"]),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "3D AI Simulation Backend",
        "version": "1.0.0",
        "status": "running",
        "simulation_status": "running" if simulation_bridge.running else "stopped",
        "websocket_connections": len(simulation_bridge.websocket_connections)
    }

@app.post("/simulation/initialize")
async def initialize_simulation(num_agents: int = 100):
    """Initialize the simulation with specified number of agents."""
    success = simulation_bridge.initialize_simulation(num_agents)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to initialize simulation")

    return {
        "status": "initialized",
        "num_agents": num_agents,
        "message": f"Simulation initialized with {num_agents} agents"
    }

@app.post("/simulation/start")
async def start_simulation(steps: int = 100, background_tasks: BackgroundTasks = None):
    """Start the simulation."""
    success = simulation_bridge.start_simulation(steps)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start simulation")

    return {
        "status": "started",
        "steps": steps,
        "message": f"Simulation started for {steps} steps"
    }

@app.post("/simulation/stop")
async def stop_simulation():
    """Stop the simulation."""
    simulation_bridge.stop_simulation()
    return {"status": "stopped", "message": "Simulation stopped"}

@app.get("/simulation/status")
async def get_simulation_status():
    """Get current simulation status."""
    return simulation_bridge.get_simulation_stats()

@app.get("/agents")
async def get_agents():
    """Get all agents in 3D format."""
    agents = simulation_bridge.get_agents_3d()
    return {"agents": [asdict(agent) for agent in agents]}

@app.get("/simulation/state")
async def get_simulation_state():
    """Get current 3D simulation state."""
    state = simulation_bridge._create_3d_simulation_state()
    return asdict(state)

@app.websocket("/ws/simulation")
async def websocket_simulation_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time simulation updates."""
    await websocket.accept()
    simulation_bridge.websocket_connections.add(websocket)

    logger.info(f"WebSocket client connected. Total connections: {len(simulation_bridge.websocket_connections)}")

    try:
        # Send initial state
        initial_state = simulation_bridge._create_3d_simulation_state()
        await websocket.send_json({
            "type": "initial_state",
            "data": asdict(initial_state),
            "timestamp": time.time()
        })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (ping/pong, control commands, etc.)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)

                # Handle client messages if needed
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": time.time()})

            except asyncio.TimeoutError:
                # Send periodic updates to keep connection alive
                pass
            except json.JSONDecodeError:
                logger.warning("Received invalid JSON from client")
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        simulation_bridge.websocket_connections.discard(websocket)
        logger.info(f"WebSocket client removed. Total connections: {len(simulation_bridge.websocket_connections)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "simulation_running": simulation_bridge.running,
        "websocket_connections": len(simulation_bridge.websocket_connections),
        "simulation_stats": simulation_bridge.get_simulation_stats()
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    return {
        "simulation_metrics": simulation_bridge.get_simulation_stats(),
        "monitoring_metrics": simulation_bridge.monitoring.get_system_health(),
        "timestamp": time.time()
    }

if __name__ == "__main__":
    port = get_config('backend.port', 8000)
    host = get_config('backend.host', '0.0.0.0')

    logger.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=get_config('backend.reload', False),
        log_level=get_config('backend.log_level', 'info').lower()
    )