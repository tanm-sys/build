from mesa import Agent
import numpy as np
from sklearn.ensemble import IsolationForest
import random
import time
import json
from typing import Any, Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
from functools import lru_cache
from logging_setup import get_logger

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


class AnomalyAgent(Agent):
    """
    Agent representing a node in the decentralized anomaly detection network.

    Inherits from mesa.Agent for integration with Mesa simulation framework.
    Handles local anomaly detection, signature generation, broadcasting,
    validation, and model updates with improved type safety and structure.
    """

    def __init__(self, model) -> None:
        """
        Initialize the agent with modern type annotations.

        Args:
            model: The simulation model instance containing ledger and configuration.
        """
        super().__init__(model)
        self.node_id: str = f"Node_{self.unique_id}"
        self.anomaly_model: IsolationForest = IsolationForest(
            contamination=0.05, random_state=42
        )
        self.recent_data: List[float] = []
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

        logger.info(f"Initialized {self.node_id} with enhanced type safety")

    def generate_traffic(self, batch_size: int = 100, force_anomaly: bool = False) -> TrafficData:
        """
        Generate simulated network traffic data with enhanced structure.

        Args:
            batch_size: Number of data points to generate.
            force_anomaly: Whether to force an anomaly injection.

        Returns:
            TrafficData object containing generated data and anomaly information.
        """
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

        # Update recent data buffer
        self.recent_data = data.tolist()[-100:]

        return TrafficData(
            data=data,
            has_anomaly=len(anomaly_indices) > 0,
            anomaly_indices=anomaly_indices
        )

    def detect_anomaly(self, traffic_data: TrafficData) -> Tuple[bool, List[int], np.ndarray, List[str], np.ndarray]:
        """
        Detect anomalies in traffic data using Isolation Forest with improved structure.

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
        if len(traffic_data.data) == 0:
            logger.warning(f"{self.node_id}: Empty traffic data provided")
            return False, [], np.array([]), [], np.array([])

        # Fit model and get anomaly scores
        data_reshaped = traffic_data.data.reshape(-1, 1)
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
            combined_data = np.array(self.recent_data + anomaly_sizes)

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
