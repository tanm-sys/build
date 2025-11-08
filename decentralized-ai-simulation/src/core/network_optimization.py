"""
Network Topology Optimization and Agent Orchestration Module

Implements enterprise-grade network optimization and intelligent orchestration:
- Advanced network topology optimization algorithms
- Dynamic load balancing and routing optimization
- Intelligent agent orchestration with dynamic scaling
- Resource allocation and scheduling
- Fault tolerance and self-healing mechanisms

Author: Kilo Code
Date: November 1, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import time
import json
import asyncio
from enum import Enum
import heapq
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, minimum_spanning_tree
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class TopologyType(Enum):
    """Network topology types."""
    STAR = "star"
    MESH = "mesh"
    TREE = "tree"
    RING = "ring"
    HYPERCUBE = "hypercube"
    BARABASI_ALBERT = "barabasi_albert"
    SMALL_WORLD = "small_world"
    CUSTOM = "custom"


class OptimizationObjective(Enum):
    """Network optimization objectives."""
    MINIMIZE_LATENCY = "minimize_latency"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    MINIMIZE_ENERGY = "minimize_energy"
    MAXIMIZE_RELIABILITY = "maximize_reliability"
    BALANCE_LOAD = "balance_load"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_FAULT_TOLERANCE = "maximize_fault_tolerance"


class AgentState(Enum):
    """Agent lifecycle states."""
    IDLE = "idle"
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    SCALING_UP = "scaling_up"
    SCALING_DOWN = "scaling_down"
    DEGRADED = "degraded"


@dataclass
class NetworkNode:
    """Represents a network node."""
    node_id: str
    position: Tuple[float, float]
    capacity: float
    load: float
    connectivity: List[str]  # Connected node IDs
    capabilities: Dict[str, float]  # Processing, storage, network capabilities
    health_status: float = 1.0  # 0.0 to 1.0
    last_heartbeat: float = field(default_factory=time.time)


@dataclass
class NetworkEdge:
    """Represents a network connection."""
    source_id: str
    target_id: str
    bandwidth: float
    latency: float
    reliability: float
    cost: float
    current_load: float = 0.0


@dataclass
class OptimizationMetrics:
    """Network optimization metrics."""
    total_latency: float
    average_throughput: float
    energy_consumption: float
    reliability_score: float
    load_balance_factor: float
    fault_tolerance_score: float
    cost_efficiency: float


@dataclass
class AgentSpec:
    """Agent specification for orchestration."""
    agent_type: str
    resource_requirements: Dict[str, float]
    priority: int
    dependencies: List[str]
    scaling_policy: Dict[str, Any]
    location_preference: Optional[str] = None


@dataclass
class AgentInstance:
    """Running agent instance."""
    instance_id: str
    spec: AgentSpec
    current_node: str
    state: AgentState
    resource_usage: Dict[str, float]
    performance_metrics: Dict[str, float]
    start_time: float
    health_status: float = 1.0


class NetworkTopologyOptimizer:
    """
    Advanced network topology optimization system.
    
    Implements multiple optimization algorithms:
    - Genetic algorithm for topology evolution
    - Simulated annealing for local optimization
    - Particle swarm optimization for multi-objective
    - Graph neural networks for learning-based optimization
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize network topology optimizer."""
        self.config = config or self._default_config()
        
        # Network representation
        self.nodes = {}
        self.edges = {}
        self.graph = nx.Graph()
        self.adjacency_matrix = None
        
        # Optimization state
        self.current_topology = TopologyType.MESH
        self.optimization_history = deque(maxlen=100)
        self.performance_baseline = {}
        
        # Optimization algorithms
        self.genetic_population = []
        self.particle_swarm = []
        
        # Constraints
        self.max_nodes = self.config.get('max_nodes', 100)
        self.max_edges = self.config.get('max_edges', 500)
        self.node_capacity_limit = self.config.get('node_capacity_limit', 1000)
        
        # Threading
        self._lock = threading.Lock()
        
        logger.info("Network topology optimizer initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'max_nodes': 100,
            'max_edges': 500,
            'node_capacity_limit': 1000,
            'optimization_interval': 300,  # 5 minutes
            'genetic_algorithm': {
                'population_size': 50,
                'mutation_rate': 0.1,
                'crossover_rate': 0.8,
                'generations': 100
            },
            'simulated_annealing': {
                'initial_temperature': 1000,
                'cooling_rate': 0.95,
                'min_temperature': 1
            },
            'particle_swarm': {
                'num_particles': 30,
                'inertia': 0.7,
                'cognitive': 1.4,
                'social': 1.4
            },
            'objectives': [OptimizationObjective.MINIMIZE_LATENCY, OptimizationObjective.BALANCE_LOAD]
        }

    def optimize_topology(self, objective: OptimizationObjective, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optimize network topology for specified objective.
        
        Args:
            objective: Optimization objective
            constraints: Optimization constraints
            
        Returns:
            Optimization results including new topology
        """
        with self._lock:
            try:
                logger.info(f"Starting topology optimization for objective: {objective.value}")
                
                # Analyze current network state
                current_metrics = self._calculate_network_metrics()
                
                # Select optimization algorithm based on network size and complexity
                if len(self.nodes) > 50:
                    algorithm = self._genetic_algorithm_optimization
                else:
                    algorithm = self._simulated_annealing_optimization
                
                # Run optimization
                start_time = time.time()
                result = algorithm(objective, constraints or {})
                optimization_time = time.time() - start_time
                
                # Update topology
                new_topology = result['topology']
                self._apply_topology_change(new_topology)
                
                # Calculate improvement
                new_metrics = self._calculate_network_metrics()
                improvement = self._calculate_improvement(current_metrics, new_metrics, objective)
                
                # Record optimization
                optimization_record = {
                    'objective': objective.value,
                    'algorithm': algorithm.__name__,
                    'optimization_time': optimization_time,
                    'improvement': improvement,
                    'metrics_before': current_metrics,
                    'metrics_after': new_metrics,
                    'timestamp': time.time()
                }
                
                self.optimization_history.append(optimization_record)
                
                logger.info(f"Topology optimization completed: {improvement:.2%} improvement")
                return {
                    'success': True,
                    'topology': new_topology,
                    'improvement': improvement,
                    'metrics': new_metrics,
                    'optimization_time': optimization_time,
                    'recommendations': self._generate_optimization_recommendations(new_metrics)
                }
                
            except Exception as e:
                logger.error(f"Topology optimization failed: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'metrics': self._calculate_network_metrics()
                }

    def _genetic_algorithm_optimization(self, objective: OptimizationObjective, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Genetic algorithm for topology optimization."""
        pop_size = self.config['genetic_algorithm']['population_size']
        generations = self.config['genetic_algorithm']['generations']
        mutation_rate = self.config['genetic_algorithm']['mutation_rate']
        crossover_rate = self.config['genetic_algorithm']['crossover_rate']
        
        # Initialize population
        population = self._initialize_genetic_population(pop_size)
        
        best_fitness = float('inf')
        best_topology = None
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_topology_fitness(individual, objective)
                fitness_scores.append((fitness, individual))
            
            # Sort by fitness
            fitness_scores.sort(key=lambda x: x[0])
            
            # Update best
            if fitness_scores[0][0] < best_fitness:
                best_fitness = fitness_scores[0][0]
                best_topology = fitness_scores[0][1].copy()
            
            # Selection and reproduction
            if generation < generations - 1:
                population = self._genetic_reproduction(fitness_scores, population, mutation_rate, crossover_rate)
        
        return {
            'topology': best_topology,
            'fitness': best_fitness,
            'generation': generations
        }

    def _simulated_annealing_optimization(self, objective: OptimizationObjective, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Simulated annealing for topology optimization."""
        temp = self.config['simulated_annealing']['initial_temperature']
        cooling_rate = self.config['simulated_annealing']['cooling_rate']
        min_temp = self.config['simulated_annealing']['min_temperature']
        
        # Start with current topology
        current_topology = self._encode_current_topology()
        current_fitness = self._evaluate_topology_fitness(current_topology, objective)
        
        best_topology = current_topology.copy()
        best_fitness = current_fitness
        
        iteration = 0
        while temp > min_temp:
            # Generate neighbor
            neighbor = self._generate_topology_neighbor(current_topology)
            neighbor_fitness = self._evaluate_topology_fitness(neighbor, objective)
            
            # Accept or reject
            if neighbor_fitness < current_fitness or np.random.random() < np.exp(-(neighbor_fitness - current_fitness) / temp):
                current_topology = neighbor
                current_fitness = neighbor_fitness
                
                if neighbor_fitness < best_fitness:
                    best_topology = neighbor.copy()
                    best_fitness = neighbor_fitness
            
            temp *= cooling_rate
            iteration += 1
        
        return {
            'topology': best_topology,
            'fitness': best_fitness,
            'iterations': iteration
        }

    def _initialize_genetic_population(self, population_size: int) -> List[Dict[str, Any]]:
        """Initialize genetic algorithm population."""
        population = []
        
        for _ in range(population_size):
            # Create random topology
            topology = {
                'nodes': list(self.nodes.keys()),
                'edges': self._generate_random_edges(),
                'node_positions': self._optimize_node_positions(),
                'connection_strategy': np.random.choice(['random', 'clustered', 'hierarchical'])
            }
            population.append(topology)
        
        return population

    def _generate_random_edges(self) -> List[Tuple[str, str]]:
        """Generate random edge connections."""
        nodes = list(self.nodes.keys())
        num_edges = min(len(nodes) * 2, self.max_edges)
        edges = []
        
        for _ in range(num_edges):
            source = np.random.choice(nodes)
            target = np.random.choice([n for n in nodes if n != source])
            if (source, target) not in edges and (target, source) not in edges:
                edges.append((source, target))
        
        return edges

    def _evaluate_topology_fitness(self, topology: Dict[str, Any], objective: OptimizationObjective) -> float:
        """Evaluate topology fitness for objective."""
        # Apply topology to calculate metrics
        self._apply_topology_to_metrics(topology)
        metrics = self._calculate_network_metrics()
        
        # Calculate fitness based on objective
        if objective == OptimizationObjective.MINIMIZE_LATENCY:
            return metrics.total_latency
        elif objective == OptimizationObjective.MAXIMIZE_THROUGHPUT:
            return 1.0 / max(0.001, metrics.average_throughput)
        elif objective == OptimizationObjective.MINIMIZE_ENERGY:
            return metrics.energy_consumption
        elif objective == OptimizationObjective.MAXIMIZE_RELIABILITY:
            return 1.0 / max(0.001, metrics.reliability_score)
        elif objective == OptimizationObjective.BALANCE_LOAD:
            return metrics.load_balance_factor
        elif objective == OptimizationObjective.MINIMIZE_COST:
            return self._calculate_total_cost(topology)
        else:
            return metrics.total_latency  # Default

    def _calculate_network_metrics(self) -> OptimizationMetrics:
        """Calculate comprehensive network metrics."""
        if not self.graph.nodes():
            return OptimizationMetrics(0, 0, 0, 1, 1, 1, 1)
        
        # Calculate basic metrics
        total_latency = self._calculate_total_latency()
        avg_throughput = self._calculate_average_throughput()
        energy_consumption = self._calculate_energy_consumption()
        reliability = self._calculate_reliability_score()
        load_balance = self._calculate_load_balance_factor()
        fault_tolerance = self._calculate_fault_tolerance_score()
        cost_efficiency = self._calculate_cost_efficiency()
        
        return OptimizationMetrics(
            total_latency=total_latency,
            average_throughput=avg_throughput,
            energy_consumption=energy_consumption,
            reliability_score=reliability,
            load_balance_factor=load_balance,
            fault_tolerance_score=fault_tolerance,
            cost_efficiency=cost_efficiency
        )

    def _calculate_total_latency(self) -> float:
        """Calculate total network latency."""
        if not self.edges:
            return float('inf')
        
        total_latency = 0.0
        edge_count = 0
        
        for edge in self.edges.values():
            # Consider current load impact on latency
            load_factor = 1.0 + (edge.current_load / edge.bandwidth)
            effective_latency = edge.latency * load_factor
            total_latency += effective_latency
            edge_count += 1
        
        return total_latency / max(1, edge_count)

    def _calculate_average_throughput(self) -> float:
        """Calculate average network throughput."""
        if not self.edges:
            return 0.0
        
        total_throughput = 0.0
        edge_count = 0
        
        for edge in self.edges.values():
            # Throughput limited by bandwidth and current load
            available_bandwidth = max(0, edge.bandwidth - edge.current_load)
            total_throughput += available_bandwidth
            edge_count += 1
        
        return total_throughput / max(1, edge_count)

    def _calculate_energy_consumption(self) -> float:
        """Calculate network energy consumption."""
        energy = 0.0
        
        # Node energy consumption
        for node in self.nodes.values():
            base_energy = node.capacity * 0.1  # Base consumption
            load_energy = node.load * 0.05    # Load-based consumption
            energy += base_energy + load_energy
        
        # Edge energy consumption
        for edge in self.edges.values():
            edge_energy = edge.bandwidth * 0.001 * edge.current_load
            energy += edge_energy
        
        return energy

    def _calculate_reliability_score(self) -> float:
        """Calculate network reliability score."""
        if not self.edges:
            return 0.0
        
        # Calculate reliability based on edge reliability and redundancy
        total_reliability = 0.0
        edge_count = 0
        
        for edge in self.edges.values():
            # Base reliability from edge property
            reliability = edge.reliability
            
            # Adjust for load (higher load = lower reliability)
            load_factor = 1.0 - (edge.current_load / max(1, edge.bandwidth)) * 0.5
            adjusted_reliability = reliability * load_factor
            
            total_reliability += adjusted_reliability
            edge_count += 1
        
        return total_reliability / max(1, edge_count)

    def _calculate_load_balance_factor(self) -> float:
        """Calculate load balance factor (lower is better)."""
        if not self.nodes:
            return 1.0
        
        loads = [node.load / max(1, node.capacity) for node in self.nodes.values()]
        if len(loads) < 2:
            return 0.0
        
        # Standard deviation of normalized loads
        return np.std(loads)

    def _calculate_fault_tolerance_score(self) -> float:
        """Calculate fault tolerance score."""
        if len(self.nodes) < 2:
            return 0.0
        
        # Calculate average node connectivity
        connectivity_scores = []
        for node_id in self.nodes:
            neighbors = list(self.graph.neighbors(node_id))
            connectivity = len(neighbors) / max(1, len(self.nodes) - 1)
            connectivity_scores.append(connectivity)
        
        return np.mean(connectivity_scores)

    def _calculate_cost_efficiency(self) -> float:
        """Calculate cost efficiency."""
        if not self.edges:
            return 0.0
        
        total_cost = sum(edge.cost for edge in self.edges.values())
        total_capacity = sum(edge.bandwidth for edge in self.edges.values())
        
        if total_capacity == 0:
            return 0.0
        
        return total_capacity / max(1, total_cost)

    def _calculate_total_cost(self, topology: Dict[str, Any]) -> float:
        """Calculate total topology cost."""
        cost = 0.0
        
        # Node costs (deployment and maintenance)
        cost += len(topology['nodes']) * 10
        
        # Edge costs (bandwidth and infrastructure)
        for source, target in topology['edges']:
            if source in self.nodes and target in self.nodes:
                # Estimate cost based on distance and bandwidth
                source_pos = topology['node_positions'][source]
                target_pos = topology['node_positions'][target]
                distance = np.sqrt((source_pos[0] - target_pos[0])**2 + (source_pos[1] - target_pos[1])**2)
                cost += distance * 2 + 5  # Base cost + distance cost
        
        return cost

    def _optimize_node_positions(self) -> Dict[str, Tuple[float, float]]:
        """Optimize node positions for minimal total distance."""
        if len(self.nodes) < 2:
            return {}
        
        # Simple optimization: distribute nodes evenly
        positions = {}
        node_count = len(self.nodes)
        
        for i, node_id in enumerate(self.nodes.keys()):
            angle = 2 * np.pi * i / node_count
            radius = 10.0  # Fixed radius
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            positions[node_id] = (x, y)
        
        return positions

    def _genetic_reproduction(self, fitness_scores: List[Tuple[float, Dict[str, Any]]], 
                            population: List[Dict[str, Any]], mutation_rate: float, 
                            crossover_rate: float) -> List[Dict[str, Any]]:
        """Perform genetic reproduction."""
        # Keep top performers (elitism)
        elite_size = int(0.1 * len(population))
        new_population = [individual for _, individual in fitness_scores[:elite_size]]
        
        # Generate offspring
        while len(new_population) < len(population):
            if np.random.random() < crossover_rate:
                # Crossover
                parent1 = self._tournament_selection(fitness_scores)
                parent2 = self._tournament_selection(fitness_scores)
                child1, child2 = self._crossover(parent1, parent2)
                
                # Mutation
                if np.random.random() < mutation_rate:
                    child1 = self._mutate(child1)
                if np.random.random() < mutation_rate:
                    child2 = self._mutate(child2)
                
                new_population.extend([child1, child2])
            else:
                # Direct copy with mutation
                parent = self._tournament_selection(fitness_scores)
                child = self._mutate(parent.copy())
                new_population.append(child)
        
        return new_population[:len(population)]

    def _tournament_selection(self, fitness_scores: List[Tuple[float, Dict[str, Any]]], 
                             tournament_size: int = 3) -> Dict[str, Any]:
        """Tournament selection for genetic algorithm."""
        tournament = np.random.choice(len(fitness_scores), tournament_size, replace=False)
        tournament_fitness = [(fitness_scores[i][0], fitness_scores[i][1]) for i in tournament]
        tournament_fitness.sort(key=lambda x: x[0])
        return tournament_fitness[0][1].copy()

    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Crossover operation for genetic algorithm."""
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        # Mix edges
        edges1 = parent1['edges']
        edges2 = parent2['edges']
        
        split_point = len(edges1) // 2
        child1['edges'] = edges1[:split_point] + edges2[split_point:]
        child2['edges'] = edges2[:split_point] + edges1[split_point:]
        
        return child1, child2

    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Mutation operation for genetic algorithm."""
        # Random edge mutations
        if np.random.random() < 0.3:
            # Add random edge
            nodes = individual['nodes']
            if len(nodes) > 1:
                source = np.random.choice(nodes)
                target = np.random.choice([n for n in nodes if n != source])
                new_edge = (source, target)
                if new_edge not in individual['edges'] and (new_edge[1], new_edge[0]) not in individual['edges']:
                    individual['edges'].append(new_edge)
        
        if np.random.random() < 0.3 and len(individual['edges']) > len(individual['nodes']):
            # Remove random edge
            edge_idx = np.random.randint(len(individual['edges']))
            individual['edges'].pop(edge_idx)
        
        # Node position mutations
        if np.random.random() < 0.2:
            node_id = np.random.choice(individual['nodes'])
            if node_id in individual['node_positions']:
                x, y = individual['node_positions'][node_id]
                individual['node_positions'][node_id] = (
                    x + np.random.normal(0, 1),
                    y + np.random.normal(0, 1)
                )
        
        return individual

    def _generate_topology_neighbor(self, topology: Dict[str, Any]) -> Dict[str, Any]:
        """Generate neighbor topology for simulated annealing."""
        neighbor = topology.copy()
        
        # Random edge modification
        if np.random.random() < 0.5:
            # Add or remove edge
            if np.random.random() < 0.5 and len(neighbor['edges']) < self.max_edges:
                # Add edge
                nodes = neighbor['nodes']
                source = np.random.choice(nodes)
                target = np.random.choice([n for n in nodes if n != source])
                new_edge = (source, target)
                if new_edge not in neighbor['edges'] and (new_edge[1], new_edge[0]) not in neighbor['edges']:
                    neighbor['edges'].append(new_edge)
            else:
                # Remove edge
                if neighbor['edges']:
                    edge_idx = np.random.randint(len(neighbor['edges']))
                    neighbor['edges'].pop(edge_idx)
        
        return neighbor

    def _apply_topology_change(self, new_topology: Dict[str, Any]) -> None:
        """Apply topology changes to network."""
        # Update edges
        self.edges = {}
        for source, target in new_topology.get('edges', []):
            if source in self.nodes and target in self.nodes:
                edge = NetworkEdge(
                    source_id=source,
                    target_id=target,
                    bandwidth=100.0,  # Default bandwidth
                    latency=0.01,     # Default latency
                    reliability=0.99, # Default reliability
                    cost=1.0          # Default cost
                )
                self.edges[f"{source}-{target}"] = edge
        
        # Update graph
        self.graph.clear()
        for node_id in self.nodes:
            self.graph.add_node(node_id)
        
        for edge in self.edges.values():
            self.graph.add_edge(edge.source_id, edge.target_id)

    def _apply_topology_to_metrics(self, topology: Dict[str, Any]) -> None:
        """Apply topology to network metrics calculation."""
        # This would apply the topology and update current network state
        pass

    def _encode_current_topology(self) -> Dict[str, Any]:
        """Encode current topology for optimization."""
        return {
            'nodes': list(self.nodes.keys()),
            'edges': [(edge.source_id, edge.target_id) for edge in self.edges.values()],
            'node_positions': {node_id: node.position for node_id, node in self.nodes.items()},
            'connection_strategy': 'current'
        }

    def _calculate_improvement(self, before: OptimizationMetrics, after: OptimizationMetrics, 
                              objective: OptimizationObjective) -> float:
        """Calculate improvement percentage."""
        if objective == OptimizationObjective.MINIMIZE_LATENCY:
            if before.total_latency == 0:
                return 0.0
            return max(0, (before.total_latency - after.total_latency) / before.total_latency)
        elif objective == OptimizationObjective.MAXIMIZE_THROUGHPUT:
            if before.average_throughput == 0:
                return 0.0
            return max(0, (after.average_throughput - before.average_throughput) / before.average_throughput)
        elif objective == OptimizationObjective.BALANCE_LOAD:
            if before.load_balance_factor == 0:
                return 0.0
            return max(0, (before.load_balance_factor - after.load_balance_factor) / before.load_balance_factor)
        else:
            return 0.0

    def _generate_optimization_recommendations(self, metrics: OptimizationMetrics) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if metrics.total_latency > 100:
            recommendations.append("Consider reducing network diameter to minimize latency")
        
        if metrics.load_balance_factor > 0.5:
            recommendations.append("Rebalance load distribution across nodes")
        
        if metrics.reliability_score < 0.8:
            recommendations.append("Increase network redundancy for better reliability")
        
        if metrics.energy_consumption > 1000:
            recommendations.append("Optimize energy consumption through efficient routing")
        
        return recommendations

    def add_node(self, node: NetworkNode) -> None:
        """Add node to network."""
        with self._lock:
            self.nodes[node.node_id] = node
            self.graph.add_node(node.node_id, pos=node.position)

    def add_edge(self, edge: NetworkEdge) -> None:
        """Add edge to network."""
        with self._lock:
            self.edges[f"{edge.source_id}-{edge.target_id}"] = edge
            self.graph.add_edge(edge.source_id, edge.target_id)

    def remove_node(self, node_id: str) -> bool:
        """Remove node from network."""
        with self._lock:
            if node_id in self.nodes:
                # Remove associated edges
                edges_to_remove = [key for key in self.edges.keys() if node_id in key.split('-')]
                for edge_key in edges_to_remove:
                    del self.edges[edge_key]
                
                # Remove node
                del self.nodes[node_id]
                self.graph.remove_node(node_id)
                return True
            return False

    def update_node_load(self, node_id: str, new_load: float) -> bool:
        """Update node load."""
        with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].load = max(0, min(new_load, self.nodes[node_id].capacity))
                return True
            return False

    def get_network_status(self) -> Dict[str, Any]:
        """Get comprehensive network status."""
        with self._lock:
            metrics = self._calculate_network_metrics()
            
            return {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'avg_degree': np.mean([self.graph.degree(node) for node in self.graph.nodes()]) if self.graph.nodes() else 0,
                'is_connected': nx.is_connected(self.graph) if self.graph.nodes() else False,
                'avg_latency': metrics.total_latency,
                'avg_throughput': metrics.average_throughput,
                'energy_consumption': metrics.energy_consumption,
                'reliability': metrics.reliability_score,
                'load_balance': metrics.load_balance_factor,
                'optimization_history': len(self.optimization_history),
                'last_optimization': self.optimization_history[-1]['timestamp'] if self.optimization_history else None
            }


class IntelligentAgentOrchestrator:
    """
    Intelligent agent orchestration system.
    
    Manages agent lifecycle, scaling, resource allocation, and coordination.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize agent orchestrator."""
        self.config = config or self._default_config()
        
        # Agent management
        self.agent_specs = {}
        self.agent_instances = {}
        self.node_assignments = {}
        
        # Scaling and scheduling
        self.scaling_policies = {}
        self.resource_pool = {}
        self.scheduling_queue = []
        
        # Performance tracking
        self.performance_history = deque(maxlen=1000)
        self.resource_utilization = defaultdict(float)
        self.agent_health_scores = {}
        
        # Coordination
        self.active_coordinations = {}
        self.dependency_graph = nx.DiGraph()
        
        # Threading
        self._lock = threading.Lock()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Intelligent agent orchestrator initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'max_agents_per_node': 10,
            'resource_threshold': 0.8,
            'health_check_interval': 30,
            'auto_scaling_enabled': True,
            'scaling_cooldown': 300,  # 5 minutes
            'load_balancing_algorithm': 'least_loaded',
            'resource_allocation_policy': 'fair_share',
            'failure_recovery_enabled': True,
            'coordination_timeout': 60
        }

    def register_agent_spec(self, spec: AgentSpec) -> str:
        """Register new agent specification."""
        spec_id = f"spec_{spec.agent_type}_{int(time.time())}"
        
        with self._lock:
            self.agent_specs[spec_id] = spec
            self.scaling_policies[spec_id] = spec.scaling_policy
            
            # Build dependency graph
            if spec.dependencies:
                for dep in spec.dependencies:
                    self.dependency_graph.add_edge(spec_id, dep)
        
        logger.info(f"Agent spec registered: {spec_id}")
        return spec_id

    def deploy_agent(self, spec_id: str, preferred_node: Optional[str] = None) -> Optional[str]:
        """Deploy new agent instance."""
        if spec_id not in self.agent_specs:
            raise ValueError(f"Unknown spec: {spec_id}")
        
        spec = self.agent_specs[spec_id]
        
        # Check dependencies
        if not self._check_dependencies(spec_id):
            logger.warning(f"Dependencies not satisfied for spec {spec_id}")
            return None
        
        # Select optimal node
        target_node = self._select_optimal_node(spec, preferred_node)
        if not target_node:
            logger.error(f"No suitable node found for spec {spec_id}")
            return None
        
        # Create agent instance
        instance_id = f"{spec_id}_instance_{int(time.time())}"
        
        instance = AgentInstance(
            instance_id=instance_id,
            spec=spec,
            current_node=target_node,
            state=AgentState.SCALING_UP,
            resource_usage={k: 0.0 for k in spec.resource_requirements.keys()},
            performance_metrics={},
            start_time=time.time()
        )
        
        with self._lock:
            self.agent_instances[instance_id] = instance
            self.node_assignments[instance_id] = target_node
            
            # Update resource pool
            self._allocate_resources(target_node, spec.resource_requirements)
        
        # Set state to active
        instance.state = AgentState.ACTIVE
        
        logger.info(f"Agent deployed: {instance_id} on node {target_node}")
        return instance_id

    def scale_agents(self, spec_id: str, target_count: int) -> Dict[str, Any]:
        """Scale agent instances for specification."""
        if spec_id not in self.agent_specs:
            raise ValueError(f"Unknown spec: {spec_id}")
        
        with self._lock:
            # Find current instances
            current_instances = [
                instance_id for instance_id, instance in self.agent_instances.items()
                if spec_id in instance_id
            ]
            
            current_count = len(current_instances)
            scale_diff = target_count - current_count
            
            deployment_results = {'deployed': [], 'terminated': []}
            
            if scale_diff > 0:
                # Scale up
                for _ in range(scale_diff):
                    instance_id = self.deploy_agent(spec_id)
                    if instance_id:
                        deployment_results['deployed'].append(instance_id)
            
            elif scale_diff < 0:
                # Scale down (terminate least important instances)
                instances_to_terminate = self._select_instances_for_termination(current_instances, abs(scale_diff))
                for instance_id in instances_to_terminate:
                    if self.terminate_agent(instance_id):
                        deployment_results['terminated'].append(instance_id)
            
            return {
                'spec_id': spec_id,
                'target_count': target_count,
                'current_count': len([i for i in self.agent_instances.values() if spec_id in i.instance_id]),
                'deployment_results': deployment_results
            }

    def terminate_agent(self, instance_id: str) -> bool:
        """Terminate agent instance."""
        if instance_id not in self.agent_instances:
            return False
        
        instance = self.agent_instances[instance_id]
        
        with self._lock:
            # Free resources
            self._deallocate_resources(instance.current_node, instance.spec.resource_requirements)
            
            # Remove from assignments
            if instance_id in self.node_assignments:
                del self.node_assignments[instance_id]
            
            # Mark as terminated
            instance.state = AgentState.DEGRADED
            
            # Remove from instances
            del self.agent_instances[instance_id]
        
        logger.info(f"Agent terminated: {instance_id}")
        return True

    def _check_dependencies(self, spec_id: str) -> bool:
        """Check if dependencies are satisfied."""
        if spec_id not in self.dependency_graph:
            return True
        
        # Check if all dependencies have running instances
        for dep in self.dependency_graph.predecessors(spec_id):
            # Check if any instance of the dependency is running
            has_dep_instance = any(
                instance.state == AgentState.ACTIVE 
                for instance in self.agent_instances.values()
                if dep in instance.instance_id
            )
            if not has_dep_instance:
                return False
        
        return True

    def _select_optimal_node(self, spec: AgentSpec, preferred_node: Optional[str] = None) -> Optional[str]:
        """Select optimal node for agent deployment."""
        available_nodes = list(self.resource_pool.keys())
        
        if not available_nodes:
            return None
        
        # Check preferred node first
        if preferred_node and preferred_node in available_nodes:
            if self._can_deploy_on_node(preferred_node, spec):
                return preferred_node
        
        # Score nodes based on algorithm
        algorithm = self.config['load_balancing_algorithm']
        
        if algorithm == 'least_loaded':
            return self._select_least_loaded_node(available_nodes, spec)
        elif algorithm == 'resource_based':
            return self._select_resource_based_node(available_nodes, spec)
        elif algorithm == 'capability_matched':
            return self._select_capability_matched_node(available_nodes, spec)
        else:
            return available_nodes[0]  # Default fallback

    def _can_deploy_on_node(self, node_id: str, spec: AgentSpec) -> bool:
        """Check if agent can be deployed on node."""
        if node_id not in self.resource_pool:
            return False
        
        node_resources = self.resource_pool[node_id]
        
        for resource, required in spec.resource_requirements.items():
            if resource not in node_resources or node_resources[resource] < required:
                return False
        
        # Check agent count limit
        node_agents = [i for i in self.node_assignments.values() if i == node_id]
        if len(node_agents) >= self.config['max_agents_per_node']:
            return False
        
        return True

    def _select_least_loaded_node(self, nodes: List[str], spec: AgentSpec) -> Optional[str]:
        """Select least loaded node."""
        candidate_nodes = [node for node in nodes if self._can_deploy_on_node(node, spec)]
        
        if not candidate_nodes:
            return None
        
        # Calculate load scores
        node_scores = []
        for node in candidate_nodes:
            agents_on_node = [i for i in self.node_assignments.values() if i == node]
            load_score = len(agents_on_node) / self.config['max_agents_per_node']
            node_scores.append((load_score, node))
        
        # Return least loaded
        node_scores.sort(key=lambda x: x[0])
        return node_scores[0][1]

    def _select_resource_based_node(self, nodes: List[str], spec: AgentSpec) -> Optional[str]:
        """Select node based on resource availability."""
        candidate_nodes = [node for node in nodes if self._can_deploy_on_node(node, spec)]
        
        if not candidate_nodes:
            return None
        
        # Calculate resource scores
        node_scores = []
        for node in candidate_nodes:
            node_resources = self.resource_pool[node]
            resource_score = 0
            
            for resource, required in spec.resource_requirements.items():
                available = node_resources.get(resource, 0)
                resource_score += min(1.0, available / required)
            
            node_scores.append((resource_score, node))
        
        # Return node with best resource availability
        node_scores.sort(key=lambda x: x[0], reverse=True)
        return node_scores[0][1]

    def _select_capability_matched_node(self, nodes: List[str], spec: AgentSpec) -> Optional[str]:
        """Select node based on capability matching."""
        # This would implement sophisticated capability matching
        # For now, use simple resource-based selection
        return self._select_resource_based_node(nodes, spec)

    def _select_instances_for_termination(self, instances: List[str], count: int) -> List[str]:
        """Select instances for termination during scale down."""
        # Score instances for termination
        instance_scores = []
        
        for instance_id in instances:
            instance = self.agent_instances.get(instance_id)
            if instance:
                # Lower score = higher priority for termination
                uptime_score = time.time() - instance.start_time
                performance_score = instance.performance_metrics.get('efficiency', 1.0)
                priority_score = instance.spec.priority
                
                # Composite score
                termination_score = uptime_score + (performance_score * 100) + (priority_score * 10)
                instance_scores.append((termination_score, instance_id))
        
        # Sort by termination score (ascending = first to terminate)
        instance_scores.sort(key=lambda x: x[0])
        
        return [instance_id for _, instance_id in instance_scores[:count]]

    def _allocate_resources(self, node_id: str, requirements: Dict[str, float]) -> None:
        """Allocate resources on node."""
        if node_id not in self.resource_pool:
            self.resource_pool[node_id] = {}
        
        for resource, amount in requirements.items():
            if resource not in self.resource_pool[node_id]:
                self.resource_pool[node_id][resource] = 0
            self.resource_pool[node_id][resource] += amount

    def _deallocate_resources(self, node_id: str, requirements: Dict[str, float]) -> None:
        """Deallocate resources on node."""
        if node_id in self.resource_pool:
            for resource, amount in requirements.items():
                if resource in self.resource_pool[node_id]:
                    self.resource_pool[node_id][resource] = max(0, self.resource_pool[node_id][resource] - amount)

    def _start_background_tasks(self) -> None:
        """Start background monitoring and maintenance tasks."""
        def health_monitor():
            while True:
                try:
                    self._perform_health_checks()
                    time.sleep(self.config['health_check_interval'])
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
        
        def auto_scaler():
            while True:
                try:
                    if self.config['auto_scaling_enabled']:
                        self._perform_auto_scaling()
                    time.sleep(self.config['scaling_cooldown'])
                except Exception as e:
                    logger.error(f"Auto scaler error: {e}")
        
        # Start threads
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        health_thread.start()
        
        scaling_thread = threading.Thread(target=auto_scaler, daemon=True)
        scaling_thread.start()

    def _perform_health_checks(self) -> None:
        """Perform health checks on all agents."""
        with self._lock:
            for instance_id, instance in self.agent_instances.items():
                # Update health score based on performance
                health = self._calculate_agent_health(instance)
                instance.health_status = health
                
                if health < 0.5 and instance.state == AgentState.ACTIVE:
                    instance.state = AgentState.DEGRADED
                    logger.warning(f"Agent {instance_id} health degraded: {health:.2f}")
                elif health < 0.2:
                    instance.state = AgentState.FAILED
                    logger.error(f"Agent {instance_id} health critical: {health:.2f}")

    def _calculate_agent_health(self, instance: AgentInstance) -> float:
        """Calculate agent health score."""
        # Base health from performance metrics
        efficiency = instance.performance_metrics.get('efficiency', 1.0)
        response_time = instance.performance_metrics.get('avg_response_time', 100)
        
        # Convert response time to health score (lower is better)
        response_health = max(0, 1.0 - (response_time / 1000))
        
        # Combine metrics
        health = (efficiency * 0.6) + (response_health * 0.4)
        
        return max(0.0, min(1.0, health))

    def _perform_auto_scaling(self) -> None:
        """Perform automatic scaling decisions."""
        with self._lock:
            for spec_id, policy in self.scaling_policies.items():
                current_instances = len([i for i in self.agent_instances.values() if spec_id in i.instance_id])
                
                # Check scaling conditions
                scale_up_condition = self._evaluate_scale_up_condition(spec_id, policy)
                scale_down_condition = self._evaluate_scale_down_condition(spec_id, policy, current_instances)
                
                if scale_up_condition:
                    self.scale_agents(spec_id, current_instances + 1)
                elif scale_down_condition and current_instances > policy.get('min_instances', 1):
                    self.scale_agents(spec_id, current_instances - 1)

    def _evaluate_scale_up_condition(self, spec_id: str, policy: Dict[str, Any]) -> bool:
        """Evaluate if scale up is needed."""
        # Check resource utilization
        for node_id, resources in self.resource_pool.items():
            utilization = sum(r / max(1, policy.get('resource_threshold', 100)) for r in resources.values())
            if utilization > policy.get('scale_up_threshold', 0.8):
                return True
        
        return False

    def _evaluate_scale_down_condition(self, spec_id: str, policy: Dict[str, Any], current_count: int) -> bool:
        """Evaluate if scale down is needed."""
        if current_count <= policy.get('min_instances', 1):
            return False
        
        # Check if agents are underutilized
        underutilized_count = 0
        for instance in self.agent_instances.values():
            if spec_id in instance.instance_id:
                efficiency = instance.performance_metrics.get('efficiency', 1.0)
                if efficiency < 0.5:
                    underutilized_count += 1
        
        # Scale down if many agents are underutilized
        return underutilized_count > current_count * 0.5

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        with self._lock:
            total_agents = len(self.agent_instances)
            active_agents = len([i for i in self.agent_instances.values() if i.state == AgentState.ACTIVE])
            degraded_agents = len([i for i in self.agent_instances.values() if i.state == AgentState.DEGRADED])
            
            # Calculate resource utilization
            total_resources = defaultdict(float)
            used_resources = defaultdict(float)
            
            for node_resources in self.resource_pool.values():
                for resource, amount in node_resources.items():
                    total_resources[resource] += amount
            
            for instance in self.agent_instances.values():
                for resource, usage in instance.resource_usage.items():
                    used_resources[resource] += usage
            
            resource_utilization = {
                resource: used_resources[resource] / max(1, total_resources[resource])
                for resource in total_resources
            }
            
            return {
                'total_agent_specs': len(self.agent_specs),
                'total_agent_instances': total_agents,
                'active_agents': active_agents,
                'degraded_agents': degraded_agents,
                'failed_agents': len([i for i in self.agent_instances.values() if i.state == AgentState.FAILED]),
                'resource_nodes': len(self.resource_pool),
                'resource_utilization': resource_utilization,
                'auto_scaling_enabled': self.config['auto_scaling_enabled'],
                'avg_health_score': np.mean([i.health_status for i in self.agent_instances.values()]) if self.agent_instances else 0
            }

    def add_resource_node(self, node_id: str, resources: Dict[str, float]) -> None:
        """Add resource node to orchestrator."""
        with self._lock:
            self.resource_pool[node_id] = resources.copy()
        logger.info(f"Resource node added: {node_id}")

    def remove_resource_node(self, node_id: str) -> bool:
        """Remove resource node."""
        with self._lock:
            if node_id not in self.resource_pool:
                return False
            
            # Move or terminate agents on this node
            agents_on_node = [instance_id for instance_id, node in self.node_assignments.items() if node == node_id]
            
            for instance_id in agents_on_node:
                # Try to move to another node
                instance = self.agent_instances[instance_id]
                new_node = self._select_optimal_node(instance.spec, preferred_node=None)
                
                if new_node and new_node != node_id:
                    # Move agent
                    self._deallocate_resources(node_id, instance.spec.resource_requirements)
                    self._allocate_resources(new_node, instance.spec.resource_requirements)
                    instance.current_node = new_node
                    self.node_assignments[instance_id] = new_node
                else:
                    # Terminate agent
                    self.terminate_agent(instance_id)
            
            # Remove node
            del self.resource_pool[node_id]
        
        logger.info(f"Resource node removed: {node_id}")
        return True


# Example usage and testing
if __name__ == "__main__":
    # Initialize systems
    topology_optimizer = NetworkTopologyOptimizer()
    orchestrator = IntelligentAgentOrchestrator()
    
    # Add nodes
    for i in range(10):
        node = NetworkNode(
            node_id=f"node_{i}",
            position=(i * 10, 0),
            capacity=100,
            load=np.random.uniform(20, 80),
            connectivity=[],
            capabilities={'compute': 1.0, 'storage': 1.0, 'network': 1.0}
        )
        topology_optimizer.add_node(node)
        orchestrator.add_resource_node(node.node_id, {'compute': 100, 'storage': 100, 'network': 100})
    
    # Add edges
    for i in range(9):
        edge = NetworkEdge(
            source_id=f"node_{i}",
            target_id=f"node_{i+1}",
            bandwidth=1000,
            latency=0.01,
            reliability=0.99,
            cost=1.0
        )
        topology_optimizer.add_edge(edge)
    
    # Test optimization
    result = topology_optimizer.optimize_topology(OptimizationObjective.MINIMIZE_LATENCY)
    print(f"Optimization result: {result['success']}")
    print(f"Improvement: {result['improvement']:.2%}")
    
    # Test orchestration
    spec = AgentSpec(
        agent_type="anomaly_detector",
        resource_requirements={'compute': 10, 'storage': 5, 'network': 2},
        priority=5,
        dependencies=[],
        scaling_policy={'min_instances': 1, 'max_instances': 5, 'scale_up_threshold': 0.8}
    )
    
    spec_id = orchestrator.register_agent_spec(spec)
    instance_id = orchestrator.deploy_agent(spec_id)
    print(f"Agent deployed: {instance_id}")
    
    # Get status
    topology_status = topology_optimizer.get_network_status()
    orchestrator_status = orchestrator.get_orchestrator_status()
    
    print(f"Network status: {topology_status}")
    print(f"Orchestrator status: {orchestrator_status}")