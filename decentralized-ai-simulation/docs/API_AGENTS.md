# Agents Module API Documentation

## Overview

The `agents` module provides a comprehensive framework for decentralized anomaly detection agents with modern type safety, enhanced data structures, and sophisticated validation mechanisms. It implements the Mesa Agent pattern with advanced features for anomaly signature generation, validation, and consensus participation.

## Data Classes

### AnomalySignature

**Description:**
Data class representing an anomaly signature with comprehensive validation and type safety.

```python
@dataclass
class AnomalySignature:
    timestamp: float
    features: List[Dict[str, Union[int, float, str]]]
    confidence: float
    node_id: str
    signature_id: Optional[int] = None
```

**Fields:**
- `timestamp` (float): Unix timestamp when the signature was created
- `features` (List[Dict[str, Union[int, float, str]]]): List of feature dictionaries containing anomaly characteristics
- `confidence` (float): Confidence score between 0.0 and 1.0
- `node_id` (str): Identifier of the node that generated the signature
- `signature_id` (Optional[int]): Database ID assigned after ledger storage

**Validation (via __post_init__):**
- Features list cannot be empty
- Confidence must be between 0 and 1
- Node ID cannot be empty

**Example:**
```python
from agents import AnomalySignature

# Create anomaly signature
signature = AnomalySignature(
    timestamp=time.time(),
    features=[
        {'packet_size': 500, 'source_ip': '192.168.1.100'},
        {'packet_size': 750, 'source_ip': '192.168.1.101'}
    ],
    confidence=0.85,
    node_id="Node_1"
)
```

### ValidationResult

**Description:**
Data class representing the result of signature validation with automatic validator tracking.

```python
@dataclass
class ValidationResult:
    signature_id: int
    is_valid: bool
    validator_id: str = field(init=False)
```

**Fields:**
- `signature_id` (int): ID of the validated signature
- `is_valid` (bool): Validation outcome (True = valid, False = invalid)
- `validator_id` (str): Auto-generated validator identifier for tracking

**Auto-generation:**
- `validator_id` is automatically set to `"validation_{signature_id}"` format

**Example:**
```python
from agents import ValidationResult

# Create validation result
result = ValidationResult(signature_id=123, is_valid=True)
print(f"Validated by: {result.validator_id}")  # "validation_123"
```

### TrafficData

**Description:**
Data class representing network traffic data with anomaly detection results.

```python
@dataclass
class TrafficData:
    data: np.ndarray
    has_anomaly: bool = False
    anomaly_indices: List[int] = field(default_factory=list)
    anomaly_scores: np.ndarray = field(default_factory=lambda: np.array([]))
```

**Fields:**
- `data` (np.ndarray): Raw traffic data points
- `has_anomaly` (bool): Whether anomalies were detected in the data
- `anomaly_indices` (List[int]): Indices of detected anomalous data points
- `anomaly_scores` (np.ndarray): Anomaly scores for each data point

**Example:**
```python
from agents import TrafficData
import numpy as np

# Create traffic data with anomalies
data = np.array([100, 105, 500, 98, 750, 102])  # Anomalies at indices 2, 4
traffic = TrafficData(
    data=data,
    has_anomaly=True,
    anomaly_indices=[2, 4],
    anomaly_scores=np.array([-0.8, -0.3])
)
```

## Class: AnomalyAgent

### Constructor

```python
AnomalyAgent(model) -> None
```

**Description:**
Initialize the agent with modern type annotations and enhanced configuration for anomaly detection.

**Parameters:**
- `model`: The simulation model instance containing ledger and configuration

**Initialization Features:**
- Unique node ID generation (`Node_{unique_id}`)
- Isolation Forest model setup with optimized parameters
- Local blacklist file path configuration
- Performance optimization caches
- Comprehensive logging setup

**Configuration:**
- `anomaly_threshold`: Threshold for anomaly detection (-0.05 default)
- `validation_failure_rate`: Simulated validation failure rate (0.2 default)
- `min_data_points`: Minimum data points required for validation (10 default)

**Example:**
```python
from agents import AnomalyAgent
from simulation import Simulation

# Create simulation and agent
sim = Simulation(num_agents=10)
agent = AnomalyAgent(sim)

print(f"Agent ID: {agent.node_id}")
print(f"Anomaly threshold: {agent.anomaly_threshold}")
```

### Traffic Generation and Anomaly Detection

#### `generate_traffic(batch_size: int = 100, force_anomaly: bool = False) -> TrafficData`

**Description:**
Generate simulated network traffic data with optional anomaly injection for testing and training.

**Parameters:**
- `batch_size` (int): Number of data points to generate (default: 100)
- `force_anomaly` (bool): Whether to force injection of an anomaly (default: False)

**Generation Logic:**
- Normal traffic follows normal distribution (μ=100, σ=20)
- Anomaly injection occurs randomly (5% probability) or when forced
- Anomalies injected at random position with value 500
- Updates agent's recent data buffer (last 100 points)

**Returns:**
`TrafficData` object containing generated data and anomaly information

**Example:**
```python
# Generate normal traffic
normal_traffic = agent.generate_traffic(batch_size=50)
print(f"Normal traffic anomaly: {normal_traffic.has_anomaly}")

# Force anomaly generation
anomaly_traffic = agent.generate_traffic(batch_size=50, force_anomaly=True)
print(f"Forced anomaly traffic: {anomaly_traffic.has_anomaly}")
print(f"Anomaly at indices: {anomaly_traffic.anomaly_indices}")
```

#### `detect_anomaly(traffic_data: TrafficData) -> Tuple[bool, List[int], np.ndarray, List[str], np.ndarray]`

**Description:**
Detect anomalies in traffic data using Isolation Forest with enhanced structure and comprehensive return values.

**Parameters:**
- `traffic_data` (TrafficData): TrafficData object containing the data to analyze

**Returns:**
Tuple containing:
- `has_anomaly` (bool): Whether anomalies were detected
- `indices` (List[int]): List of anomaly indices in the data
- `anomaly_data` (np.ndarray): Array of anomalous data points
- `ips` (List[str]): List of generated IP addresses for anomalies
- `scores` (np.ndarray): Array of anomaly scores from the model

**Detection Process:**
1. Validate input data (return empty results for empty data)
2. Fit Isolation Forest model to reshaped data
3. Calculate decision function scores
4. Identify anomalies based on threshold
5. Generate IP addresses for detected anomalies

**Example:**
```python
# Generate and analyze traffic
traffic = agent.generate_traffic(batch_size=100, force_anomaly=True)
has_anomaly, indices, data, ips, scores = agent.detect_anomaly(traffic)

if has_anomaly:
    print(f"Detected {len(indices)} anomalies:")
    for i, (idx, ip, score) in enumerate(zip(indices, ips, scores)):
        print(f"  Anomaly {i+1}: Index {idx}, IP {ip}, Score {score:.3f}")
```

### Signature Management

#### `generate_signature(anomaly_data: np.ndarray, anomaly_ips: List[str], anomaly_scores: np.ndarray) -> AnomalySignature`

**Description:**
Generate a structured threat signature from detected anomalies with comprehensive validation.

**Parameters:**
- `anomaly_data` (np.ndarray): Array of anomalous data points
- `anomaly_ips` (List[str]): Corresponding IP addresses
- `anomaly_scores` (np.ndarray): Anomaly scores from detection

**Returns:**
`AnomalySignature` object containing structured signature data

**Raises:**
- `ValueError`: If input arrays have mismatched lengths or are empty

**Signature Creation:**
1. Validate input array lengths match
2. Create feature dictionaries with packet_size and source_ip
3. Calculate confidence score from mean absolute anomaly scores
4. Ensure confidence is within [0, 1] range

**Example:**
```python
# Detect anomalies and generate signature
traffic = agent.generate_traffic(force_anomaly=True)
has_anomaly, indices, data, ips, scores = agent.detect_anomaly(traffic)

if has_anomaly:
    signature = agent.generate_signature(data, ips, scores)
    print(f"Generated signature with confidence: {signature.confidence:.3f}")
    print(f"Features: {len(signature.features)}")
```

#### `broadcast_signature(signature: AnomalySignature) -> None`

**Description:**
Broadcast the signature to the shared ledger with enhanced error handling and ID assignment.

**Parameters:**
- `signature` (AnomalySignature): The generated signature object to broadcast

**Process:**
1. Convert signature to dictionary format for ledger storage
2. Append to ledger and retrieve assigned ID
3. Update signature object with assigned ID
4. Log successful broadcast

**Raises:**
- `RuntimeError`: If broadcasting to ledger fails

**Example:**
```python
# Generate and broadcast signature
signature = agent.generate_signature(anomaly_data, anomaly_ips, anomaly_scores)
agent.broadcast_signature(signature)
print(f"Broadcast signature ID: {signature.signature_id}")
```

### Validation System

#### `poll_and_validate() -> List[ValidationResult]`

**Description:**
Poll the ledger for new entries and validate them with enhanced structure and performance optimizations.

**Returns:**
List of `ValidationResult` objects containing validation outcomes for new signatures

**Process:**
1. Retrieve new entries from ledger since last seen ID
2. Skip self-generated signatures
3. Validate each new signature
4. Create ValidationResult objects
5. Update last seen ID for next polling cycle

**Error Handling:**
- Returns empty list on polling errors
- Continues execution even if individual validations fail
- Comprehensive error logging

**Example:**
```python
# Poll for new signatures and validate
validation_results = agent.poll_and_validate()
print(f"Validated {len(validation_results)} new signatures")

for result in validation_results:
    status = "VALID" if result.is_valid else "INVALID"
    print(f"Signature {result.signature_id}: {status}")
```

#### `validate_signature(signature: Dict[str, Any]) -> bool`

**Description:**
Validate a received signature with enhanced caching and performance optimizations using cosine similarity.

**Parameters:**
- `signature` (Dict[str, Any]): The signature dictionary to validate

**Returns:**
Boolean indicating whether the signature is considered valid

**Validation Algorithm:**
1. Check cache for previous validation result
2. Verify sufficient recent data available
3. Extract signature mean packet size
4. Calculate cosine similarity with recent data
5. Cache result for performance

**Performance Features:**
- Intelligent caching with size limits (100 entries max)
- Cache hit/miss statistics tracking
- Optimized similarity calculations

**Example:**
```python
# Validate individual signature
signature = {'id': 123, 'features': [{'packet_size': 500}], 'confidence': 0.8}
is_valid = agent.validate_signature(signature)
print(f"Signature validation: {'Valid' if is_valid else 'Invalid'}")

# Check cache performance
stats = agent.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate_percent']:.1f}%")
```

#### `get_cache_stats() -> Dict[str, int]`

**Description:**
Get validation cache statistics for performance monitoring and optimization.

**Returns:**
Dictionary containing cache performance metrics:
- `cache_hits`: Number of cache hits
- `cache_misses`: Number of cache misses
- `hit_rate_percent`: Cache hit rate as percentage
- `cache_size`: Current cache size

**Example:**
```python
# Monitor cache performance
stats = agent.get_cache_stats()
print(f"Cache Performance:")
print(f"  Hits: {stats['cache_hits']}")
print(f"  Misses: {stats['cache_misses']}")
print(f"  Hit Rate: {stats['hit_rate_percent']:.1f}%")
print(f"  Size: {stats['cache_size']} entries")
```

### Model and Blacklist Management

#### `update_model_and_blacklist(signature: AnomalySignature) -> None`

**Description:**
Update local blacklist and retrain the anomaly detection model with new confirmed anomaly data.

**Parameters:**
- `signature` (AnomalySignature): The confirmed signature containing anomaly data

**Process:**
1. Update local blacklist file with signature data
2. Retrain Isolation Forest model with combined data
3. Log successful updates

**Example:**
```python
# Update model with confirmed signature
confirmed_signature = AnomalySignature(...)
agent.update_model_and_blacklist(confirmed_signature)
print("Model and blacklist updated successfully")
```

#### `_update_blacklist(signature: AnomalySignature) -> None`

**Description:**
Update local blacklist file with new signature data for persistent threat tracking.

**Process:**
1. Load existing blacklist from JSON file
2. Handle file corruption gracefully
3. Append new signature data
4. Write updated blacklist with proper formatting

**File Format:**
```json
[
    {
        "timestamp": 1234567890.123,
        "node_id": "Node_1",
        "confidence": 0.85,
        "features": [...]
    }
]
```

#### `_retrain_model(signature: AnomalySignature) -> None`

**Description:**
Retrain the Isolation Forest model with new signature data to improve future detection accuracy.

**Process:**
1. Extract packet sizes from signature features
2. Combine with recent data buffer
3. Validate sufficient data for retraining
4. Fit model with combined dataset

**Requirements:**
- Minimum data points threshold (configurable)
- Valid numeric packet sizes in features
- Proper error handling for model fitting failures

### Agent Lifecycle

#### `step() -> None`

**Description:**
Main step method for the agent in the Mesa simulation framework implementing the perceive-decide-act cycle.

**Phases:**
1. **Perceive**: Generate traffic and detect anomalies
2. **Decide**: Generate signatures for detected anomalies
3. **Act**: Broadcast signatures and update local model
4. **Validate**: Poll and validate other agents' signatures

**Error Handling:**
- Comprehensive exception handling
- Continues execution on individual failures
- Detailed error logging for debugging

**Example:**
```python
# Manual step execution (normally called by Mesa framework)
agent.step()

# Check for new signatures generated
if hasattr(agent, 'last_signature'):
    print(f"Generated signature: {agent.last_signature.signature_id}")
```

### Utility Methods

#### `_generate_anomaly_ips(anomaly_indices: np.ndarray) -> List[str]`

**Description:**
Generate realistic IP addresses for detected anomalies for signature creation and tracking.

**Parameters:**
- `anomaly_indices` (np.ndarray): Array of indices where anomalies were detected

**Returns:**
List of IP addresses in format "192.168.1.X" where X is random between 1-255

#### `_extract_packet_sizes(features: List[Dict[str, Any]]) -> List[float]`

**Description:**
Extract numeric packet sizes from signature features for model retraining and analysis.

**Parameters:**
- `features` (List[Dict[str, Any]]): List of feature dictionaries

**Returns:**
List of float values representing packet sizes, filtering out invalid entries

**Error Handling:**
- Graceful handling of invalid packet size values
- Warning logs for malformed data
- Returns empty list for completely invalid input

### Performance Optimizations

#### Caching Strategy

The agent implements multiple caching layers for performance:

1. **Validation Cache**: Stores signature validation results
   - Maximum 100 entries with LRU-style eviction
   - Cache key generation from signature characteristics
   - Hit/miss statistics tracking

2. **Data Buffers**: Maintains recent data for validation
   - 100-point rolling buffer for recent traffic
   - Efficient similarity calculations
   - Memory-conscious storage

#### Computational Optimizations

- **Vectorized Operations**: Uses NumPy for efficient numerical computations
- **Early Termination**: Quick returns for invalid inputs
- **Similarity Calculations**: Optimized cosine similarity with zero-division protection
- **Memory Management**: Efficient data structure usage and cleanup

### Configuration Parameters

```python
# Agent configuration (set during initialization)
anomaly_threshold: float = -0.05      # Isolation Forest decision threshold
validation_failure_rate: float = 0.2  # Simulated validation failure probability
min_data_points: int = 10             # Minimum data for validation
```

### Integration with Simulation Framework

#### Mesa Integration

```python
from mesa import Model, Agent
from agents import AnomalyAgent

class CustomSimulation(Model):
    def __init__(self):
        super().__init__()
        self.agents = [AnomalyAgent(self) for _ in range(10)]

    def step(self):
        for agent in self.agents:
            agent.step()  # Calls AnomalyAgent.step()
```

#### Custom Agent Extension

```python
class CustomAnomalyAgent(AnomalyAgent):
    def __init__(self, model):
        super().__init__(model)
        self.custom_threshold = 0.1

    def custom_validation(self, signature):
        # Custom validation logic
        return super().validate_signature(signature) and self.custom_check(signature)
```

### Error Handling Patterns

#### Exception Types

- **ValueError**: Invalid input parameters or data
- **RuntimeError**: Critical system failures during broadcast
- **FileNotFoundError**: Missing blacklist file (handled gracefully)
- **json.JSONDecodeError**: Corrupted blacklist file (recreated)

#### Recovery Strategies

1. **File Operations**: Graceful handling of missing/corrupted files
2. **Model Operations**: Skip retraining on insufficient data
3. **Network Operations**: Continue on individual validation failures
4. **Cache Operations**: Automatic cleanup on cache overflow

### Best Practices

#### Performance Optimization

1. **Batch Processing**: Process multiple signatures together when possible
2. **Cache Monitoring**: Regularly check cache hit rates for optimization opportunities
3. **Memory Management**: Monitor data buffer sizes in long-running simulations
4. **Error Logging**: Use detailed logging for debugging and monitoring

#### Reliability Patterns

1. **Graceful Degradation**: Continue operation even when individual components fail
2. **Data Validation**: Always validate inputs before processing
3. **Resource Cleanup**: Ensure proper cleanup of file handles and resources
4. **State Consistency**: Maintain consistent internal state across operations

### Troubleshooting

#### Common Issues

**Low Validation Accuracy:**
- Check anomaly threshold settings
- Verify sufficient training data
- Monitor cache hit rates for optimization opportunities

**High Memory Usage:**
- Monitor data buffer sizes
- Check cache size limits
- Consider reducing batch sizes for large datasets

**File I/O Errors:**
- Verify file system permissions
- Check available disk space
- Monitor for concurrent access issues

**Model Retraining Failures:**
- Ensure sufficient data points available
- Validate feature data integrity
- Check for numeric overflow in calculations

### API Version History

- **v1.0**: Basic Mesa Agent implementation
- **v1.1**: Added data classes for type safety
- **v1.2**: Enhanced validation with caching
- **v1.3**: Performance optimizations and monitoring
- **v1.4**: Comprehensive error handling and recovery
- **v1.5**: Modern type hints and documentation