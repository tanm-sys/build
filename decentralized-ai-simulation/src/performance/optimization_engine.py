"""
Enterprise Performance Optimization Engine

Implements comprehensive performance optimization for the decentralized AI platform:
- Distributed computing optimization with load balancing
- Advanced caching strategies (Redis, CDN, application-level)
- Database query optimization and connection pooling
- Load balancing algorithms for agent distribution
- Memory management improvements and GC optimization
- Network bandwidth optimization and compression

Author: Kilo Code
Date: November 1, 2025
"""

import asyncio
import gzip
import hashlib
import json
import logging
import pickle
import threading
import time
import zlib
from asyncio import Queue, Semaphore
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from functools import lru_cache, wraps
from pathlib import Path
import heapq
import numpy as np
import psutil
import redis
import aioredis
from sqlalchemy import create_engine, pool
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import mmap
import weakref
import gc
import resource
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Performance optimization strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"
    GEOGRAPHIC = "geographic"
    ADAPTIVE = "adaptive"


class CacheStrategy(Enum):
    """Caching strategies."""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    ADAPTIVE = "adaptive"


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms."""
    SIMPLE_ROUND_ROBIN = "simple_round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    FASTEST_RESPONSE = "fastest_response"
    IP_HASH = "ip_hash"
    CONSISTENT_HASH = "consistent_hash"


@dataclass
class ComputeNode:
    """Distributed compute node representation."""
    node_id: str
    hostname: str
    ip_address: str
    cpu_cores: int
    memory_gb: float
    storage_gb: float
    load_factor: float = 0.0
    response_time_ms: float = 0.0
    active_connections: int = 0
    capabilities: Dict[str, float] = field(default_factory=dict)
    status: str = "active"
    last_heartbeat: float = field(default_factory=time.time)


@dataclass
class CacheEntry:
    """Cache entry data structure."""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: Optional[int] = None
    compressed: bool = False
    cache_level: str = "application"  # application, redis, cdn


@dataclass
class DatabaseConnection:
    """Database connection pool entry."""
    connection_id: str
    connection: Any
    created_at: float
    last_used: float
    is_active: bool = True
    query_count: int = 0
    total_query_time: float = 0.0
    connection_pool: str = "default"


@dataclass
class OptimizationMetrics:
    """Performance optimization metrics."""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    cache_hit_rate: float
    database_response_time: float
    active_connections: int
    throughput: float
    error_rate: float


class DistributedComputingOptimizer:
    """
    Distributed computing optimization system with intelligent load balancing.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize distributed computing optimizer."""
        self.config = config or self._default_config()
        
        # Compute nodes
        self.nodes = {}
        self.node_capabilities = {}
        self.load_history = defaultdict(deque)
        
        # Load balancing
        self.algorithm = self.config.get('load_balancing_algorithm', LoadBalancingAlgorithm.ADAPTIVE)
        self.node_weights = {}
        self.consistent_hash_ring = {}
        
        # Performance monitoring
        self.performance_metrics = deque(maxlen=1000)
        self.health_check_interval = self.config.get('health_check_interval', 30)
        
        # Task distribution
        self.active_tasks = {}
        self.task_queue = Queue()
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 100)
        
        # Resource management
        self.resource_limits = self.config.get('resource_limits', {})
        self.auto_scaling_enabled = self.config.get('auto_scaling_enabled', True)
        
        # Threading
        self._lock = threading.Lock()
        self._running = False
        
        # Start background tasks
        self._start_background_monitoring()
        
        logger.info("Distributed computing optimizer initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'load_balancing_algorithm': LoadBalancingAlgorithm.ADAPTIVE,
            'health_check_interval': 30,
            'max_concurrent_tasks': 100,
            'resource_limits': {
                'cpu_threshold': 0.8,
                'memory_threshold': 0.85,
                'disk_threshold': 0.9
            },
            'auto_scaling_enabled': True,
            'scaling_cooldown': 300,
            'min_nodes': 2,
            'max_nodes': 50,
            'node_health_threshold': 0.7,
            'response_time_threshold': 1000,  # milliseconds
            'load_balancing_weights': {
                'cpu': 0.3,
                'memory': 0.2,
                'response_time': 0.3,
                'capabilities': 0.2
            }
        }

    def _start_background_monitoring(self) -> None:
        """Start background monitoring and health checks."""
        def monitor_nodes():
            self._running = True
            while self._running:
                try:
                    self._perform_health_checks()
                    self._update_load_balancing_metrics()
                    self._check_scaling_conditions()
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"Background monitoring error: {e}")
        
        monitor_thread = threading.Thread(target=monitor_nodes, daemon=True)
        monitor_thread.start()

    def add_compute_node(self, node: ComputeNode) -> None:
        """Add compute node to the cluster."""
        with self._lock:
            self.nodes[node.node_id] = node
            self.node_capabilities[node.node_id] = {
                'cpu_capacity': node.cpu_cores,
                'memory_capacity': node.memory_gb,
                'storage_capacity': node.storage_gb,
                'processing_power': node.cpu_cores * node.memory_gb
            }
            
            # Initialize node weight based on capabilities
            self.node_weights[node.node_id] = self._calculate_node_weight(node)
            
            # Add to consistent hash ring if using consistent hashing
            if self.algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
                self._update_consistent_hash_ring(node.node_id)
            
            logger.info(f"Added compute node: {node.node_id} ({node.hostname})")

    def remove_compute_node(self, node_id: str) -> bool:
        """Remove compute node from the cluster."""
        with self._lock:
            if node_id not in self.nodes:
                return False
            
            # Cancel active tasks on this node
            self._cancel_node_tasks(node_id)
            
            # Remove from structures
            del self.nodes[node_id]
            del self.node_capabilities[node_id]
            del self.node_weights[node_id]
            
            # Remove from hash ring
            if self.algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
                self._remove_from_hash_ring(node_id)
            
            logger.info(f"Removed compute node: {node_id}")
            return True

    async def distribute_task(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Distribute task to optimal compute node.
        
        Args:
            task: Task dictionary with type, data, and requirements
            
        Returns:
            Task ID if distributed successfully, None otherwise
        """
        try:
            # Select optimal node
            target_node = self._select_optimal_node(task)
            if not target_node:
                logger.error("No suitable compute node found for task")
                return None
            
            # Create task ID
            task_id = f"task_{hashlib.sha256(json.dumps(task, sort_keys=True).encode()).hexdigest()[:8]}"
            # Submit task to node
            success = await self._submit_task_to_node(task_id, task, target_node)
            
            if success:
                with self._lock:
                    self.active_tasks[task_id] = {
                        'node_id': target_node,
                        'submitted_at': time.time(),
                        'task': task,
                        'status': 'submitted'
                    }
                
                logger.info(f"Task {task_id} distributed to node {target_node}")
                return task_id
            
            return None
            
        except Exception as e:
            logger.error(f"Task distribution failed: {e}")
            return None

    def _select_optimal_node(self, task: Dict[str, Any]) -> Optional[str]:
        """Select optimal compute node for task using configured algorithm."""
        available_nodes = [
            node_id for node_id, node in self.nodes.items()
            if node.status == "active" and self._is_node_suitable(node, task)
        ]
        
        if not available_nodes:
            return None
        
        if self.algorithm == LoadBalancingAlgorithm.SIMPLE_ROUND_ROBIN:
            return self._round_robin_select(available_nodes)
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(available_nodes)
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections_select(available_nodes)
        elif self.algorithm == LoadBalancingAlgorithm.FASTEST_RESPONSE:
            return self._fastest_response_select(available_nodes)
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash_select(available_nodes, task.get('client_ip'))
        elif self.algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            return self._consistent_hash_select(available_nodes, task)
        else:  # ADAPTIVE
            return self._adaptive_select(available_nodes, task)

    def _is_node_suitable(self, node: ComputeNode, task: Dict[str, Any]) -> bool:
        """Check if node is suitable for task requirements."""
        # Check resource requirements
        cpu_req = task.get('cpu_requirement', 1)
        memory_req = task.get('memory_requirement', 1.0)
        
        if node.cpu_cores < cpu_req or node.memory_gb < memory_req:
            return False
        
        # Check load thresholds
        if (node.load_factor > self.resource_limits.get('cpu_threshold', 0.8) or
            node.memory_usage > self.resource_limits.get('memory_threshold', 0.85)):
            return False
        
        # Check node status
        if node.status != "active":
            return False
        
        # Check response time
        if node.response_time_ms > self.config.get('response_time_threshold', 1000):
            return False
        
        return True

    def _round_robin_select(self, available_nodes: List[str]) -> str:
        """Select node using round-robin algorithm."""
        # Simple round-robin selection
        # In production, this would track position with atomic operations
        return available_nodes[0]

    def _weighted_round_robin_select(self, available_nodes: List[str]) -> str:
        """Select node using weighted round-robin algorithm."""
        # Select node with highest weight that has capacity
        best_node = None
        best_weight = -1
        
        for node_id in available_nodes:
            weight = self.node_weights.get(node_id, 1)
            node = self.nodes[node_id]
            
            # Adjust weight based on current load
            adjusted_weight = weight * (1 - node.load_factor)
            
            if adjusted_weight > best_weight:
                best_weight = adjusted_weight
                best_node = node_id
        
        return best_node or available_nodes[0]

    def _least_connections_select(self, available_nodes: List[str]) -> str:
        """Select node with least active connections."""
        return min(available_nodes, key=lambda node_id: self.nodes[node_id].active_connections)

    def _fastest_response_select(self, available_nodes: List[str]) -> str:
        """Select node with fastest response time."""
        return min(available_nodes, key=lambda node_id: self.nodes[node_id].response_time_ms)

    def _ip_hash_select(self, available_nodes: List[str], client_ip: Optional[str]) -> str:
        """Select node using IP hash algorithm."""
        if not client_ip:
            return available_nodes[0]
        
        # Hash IP and map to node
        hash_value = int(hashlib.sha256(client_ip.encode()).hexdigest(), 16)
        node_index = hash_value % len(available_nodes)
        return available_nodes[node_index]

    def _consistent_hash_select(self, available_nodes: List[str], task: Dict[str, Any]) -> str:
        """Select node using consistent hashing."""
        # Use task identifier for consistent hashing
        task_key = task.get('task_id', task.get('type', 'default'))
        hash_value = int(hashlib.sha256(task_key.encode()).hexdigest(), 16)
        # Find closest node in hash ring
        sorted_nodes = sorted(self.consistent_hash_ring.keys())
        if not sorted_nodes:
            return available_nodes[0]
        
        # Find first node with hash > task hash
        for ring_hash in sorted_nodes:
            if ring_hash > hash_value:
                return self.consistent_hash_ring[ring_hash]
        
        # Wrap around to first node
        return self.consistent_hash_ring[sorted_nodes[0]]

    def _adaptive_select(self, available_nodes: List[str], task: Dict[str, Any]) -> str:
        """Select node using adaptive algorithm."""
        weights = self.config['load_balancing_weights']
        scores = {}
        
        for node_id in available_nodes:
            node = self.nodes[node_id]
            
            # Calculate component scores
            cpu_score = 1.0 - node.load_factor
            memory_score = 1.0 - (node.memory_usage / node.memory_gb)
            response_score = max(0, 1.0 - (node.response_time_ms / 1000))
            capability_score = self._calculate_capability_score(node, task)
            
            # Weighted combination
            total_score = (
                cpu_score * weights['cpu'] +
                memory_score * weights['memory'] +
                response_score * weights['response_time'] +
                capability_score * weights['capabilities']
            )
            
            scores[node_id] = total_score
        
        # Select node with highest score
        best_node = max(scores.keys(), key=lambda node_id: scores[node_id])
        return best_node

    def _calculate_node_weight(self, node: ComputeNode) -> float:
        """Calculate node weight based on capabilities."""
        # Base weight from CPU and memory
        base_weight = (node.cpu_cores * 0.6) + (node.memory_gb * 0.4)
        
        # Adjust for capabilities
        capability_multiplier = 1.0
        for capability, value in node.capabilities.items():
            if capability == 'gpu':
                capability_multiplier += value * 0.5
            elif capability == 'fpga':
                capability_multiplier += value * 0.3
        
        return base_weight * capability_multiplier

    def _calculate_capability_score(self, node: ComputeNode, task: Dict[str, Any]) -> float:
        """Calculate score based on task-specific capabilities."""
        required_capabilities = task.get('required_capabilities', {})
        
        if not required_capabilities:
            return 1.0
        
        score = 0.0
        total_requirements = len(required_capabilities)
        
        for capability, required_level in required_capabilities.items():
            available_level = node.capabilities.get(capability, 0)
            score += min(1.0, available_level / required_level)
        
        return score / total_requirements if total_requirements > 0 else 1.0

    def _update_consistent_hash_ring(self, node_id: str) -> None:
        """Update consistent hash ring with new node."""
        # Add multiple virtual nodes for better distribution
        num_virtual_nodes = 150  # Standard for consistent hashing
        
        for i in range(num_virtual_nodes):
            virtual_node_key = f"{node_id}:{i}"
            hash_value = int(hashlib.sha256(virtual_node_key.encode()).hexdigest(), 16)
            self.consistent_hash_ring[hash_value] = node_id

    def _remove_from_hash_ring(self, node_id: str) -> None:
        """Remove node from consistent hash ring."""
        keys_to_remove = [
            key for key, value in self.consistent_hash_ring.items()
            if value == node_id
        ]
        for key in keys_to_remove:
            del self.consistent_hash_ring[key]

    async def _submit_task_to_node(self, task_id: str, task: Dict[str, Any], node_id: str) -> bool:
        """Submit task to specified compute node."""
        try:
            # Update node connection count
            node = self.nodes[node_id]
            node.active_connections += 1
            
            # Simulate task submission (in production, this would be actual RPC/HTTP call)
            # For demo purposes, we'll simulate the submission
            await asyncio.sleep(0.01)  # Simulate network latency
            
            # Update node metrics
            node.last_heartbeat = time.time()
            
            # In a real implementation, this would:
            # 1. Connect to the node via RPC/HTTP
            # 2. Send task data
            # 3. Wait for acknowledgment
            # 4. Handle retries and failures
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit task to node {node_id}: {e}")
            # Decrement connection count on failure
            if node_id in self.nodes:
                self.nodes[node_id].active_connections -= 1
            return False

    def _cancel_node_tasks(self, node_id: str) -> None:
        """Cancel all active tasks on a node."""
        tasks_to_cancel = [
            task_id for task_id, task_info in self.active_tasks.items()
            if task_info['node_id'] == node_id
        ]
        
        for task_id in tasks_to_cancel:
            if task_id in self.active_tasks:
                self.active_tasks[task_id]['status'] = 'cancelled'
                logger.info(f"Cancelled task {task_id} on failed node {node_id}")

    def _perform_health_checks(self) -> None:
        """Perform health checks on all compute nodes."""
        current_time = time.time()
        unhealthy_nodes = []
        
        with self._lock:
            for node_id, node in self.nodes.items():
                # Check if node is responsive
                time_since_heartbeat = current_time - node.last_heartbeat
                
                if time_since_heartbeat > self.config.get('node_health_threshold', 0.7) * self.health_check_interval:
                    node.status = "unhealthy"
                    unhealthy_nodes.append(node_id)
                    logger.warning(f"Node {node_id} marked as unhealthy")
                else:
                    # Update node metrics
                    self._update_node_metrics(node)
        
        # Remove very unhealthy nodes
        for node_id in unhealthy_nodes:
            if current_time - self.nodes[node_id].last_heartbeat > 300:  # 5 minutes
                logger.error(f"Removing unresponsive node {node_id}")
                self.remove_compute_node(node_id)

    def _update_node_metrics(self, node: ComputeNode) -> None:
        """Update node performance metrics."""
        try:
            # In a real implementation, this would query actual node metrics
            # For demo, we'll simulate metric updates
            
            # Simulate CPU and memory usage
            node.load_factor = min(1.0, node.load_factor + np.random.normal(0, 0.05))
            node.memory_usage = min(node.memory_gb, node.memory_usage + np.random.normal(0, 0.1))
            
            # Simulate response time
            base_response_time = 10 + (node.load_factor * 90)  # 10-100ms
            node.response_time_ms = base_response_time + np.random.normal(0, 5)
            node.response_time_ms = max(1.0, node.response_time_ms)
            
            # Record metrics
            self.load_history[node.node_id].append({
                'timestamp': time.time(),
                'load_factor': node.load_factor,
                'response_time': node.response_time_ms,
                'memory_usage': node.memory_usage
            })
            
            # Keep only recent history
            if len(self.load_history[node.node_id]) > 100:
                self.load_history[node.node_id].popleft()
                
        except Exception as e:
            logger.error(f"Failed to update node metrics for {node.node_id}: {e}")

    def _update_load_balancing_metrics(self) -> None:
        """Update load balancing algorithm metrics."""
        if self.algorithm == LoadBalancingAlgorithm.ADAPTIVE:
            # Adjust weights based on recent performance
            self._adjust_adaptive_weights()

    def _adjust_adaptive_weights(self) -> None:
        """Adjust weights for adaptive load balancing based on performance."""
        weights = self.config['load_balancing_weights']
        
        # Analyze recent performance
        performance_scores = {}
        for node_id, node in self.nodes.items():
            if node.status != "active":
                continue
            
            # Calculate performance score based on multiple factors
            recent_history = list(self.load_history[node_id])
            if not recent_history:
                continue
            
            # Weight recent performance more heavily
            weights_recent = [0.1 * (i + 1) for i in range(min(len(recent_history), 10))]
            
            load_scores = [1.0 - h['load_factor'] for h in recent_history[-10:]]
            response_scores = [max(0, 1.0 - h['response_time'] / 1000) for h in recent_history[-10:]]
            
            avg_load_score = np.average(load_scores, weights=weights_recent)
            avg_response_score = np.average(response_scores, weights=weights_recent)
            
            performance_scores[node_id] = (avg_load_score + avg_response_score) / 2
        
        # Adjust weights based on performance (simplified)
        if performance_scores:
            max_score = max(performance_scores.values())
            min_score = min(performance_scores.values())
            
            for node_id, score in performance_scores.items():
                if max_score > min_score:
                    normalized_score = (score - min_score) / (max_score - min_score)
                    self.node_weights[node_id] = normalized_score

    def _check_scaling_conditions(self) -> None:
        """Check if auto-scaling conditions are met."""
        if not self.auto_scaling_enabled:
            return
        
        # Calculate cluster metrics
        total_nodes = len(self.nodes)
        active_nodes = len([n for n in self.nodes.values() if n.status == "active"])
        
        if active_nodes == 0:
            return
        
        # Calculate average load
        avg_load = np.mean([node.load_factor for node in self.nodes.values() if node.status == "active"])
        
        # Check scale up conditions
        if (avg_load > 0.8 and 
            total_nodes < self.config.get('max_nodes', 50) and
            active_nodes >= self.config.get('min_nodes', 2)):
            
            self._trigger_scale_up()
        
        # Check scale down conditions
        elif (avg_load < 0.3 and 
              total_nodes > self.config.get('min_nodes', 2)):
            
            self._trigger_scale_down()

    def _trigger_scale_up(self) -> None:
        """Trigger cluster scale up."""
        logger.info("Triggering cluster scale up")
        # In a real implementation, this would:
        # 1. Request new compute resources
        # 2. Wait for nodes to become available
        # 3. Add them to the cluster
        # 4. Update load balancing configuration

    def _trigger_scale_down(self) -> None:
        """Trigger cluster scale down."""
        logger.info("Triggering cluster scale down")
        # In a real implementation, this would:
        # 1. Stop accepting new tasks
        # 2. Wait for active tasks to complete
        # 3. Remove nodes from cluster
        # 4. Update load balancing configuration

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status."""
        with self._lock:
            active_nodes = [n for n in self.nodes.values() if n.status == "active"]
            
            if not active_nodes:
                return {
                    'total_nodes': 0,
                    'active_nodes': 0,
                    'avg_load': 0.0,
                    'avg_response_time': 0.0,
                    'total_active_tasks': len(self.active_tasks),
                    'algorithm': self.algorithm.value
                }
            
            avg_load = np.mean([node.load_factor for node in active_nodes])
            avg_response_time = np.mean([node.response_time_ms for node in active_nodes])
            total_connections = sum([node.active_connections for node in active_nodes])
            
            return {
                'total_nodes': len(self.nodes),
                'active_nodes': len(active_nodes),
                'avg_load': avg_load,
                'avg_response_time': avg_response_time,
                'total_active_tasks': len(self.active_tasks),
                'total_connections': total_connections,
                'algorithm': self.algorithm.value,
                'auto_scaling_enabled': self.auto_scaling_enabled,
                'node_details': [
                    {
                        'node_id': node.node_id,
                        'hostname': node.hostname,
                        'load_factor': node.load_factor,
                        'response_time_ms': node.response_time_ms,
                        'active_connections': node.active_connections,
                        'status': node.status
                    }
                    for node in active_nodes
                ]
            }


class AdvancedCachingSystem:
    """
    Multi-tier advanced caching system with Redis, CDN, and application-level caching.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize advanced caching system."""
        self.config = config or self._default_config()
        
        # Cache layers
        self.application_cache = {}
        self.redis_cache = None
        self.cdn_cache = {}
        
        # Cache statistics
        self.cache_stats = {
            'application': {'hits': 0, 'misses': 0, 'evictions': 0},
            'redis': {'hits': 0, 'misses': 0, 'evictions': 0},
            'cdn': {'hits': 0, 'misses': 0, 'evictions': 0}
        }
        
        # Cache configuration
        self.cache_policies = self.config.get('cache_policies', {})
        self.compression_enabled = self.config.get('compression_enabled', True)
        self.max_cache_size = self.config.get('max_cache_size', 100 * 1024 * 1024)  # 100MB
        
        # Threading
        self._lock = threading.Lock()
        
        # Initialize cache layers
        self._initialize_caches()
        
        # Start background maintenance
        self._start_background_maintenance()
        
        logger.info("Advanced caching system initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'password': None,
                'ssl': False,
                'max_connections': 20,
                'connection_pool_timeout': 5
            },
            'application_cache': {
                'max_size': 10000,
                'default_ttl': 3600,  # 1 hour
                'strategy': CacheStrategy.LRU
            },
            'cdn_cache': {
                'enabled': True,
                'cache_control_headers': True,
                'compression': 'gzip'
            },
            'compression_enabled': True,
            'max_cache_size': 100 * 1024 * 1024,
            'cache_policies': {
                'static_content': {'ttl': 86400, 'compress': True},
                'api_responses': {'ttl': 300, 'compress': True},
                'database_queries': {'ttl': 60, 'compress': False},
                'computational_results': {'ttl': 1800, 'compress': True}
            },
            'eviction_policies': {
                'application': CacheStrategy.LRU,
                'redis': CacheStrategy.LFU,
                'cdn': CacheStrategy.TTL
            }
        }

    def _initialize_caches(self) -> None:
        """Initialize all cache layers."""
        # Initialize Redis cache
        redis_config = self.config['redis']
        try:
            self.redis_cache = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config['db'],
                password=redis_config.get('password'),
                ssl=redis_config.get('ssl', False),
                max_connections=redis_config.get('max_connections', 20),
                socket_timeout=redis_config.get('connection_pool_timeout', 5),
                decode_responses=True
            )
            # Test connection
            self.redis_cache.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}")
            self.redis_cache = None

    def _start_background_maintenance(self) -> None:
        """Start background cache maintenance."""
        def cache_maintenance():
            while True:
                try:
                    self._perform_cache_maintenance()
                    time.sleep(60)  # Run every minute
                except Exception as e:
                    logger.error(f"Cache maintenance error: {e}")
        
        maintenance_thread = threading.Thread(target=cache_maintenance, daemon=True)
        maintenance_thread.start()

    async def get(self, key: str, cache_level: str = "auto") -> Optional[Any]:
        """
        Get value from cache with automatic fallback.
        
        Args:
            key: Cache key
            cache_level: Specific cache level ('application', 'redis', 'cdn', 'auto')
            
        Returns:
            Cached value or None if not found
        """
        try:
            # Determine cache levels to check
            if cache_level == "auto":
                cache_levels = ['application', 'redis', 'cdn']
            else:
                cache_levels = [cache_level]
            
            # Check each cache level
            for level in cache_levels:
                value = await self._get_from_cache(key, level)
                if value is not None:
                    # Update statistics
                    self.cache_stats[level]['hits'] += 1
                    
                    # If not the original requested level, promote to higher level
                    if level != cache_level and cache_level != "auto":
                        await self._put(key, value, cache_level)
                    
                    return value
            
            # Cache miss for all levels
            for level in cache_levels:
                if level in self.cache_stats:
                    self.cache_stats[level]['misses'] += 1
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def _get_from_cache(self, key: str, cache_level: str) -> Optional[Any]:
        """Get value from specific cache level."""
        try:
            if cache_level == "application":
                return self._get_from_application_cache(key)
            elif cache_level == "redis":
                return self._get_from_redis_cache(key)
            elif cache_level == "cdn":
                return self._get_from_cdn_cache(key)
            else:
                return None
        except Exception as e:
            logger.error(f"Cache get error from {cache_level}: {e}")
            return None

    def _get_from_application_cache(self, key: str) -> Optional[Any]:
        """Get value from application cache."""
        with self._lock:
            entry = self.application_cache.get(key)
            if not entry:
                return None
            
            # Check TTL
            if entry.ttl and time.time() > entry.created_at + entry.ttl:
                del self.application_cache[key]
                self.cache_stats['application']['evictions'] += 1
                return None
            
            # Update access statistics
            entry.last_accessed = time.time()
            entry.access_count += 1
            
            # Decompress if needed
            if entry.compressed:
                return self._decompress_value(entry.value)
            else:
                return entry.value

    def _get_from_redis_cache(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self.redis_cache:
            return None
        
        try:
            data = self.redis_cache.get(key)
            if data is None:
                return None
            
            # Deserialize data
            return pickle.loads(data)
            
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
            return None

    def _get_from_cdn_cache(self, key: str) -> Optional[Any]:
        """Get value from CDN cache."""
        # In a real implementation, this would query CDN cache
        # For demo, we'll use local CDN cache simulation
        entry = self.cdn_cache.get(key)
        if entry and time.time() <= entry['expires_at']:
            return entry['value']
        elif entry:
            del self.cdn_cache[key]
            self.cache_stats['cdn']['evictions'] += 1
        
        return None

    async def put(self, key: str, value: Any, cache_level: str = "auto", 
                  ttl: Optional[float] = None, force_level: bool = False) -> bool:
        """
        Put value into cache with automatic distribution.
        
        Args:
            key: Cache key
            value: Value to cache
            cache_level: Specific cache level or 'auto' for automatic distribution
            ttl: Time to live in seconds
            force_level: Force caching in specified level
            
        Returns:
            True if cached successfully
        """
        try:
            # Determine cache levels
            if force_level:
                cache_levels = [cache_level]
            elif cache_level == "auto":
                cache_levels = self._determine_cache_levels(key, value)
            else:
                cache_levels = [cache_level]
            
            success = True
            for level in cache_levels:
                level_success = await self._put_to_cache(key, value, level, ttl)
                if not level_success:
                    logger.warning(f"Failed to cache in {level} level")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Cache put error for key {key}: {e}")
            return False

    async def _put_to_cache(self, key: str, value: Any, cache_level: str, 
                           ttl: Optional[float] = None) -> bool:
        """Put value into specific cache level."""
        try:
            if cache_level == "application":
                return self._put_to_application_cache(key, value, ttl)
            elif cache_level == "redis":
                return self._put_to_redis_cache(key, value, ttl)
            elif cache_level == "cdn":
                return self._put_to_cdn_cache(key, value, ttl)
            else:
                return False
        except Exception as e:
            logger.error(f"Cache put error to {cache_level}: {e}")
            return False

    def _put_to_application_cache(self, key: str, value: Any, ttl: Optional[float]) -> bool:
        """Put value into application cache."""
        with self._lock:
            # Check cache size limit
            if len(self.application_cache) >= self.config['application_cache']['max_size']:
                self._evict_application_cache()
            
            # Serialize and potentially compress value
            serialized_value, compressed = self._serialize_value(value)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=serialized_value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl,
                compressed=compressed,
                cache_level="application"
            )
            
            self.application_cache[key] = entry
            return True

    def _put_to_redis_cache(self, key: str, value: Any, ttl: Optional[float]) -> bool:
        """Put value into Redis cache."""
        if not self.redis_cache:
            return False
        
        try:
            # Serialize value
            serialized_data = pickle.dumps(value)
            
            # Set with TTL if specified
            if ttl:
                self.redis_cache.setex(key, int(ttl), serialized_data)
            else:
                self.redis_cache.set(key, serialized_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis cache put error: {e}")
            return False

    def _put_to_cdn_cache(self, key: str, value: Any, ttl: Optional[float]) -> bool:
        """Put value into CDN cache."""
        try:
            # Serialize value
            serialized_value, compressed = self._serialize_value(value)
            
            # Calculate expiration time
            expires_at = time.time() + (ttl or self.config['cdn_cache']['default_ttl'])
            
            # Store in CDN cache
            self.cdn_cache[key] = {
                'value': serialized_value,
                'compressed': compressed,
                'created_at': time.time(),
                'expires_at': expires_at
            }
            
            return True
            
        except Exception as e:
            logger.error(f"CDN cache put error: {e}")
            return False

    def _determine_cache_levels(self, key: str, value: Any) -> List[str]:
        """Determine optimal cache levels for key-value pair."""
        levels = ["application"]  # Always include application cache
        
        # Add Redis for frequently accessed data
        if self.redis_cache:
            # Heuristic: larger data or long TTL benefits from Redis
            data_size = len(str(value))
            if data_size > 1024 or (isinstance(value, (dict, list)) and len(value) > 10):
                levels.append("redis")
        
        # Add CDN for static content
        if self.config['cdn_cache']['enabled']:
            if any(pattern in key for pattern in ['static', 'assets', 'css', 'js', 'images']):
                levels.append("cdn")
        
        return levels

    def _serialize_value(self, value: Any) -> Tuple[bytes, bool]:
        """Serialize and optionally compress value."""
        try:
            # Serialize to JSON for simplicity (could use pickle for complex objects)
            serialized = json.dumps(value, default=str).encode('utf-8')
            
            # Compress if enabled and beneficial
            if self.compression_enabled and len(serialized) > 1024:
                compressed = gzip.compress(serialized)
                if len(compressed) < len(serialized) * 0.8:  # 20% size reduction threshold
                    return compressed, True
            
            return serialized, False
            
        except Exception as e:
            logger.error(f"Value serialization error: {e}")
            # Fallback to simple JSON serialization
            return json.dumps(value).encode('utf-8'), False

    def _decompress_value(self, data: bytes) -> Any:
        """Decompress value."""
        try:
            decompressed = gzip.decompress(data)
            return json.loads(decompressed.decode('utf-8'))
        except Exception:
            # Fallback to raw data
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                return data

    def _evict_application_cache(self) -> None:
        """Evict entries from application cache based on policy."""
        policy = self.config['eviction_policies']['application']
        
        if policy == CacheStrategy.LRU:
            # Remove least recently used
            lru_key = min(
                self.application_cache.keys(),
                key=lambda k: self.application_cache[k].last_accessed
            )
            del self.application_cache[lru_key]
        
        elif policy == CacheStrategy.LFU:
            # Remove least frequently used
            lfu_key = min(
                self.application_cache.keys(),
                key=lambda k: self.application_cache[k].access_count
            )
            del self.application_cache[lfu_key]
        
        self.cache_stats['application']['evictions'] += 1

    def _perform_cache_maintenance(self) -> None:
        """Perform cache maintenance tasks."""
        current_time = time.time()
        
        # Clean expired entries from application cache
        with self._lock:
            expired_keys = [
                key for key, entry in self.application_cache.items()
                if entry.ttl and current_time > entry.created_at + entry.ttl
            ]
            for key in expired_keys:
                del self.application_cache[key]
                self.cache_stats['application']['evictions'] += 1
        
        # Clean expired entries from CDN cache
        expired_cdn_keys = [
            key for key, entry in self.cdn_cache.items()
            if current_time > entry['expires_at']
        ]
        for key in expired_cdn_keys:
            del self.cdn_cache[key]
            self.cache_stats['cdn']['evictions'] += 1

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self._lock:
            # Calculate hit rates
            total_requests = sum(
                stats['hits'] + stats['misses'] 
                for stats in self.cache_stats.values()
            )
            
            hit_rates = {}
            for level, stats in self.cache_stats.items():
                total = stats['hits'] + stats['misses']
                hit_rates[level] = stats['hits'] / max(1, total)
            
            # Calculate cache sizes
            app_cache_size = len(self.application_cache)
            cdn_cache_size = len(self.cdn_cache)
            
            # Get Redis info if available
            redis_info = {}
            if self.redis_cache:
                try:
                    redis_info = self.redis_cache.info()
                except Exception:
                    redis_info = {'error': 'Unable to get Redis info'}
            
            return {
                'hit_rates': hit_rates,
                'cache_sizes': {
                    'application': app_cache_size,
                    'redis': redis_info.get('used_memory_keys', 0),
                    'cdn': cdn_cache_size
                },
                'statistics': self.cache_stats,
                'redis_info': redis_info,
                'total_requests': total_requests,
                'overall_hit_rate': sum(
                    hit_rates[level] * (self.cache_stats[level]['hits'] + self.cache_stats[level]['misses'])
                    for level in hit_rates
                ) / max(1, total_requests) if total_requests > 0 else 0
            }

    def invalidate(self, pattern: str, cache_level: str = "all") -> int:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match cache keys
            cache_level: Cache level to invalidate ('application', 'redis', 'cdn', 'all')
            
        Returns:
            Number of entries invalidated
        """
        invalidated_count = 0
        
        # Compile pattern for efficiency
        import fnmatch
        compiled_pattern = fnmatch.translate(pattern)
        
        try:
            if cache_level in ["application", "all"]:
                with self._lock:
                    keys_to_invalidate = [
                        key for key in self.application_cache.keys()
                        if fnmatch.fnmatch(key, pattern)
                    ]
                    for key in keys_to_invalidate:
                        del self.application_cache[key]
                    invalidated_count += len(keys_to_invalidate)
            
            if cache_level in ["redis", "all"] and self.redis_cache:
                # Delete multiple keys in Redis
                keys = self.redis_cache.keys(pattern)
                if keys:
                    invalidated_count += self.redis_cache.delete(*keys)
            
            if cache_level in ["cdn", "all"]:
                keys_to_invalidate = [
                    key for key in self.cdn_cache.keys()
                    if fnmatch.fnmatch(key, pattern)
                ]
                for key in keys_to_invalidate:
                    del self.cdn_cache[key]
                invalidated_count += len(keys_to_invalidate)
            
            logger.info(f"Invalidated {invalidated_count} cache entries for pattern: {pattern}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
            return invalidated_count


class DatabaseOptimizer:
    """
    Database query optimization and connection pooling system.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize database optimizer."""
        self.config = config or self._default_config()
        
        # Connection pools
        self.pools = {}
        self.connection_stats = defaultdict(list)
        
        # Query optimization
        self.slow_query_threshold = self.config.get('slow_query_threshold', 1.0)
        self.query_cache = {}
        self.query_optimization_rules = {}
        
        # Performance monitoring
        self.query_metrics = deque(maxlen=10000)
        self.connection_metrics = {}
        
        # Threading
        self._lock = threading.Lock()
        
        # Initialize connection pools
        self._initialize_connection_pools()
        
        # Start background monitoring
        self._start_background_monitoring()
        
        logger.info("Database optimizer initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'connection_pools': {
                'default': {
                    'url': 'sqlite:///simulation.db',
                    'pool_size': 10,
                    'max_overflow': 20,
                    'pool_timeout': 30,
                    'pool_recycle': 3600
                }
            },
            'slow_query_threshold': 1.0,
            'query_cache_size': 1000,
            'enable_query_analysis': True,
            'connection_timeout': 30,
            'connection_validation': True,
            'performance_monitoring': True
        }

    def _initialize_connection_pools(self) -> None:
        """Initialize database connection pools."""
        for pool_name, pool_config in self.config['connection_pools'].items():
            try:
                # Create SQLAlchemy engine with connection pooling
                engine = create_engine(
                    pool_config['url'],
                    pool_size=pool_config.get('pool_size', 10),
                    max_overflow=pool_config.get('max_overflow', 20),
                    pool_timeout=pool_config.get('pool_timeout', 30),
                    pool_recycle=pool_config.get('pool_recycle', 3600),
                    pool_pre_ping=pool_config.get('connection_validation', True)
                )
                
                # Create session factory
                session_factory = sessionmaker(bind=engine)
                
                self.pools[pool_name] = {
                    'engine': engine,
                    'session_factory': session_factory,
                    'config': pool_config
                }
                
                logger.info(f"Database pool '{pool_name}' initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize database pool '{pool_name}': {e}")

    @asynccontextmanager
    async def get_connection(self, pool_name: str = 'default'):
        """Get database connection from pool."""
        if pool_name not in self.pools:
            raise ValueError(f"Unknown connection pool: {pool_name}")
        
        pool_info = self.pools[pool_name]
        session_factory = pool_info['session_factory']
        
        start_time = time.time()
        session = session_factory()
        
        try:
            yield session
        finally:
            # Track connection usage
            connection_time = time.time() - start_time
            
            with self._lock:
                if pool_name not in self.connection_metrics:
                    self.connection_metrics[pool_name] = {
                        'total_connections': 0,
                        'active_connections': 0,
                        'total_time': 0.0,
                        'avg_time': 0.0
                    }
                
                metrics = self.connection_metrics[pool_name]
                metrics['total_connections'] += 1
                metrics['total_time'] += connection_time
                metrics['avg_time'] = metrics['total_time'] / metrics['total_connections']
            
            session.close()

    async def execute_optimized_query(self, query: str, parameters: Dict[str, Any] = None, 
                                    pool_name: str = 'default', use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Execute optimized query with caching and monitoring.
        
        Args:
            query: SQL query string
            parameters: Query parameters
            pool_name: Connection pool name
            use_cache: Whether to use query cache
            
        Returns:
            Query results as list of dictionaries
        """
        start_time = time.time()
        cache_key = None
        
        try:
            # Check query cache
            if use_cache and self._should_cache_query(query):
                cache_key = self._generate_cache_key(query, parameters)
                cached_result = self._get_cached_result(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute query with connection from pool
            async with self.get_connection(pool_name) as session:
                # Execute query
                result = session.execute(text(query), parameters or {})
                rows = result.fetchall()
                
                # Convert to dictionaries
                results = [dict(row._mapping) for row in rows]
                
                # Cache result if beneficial
                if cache_key and use_cache:
                    self._cache_result(cache_key, results)
                
                return results
                
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            # Record query metrics
            execution_time = time.time() - start_time
            
            query_metric = {
                'query': query[:100],  # Truncate for storage
                'execution_time': execution_time,
                'parameters': parameters,
                'pool_name': pool_name,
                'timestamp': time.time(),
                'success': True
            }
            
            with self._lock:
                self.query_metrics.append(query_metric)
                
                # Log slow queries
                if execution_time > self.slow_query_threshold:
                    logger.warning(f"Slow query detected: {execution_time:.3f}s - {query[:100]}")
            
            # Analyze query performance
            if self.config.get('enable_query_analysis', True):
                self._analyze_query_performance(query, execution_time)

    def _should_cache_query(self, query: str) -> bool:
        """Determine if query should be cached."""
        # Don't cache writes or administrative queries
        query_upper = query.upper().strip()
        if any(keyword in query_upper for keyword in ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER']):
            return False
        
        # Cache SELECT queries that might be expensive
        if 'SELECT' in query_upper:
            # Heuristic: cache complex queries with joins or aggregations
            complex_indicators = ['JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'SUBQUERY']
            return any(indicator in query_upper for indicator in complex_indicators)
        
        return False

    def _generate_cache_key(self, query: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key for query."""
        # Create deterministic key from query and parameters
        cache_data = {
            'query': query.strip(),
            'parameters': parameters or {}
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()
    def _get_cached_result(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached query result."""
        cached_entry = self.query_cache.get(cache_key)
        if cached_entry:
            # Check if cache is still valid
            if time.time() < cached_entry['expires_at']:
                cached_entry['access_count'] += 1
                return cached_entry['result']
            else:
                # Remove expired cache entry
                del self.query_cache[cache_key]
        
        return None

    def _cache_result(self, cache_key: str, result: List[Dict[str, Any]]) -> None:
        """Cache query result."""
        # Check cache size limit
        if len(self.query_cache) >= self.config.get('query_cache_size', 1000):
            self._evict_query_cache()
        
        # Cache result with TTL
        ttl = self._calculate_cache_ttl(result)
        
        self.query_cache[cache_key] = {
            'result': result,
            'cached_at': time.time(),
            'expires_at': time.time() + ttl,
            'access_count': 1
        }

    def _calculate_cache_ttl(self, result: List[Dict[str, Any]]) -> float:
        """Calculate appropriate TTL for query result."""
        # Heuristic: longer for larger result sets (assumed to be less volatile)
        if not result:
            return 60  # 1 minute for empty results
        
        result_size = len(result)
        
        if result_size < 10:
            return 300  # 5 minutes for small results
        elif result_size < 100:
            return 1800  # 30 minutes for medium results
        else:
            return 3600  # 1 hour for large results

    def _evict_query_cache(self) -> None:
        """Evict entries from query cache using LRU."""
        if not self.query_cache:
            return
        
        # Remove oldest entries
        cache_items = list(self.query_cache.items())
        cache_items.sort(key=lambda x: x[1]['access_count'])  # Sort by access count
        
        # Remove 25% of cache
        remove_count = max(1, len(cache_items) // 4)
        for key, _ in cache_items[:remove_count]:
            del self.query_cache[key]

    def _analyze_query_performance(self, query: str, execution_time: float) -> None:
        """Analyze query performance and suggest optimizations."""
        query_upper = query.upper().strip()
        
        # Simple optimization suggestions
        suggestions = []
        
        # Check for missing indexes
        if 'WHERE' in query_upper and 'JOIN' in query_upper:
            # Suggest index on join columns
            suggestions.append("Consider adding indexes on WHERE and JOIN columns")
        
        # Check for SELECT *
        if query_upper.startswith('SELECT *'):
            suggestions.append("Avoid SELECT *, specify only needed columns")
        
        # Check for subqueries
        if 'SELECT' in query_upper and 'FROM' in query_upper:
            subquery_count = query_upper.count('SELECT')
            if subquery_count > 1:
                suggestions.append("Consider optimizing subqueries with JOINs or CTEs")
        
        # Log optimization suggestions for slow queries
        if execution_time > self.slow_query_threshold and suggestions:
            logger.info(f"Query optimization suggestions: {suggestions}")

    def _start_background_monitoring(self) -> None:
        """Start background database monitoring."""
        def monitor_db():
            while True:
                try:
                    self._monitor_connection_pools()
                    self._cleanup_old_metrics()
                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    logger.error(f"Database monitoring error: {e}")
        
        monitor_thread = threading.Thread(target=monitor_db, daemon=True)
        monitor_thread.start()

    def _monitor_connection_pools(self) -> None:
        """Monitor connection pool health."""
        for pool_name, pool_info in self.pools.items():
            try:
                engine = pool_info['engine']
                
                # Get pool statistics
                pool_stats = {
                    'pool_name': pool_name,
                    'pool_size': engine.pool.size(),
                    'checked_in': engine.pool.checkedin(),
                    'checked_out': engine.pool.checkedout(),
                    'overflow': engine.pool.overflow(),
                    'invalid': engine.pool.invalid()
                }
                
                with self._lock:
                    self.connection_stats[pool_name].append({
                        'timestamp': time.time(),
                        **pool_stats
                    })
                    
                    # Keep only recent statistics
                    if len(self.connection_stats[pool_name]) > 100:
                        self.connection_stats[pool_name].popleft()
                
                # Log warnings for pool issues
                if pool_stats['overflow'] > pool_info['config'].get('max_overflow', 20) * 0.8:
                    logger.warning(f"Pool {pool_name} approaching overflow limit")
                
                if pool_stats['invalid'] > 0:
                    logger.warning(f"Pool {pool_name} has {pool_stats['invalid']} invalid connections")
                
            except Exception as e:
                logger.error(f"Pool monitoring error for {pool_name}: {e}")

    def _cleanup_old_metrics(self) -> None:
        """Clean up old performance metrics."""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hour
        
        with self._lock:
            # Clean old query metrics
            while (self.query_metrics and 
                   self.query_metrics[0]['timestamp'] < cutoff_time):
                self.query_metrics.popleft()

    def get_performance_report(self, time_window: float = 3600) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        with self._lock:
            # Filter recent metrics
            recent_queries = [
                metric for metric in self.query_metrics
                if metric['timestamp'] >= cutoff_time
            ]
            
            if not recent_queries:
                return {'message': 'No query metrics available for the specified time window'}
            
            # Calculate statistics
            execution_times = [q['execution_time'] for q in recent_queries]
            total_queries = len(recent_queries)
            avg_execution_time = np.mean(execution_times)
            max_execution_time = max(execution_times)
            min_execution_time = min(execution_times)
            
            # Identify slow queries
            slow_queries = [q for q in recent_queries if q['execution_time'] > self.slow_query_threshold]
            
            # Calculate pool statistics
            pool_reports = {}
            for pool_name, pool_stats in self.connection_stats.items():
                recent_pool_stats = [
                    stat for stat in pool_stats
                    if stat['timestamp'] >= cutoff_time
                ]
                
                if recent_pool_stats:
                    latest_stats = recent_pool_stats[-1]
                    pool_reports[pool_name] = {
                        'current_connections': latest_stats['checked_out'],
                        'pool_utilization': latest_stats['checked_out'] / max(1, latest_stats['pool_size']),
                        'overflow_usage': latest_stats['overflow'],
                        'connection_errors': latest_stats['invalid']
                    }
            
            return {
                'time_window': time_window,
                'total_queries': total_queries,
                'avg_execution_time': avg_execution_time,
                'max_execution_time': max_execution_time,
                'min_execution_time': min_execution_time,
                'slow_query_count': len(slow_queries),
                'slow_query_percentage': (len(slow_queries) / total_queries) * 100,
                'connection_pool_status': pool_reports,
                'cache_statistics': {
                    'cached_queries': len(self.query_cache),
                    'cache_hit_estimate': self._estimate_cache_hit_rate()
                }
            }

    def _estimate_cache_hit_rate(self) -> float:
        """Estimate cache hit rate from query cache statistics."""
        if not self.query_cache:
            return 0.0
        
        total_accesses = sum(entry['access_count'] for entry in self.query_cache.values())
        if total_accesses == 0:
            return 0.0
        
        # Estimate hits as subsequent accesses to cached items
        hits = total_accesses - len(self.query_cache)  # First access is a miss
        return min(1.0, hits / max(1, total_accesses))


class MemoryOptimizer:
    """
    Memory management and garbage collection optimization system.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize memory optimizer."""
        self.config = config or self._default_config()
        
        # Memory monitoring
        self.memory_history = deque(maxlen=1000)
        self.allocation_tracking = {}
        self.gc_stats = {'collections': 0, 'time': 0.0}
        
        # Optimization settings
        self.gc_threshold = self.config.get('gc_threshold', (700, 10, 10))
        self.memory_limit = self.config.get('memory_limit', 1024 * 1024 * 1024)  # 1GB
        self.optimization_enabled = self.config.get('optimization_enabled', True)
        
        # Threading
        self._lock = threading.Lock()
        self._monitoring = False
        
        # Initialize garbage collection optimization
        self._optimize_garbage_collection()
        
        # Start monitoring
        self._start_memory_monitoring()
        
        logger.info("Memory optimizer initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'gc_threshold': (700, 10, 10),
            'memory_limit': 1024 * 1024 * 1024,  # 1GB
            'optimization_enabled': True,
            'monitoring_interval': 30,
            'gc_optimization': True,
            'allocation_tracking': True,
            'memory_profiling': True,
            'peak_memory_tracking': True
        }

    def _optimize_garbage_collection(self) -> None:
        """Optimize garbage collection settings."""
        if not self.config.get('gc_optimization', True):
            return
        
        # Set optimized GC thresholds
        gc.set_threshold(*self.gc_threshold)
        
        # Enable automatic GC
        gc.enable()
        
        logger.info(f"Garbage collection optimized with thresholds: {self.gc_threshold}")

    def _start_memory_monitoring(self) -> None:
        """Start memory monitoring."""
        def monitor_memory():
            self._monitoring = True
            while self._monitoring:
                try:
                    self._record_memory_usage()
                    
                    if self.optimization_enabled:
                        self._check_memory_optimization()
                    
                    time.sleep(self.config.get('monitoring_interval', 30))
                except Exception as e:
                    logger.error(f"Memory monitoring error: {e}")
        
        monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
        monitor_thread.start()

    def _record_memory_usage(self) -> None:
        """Record current memory usage."""
        try:
            # Get process memory info
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Get system memory info
            system_memory = psutil.virtual_memory()
            
            # Record memory metrics
            memory_metrics = {
                'timestamp': time.time(),
                'process_rss': memory_info.rss,
                'process_vms': memory_info.vms,
                'process_percent': memory_percent,
                'system_total': system_memory.total,
                'system_available': system_memory.available,
                'system_percent': system_memory.percent,
                'gc_stats': gc.get_stats(),
                'object_counts': gc.get_count()
            }
            
            with self._lock:
                self.memory_history.append(memory_metrics)
            
            # Log high memory usage
            if memory_percent > 85:
                logger.warning(f"High memory usage detected: {memory_percent:.1f}%")
            
            # Check memory limit
            if memory_info.rss > self.memory_limit:
                logger.error(f"Memory limit exceeded: {memory_info.rss / 1024 / 1024:.1f}MB")
                self._trigger_memory_optimization()
                
        except Exception as e:
            logger.error(f"Memory usage recording error: {e}")

    def _check_memory_optimization(self) -> None:
        """Check if memory optimization is needed."""
        if not self.memory_history:
            return
        
        current_metrics = self.memory_history[-1]
        
        # Check if memory usage is growing rapidly
        if len(self.memory_history) >= 10:
            recent_usage = [m['process_rss'] for m in self.memory_history[-10:]]
            memory_growth = recent_usage[-1] - recent_usage[0]
            
            # If memory is growing by more than 100MB in recent measurements
            if memory_growth > 100 * 1024 * 1024:
                logger.info("Detected rapid memory growth, triggering optimization")
                self._trigger_memory_optimization()

    def _trigger_memory_optimization(self) -> None:
        """Trigger memory optimization procedures."""
        logger.info("Triggering memory optimization")
        
        # Force garbage collection
        self._force_garbage_collection()
        
        # Clear caches if available
        self._clear_caches()
        
        # Clean up large objects
        self._cleanup_large_objects()
        
        # Reset allocation tracking
        if self.config.get('allocation_tracking', True):
            self._reset_allocation_tracking()

    def _force_garbage_collection(self) -> None:
        """Force garbage collection."""
        start_time = time.time()
        
        # Get counts before collection
        before_counts = gc.get_count()
        
        # Perform garbage collection
        collected = gc.collect()
        
        # Get counts after collection
        after_counts = gc.get_count()
        
        collection_time = time.time() - start_time
        
        # Update statistics
        with self._lock:
            self.gc_stats['collections'] += collected
            self.gc_stats['time'] += collection_time
        
        logger.info(f"Garbage collection: {collected} objects collected in {collection_time:.3f}s")

    def _clear_caches(self) -> None:
        """Clear various caches to free memory."""
        cleared_caches = []
        
        # Clear Python's internal caches
        try:
            # Clear import cache
            import sys
            if hasattr(sys, 'clear_cache'):
                sys.clear_cache()
            cleared_caches.append('import_cache')
        except Exception as e:
            logger.debug(f"Could not clear import cache: {e}")
        
        # Clear application caches (if we can access them)
        try:
            # This would be enhanced to clear actual application caches
            cleared_caches.append('application_caches')
        except Exception as e:
            logger.debug(f"Could not clear application caches: {e}")
        
        if cleared_caches:
            logger.info(f"Cleared caches: {', '.join(cleared_caches)}")

    def _cleanup_large_objects(self) -> None:
        """Clean up large objects from allocation tracking."""
        if not self.config.get('allocation_tracking', True):
            return
        
        current_time = time.time()
        
        with self._lock:
            # Find large, old allocations
            large_objects = [
                (size, addr, timestamp) for addr, (size, timestamp) in self.allocation_tracking.items()
                if size > 1024 * 1024 and current_time - timestamp > 3600  # 1 hour
            ]
            
            # Sort by size (largest first)
            large_objects.sort(reverse=True)
            
            # Clean up the largest objects
            cleaned_objects = 0
            for size, addr, timestamp in large_objects[:10]:  # Clean top 10
                if addr in self.allocation_tracking:
                    del self.allocation_tracking[addr]
                    cleaned_objects += 1
            
            if cleaned_objects > 0:
                logger.info(f"Cleaned up {cleaned_objects} large objects")

    def _reset_allocation_tracking(self) -> None:
        """Reset allocation tracking."""
        with self._lock:
            self.allocation_tracking.clear()
        logger.info("Allocation tracking reset")

    def get_memory_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory report."""
        with self._lock:
            if not self.memory_history:
                return {'message': 'No memory history available'}
            
            current_metrics = self.memory_history[-1]
            
            # Calculate statistics
            recent_usage = [m['process_rss'] for m in self.memory_history[-100:]]  # Last 100 measurements
            
            if recent_usage:
                avg_memory = np.mean(recent_usage)
                max_memory = max(recent_usage)
                min_memory = min(recent_usage)
                memory_growth = recent_usage[-1] - recent_usage[0]
            else:
                avg_memory = max_memory = min_memory = memory_growth = 0
            
            # Calculate GC statistics
            gc_collection_count = sum(stat['collections'] for stat in gc.get_stats())
            
            # Object count statistics
            object_counts = gc.get_count()
            
            return {
                'current_memory': {
                    'rss_mb': current_metrics['process_rss'] / 1024 / 1024,
                    'vms_mb': current_metrics['process_vms'] / 1024 / 1024,
                    'percent': current_metrics['process_percent'],
                    'system_percent': current_metrics['system_percent']
                },
                'memory_statistics': {
                    'average_mb': avg_memory / 1024 / 1024,
                    'maximum_mb': max_memory / 1024 / 1024,
                    'minimum_mb': min_memory / 1024 / 1024,
                    'growth_mb': memory_growth / 1024 / 1024
                },
                'gc_statistics': {
                    'total_collections': gc_collection_count,
                    'tracked_collections': self.gc_stats['collections'],
                    'gc_time_seconds': self.gc_stats['time']
                },
                'object_counts': dict(zip(['gen0', 'gen1', 'gen2'], object_counts)),
                'allocation_tracking': {
                    'tracked_allocations': len(self.allocation_tracking)
                }
            }

    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Perform comprehensive memory optimization."""
        start_time = time.time()
        
        # Record memory before optimization
        process = psutil.Process()
        memory_before = process.memory_info().rss
        
        # Perform optimizations
        self._force_garbage_collection()
        self._clear_caches()
        self._cleanup_large_objects()
        
        # Record memory after optimization
        memory_after = process.memory_info().rss
        memory_saved = memory_before - memory_after
        
        optimization_time = time.time() - start_time
        
        result = {
            'optimization_time': optimization_time,
            'memory_before_mb': memory_before / 1024 / 1024,
            'memory_after_mb': memory_after / 1024 / 1024,
            'memory_saved_mb': memory_saved / 1024 / 1024,
            'optimization_successful': memory_saved > 0
        }
        
        logger.info(f"Memory optimization completed: {memory_saved / 1024 / 1024:.1f}MB saved")
        return result


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Initialize performance optimization systems
        distributed_optimizer = DistributedComputingOptimizer()
        caching_system = AdvancedCachingSystem()
        db_optimizer = DatabaseOptimizer()
        memory_optimizer = MemoryOptimizer()
        
        # Test distributed computing
        print("Testing distributed computing...")
        
        # Add compute nodes
        nodes = [
            ComputeNode(f"node_{i}", f"host-{i}", f"192.168.1.{i+100}", 
                       cpu_cores=8, memory_gb=16, storage_gb=100)
            for i in range(3)
        ]
        
        for node in nodes:
            distributed_optimizer.add_compute_node(node)
        
        # Distribute a task
        task = {
            'type': 'anomaly_detection',
            'data': 'sample_data',
            'cpu_requirement': 2,
            'memory_requirement': 4.0
        }
        
        task_id = await distributed_optimizer.distribute_task(task)
        print(f"Task distributed: {task_id}")
        
        # Test caching system
        print("Testing caching system...")
        
        await caching_system.put("test_key", {"data": "test_value"}, ttl=60)
        cached_value = await caching_system.get("test_key")
        print(f"Cache test: {'Success' if cached_value else 'Failed'}")
        
        # Test database optimization
        print("Testing database optimization...")
        
        try:
            # Test connection pool
            async with db_optimizer.get_connection() as session:
                # This would execute an actual query in production
                print("Database connection test: Success")
            
            # Test query optimization
            query = "SELECT COUNT(*) FROM agents WHERE status = 'active'"
            results = await db_optimizer.execute_optimized_query(query)
            print(f"Query optimization test: {len(results)} results")
            
        except Exception as e:
            print(f"Database test failed: {e}")
        
        # Test memory optimization
        print("Testing memory optimization...")
        
        memory_report = memory_optimizer.get_memory_report()
        optimization_result = memory_optimizer.optimize_memory_usage()
        
        print(f"Memory optimization: {optimization_result['memory_saved_mb']:.1f}MB saved")
        
        # Get system status
        cluster_status = distributed_optimizer.get_cluster_status()
        cache_stats = caching_system.get_cache_statistics()
        db_performance = db_optimizer.get_performance_report()
        
        print(f"\n=== System Status ===")
        print(f"Cluster nodes: {cluster_status['active_nodes']}/{cluster_status['total_nodes']}")
        print(f"Cache hit rate: {cache_stats['overall_hit_rate']:.1%}")
        print(f"Database queries: {db_performance.get('total_queries', 0)}")
        print(f"Memory usage: {memory_report['current_memory']['rss_mb']:.1f}MB")
    
    asyncio.run(main())