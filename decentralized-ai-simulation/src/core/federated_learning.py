"""
Federated Learning and Byzantine Fault Tolerance Module

Implements enterprise-grade distributed learning capabilities:
- Federated learning with privacy preservation
- Byzantine Fault Tolerant consensus mechanisms
- Secure model aggregation
- Distributed gradient descent
- Fault detection and recovery

Author: Kilo Code
Date: November 1, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import time
import json
import hashlib
import asyncio
import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class ConsensusState(Enum):
    """Consensus states for Byzantine fault tolerance."""
    IDLE = "idle"
    PROPOSING = "proposing"
    VOTING = "voting"
    COMMITTING = "committing"
    FINALIZED = "finalized"
    FAILED = "failed"


class FaultType(Enum):
    """Types of Byzantine faults."""
    DROP = "drop"           # Drop messages
    DELAY = "delay"         # Delay messages
    DUPLICATE = "duplicate" # Duplicate messages
    CORRUPT = "corrupt"     # Corrupt data
    BYZANTINE = "byzantine" # Arbitrary behavior


@dataclass
class ModelUpdate:
    """Data class for federated learning model updates."""
    agent_id: str
    round_number: int
    model_parameters: Dict[str, np.ndarray]
    gradient_norms: Dict[str, float]
    local_accuracy: float
    data_sample_count: int
    timestamp: float
    signature: Optional[str] = None
    public_key: Optional[bytes] = None


@dataclass
class ConsensusMessage:
    """Data class for consensus protocol messages."""
    message_id: str
    sender_id: str
    message_type: str  # PROPOSAL, VOTE, COMMIT
    round_number: int
    data: Dict[str, Any]
    timestamp: float
    signature: str


@dataclass
class ByzantineFault:
    """Data class for Byzantine fault detection."""
    agent_id: str
    fault_type: FaultType
    detected_at: float
    severity: float
    evidence: List[str]
    quarantine_until: float


class FederatedLearningCoordinator:
    """
    Coordinates federated learning across distributed agents.
    
    Implements:
    - Secure model aggregation
    - Privacy-preserving updates
    - Byzantine fault tolerance
    - Dynamic participant selection
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize federated learning coordinator."""
        self.config = config or self._default_config()
        
        # Core federated learning parameters
        self.min_participants = self.config.get('min_participants', 5)
        self.max_participants = self.config.get('max_participants', 50)
        self.aggregation_rounds = self.config.get('aggregation_rounds', 10)
        self.privacy_budget = self.config.get('privacy_budget', 1.0)
        
        # Model and participant tracking
        self.global_model = None
        self.participants = {}
        self.update_history = deque(maxlen=1000)
        self.model_versions = {}
        
        # Byzantine fault tolerance
        self.byzantine_threshold = self.config.get('byzantine_threshold', 0.33)
        self.fault_detection_enabled = True
        self.quarantined_agents = set()
        
        # Performance tracking
        self.performance_metrics = defaultdict(list)
        self.learning_stats = defaultdict(int)
        
        # Security
        self.private_keys = {}
        self.public_keys = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Threading
        self._lock = threading.Lock()
        
        logger.info("Federated learning coordinator initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'min_participants': 5,
            'max_participants': 50,
            'aggregation_rounds': 10,
            'privacy_budget': 1.0,
            'byzantine_threshold': 0.33,
            'fault_detection_enabled': True,
            'model_size_limit': 100 * 1024 * 1024,  # 100MB
            'timeout_seconds': 300,
            'retry_attempts': 3,
            'encryption_enabled': True,
            'differential_privacy': True
        }

    async def start_federated_round(self, round_number: int, participants: List[str] = None) -> Dict[str, Any]:
        """
        Start a new federated learning round.
        
        Args:
            round_number: Current round number
            participants: Optional list of participant IDs
            
        Returns:
            Round results including global model update
        """
        with self._lock:
            try:
                logger.info(f"Starting federated learning round {round_number}")
                
                # Select participants if not provided
                if participants is None:
                    participants = self._select_participants()
                
                if len(participants) < self.min_participants:
                    raise ValueError(f"Insufficient participants: {len(participants)} < {self.min_participants}")
                
                # Send current global model to participants
                global_model = await self._distribute_model_to_participants(participants, round_number)
                
                # Collect updates from participants
                updates = await self._collect_participant_updates(participants, round_number)
                
                # Validate and filter updates
                valid_updates = await self._validate_updates(updates)
                
                # Aggregate models
                aggregated_model = await self._aggregate_models(valid_updates)
                
                # Update global model
                self.global_model = aggregated_model
                self.model_versions[round_number] = aggregated_model
                
                # Calculate round metrics
                round_metrics = self._calculate_round_metrics(valid_updates, round_number)
                
                # Log performance
                self.learning_stats['total_rounds'] += 1
                self.learning_stats['successful_aggregations'] += 1
                self.learning_stats['participants_per_round'] = np.mean([u.data_sample_count for u in valid_updates])
                
                logger.info(f"Round {round_number} completed successfully with {len(valid_updates)} valid updates")
                return {
                    'round_number': round_number,
                    'participants': len(participants),
                    'valid_updates': len(valid_updates),
                    'global_model_version': round_number,
                    'metrics': round_metrics,
                    'next_round_estimated': time.time() + 60  # Estimate next round
                }
                
            except Exception as e:
                logger.error(f"Federated round {round_number} failed: {e}")
                self.learning_stats['failed_rounds'] += 1
                raise

    def _select_participants(self) -> List[str]:
        """Select participants for the learning round."""
        available_agents = list(self.participants.keys())
        
        # Remove quarantined agents
        available_agents = [agent for agent in available_agents if agent not in self.quarantined_agents]
        
        # Score agents based on performance history
        agent_scores = []
        for agent_id in available_agents:
            history = self.performance_metrics[agent_id]
            if history:
                avg_accuracy = np.mean([h.get('accuracy', 0) for h in history])
                consistency = np.std([h.get('accuracy', 0) for h in history])
                score = avg_accuracy - (0.1 * consistency)  # Reward consistency
            else:
                score = 0.5  # Default score for new agents
            
            agent_scores.append((agent_id, score))
        
        # Sort by score and select top participants
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        num_participants = min(self.max_participants, len(agent_scores))
        
        selected = [agent_scores[i][0] for i in range(num_participants)]
        logger.debug(f"Selected {len(selected)} participants: {selected[:5]}...")
        
        return selected

    async def _distribute_model_to_participants(self, participants: List[str], round_number: int) -> Dict[str, Any]:
        """Distribute global model to participants."""
        if self.global_model is None:
            raise ValueError("No global model available for distribution")
        
        distribution_tasks = []
        for participant_id in participants:
            task = self._send_model_to_participant(participant_id, self.global_model, round_number)
            distribution_tasks.append(task)
        
        # Wait for all distributions (with timeout)
        completed_tasks = await asyncio.wait_for(
            asyncio.gather(*distribution_tasks, return_exceptions=True),
            timeout=self.config['timeout_seconds']
        )
        
        # Log results
        successful = sum(1 for task in completed_tasks if not isinstance(task, Exception))
        logger.info(f"Model distributed to {successful}/{len(participants)} participants")
        
        return self.global_model

    async def _send_model_to_participant(self, participant_id: str, model: Dict[str, Any], round_number: int) -> bool:
        """Send model to a single participant."""
        try:
            # Encrypt model data
            if self.config['encryption_enabled']:
                model_data = self.cipher.encrypt(json.dumps(model).encode())
            else:
                model_data = json.dumps(model).encode()
            
            # Create distribution message
            message = {
                'type': 'model_distribution',
                'round_number': round_number,
                'model_data': base64.b64encode(model_data).decode(),
                'timestamp': time.time(),
                'sender': 'coordinator'
            }
            
            # Send to participant (simulated - replace with actual network call)
            # In real implementation, this would use aiohttp or similar
            response = await self._simulate_network_send(participant_id, message)
            
            return response.get('status') == 'success'
            
        except Exception as e:
            logger.error(f"Failed to send model to {participant_id}: {e}")
            return False

    async def _collect_participant_updates(self, participants: List[str], round_number: int) -> List[ModelUpdate]:
        """Collect model updates from participants."""
        collection_tasks = []
        for participant_id in participants:
            task = self._collect_update_from_participant(participant_id, round_number)
            collection_tasks.append(task)
        
        # Wait for updates with timeout
        completed_tasks = await asyncio.wait_for(
            asyncio.gather(*collection_tasks, return_exceptions=True),
            timeout=self.config['timeout_seconds']
        )
        
        # Filter successful updates
        updates = []
        for task in completed_tasks:
            if isinstance(task, ModelUpdate):
                updates.append(task)
            elif isinstance(task, Exception):
                logger.warning(f"Update collection failed: {task}")
        
        logger.info(f"Collected {len(updates)} updates from participants")
        return updates

    async def _collect_update_from_participant(self, participant_id: str, round_number: int) -> Optional[ModelUpdate]:
        """Collect update from a single participant."""
        try:
            # Request update from participant
            message = {
                'type': 'request_update',
                'round_number': round_number,
                'timestamp': time.time(),
                'sender': 'coordinator'
            }
            
            response = await self._simulate_network_send(participant_id, message)
            
            if response.get('status') != 'success':
                return None
            
            # Parse update data
            update_data = response.get('update_data', {})
            
            # Reconstruct model parameters
            model_parameters = {}
            for param_name, param_data in update_data.get('model_parameters', {}).items():
                model_parameters[param_name] = np.array(param_data)
            
            # Create ModelUpdate object
            update = ModelUpdate(
                agent_id=participant_id,
                round_number=round_number,
                model_parameters=model_parameters,
                gradient_norms=update_data.get('gradient_norms', {}),
                local_accuracy=update_data.get('local_accuracy', 0.0),
                data_sample_count=update_data.get('data_sample_count', 0),
                timestamp=time.time()
            )
            
            return update
            
        except Exception as e:
            logger.error(f"Failed to collect update from {participant_id}: {e}")
            return None

    async def _validate_updates(self, updates: List[ModelUpdate]) -> List[ModelUpdate]:
        """Validate and filter participant updates."""
        valid_updates = []
        
        for update in updates:
            # Check for Byzantine behavior
            is_byzantine = await self._detect_byzantine_behavior(update)
            if is_byzantine:
                await self._quarantine_agent(update.agent_id, "byzantine_behavior")
                continue
            
            # Validate update integrity
            if not await self._validate_update_integrity(update):
                logger.warning(f"Invalid update from {update.agent_id}")
                continue
            
            # Check data quality
            if not self._validate_data_quality(update):
                logger.warning(f"Poor quality update from {update.agent_id}")
                continue
            
            valid_updates.append(update)
        
        # Apply Byzantine fault tolerance threshold
        max_byzantine = int(len(updates) * self.byzantine_threshold)
        if len(updates) - len(valid_updates) > max_byzantine:
            logger.error(f"Too many invalid updates: {len(updates) - len(valid_updates)} > {max_byzantine}")
            return []
        
        return valid_updates

    async def _detect_byzantine_behavior(self, update: ModelUpdate) -> bool:
        """Detect Byzantine behavior in update."""
        agent_id = update.agent_id
        
        # Check for suspicious gradient norms
        for param_name, gradient_norm in update.gradient_norms.items():
            if gradient_norm > 1000:  # Suspiciously large gradient
                logger.warning(f"Suspicious gradient norm from {agent_id}: {gradient_norm}")
                await self._record_byzantine_fault(agent_id, FaultType.CORRUPT, f"Large gradient: {gradient_norm}")
                return True
        
        # Check for unusual accuracy patterns
        history = self.performance_metrics.get(agent_id, [])
        if len(history) > 5:
            recent_accuracies = [h.get('accuracy', 0) for h in history[-5:]]
            if np.std(recent_accuracies) > 0.5:  # High variance in accuracy
                logger.warning(f"Unusual accuracy pattern from {agent_id}")
                await self._record_byzantine_fault(agent_id, FaultType.CORRUPT, "Unusual accuracy variance")
                return True
        
        # Check for impossible values
        if update.local_accuracy > 1.0 or update.local_accuracy < 0.0:
            logger.warning(f"Invalid accuracy from {agent_id}: {update.local_accuracy}")
            await self._record_byzantine_fault(agent_id, FaultType.CORRUPT, f"Invalid accuracy: {update.local_accuracy}")
            return True
        
        return False

    async def _validate_update_integrity(self, update: ModelUpdate) -> bool:
        """Validate update integrity."""
        try:
            # Check that model parameters have expected structure
            for param_name, param_values in update.model_parameters.items():
                if not isinstance(param_values, np.ndarray):
                    return False
                if np.any(np.isnan(param_values)) or np.any(np.isinf(param_values)):
                    return False
            
            # Check gradient norms consistency
            for param_name, gradient_norm in update.gradient_norms.items():
                if param_name not in update.model_parameters:
                    return False
                if gradient_norm < 0:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Update integrity validation failed: {e}")
            return False

    def _validate_data_quality(self, update: ModelUpdate) -> bool:
        """Validate data quality of update."""
        # Check if agent has sufficient data
        if update.data_sample_count < 10:
            return False
        
        # Check if accuracy is reasonable
        if update.local_accuracy < 0.1 and update.data_sample_count > 100:
            return False  # Suspiciously poor performance with substantial data
        
        return True

    async def _aggregate_models(self, updates: List[ModelUpdate]) -> Dict[str, np.ndarray]:
        """Aggregate participant models using FedAvg with differential privacy."""
        if not updates:
            raise ValueError("No valid updates to aggregate")
        
        # Calculate weights based on data sample count
        total_samples = sum(update.data_sample_count for update in updates)
        weights = [update.data_sample_count / total_samples for update in updates]
        
        # Aggregate parameters
        aggregated_model = {}
        
        # Get all parameter names
        param_names = set()
        for update in updates:
            param_names.update(update.model_parameters.keys())
        
        for param_name in param_names:
            # Weighted average of parameters
            weighted_sum = np.zeros_like(list(updates[0].model_parameters[param_name]))
            
            for i, update in enumerate(updates):
                if param_name in update.model_parameters:
                    weighted_sum += weights[i] * update.model_parameters[param_name]
            
            # Add differential privacy noise
            if self.config['differential_privacy']:
                noise_scale = self.privacy_budget / (2 * np.sqrt(total_samples))
                noise = np.random.laplace(0, noise_scale, weighted_sum.shape)
                weighted_sum += noise
            
            aggregated_model[param_name] = weighted_sum
        
        # Log aggregation results
        logger.info(f"Model aggregated from {len(updates)} participants with total samples: {total_samples}")
        
        return aggregated_model

    def _calculate_round_metrics(self, updates: List[ModelUpdate], round_number: int) -> Dict[str, Any]:
        """Calculate performance metrics for the round."""
        if not updates:
            return {}
        
        metrics = {
            'participants': len(updates),
            'avg_accuracy': np.mean([update.local_accuracy for update in updates]),
            'total_samples': sum(update.data_sample_count for update in updates),
            'avg_gradient_norm': np.mean([
                np.mean(list(update.gradient_norms.values())) for update in updates
            ]),
            'round_duration': time.time() - self._round_start_times.get(round_number, time.time())
        }
        
        # Store performance metrics for each participant
        for update in updates:
            self.performance_metrics[update.agent_id].append({
                'accuracy': update.local_accuracy,
                'samples': update.data_sample_count,
                'round': round_number,
                'timestamp': update.timestamp
            })
        
        return metrics

    async def _quarantine_agent(self, agent_id: str, reason: str) -> None:
        """Quarantine a suspicious agent."""
        if agent_id not in self.quarantined_agents:
            self.quarantined_agents.add(agent_id)
            logger.warning(f"Agent {agent_id} quarantined: {reason}")
            
            # Remove from participants
            if agent_id in self.participants:
                del self.participants[agent_id]

    async def _record_byzantine_fault(self, agent_id: str, fault_type: FaultType, evidence: str) -> None:
        """Record a Byzantine fault."""
        fault = ByzantineFault(
            agent_id=agent_id,
            fault_type=fault_type,
            detected_at=time.time(),
            severity=1.0,
            evidence=[evidence],
            quarantine_until=time.time() + 3600  # Quarantine for 1 hour
        )
        
        logger.warning(f"Byzantine fault detected from {agent_id}: {fault_type.value}")

    async def _simulate_network_send(self, recipient_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate network communication (replace with real implementation)."""
        # Simulate network latency
        await asyncio.sleep(0.1)
        
        # Simulate response
        return {
            'status': 'success',
            'response_data': {
                'message_id': f"resp_{message.get('timestamp', 0)}",
                'timestamp': time.time()
            }
        }

    def register_participant(self, agent_id: str, agent_metadata: Dict[str, Any]) -> bool:
        """Register a new participant."""
        with self._lock:
            try:
                # Generate key pair for participant
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                public_key = private_key.public_key()
                
                self.private_keys[agent_id] = private_key
                self.public_keys[agent_id] = public_key
                
                # Register participant
                self.participants[agent_id] = {
                    'metadata': agent_metadata,
                    'registered_at': time.time(),
                    'last_activity': time.time(),
                    'total_rounds': 0,
                    'successful_rounds': 0
                }
                
                logger.info(f"Participant {agent_id} registered successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to register participant {agent_id}: {e}")
                return False

    def unregister_participant(self, agent_id: str) -> bool:
        """Unregister a participant."""
        with self._lock:
            try:
                if agent_id in self.participants:
                    del self.participants[agent_id]
                
                if agent_id in self.private_keys:
                    del self.private_keys[agent_id]
                
                if agent_id in self.public_keys:
                    del self.public_keys[agent_id]
                
                if agent_id in self.quarantined_agents:
                    self.quarantined_agents.discard(agent_id)
                
                logger.info(f"Participant {agent_id} unregistered")
                return True
                
            except Exception as e:
                logger.error(f"Failed to unregister participant {agent_id}: {e}")
                return False

    def get_system_status(self) -> Dict[str, Any]:
        """Get federated learning system status."""
        with self._lock:
            return {
                'total_participants': len(self.participants),
                'active_participants': len(self.participants) - len(self.quarantined_agents),
                'quarantined_agents': len(self.quarantined_agents),
                'total_rounds': self.learning_stats['total_rounds'],
                'success_rate': self.learning_stats['successful_aggregations'] / max(1, self.learning_stats['total_rounds']),
                'avg_participants_per_round': self.learning_stats.get('participants_per_round', 0),
                'byzantine_threshold': self.byzantine_threshold,
                'privacy_budget': self.privacy_budget,
                'global_model_available': self.global_model is not None
            }

    _round_start_times = {}


class ByzantineConsensus:
    """
    Byzantine Fault Tolerant consensus mechanism.
    
    Implements PBFT-style consensus for secure distributed decision making.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Byzantine consensus mechanism."""
        self.config = config or self._default_config()
        
        self.node_id = config.get('node_id', 'coordinator')
        self.byzantine_threshold = config.get('byzantine_threshold', 0.33)
        self.min_nodes = config.get('min_nodes', 3)
        self.timeout = config.get('timeout', 30)
        
        # Consensus state
        self.active_consensus = {}
        self.node_reputation = defaultdict(float)
        self.consensus_history = deque(maxlen=1000)
        
        # Message tracking
        self.message_buffer = defaultdict(list)
        self.pending_requests = {}
        
        self._lock = threading.Lock()
        
        logger.info(f"Byzantine consensus initialized for node {self.node_id}")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'node_id': 'coordinator',
            'byzantine_threshold': 0.33,
            'min_nodes': 3,
            'timeout': 30,
            'view_change_timeout': 60,
            'max_retries': 3
        }

    async def propose_consensus(self, proposal_id: str, proposal_data: Dict[str, Any], nodes: List[str]) -> str:
        """
        Start a new consensus proposal.
        
        Args:
            proposal_id: Unique identifier for the proposal
            proposal_data: Data to be agreed upon
            nodes: List of participating nodes
            
        Returns:
            Consensus result
        """
        if len(nodes) < self.min_nodes:
            raise ValueError(f"Insufficient nodes: {len(nodes)} < {self.min_nodes}")
        
        max_byzantine = int(len(nodes) * self.byzantine_threshold)
        if max_byzantine >= len(nodes) // 2:
            raise ValueError("Too many Byzantine nodes to achieve consensus")
        
        consensus_id = f"consensus_{proposal_id}_{int(time.time())}"
        
        with self._lock:
            # Create consensus state
            self.active_consensus[consensus_id] = {
                'proposal_id': proposal_id,
                'proposal_data': proposal_data,
                'nodes': nodes,
                'proposer': self.node_id,
                'state': ConsensusState.PROPOSING,
                'votes': {},
                'prepare_votes': {},
                'commit_votes': {},
                'start_time': time.time(),
                'view': 0
            }
        
        try:
            # Phase 1: Pre-prepare
            await self._pre_prepare_phase(consensus_id)
            
            # Phase 2: Prepare
            prepare_result = await self._prepare_phase(consensus_id)
            if not prepare_result:
                raise ValueError("Prepare phase failed")
            
            # Phase 3: Commit
            commit_result = await self._commit_phase(consensus_id)
            if not commit_result:
                raise ValueError("Commit phase failed")
            
            # Finalize
            with self._lock:
                self.active_consensus[consensus_id]['state'] = ConsensusState.FINALIZED
            
            # Record in history
            self.consensus_history.append({
                'consensus_id': consensus_id,
                'proposal_id': proposal_id,
                'nodes': len(nodes),
                'success': True,
                'duration': time.time() - self.active_consensus[consensus_id]['start_time']
            })
            
            logger.info(f"Consensus {consensus_id} completed successfully")
            return consensus_id
            
        except Exception as e:
            logger.error(f"Consensus {consensus_id} failed: {e}")
            with self._lock:
                if consensus_id in self.active_consensus:
                    self.active_consensus[consensus_id]['state'] = ConsensusState.FAILED
            
            raise

    async def _pre_prepare_phase(self, consensus_id: str) -> None:
        """Phase 1: Pre-prepare."""
        consensus = self.active_consensus[consensus_id]
        consensus['state'] = ConsensusState.PROPOSING
        
        # Create pre-prepare message
        message = {
            'type': 'pre-prepare',
            'consensus_id': consensus_id,
            'proposal_id': consensus['proposal_id'],
            'proposal_data': consensus['proposal_data'],
            'view': consensus['view'],
            'proposer': consensus['proposer'],
            'timestamp': time.time(),
            'sender': self.node_id
        }
        
        # Send to all nodes
        for node_id in consensus['nodes']:
            if node_id != self.node_id:
                await self._send_message(node_id, message)
        
        logger.debug(f"Pre-prepare phase completed for {consensus_id}")

    async def _prepare_phase(self, consensus_id: str) -> bool:
        """Phase 2: Prepare."""
        consensus = self.active_consensus[consensus_id]
        consensus['state'] = ConsensusState.VOTING
        
        # Wait for prepare messages
        timeout_time = time.time() + self.timeout
        required_prepares = len(consensus['nodes']) - int(len(consensus['nodes']) * self.byzantine_threshold)
        
        while time.time() < timeout_time:
            with self._lock:
                prepares_received = len(consensus['prepare_votes'])
            
            if prepares_received >= required_prepares:
                logger.debug(f"Prepare phase completed for {consensus_id} with {prepares_received} votes")
                return True
            
            await asyncio.sleep(0.1)
        
        logger.warning(f"Prepare phase timeout for {consensus_id}")
        return False

    async def _commit_phase(self, consensus_id: str) -> bool:
        """Phase 3: Commit."""
        consensus = self.active_consensus[consensus_id]
        consensus['state'] = ConsensusState.COMMITTING
        
        # Send commit message
        commit_message = {
            'type': 'commit',
            'consensus_id': consensus_id,
            'proposal_id': consensus['proposal_id'],
            'view': consensus['view'],
            'timestamp': time.time(),
            'sender': self.node_id
        }
        
        for node_id in consensus['nodes']:
            if node_id != self.node_id:
                await self._send_message(node_id, commit_message)
        
        # Wait for commit messages
        timeout_time = time.time() + self.timeout
        required_commits = len(consensus['nodes']) - int(len(consensus['nodes']) * self.byzantine_threshold)
        
        while time.time() < timeout_time:
            with self._lock:
                commits_received = len(consensus['commit_votes'])
            
            if commits_received >= required_commits:
                logger.debug(f"Commit phase completed for {consensus_id} with {commits_received} votes")
                return True
            
            await asyncio.sleep(0.1)
        
        logger.warning(f"Commit phase timeout for {consensus_id}")
        return False

    async def _send_message(self, recipient_id: str, message: Dict[str, Any]) -> bool:
        """Send message to another node (simulated)."""
        try:
            # In real implementation, this would use network communication
            await asyncio.sleep(0.05)  # Simulate network latency
            
            # Store message in buffer
            with self._lock:
                self.message_buffer[recipient_id].append(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {recipient_id}: {e}")
            return False

    async def receive_message(self, message: Dict[str, Any]) -> bool:
        """Receive and process a consensus message."""
        message_type = message.get('type')
        consensus_id = message.get('consensus_id')
        
        if consensus_id not in self.active_consensus:
            logger.warning(f"Unknown consensus ID: {consensus_id}")
            return False
        
        consensus = self.active_consensus[consensus_id]
        
        try:
            if message_type == 'prepare':
                return await self._handle_prepare_message(message, consensus)
            elif message_type == 'commit':
                return await self._handle_commit_message(message, consensus)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False

    async def _handle_prepare_message(self, message: Dict[str, Any], consensus: Dict[str, Any]) -> bool:
        """Handle prepare phase message."""
        sender_id = message.get('sender')
        
        with self._lock:
            consensus['prepare_votes'][sender_id] = message
        
        logger.debug(f"Received prepare vote from {sender_id} for {consensus['consensus_id']}")
        return True

    async def _handle_commit_message(self, message: Dict[str, Any], consensus: Dict[str, Any]) -> bool:
        """Handle commit phase message."""
        sender_id = message.get('sender')
        
        with self._lock:
            consensus['commit_votes'][sender_id] = message
        
        logger.debug(f"Received commit vote from {sender_id} for {consensus['consensus_id']}")
        return True

    def get_consensus_status(self) -> Dict[str, Any]:
        """Get consensus system status."""
        with self._lock:
            active_count = len([c for c in self.active_consensus.values() if c['state'] != ConsensusState.FINALIZED])
            
            return {
                'active_consensus': active_count,
                'total_consensus': len(self.consensus_history),
                'average_duration': np.mean([c['duration'] for c in self.consensus_history]) if self.consensus_history else 0,
                'success_rate': np.mean([c['success'] for c in self.consensus_history]) if self.consensus_history else 0,
                'node_reputation': dict(self.node_reputation),
                'byzantine_threshold': self.byzantine_threshold
            }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Initialize federated learning coordinator
        coordinator = FederatedLearningCoordinator()
        
        # Register some participants
        for i in range(10):
            coordinator.register_participant(f"agent_{i}", {
                'capabilities': {'compute': 1.0, 'network': 1.0},
                'reliability': 0.9
            })
        
        # Start federated learning round
        result = await coordinator.start_federated_round(1)
        print(f"Federated round result: {result}")
        
        # Initialize Byzantine consensus
        consensus = ByzantineConsensus({'node_id': 'coordinator'})
        
        # Propose consensus
        try:
            consensus_id = await consensus.propose_consensus(
                "test_proposal",
                {"decision": "approve"},
                ["node_1", "node_2", "node_3"]
            )
            print(f"Consensus ID: {consensus_id}")
        except Exception as e:
            print(f"Consensus failed: {e}")
        
        # Get system status
        status = coordinator.get_system_status()
        print(f"System status: {status}")
    
    asyncio.run(main())