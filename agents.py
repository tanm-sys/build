from mesa import Agent
import numpy as np
from sklearn.ensemble import IsolationForest
import random
import time
import json
from typing import Any, Dict, List, Tuple
from logging_setup import get_logger

logger = get_logger(__name__)

# Initialize numpy random generator for modern random number generation
rng = np.random.default_rng(42)  # Use fixed seed for reproducibility


class AnomalyAgent(Agent):
    """
    Agent representing a node in the decentralized anomaly detection network.
    Inherits from mesa.Agent for integration with Mesa simulation framework.
    Handles local anomaly detection, signature generation, broadcasting,
    validation, and model updates.
    """

    def __init__(self, model):
        """
        Initialize the agent.

        Args:
            model: The simulation model instance.
        """
        super().__init__(model)
        self.node_id = f"Node_{self.unique_id}"
        self.anomaly_model = IsolationForest(contamination=0.05, random_state=42)
        self.recent_data: List[float] = []
        self.last_seen_id = 0
        self.local_blacklist_file = f"blacklist_{self.node_id}.json"
        # Ledger access via model
        self.ledger = model.ledger

    def generate_traffic(self, batch_size: int = 100, force_anomaly: bool = False) -> np.ndarray:
        """
        Generate simulated network traffic data.

        Args:
            batch_size: Number of data points to generate.
            force_anomaly: Whether to force an anomaly injection.

        Returns:
            Generated traffic data as numpy array.
        """
        normal = rng.normal(100, 20, batch_size)
        data = normal.copy()
        inject = force_anomaly or random.random() < 0.05
        if inject:
            idx = random.randint(0, batch_size - 1)
            data[idx] = 500
            logger.info(f"{self.node_id}: Generated traffic with anomaly")
        else:
            logger.debug(f"{self.node_id}: Generated normal traffic")
        self.recent_data = data.tolist()[-100:]
        return data

    def detect_anomaly(self, data: np.ndarray, threshold: float = -0.05) -> Tuple[bool, List[int], np.ndarray, List[str], np.ndarray]:
        """
        Detect anomalies in traffic data using Isolation Forest.

        Args:
            data: Traffic data as numpy array.
            threshold: Anomaly score threshold.

        Returns:
            Tuple containing:
            - has_anomaly: Boolean indicating if anomalies were detected
            - indices: List of anomaly indices
            - anomaly_data: Numpy array of anomalous data points
            - ips: List of anomaly IP addresses
            - scores: Numpy array of anomaly scores
        """
        self.anomaly_model.fit(data.reshape(-1, 1))
        scores = self.anomaly_model.decision_function(data.reshape(-1, 1)).flatten()
        anomalies = scores < threshold
        if np.any(anomalies):
            anomaly_indices = np.nonzero(anomalies)[0]
            anomaly_data = data[anomaly_indices]
            anomaly_scores = scores[anomaly_indices]
            ips = [f"192.168.1.{random.randint(1, 255)}" for _ in data]
            anomaly_ips = [ips[i] for i in anomaly_indices]
            logger.info(f"{self.node_id}: Detected anomaly")
            return True, anomaly_indices.tolist(), anomaly_data, anomaly_ips, anomaly_scores
        return False, [], np.array([]), [], np.array([])

    def generate_signature(self, anomaly_data: np.ndarray, anomaly_ips: List[str], anomaly_scores: np.ndarray) -> Dict[str, Any]:
        """
        Generate a threat signature from detected anomalies.

        Args:
            anomaly_data: Anomalous data points as numpy array.
            anomaly_ips: Corresponding IP addresses as list of strings.
            anomaly_scores: Anomaly scores as numpy array.

        Returns:
            Signature dictionary containing timestamp, features, confidence, and node_id.
        """
        timestamp = time.time()
        features = [{'packet_size': float(size), 'source_ip': ip} for size, ip in zip(anomaly_data, anomaly_ips)]
        confidence = float(np.mean(np.abs(anomaly_scores)))
        sig = {
            'timestamp': timestamp,
            'features': features,
            'confidence': confidence,
            'node_id': self.node_id
        }
        return sig

    def broadcast_signature(self, signature: Dict[str, Any]) -> None:
        """
        Broadcast the signature to the shared ledger.

        Args:
            signature: The generated signature dictionary.
        """
        # Assign ID via ledger
        signature['id'] = self.ledger.append_entry(signature)
        logger.info(f"{self.node_id}: Broadcasted signature {signature['id']}")

    def poll_and_validate(self) -> List[Dict[str, Any]]:
        """
        Poll the ledger for new entries and validate them.

        Returns:
            List of validation results, each containing 'sig_id' and 'valid' keys.
        """
        new_entries = self.ledger.get_new_entries(self.last_seen_id)
        validations = []
        for entry in new_entries:
            if entry['node_id'] != self.node_id:
                is_valid = self.validate_signature(entry)
                validations.append({'sig_id': entry['id'], 'valid': is_valid})
                logger.info(f"{self.node_id}: Validated sig {entry['id']} as {is_valid}")
        if new_entries:
            self.last_seen_id = max(e.get('id', 0) for e in self.ledger.read_ledger())
        return validations

    def validate_signature(self, sig: Dict[str, Any]) -> bool:
        """
        Validate a received signature using cosine similarity on means.

        Args:
            sig: The signature dictionary to validate.

        Returns:
            Boolean indicating whether the signature is valid.
        """
        if not self.recent_data or random.random() < 0.2:  # Simulate failure
            return random.random() > 0.2
        recent_mean = np.mean(self.recent_data)
        sig_mean = np.mean([f['packet_size'] for f in sig['features']])
        vec1 = np.array([recent_mean])
        vec2 = np.array([sig_mean])
        cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return cos_sim > 0.7

    def update_model_and_blacklist(self, sig: Dict[str, Any]) -> None:
        """
        Update local blacklist and retrain the model with new anomaly data.

        Args:
            sig: The confirmed signature dictionary.
        """
        # Update blacklist
        try:
            with open(self.local_blacklist_file, 'r') as f:
                bl = json.load(f)
        except FileNotFoundError:
            bl = []
        bl.append(sig)
        with open(self.local_blacklist_file, 'w') as f:
            json.dump(bl, f, indent=2)

        # Retrain model - handle different feature structures safely
        try:
            features = sig.get('features', [])
            if isinstance(features, list) and features:
                # Extract packet sizes from feature dictionaries
                anomaly_sizes = []
                for f in features:
                    if isinstance(f, dict) and 'packet_size' in f:
                        anomaly_sizes.append(f['packet_size'])
                    elif isinstance(f, (int, float)):
                        # Handle case where features are just numbers
                        anomaly_sizes.append(f)

                if anomaly_sizes:
                    train_data = np.array(self.recent_data + anomaly_sizes).reshape(-1, 1)
                    if len(train_data) > 0:
                        self.anomaly_model.fit(train_data)
        except Exception as e:
            logger.warning(f"{self.node_id}: Could not retrain model with signature features: {e}")

        logger.info(f"{self.node_id}: Updated model and blacklist")

    def step(self) -> None:
        """
        Main step method for the agent in the Mesa simulation.
        Handles perceive (generate/detect), decide (validate), act (broadcast/update).
        """
        # Perceive: Generate and detect
        data = self.generate_traffic()
        has_anom, _, anomaly_data, anomaly_ips, anomaly_scores = self.detect_anomaly(data)
        if has_anom:
            sig = self.generate_signature(anomaly_data, anomaly_ips, anomaly_scores)
            self.broadcast_signature(sig)
            self.update_model_and_blacklist(sig)  # Update own

        # Decide and Act: Poll and validate (consensus handled in model)
        self.poll_and_validate()
