from mesa import Agent
import numpy as np
from sklearn.ensemble import IsolationForest
import random
import time
import json
from typing import Any, Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from collections import deque
import threading
from contextlib import contextmanager
from functools import lru_cache
from ..utils.logging_setup import get_logger

logger = get_logger(__name__)

# Initialize numpy random generator for modern random number generation
rng = np.random.default_rng(42)  # Use fixed seed for reproducibility


@dataclass
class AnomalySignature:
    """Data class representing an anomaly signature with validation."""
    timestamp: float
    features: List[Dict[str, Union[int, float, str]]]
    confidence: float
    node_id: str
    signature_id: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate signature data after initialization."""
        if not self.features:
            raise ValueError("Features list cannot be empty")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        if not self.node_id:
            raise ValueError("Node ID cannot be empty")


@dataclass
class ValidationResult:
    """Data class representing signature validation results."""
    signature_id: int
    is_valid: bool
    validator_id: str = field(init=False)

    def __post_init__(self) -> None:
        """Set validator ID from signature ID for tracking."""
        self.validator_id = f"validation_{self.signature_id}"


@dataclass
class TrafficData:
    """Data class representing network traffic data."""
    data: np.ndarray
    has_anomaly: bool = False
    anomaly_indices: List[int] = field(default_factory=list)
    anomaly_scores: np.ndarray = field(default_factory=lambda: np.array([]))


class BoundedList:
    """
    Thread-safe bounded list that maintains a maximum size.
    When the list exceeds max_size, oldest items are removed.
    Optimized for memory efficiency and performance.
    """

    def __init__(self, max_size: int = 1000):
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self.max_size = max_size
        self._data = deque(maxlen=max_size)
        self._lock = threading.Lock()
        self._total_appended = 0  # Track total items for statistics

    def append(self, item: Any) -> None:
        """Add item to the list, removing oldest if necessary."""
        with self._lock:
            self._data.append(item)
            self._total_appended += 1

    def extend(self, items: List[Any]) -> None:
        """Add multiple items to the list."""
        with self._lock:
            self._data.extend(items)
            # If we exceed max_size, remove oldest items
            while len(self._data) > self.max_size:
                self._data.popleft()

    def clear(self) -> None:
        """Clear all items from the list."""
        with self._lock:
            self._data.clear()

    def tolist(self) -> List[Any]:
        """Convert to regular list."""
        with self._lock:
            return list(self._data)

    def __len__(self) -> int:
        """Get current length."""
        with self._lock:
            return len(self._data)

    def __getitem__(self, index: int) -> Any:
        """Get item by index."""
        with self._lock:
            return self._data[index]

    def __iter__(self) -> Any:
        """Iterate over items in the list."""
        with self._lock:
            return iter(self._data)

    def __add__(self, other: Union[List[Any], 'BoundedList']) -> List[Any]:
        """Concatenate with another list or BoundedList."""
        if isinstance(other, (list, BoundedList)):
            with self._lock:
                # Convert to regular list for concatenation
                self_list = list(self._data)
                if isinstance(other, BoundedList):
                    other_list = list(other._data)
                else:
                    other_list = other
                return self_list + other_list
        return NotImplemented

    def __radd__(self, other: List[Any]) -> List[Any]:
        """Right-side addition for concatenation."""
        if isinstance(other, list):
            with self._lock:
                self_list = list(self._data)
                return other + self_list
        return NotImplemented

    def get_memory_usage(self) -> int:
        """Get estimated memory usage in bytes."""
        with self._lock:
            # Rough estimate: each item + deque overhead
            item_size = sum(len(str(item)) if hasattr(item, '__len__') else 8 for item in self._data)
            return item_size + 64  # Approximate deque overhead

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the bounded list."""
        with self._lock:
            return {
                'current_size': len(self._data),
                'max_size': self.max_size,
                'total_appended': self._total_appended,
                'memory_usage': self.get_memory_usage()
            }

    def is_full(self) -> bool:
        """Check if the list is at maximum capacity."""
        with self._lock:
            return len(self._data) >= self.max_size


class AnomalyAgent(Agent):
    """
    Agent representing a node in the decentralized anomaly detection network.

    Inherits from mesa.Agent for integration with Mesa simulation framework.
    Handles local anomaly detection, signature generation, broadcasting,
    validation, and model updates with improved type safety and structure.

    SECURITY ENHANCEMENTS:
    - Memory leak prevention via BoundedList
    - Comprehensive input validation
    - Thread-safe operations
    - Resource management and cleanup
    """

    def __init__(self, model) -> None:
        """
        Initialize the agent with modern type annotations and security enhancements.

        Args:
            model: The simulation model instance containing ledger and configuration.

        Raises:
            ValueError: If model is invalid.
        """
        if model is None:
            raise ValueError("Model cannot be None")

        super().__init__(model)
        self.node_id: str = f"Node_{self.unique_id}"
        
        # Initialize anomaly model with lazy loading for efficiency
        self._anomaly_model = None
        self._model_config = {
            'contamination': 0.05,
            'random_state': 42
        }

        # Use bounded list to prevent memory leaks (security enhancement)
        max_recent_data = 1000  # Configurable limit
        self.recent_data = BoundedList(max_size=max_recent_data)
        
        self.last_seen_id: int = 0
        self.local_blacklist_file: str = f"blacklist_{self.node_id}.json"
        self.ledger = model.ledger

        # Configuration with type hints
        self.anomaly_threshold: float = -0.05
        self.validation_failure_rate: float = 0.2
        self.min_data_points: int = 10

        # Performance optimizations
        self._validation_cache: Dict[str, bool] = {}
        self._cache_hits: int = 0
        self._cache_misses: int = 0

        logger.info(f"Initialized {self.node_id} with enhanced type safety and security")

    @property
    def anomaly_model(self) -> IsolationForest:
        """Lazy-loaded anomaly detection model."""
        if self._anomaly_model is None:
            logger.debug(f"Lazy-loading anomaly model for agent {self.node_id}")
            self._anomaly_model = IsolationForest(**self._model_config)
        return self._anomaly_model

    @anomaly_model.setter
    def anomaly_model(self, model: IsolationForest) -> None:
        """Set the anomaly model (for compatibility)."""
        self._anomaly_model = model

    def generate_traffic(self, batch_size: int = 100, force_anomaly: bool = False) -> TrafficData:
        """
        Generate simulated network traffic data with enhanced structure and validation.

        Args:
            batch_size: Number of data points to generate. Must be positive.
            force_anomaly: Whether to force an anomaly injection.

        Returns:
            TrafficData object containing generated data and anomaly information.

        Raises:
            ValueError: If batch_size is invalid.
        """
        # Input validation (security enhancement)
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError(f"batch_size must be a positive integer, got: {batch_size}")

        if batch_size > 10000:  # Reasonable upper limit
            logger.warning(f"Large batch_size ({batch_size}) may impact performance")

        if not isinstance(force_anomaly, bool):
            raise ValueError(f"force_anomaly must be a boolean, got: {type(force_anomaly)}")

        try:
            # Generate normal traffic pattern
            normal_data = rng.normal(100, 20, batch_size)
            data = normal_data.copy()

            # Determine if anomaly should be injected
            should_inject = force_anomaly or random.random() < 0.05

            anomaly_indices = []
            if should_inject:
                anomaly_idx = random.randint(0, batch_size - 1)
                data[anomaly_idx] = 500  # Inject anomaly
                anomaly_indices = [anomaly_idx]
                logger.info(f"{self.node_id}: Generated traffic with injected anomaly at index {anomaly_idx}")
            else:
                logger.debug(f"{self.node_id}: Generated normal traffic")

            # Use bounded list to prevent memory leaks
            self.recent_data.extend(data.tolist())

            return TrafficData(
                data=data,
                has_anomaly=len(anomaly_indices) > 0,
                anomaly_indices=anomaly_indices
            )

        except Exception as e:
            logger.error(f"{self.node_id}: Error generating traffic: {e}")
            raise

    def detect_anomaly(self, traffic_data: TrafficData) -> Tuple[bool, List[int], np.ndarray, List[str], np.ndarray]:
        """
        Detect anomalies in traffic data using Isolation Forest with enhanced structure.

        Args:
            traffic_data: TrafficData object containing the data to analyze.

        Returns:
            Tuple containing:
            - has_anomaly: Boolean indicating if anomalies were detected
            - indices: List of anomaly indices
            - anomaly_data: Numpy array of anomalous data points
            - ips: List of anomaly IP addresses
            - scores: Numpy array of anomaly scores
        """
        # Input validation (security enhancement)
        if not isinstance(traffic_data, TrafficData):
            raise ValueError(f"traffic_data must be TrafficData object, got: {type(traffic_data)}")

        if len(traffic_data.data) == 0:
            logger.warning(f"{self.node_id}: Empty traffic data provided")
            return False, [], np.array([]), [], np.array([])

        try:
            # Reshape data for the model
            data_reshaped = traffic_data.data.reshape(-1, 1)

            # Fit the model and get scores
            self.anomaly_model.fit(data_reshaped)
            scores = self.anomaly_model.decision_function(data_reshaped).flatten()

            # Identify anomalies based on threshold
            anomaly_mask = scores < self.anomaly_threshold
            anomaly_indices = np.nonzero(anomaly_mask)[0]

            if len(anomaly_indices) > 0:
                anomaly_data = traffic_data.data[anomaly_indices]
                anomaly_scores = scores[anomaly_indices]

                # Generate IP addresses for anomalies
                anomaly_ips = self._generate_anomaly_ips(anomaly_indices)

                logger.info(f"{self.node_id}: Detected {len(anomaly_indices)} anomalies")
                return True, anomaly_indices.tolist(), anomaly_data, anomaly_ips, anomaly_scores

            return False, [], np.array([]), [], np.array([])

        except Exception as e:
            logger.error(f"{self.node_id}: Error during anomaly detection: {e}")
            # Return safe defaults on error
            return False, [], np.array([]), [], np.array([])

    def _generate_anomaly_ips(self, anomaly_indices: np.ndarray) -> List[str]:
        """Generate IP addresses for detected anomalies."""
        return [f"192.168.1.{random.randint(1, 255)}" for _ in anomaly_indices]

    def generate_signature(self, anomaly_data: np.ndarray, anomaly_ips: List[str], anomaly_scores: np.ndarray) -> AnomalySignature:
        """
        Generate a threat signature from detected anomalies using modern dataclass.

        Args:
            anomaly_data: Anomalous data points as numpy array.
            anomaly_ips: Corresponding IP addresses as list of strings.
            anomaly_scores: Anomaly scores as numpy array.

        Returns:
            AnomalySignature object containing structured signature data.

        Raises:
            ValueError: If input arrays have mismatched lengths or are empty.
        """
        if len(anomaly_data) != len(anomaly_ips) or len(anomaly_data) != len(anomaly_scores):
            raise ValueError("All input arrays must have the same length")

        if len(anomaly_data) == 0:
            raise ValueError("Cannot generate signature from empty anomaly data")

        # Create feature dictionaries with proper typing
        features = [
            {'packet_size': float(size), 'source_ip': str(ip)}
            for size, ip in zip(anomaly_data, anomaly_ips)
        ]

        # Calculate confidence score
        confidence = float(np.mean(np.abs(anomaly_scores)))

        return AnomalySignature(
            timestamp=time.time(),
            features=features,
            confidence=min(confidence, 1.0),  # Ensure confidence is within [0, 1]
            node_id=self.node_id
        )

    def broadcast_signature(self, signature: AnomalySignature) -> None:
        """
        Broadcast the signature to the shared ledger with enhanced error handling.

        Args:
            signature: The generated AnomalySignature object.

        Raises:
            RuntimeError: If broadcasting to ledger fails.
        """
        try:
            # Convert signature to dictionary for ledger storage
            signature_dict = {
                'timestamp': signature.timestamp,
                'node_id': signature.node_id,
                'features': signature.features,
                'confidence': signature.confidence
            }

            # Assign ID via ledger and update signature
            signature_id = self.ledger.append_entry(signature_dict)
            signature.signature_id = signature_id

            logger.info(f"{self.node_id}: Successfully broadcast signature {signature_id}")

        except Exception as e:
            logger.error(f"{self.node_id}: Failed to broadcast signature: {e}")
            raise RuntimeError(f"Signature broadcast failed for {self.node_id}") from e

    def poll_and_validate(self) -> List[ValidationResult]:
        """
        Poll the ledger for new entries and validate them with enhanced structure.

        Returns:
            List of ValidationResult objects containing validation outcomes.
        """
        try:
            new_entries = self.ledger.get_new_entries(self.last_seen_id)
            validations = []

            for entry in new_entries:
                # Skip self-generated signatures
                if entry['node_id'] == self.node_id:
                    continue

                # Validate signature and create result object
                is_valid = self.validate_signature(entry)
                validation_result = ValidationResult(
                    signature_id=entry['id'],
                    is_valid=is_valid
                )

                validations.append(validation_result)
                logger.info(f"{self.node_id}: Validated signature {entry['id']} as {is_valid}")

            # Update last seen ID if we processed any entries
            if new_entries:
                all_entries = self.ledger.read_ledger()
                if all_entries:
                    self.last_seen_id = max(e.get('id', 0) for e in all_entries)

            return validations

        except Exception as e:
            logger.error(f"{self.node_id}: Error during poll and validate: {e}")
            return []

    def validate_signature(self, signature: Dict[str, Any]) -> bool:
        """
        Validate a received signature with enhanced caching and performance optimizations.

        Args:
            signature: The signature dictionary to validate.

        Returns:
            Boolean indicating whether the signature is valid.
        """
        # Create cache key from signature characteristics
        cache_key = self._create_signature_cache_key(signature)

        # Check cache first
        if cache_key in self._validation_cache:
            self._cache_hits += 1
            logger.debug(f"{self.node_id}: Cache hit for signature validation")
            return self._validation_cache[cache_key]

        self._cache_misses += 1

        try:
            # Check if we have sufficient recent data
            if len(self.recent_data) < self.min_data_points:
                logger.debug(f"{self.node_id}: Insufficient recent data for validation")
                return self._cache_and_return(cache_key, random.random() > self.validation_failure_rate)

            # Simulate occasional validation failures
            if random.random() < self.validation_failure_rate:
                logger.debug(f"{self.node_id}: Simulated validation failure")
                return self._cache_and_return(cache_key, random.random() > self.validation_failure_rate)

            # Extract and validate features efficiently
            sig_mean = self._extract_signature_mean(signature)
            if sig_mean is None:
                return self._cache_and_return(cache_key, False)

            # Calculate similarity with optimized computation
            recent_mean = np.mean(self.recent_data)
            is_valid = self._calculate_similarity_optimized(recent_mean, sig_mean)

            logger.debug(f"{self.node_id}: Validation similarity: {recent_mean:.3f} vs {sig_mean:.3f}, valid: {is_valid}")

            return self._cache_and_return(cache_key, is_valid)

        except Exception as e:
            logger.error(f"{self.node_id}: Error validating signature: {e}")
            return self._cache_and_return(cache_key, False)

    def _create_signature_cache_key(self, signature: Dict[str, Any]) -> str:
        """Create a cache key from signature characteristics."""
        features = signature.get('features', [])
        if not features:
            return "empty"

        # Create key from mean packet size and signature structure
        packet_sizes = [
            f.get('packet_size', 0) for f in features[:5]  # Sample first 5 features
            if isinstance(f, dict) and 'packet_size' in f
        ]

        if not packet_sizes:
            return f"no_packets_{len(features)}"

        mean_size = np.mean(packet_sizes)
        return f"mean_{mean_size:.2f}_count_{len(features)}"

    def _extract_signature_mean(self, signature: Dict[str, Any]) -> Optional[float]:
        """Extract mean packet size from signature features efficiently."""
        features = signature.get('features', [])
        if not features:
            return None

        packet_sizes = []
        for feature in features:
            if isinstance(feature, dict) and 'packet_size' in feature:
                try:
                    packet_sizes.append(float(feature['packet_size']))
                except (ValueError, TypeError):
                    continue

        return np.mean(packet_sizes) if packet_sizes else None

    def _calculate_similarity_optimized(self, recent_mean: float, sig_mean: float) -> bool:
        """Calculate cosine similarity with optimized computation."""
        if abs(recent_mean) < 1e-10 or abs(sig_mean) < 1e-10:
            return abs(recent_mean - sig_mean) < 0.1

        # Use more efficient similarity calculation
        vec1 = np.array([recent_mean])
        vec2 = np.array([sig_mean])

        # Avoid division by zero and use more stable calculation
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return False

        cos_sim = dot_product / (norm1 * norm2)
        return cos_sim > 0.7

    def _cache_and_return(self, cache_key: str, result: bool) -> bool:
        """Cache result and return it."""
        # Simple cache with size limit
        if len(self._validation_cache) > 100:
            # Clear oldest half of cache
            items = list(self._validation_cache.items())
            self._validation_cache = dict(items[50:])

        self._validation_cache[cache_key] = result
        return result

    def get_cache_stats(self) -> Dict[str, int]:
        """Get validation cache statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0

        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate_percent': hit_rate,
            'cache_size': len(self._validation_cache)
        }

    def update_model_and_blacklist(self, signature: AnomalySignature) -> None:
        """
        Update local blacklist and retrain the model with new anomaly data.

        Args:
            signature: The confirmed AnomalySignature object.
        """
        # Update blacklist with enhanced error handling
        self._update_blacklist(signature)

        # Retrain model with new data
        self._retrain_model(signature)

        logger.info(f"{self.node_id}: Successfully updated model and blacklist")

    def _update_blacklist(self, signature: AnomalySignature) -> None:
        """Update local blacklist file with new signature."""
        try:
            # Load existing blacklist
            try:
                with open(self.local_blacklist_file, 'r', encoding='utf-8') as f:
                    blacklist = json.load(f)
            except FileNotFoundError:
                blacklist = []
            except json.JSONDecodeError as e:
                logger.warning(f"{self.node_id}: Corrupted blacklist file, creating new one: {e}")
                blacklist = []

            # Add signature to blacklist
            blacklist.append({
                'timestamp': signature.timestamp,
                'node_id': signature.node_id,
                'confidence': signature.confidence,
                'features': signature.features
            })

            # Write updated blacklist
            with open(self.local_blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(blacklist, f, indent=2)

        except Exception as e:
            logger.error(f"{self.node_id}: Failed to update blacklist: {e}")
            raise

    def _retrain_model(self, signature: AnomalySignature) -> None:
        """Retrain the anomaly detection model with new signature data."""
        try:
            if not signature.features:
                logger.warning(f"{self.node_id}: No features in signature for model retraining")
                return

            # Extract packet sizes from features
            anomaly_sizes = self._extract_packet_sizes(signature.features)

            if not anomaly_sizes:
                logger.warning(f"{self.node_id}: No valid packet sizes found in signature features")
                return

            # Combine recent data with new anomaly data
            combined_data = np.array(self.recent_data.tolist() + anomaly_sizes)

            if len(combined_data) < self.min_data_points:
                logger.warning(f"{self.node_id}: Insufficient data for model retraining")
                return

            # Retrain model
            self.anomaly_model.fit(combined_data.reshape(-1, 1))
            logger.debug(f"{self.node_id}: Model retrained with {len(combined_data)} data points")

        except Exception as e:
            logger.error(f"{self.node_id}: Failed to retrain model: {e}")
            raise

    def _extract_packet_sizes(self, features: List[Dict[str, Any]]) -> List[float]:
        """Extract packet sizes from signature features."""
        packet_sizes = []
        for feature in features:
            if isinstance(feature, dict) and 'packet_size' in feature:
                try:
                    packet_sizes.append(float(feature['packet_size']))
                except (ValueError, TypeError) as e:
                    logger.warning(f"{self.node_id}: Invalid packet size in feature: {e}")
            elif isinstance(feature, (int, float)):
                try:
                    packet_sizes.append(float(feature))
                except (ValueError, TypeError) as e:
                    logger.warning(f"{self.node_id}: Invalid numeric feature: {e}")

        return packet_sizes

    def cleanup(self) -> None:
        """
        Cleanup agent resources (security enhancement).
        """
        try:
            # Clear recent data to free memory
            self.recent_data.clear()

            # Clear anomaly model
            self._anomaly_model = None

            # Clear validation cache
            self._validation_cache.clear()
            self._cache_hits = 0
            self._cache_misses = 0

            logger.debug(f"{self.node_id}: Agent cleanup completed")

        except Exception as e:
            logger.error(f"{self.node_id}: Error during cleanup: {e}")

    def step(self) -> None:
        """
        Main step method for the agent in the Mesa simulation with enhanced structure.

        Handles perceive (generate/detect), decide (validate), act (broadcast/update).
        Uses modern data structures for improved type safety and maintainability.
        """
        try:
            # Phase 1: Generate traffic and detect anomalies
            traffic_data = self.generate_traffic()

            if traffic_data.has_anomaly and len(traffic_data.anomaly_indices) > 0:
                # Extract anomaly data for signature generation
                anomaly_data = traffic_data.data[traffic_data.anomaly_indices]

                # For now, generate mock IPs and scores for detected anomalies
                # In a real implementation, this would come from the detection process
                anomaly_ips = self._generate_anomaly_ips(np.array(traffic_data.anomaly_indices))
                anomaly_scores = np.random.normal(-0.5, 0.1, len(anomaly_data))

                # Generate and broadcast signature
                signature = self.generate_signature(anomaly_data, anomaly_ips, anomaly_scores)
                self.broadcast_signature(signature)

                # Update own model and blacklist
                self.update_model_and_blacklist(signature)

            # Phase 2: Poll and validate other agents' signatures
            self.poll_and_validate()

        except Exception as e:
            logger.error(f"{self.node_id}: Error during agent step: {e}")
            # Continue execution rather than crashing the simulation


def validate_agent_input(value: Any, param_name: str, expected_type: type, min_val: Any = None, max_val: Any = None) -> None:
    """Validate agent input parameters with comprehensive checks (security enhancement)."""
    # Type validation
    if not isinstance(value, expected_type):
        raise TypeError(f"{param_name} must be {expected_type.__name__}, got {type(value).__name__}")

    # Range validation for numeric types
    if expected_type in (int, float):
        if min_val is not None and value < min_val:
            raise ValueError(f"{param_name} must be >= {min_val}, got {value}")
        if max_val is not None and value > max_val:
            raise ValueError(f"{param_name} must be <= {max_val}, got {value}")
    elif expected_type == str and value == "":
        raise ValueError(f"{param_name} cannot be empty string")


def create_optimized_agent_model(model_class, unique_id: int, model_instance) -> AnomalyAgent:
    """Factory function to create optimized agent instances.

    Args:
        model_class: Class of agent to create
        unique_id: Unique identifier for the agent
        model_instance: Model instance the agent belongs to

    Returns:
        Configured agent instance

    Raises:
        RuntimeError: If agent creation fails
    """
    try:
        agent = model_class(model_instance)
        logger.debug(f"Created optimized agent {agent.node_id}")
        return agent
    except Exception as e:
        logger.error(f"Failed to create agent {unique_id}: {e}")
        raise


class AgentFactory:
    """Factory class for creating and managing optimized agents."""

    @staticmethod
    def create_agents_batch(model_instance, num_agents: int, agent_class=AnomalyAgent) -> List[AnomalyAgent]:
        """Create a batch of agents with optimized error handling.

        Args:
            model_instance: Model instance the agents belong to
            num_agents: Number of agents to create
            agent_class: Class of agents to create

        Returns:
            List of created agent instances

        Raises:
            ValueError: If num_agents is invalid
            RuntimeError: If no agents could be created
        """
        validate_agent_input(num_agents, "num_agents", int, min_val=1, max_val=10000)

        agents = []
        for i in range(num_agents):
            try:
                agent = create_optimized_agent_model(agent_class, i, model_instance)
                agents.append(agent)
            except Exception as e:
                logger.error(f"Failed to create agent {i}: {e}")
                # Continue creating remaining agents
                continue

        if not agents:
            raise RuntimeError("Failed to create any agents")

        logger.info(f"Successfully created {len(agents)}/{num_agents} agents")
        return agents

    @staticmethod
    def cleanup_agents(agents: List[AnomalyAgent]) -> int:
        """Clean up multiple agents and return count of cleaned agents.

        Args:
            agents: List of agents to clean up

        Returns:
            Number of agents successfully cleaned up
        """
        cleaned_count = 0
        for agent in agents:
            try:
                if hasattr(agent, 'cleanup'):
                    agent.cleanup()
                    cleaned_count += 1
            except Exception as e:
                logger.error(f"Error cleaning up agent {agent.node_id}: {e}")

        logger.info(f"Cleaned up {cleaned_count}/{len(agents)} agents")
        return cleaned_count
