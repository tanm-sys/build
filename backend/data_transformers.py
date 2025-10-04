"""
Data Transformation Module for 3D AI Simulation Visualization Platform

This module handles the transformation of Python simulation objects to 3D visualization
formats compatible with the frontend. It provides clean separation of concerns and
reusable transformation logic.
"""

import time
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
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
    from src.core.agents import AnomalyAgent, AnomalySignature
    from src.core.database import DatabaseLedger
    from src.utils.logging_setup import get_logger
except ImportError as e:
    # Fallback to direct imports if package structure is different
    print(f"Warning: Could not import from package structure: {e}")
    print("Attempting direct imports...")
    from agents import AnomalyAgent, AnomalySignature
    from database import DatabaseLedger
    from logging_setup import get_logger

logger = get_logger(__name__)

@dataclass
class Vector3D:
    """3D vector for frontend compatibility."""
    x: float
    y: float
    z: float

@dataclass
class Agent3D:
    """3D agent representation for frontend."""
    id: str
    position: Vector3D
    trustScore: float
    status: str
    connections: List[str]
    lastUpdate: float
    metadata: Dict[str, Any]

@dataclass
class Anomaly3D:
    """3D anomaly representation for frontend."""
    id: str
    type: str
    severity: str
    position: Vector3D
    timestamp: float
    description: str

@dataclass
class SimulationState3D:
    """3D simulation state for frontend."""
    status: str
    timestamp: float
    activeAgents: int
    totalConnections: int
    averageTrustScore: float
    anomalies: List[Anomaly3D]

class PositionMapper:
    """
    Handles mapping of agents to 3D positions for visualization.

    Uses various algorithms to create aesthetically pleasing and meaningful
    3D layouts for different types of network topologies.
    """

    def __init__(self, seed: int = 42):
        """Initialize position mapper with random seed for consistency."""
        self.rng = np.random.default_rng(seed)
        self.agent_positions: Dict[str, Vector3D] = {}
        self.connection_cache: Dict[str, List[str]] = {}

    def initialize_spherical_layout(self, agents: List[AnomalyAgent], radius: float = 10.0) -> None:
        """
        Initialize agents in a spherical layout for optimal 3D visualization.

        Args:
            agents: List of agents to position
            radius: Radius of the sphere for positioning
        """
        num_agents = len(agents)

        if num_agents == 0:
            return

        self.agent_positions.clear()

        # Use Fibonacci spiral for even distribution on sphere
        for i, agent in enumerate(agents):
            # Fibonacci spiral points on sphere
            phi = np.arccos(2 * (i / num_agents) - 1)  # Uniform distribution
            theta = np.pi * (1 + np.sqrt(5)) * i  # Golden angle

            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)

            # Add controlled randomness for organic feel
            randomness = 0.05
            x += self.rng.normal(0, radius * randomness)
            y += self.rng.normal(0, radius * randomness)
            z += self.rng.normal(0, radius * randomness)

            self.agent_positions[agent.node_id] = Vector3D(x, y, z)

        logger.info(f"Initialized spherical layout for {num_agents} agents")

    def initialize_force_layout(self, agents: List[AnomalyAgent], iterations: int = 100) -> None:
        """
        Initialize agents using force-directed layout algorithm.

        Args:
            agents: List of agents to position
            iterations: Number of force-directed layout iterations
        """
        num_agents = len(agents)

        if num_agents == 0:
            return

        # Initialize random positions
        positions = {}
        for agent in agents:
            positions[agent.node_id] = Vector3D(
                self.rng.uniform(-10, 10),
                self.rng.uniform(-10, 10),
                self.rng.uniform(-10, 10)
            )

        # Force-directed layout simulation
        for _ in range(iterations):
            forces = {agent_id: Vector3D(0, 0, 0) for agent_id in positions}

            # Calculate repulsive forces between all pairs
            agent_ids = list(positions.keys())
            for i, id1 in enumerate(agent_ids):
                for j, id2 in enumerate(agent_ids[i+1:], i+1):
                    pos1 = positions[id1]
                    pos2 = positions[id2]

                    # Vector from pos2 to pos1
                    dx = pos1.x - pos2.x
                    dy = pos1.y - pos2.y
                    dz = pos1.z - pos2.z
                    distance = math.sqrt(dx*dx + dy*dy + dz*dz)

                    if distance > 0:
                        # Repulsive force (inverse square law)
                        force = 1.0 / (distance * distance + 0.1)
                        force_x = (dx / distance) * force
                        force_y = (dy / distance) * force
                        force_z = (dz / distance) * force

                        forces[id1] = Vector3D(
                            forces[id1].x + force_x,
                            forces[id1].y + force_y,
                            forces[id1].z + force_z
                        )
                        forces[id2] = Vector3D(
                            forces[id2].x - force_x,
                            forces[id2].y - force_y,
                            forces[id2].z - force_z
                        )

            # Apply attractive forces for connections (would need connection data)
            # For now, use random connections for demonstration

            # Update positions based on forces
            for agent_id, force in forces.items():
                pos = positions[agent_id]
                damping = 0.9

                positions[agent_id] = Vector3D(
                    pos.x + force.x * damping,
                    pos.y + force.y * damping,
                    pos.z + force.z * damping
                )

        self.agent_positions = positions
        logger.info(f"Initialized force-directed layout for {num_agents} agents")

    def update_positions_from_simulation(self, agents: List[AnomalyAgent]) -> None:
        """
        Update agent positions based on simulation state and trust scores.

        Args:
            agents: Current list of agents from simulation
        """
        if not self.agent_positions:
            self.initialize_spherical_layout(agents)
            return

        # Update positions based on trust score changes and time
        current_time = time.time()

        for agent in agents:
            if agent.node_id not in self.agent_positions:
                # Add new agent at random position
                self.agent_positions[agent.node_id] = Vector3D(
                    self.rng.uniform(-10, 10),
                    self.rng.uniform(-10, 10),
                    self.rng.uniform(-10, 10)
                )
                continue

            current_pos = self.agent_positions[agent.node_id]
            trust_score = getattr(agent, 'trust_score', 0.5)

            # Subtle movement based on trust score and time
            # High trust = stable position, low trust = more movement
            movement_factor = (1.0 - trust_score) * 0.1

            # Create organic movement using sine waves
            time_offset = hash(agent.node_id) % 1000  # Consistent per agent
            movement_x = math.sin(current_time * 0.1 + time_offset) * movement_factor
            movement_y = math.cos(current_time * 0.15 + time_offset) * movement_factor
            movement_z = math.sin(current_time * 0.08 + time_offset * 0.7) * movement_factor

            # Apply movement
            new_pos = Vector3D(
                current_pos.x + movement_x,
                current_pos.y + movement_y,
                current_pos.z + movement_z
            )

            # Keep positions within reasonable bounds
            max_distance = 15.0
            distance_from_origin = math.sqrt(new_pos.x**2 + new_pos.y**2 + new_pos.z**2)
            if distance_from_origin > max_distance:
                scale = max_distance / distance_from_origin
                new_pos = Vector3D(
                    new_pos.x * scale,
                    new_pos.y * scale,
                    new_pos.z * scale
                )

            self.agent_positions[agent.node_id] = new_pos

    def calculate_connections(self, agents: List[AnomalyAgent], max_connections: int = 5) -> Dict[str, List[str]]:
        """
        Calculate agent connections based on 3D proximity and trust relationships.

        Args:
            agents: List of agents to analyze
            max_connections: Maximum connections per agent

        Returns:
            Dictionary mapping agent IDs to lists of connected agent IDs
        """
        if not self.agent_positions:
            return {}

        connections = {}

        for agent in agents:
            agent_pos = self.agent_positions[agent.node_id]
            distances = []

            # Calculate distances to all other agents
            for other_agent in agents:
                if agent.node_id == other_agent.node_id:
                    continue

                other_pos = self.agent_positions[other_agent.node_id]
                distance = self._calculate_distance(agent_pos, other_pos)

                # Include trust score in connection probability
                trust_score = getattr(other_agent, 'trust_score', 0.5)
                weighted_distance = distance / (trust_score + 0.1)  # Higher trust = closer effective distance

                distances.append((other_agent.node_id, weighted_distance))

            # Sort by weighted distance and take closest agents
            distances.sort(key=lambda x: x[1])
            closest_agents = [agent_id for agent_id, _ in distances[:max_connections]]

            connections[agent.node_id] = closest_agents

        self.connection_cache = connections
        return connections

    def _calculate_distance(self, pos1: Vector3D, pos2: Vector3D) -> float:
        """Calculate Euclidean distance between two 3D positions."""
        return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2)

    def get_agent_position(self, agent_id: str) -> Optional[Vector3D]:
        """Get position for specific agent."""
        return self.agent_positions.get(agent_id)

    def get_all_positions(self) -> Dict[str, Vector3D]:
        """Get all agent positions."""
        return self.agent_positions.copy()

class AnomalyTransformer:
    """
    Transforms anomaly signatures from simulation to 3D visualization format.

    Handles the conversion of anomaly data to formats suitable for 3D rendering
    and user interaction.
    """

    def __init__(self):
        """Initialize anomaly transformer."""
        self.severity_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 1.0
        }

    def transform_anomalies_from_ledger(self,
                                     ledger: DatabaseLedger,
                                     position_mapper: PositionMapper,
                                     max_anomalies: int = 10) -> List[Anomaly3D]:
        """
        Transform recent anomalies from ledger to 3D format.

        Args:
            ledger: Database ledger containing anomaly signatures
            position_mapper: Position mapper for agent locations
            max_anomalies: Maximum number of anomalies to transform

        Returns:
            List of 3D anomaly objects
        """
        try:
            entries = ledger.read_ledger()
            if not entries:
                return []

            # Take most recent anomalies
            recent_entries = entries[-max_anomalies:]

            anomalies_3d = []
            for entry in recent_entries:
                anomaly_3d = self._transform_single_entry(entry, position_mapper)
                if anomaly_3d:
                    anomalies_3d.append(anomaly_3d)

            logger.debug(f"Transformed {len(anomalies_3d)} anomalies from ledger")
            return anomalies_3d

        except Exception as e:
            logger.error(f"Error transforming anomalies from ledger: {e}")
            return []

    def _transform_single_entry(self,
                              entry: Dict[str, Any],
                              position_mapper: PositionMapper) -> Optional[Anomaly3D]:
        """Transform a single ledger entry to 3D anomaly format."""
        try:
            node_id = entry.get('node_id', '')
            position = position_mapper.get_agent_position(node_id)

            if not position:
                logger.warning(f"No position found for node {node_id}")
                return None

            confidence = entry.get('confidence', 0.0)
            severity = self._calculate_severity(confidence)

            # Create enhanced description
            features = entry.get('features', [])
            feature_count = len(features)

            description = (
                f"Anomaly detected by {node_id} "
                f"(Confidence: {confidence:.2f}, "
                f"Features: {feature_count})"
            )

            return Anomaly3D(
                id=f"anomaly_{entry.get('id', 0)}",
                type=self._classify_anomaly_type(entry),
                severity=severity,
                position=position,
                timestamp=entry.get('timestamp', time.time()),
                description=description
            )

        except Exception as e:
            logger.error(f"Error transforming single entry: {e}")
            return None

    def _calculate_severity(self, confidence: float) -> str:
        """Calculate severity level from confidence score."""
        if confidence >= self.severity_thresholds['critical']:
            return 'critical'
        elif confidence >= self.severity_thresholds['high']:
            return 'high'
        elif confidence >= self.severity_thresholds['medium']:
            return 'medium'
        else:
            return 'low'

    def _classify_anomaly_type(self, entry: Dict[str, Any]) -> str:
        """Classify anomaly type based on features and confidence."""
        confidence = entry.get('confidence', 0.0)
        features = entry.get('features', [])

        if confidence > 0.8:
            return 'trust_drop'
        elif len(features) > 5:
            return 'connection_spike'
        else:
            return 'unusual_activity'

class AgentTransformer:
    """
    Transforms simulation agents to 3D visualization format.

    Handles the conversion of agent data to formats suitable for 3D rendering,
    including trust scores, connections, and metadata.
    """

    def __init__(self):
        """Initialize agent transformer."""
        self.status_colors = {
            'active': '#00ff00',
            'inactive': '#ffff00',
            'suspended': '#ff0000'
        }

    def transform_agents(self,
                        agents: List[AnomalyAgent],
                        position_mapper: PositionMapper) -> List[Agent3D]:
        """
        Transform simulation agents to 3D format.

        Args:
            agents: List of simulation agents
            position_mapper: Position mapper for agent locations

        Returns:
            List of 3D agent objects
        """
        agents_3d = []

        for agent in agents:
            agent_3d = self._transform_single_agent(agent, position_mapper)
            if agent_3d:
                agents_3d.append(agent_3d)

        logger.debug(f"Transformed {len(agents_3d)} agents to 3D format")
        return agents_3d

    def _transform_single_agent(self,
                              agent: AnomalyAgent,
                              position_mapper: PositionMapper) -> Optional[Agent3D]:
        """Transform a single agent to 3D format."""
        try:
            position = position_mapper.get_agent_position(agent.node_id)
            if not position:
                logger.warning(f"No position found for agent {agent.node_id}")
                return None

            # Get trust score (with fallback)
            trust_score = getattr(agent, 'trust_score', 0.5)

            # Get connections from position mapper
            connections = position_mapper.connection_cache.get(agent.node_id, [])

            # Create metadata
            metadata = self._extract_agent_metadata(agent)

            return Agent3D(
                id=agent.node_id,
                position=position,
                trustScore=trust_score,
                status='active',  # Could be enhanced with actual status tracking
                connections=connections,
                lastUpdate=time.time(),
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error transforming agent {agent.node_id}: {e}")
            return None

    def _extract_agent_metadata(self, agent: AnomalyAgent) -> Dict[str, Any]:
        """Extract metadata from agent for 3D visualization."""
        metadata = {
            'validation_cache_size': len(getattr(agent, '_validation_cache', {})),
            'anomaly_threshold': getattr(agent, 'anomaly_threshold', -0.05),
            'validation_failure_rate': getattr(agent, 'validation_failure_rate', 0.2)
        }

        # Add cache statistics if available
        if hasattr(agent, 'get_cache_stats'):
            try:
                cache_stats = agent.get_cache_stats()
                metadata['cache_stats'] = cache_stats
            except Exception:
                pass  # Ignore cache stat errors

        return metadata

class SimulationStateTransformer:
    """
    Transforms overall simulation state to 3D visualization format.

    Aggregates data from multiple sources to create a comprehensive
    3D simulation state for frontend consumption.
    """

    def __init__(self):
        """Initialize simulation state transformer."""
        self.position_mapper = PositionMapper()
        self.anomaly_transformer = AnomalyTransformer()
        self.agent_transformer = AgentTransformer()

    def transform_simulation_state(self,
                                 agents: List[AnomalyAgent],
                                 ledger: DatabaseLedger,
                                 running: bool = False) -> SimulationState3D:
        """
        Transform complete simulation state to 3D format.

        Args:
            agents: Current simulation agents
            ledger: Database ledger for anomaly data
            running: Whether simulation is currently running

        Returns:
            Complete 3D simulation state
        """
        try:
            # Update position mapping
            self.position_mapper.update_positions_from_simulation(agents)
            connections = self.position_mapper.calculate_connections(agents)

            # Transform anomalies
            anomalies_3d = self.anomaly_transformer.transform_anomalies_from_ledger(
                ledger, self.position_mapper
            )

            # Calculate aggregate statistics
            total_connections = sum(len(conns) for conns in connections.values())
            avg_trust_score = np.mean([getattr(agent, 'trust_score', 0.5) for agent in agents]) if agents else 0.0

            return SimulationState3D(
                status='running' if running else 'paused',
                timestamp=time.time(),
                activeAgents=len(agents),
                totalConnections=total_connections,
                averageTrustScore=float(avg_trust_score),
                anomalies=anomalies_3d
            )

        except Exception as e:
            logger.error(f"Error transforming simulation state: {e}")
            # Return safe default state
            return SimulationState3D(
                status='error',
                timestamp=time.time(),
                activeAgents=0,
                totalConnections=0,
                averageTrustScore=0.0,
                anomalies=[]
            )

    def get_agents_3d(self, agents: List[AnomalyAgent]) -> List[Agent3D]:
        """Get agents in 3D format."""
        return self.agent_transformer.transform_agents(agents, self.position_mapper)

# Convenience functions for easy access
def create_3d_simulation_state(agents: List[AnomalyAgent],
                              ledger: DatabaseLedger,
                              running: bool = False) -> SimulationState3D:
    """Create 3D simulation state from simulation components."""
    transformer = SimulationStateTransformer()
    return transformer.transform_simulation_state(agents, ledger, running)

def create_3d_agents(agents: List[AnomalyAgent]) -> List[Agent3D]:
    """Create 3D agents from simulation agents."""
    transformer = SimulationStateTransformer()
    return transformer.get_agents_3d(agents)

def create_3d_anomalies_from_ledger(ledger: DatabaseLedger,
                                   agents: List[AnomalyAgent],
                                   max_anomalies: int = 10) -> List[Anomaly3D]:
    """Create 3D anomalies from ledger entries."""
    transformer = SimulationStateTransformer()
    transformer.position_mapper.initialize_spherical_layout(agents)
    return transformer.anomaly_transformer.transform_anomalies_from_ledger(
        ledger, transformer.position_mapper, max_anomalies
    )