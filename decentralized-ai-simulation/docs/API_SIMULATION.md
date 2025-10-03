# Simulation Module API Documentation

## Overview

The `Simulation` class provides a comprehensive framework for running decentralized AI anomaly detection simulations using the Mesa framework. It manages agent coordination, consensus resolution, parallel execution, and comprehensive monitoring with enhanced type safety and modern patterns.

## Class: Simulation

### Constructor

```python
Simulation(num_agents: int = 100, seed: Optional[int] = None) -> None
```

**Description:**
Initialize the simulation model with enhanced configuration and resource management.

**Parameters:**
- `num_agents` (int): Number of agents in the simulation. Must be positive.
- `seed` (Optional[int]): Random seed for reproducibility.

**Raises:**
- `ValueError`: If `num_agents` is not positive or exceeds parallel threshold without proper configuration.

**Example:**
```python
from simulation import Simulation

# Create simulation with 50 agents
sim = Simulation(num_agents=50, seed=42)

# Create large simulation with parallel execution
large_sim = Simulation(num_agents=200, seed=123)
```

### Core Methods

#### `step() -> None`

**Description:**
Execute one simulation step with enhanced parallel processing and monitoring. This is the main simulation advancement method that coordinates all agents and resolves consensus.

**Workflow:**
1. Execute agent steps in parallel or sequential based on configuration
2. Collect validations from all agents
3. Resolve consensus for signatures
4. Record comprehensive metrics

**Performance:**
- Automatically scales execution strategy based on agent count
- Uses Ray for distributed execution when available
- ThreadPoolExecutor for concurrent processing
- Sequential execution with shuffling for smaller simulations

**Example:**
```python
# Single step execution
sim.step()

# Monitor step performance
stats = sim.get_simulation_stats()
print(f"Step {stats['step_count']} completed in {stats['avg_step_time']:.3f}s")
```

#### `run(steps: int = 100) -> None`

**Description:**
Run the simulation for a specified number of steps with enhanced monitoring and progress tracking.

**Parameters:**
- `steps` (int): Number of simulation steps to run. Must be a positive integer.

**Raises:**
- `ValueError`: If `steps` is not a positive integer.
- `KeyboardInterrupt`: If simulation is interrupted by user.

**Features:**
- Progress logging at 10% intervals
- ETA calculation for long-running simulations
- Automatic error recovery (configurable)
- Comprehensive final statistics

**Example:**
```python
# Run simulation for 1000 steps
sim.run(steps=1000)

# Run with error handling
try:
    sim.run(steps=500)
except KeyboardInterrupt:
    print("Simulation interrupted by user")
    stats = sim.get_simulation_stats()
    print(f"Completed {stats['step_count']} steps")
```

#### `resolve_consensus(all_validations: Dict[int, List[bool]]) -> None`

**Description:**
Resolve consensus for signatures with enhanced parallel processing and comprehensive validation.

**Parameters:**
- `all_validations` (Dict[int, List[bool]]): Dictionary mapping signature_id to list of boolean validations from all agents.

**Consensus Logic:**
- Requires majority approval (threshold = num_agents // 2 + 1)
- Updates all agents with confirmed signatures
- Records detailed consensus metrics

**Metrics Recorded:**
- `consensus_reached`: Binary indicator of consensus achievement
- `consensus_votes`: Number of positive validations
- `consensus_rate`: Ratio of positive to total validations

**Example:**
```python
# Manual consensus resolution
validations = {
    1: [True, True, False, True],    # 75% approval
    2: [True, False, False, False],  # 25% approval - no consensus
    3: [True, True, True, True, True] # 100% approval
}

sim.resolve_consensus(validations)
```

### Parallel Execution Methods

#### `_execute_agent_steps_parallel() -> None`

**Description:**
Execute agent steps using the most appropriate parallel execution strategy based on configuration and available resources.

**Execution Strategies:**
1. **Ray Distributed**: Uses Ray framework for true distributed execution across multiple nodes/processes
2. **ThreadPoolExecutor**: Uses concurrent.futures for multi-threaded execution
3. **Sequential with Shuffling**: Single-threaded execution with random agent ordering for fairness

**Configuration:**
- Automatically enabled when `num_agents > parallel_threshold` (default: 50)
- Ray initialization with CPU count optimization
- Thread pool sizing based on agent count

#### `_collect_validations_parallel() -> Dict[int, List[bool]]`

**Description:**
Collect validation results from all agents using parallel processing for improved performance.

**Returns:**
Dictionary mapping signature_id to list of boolean validation results from all agents.

**Performance Optimizations:**
- Parallel signature polling across all agents
- Efficient aggregation of validation results
- Memory-efficient processing of large validation sets

### Agent Management

#### `agent_step(agent: AnomalyAgent) -> None`

**Description:**
Wrapper for individual agent step execution with comprehensive error handling.

**Parameters:**
- `agent` (AnomalyAgent): The agent instance to execute.

**Error Handling:**
- Logs errors without stopping simulation
- Continues with remaining agents
- Records error metrics for monitoring

#### `agent_poll(agent: AnomalyAgent) -> List[ValidationResult]`

**Description:**
Wrapper for agent polling and validation with enhanced error handling and result processing.

**Parameters:**
- `agent` (AnomalyAgent): The agent instance to poll.

**Returns:**
List of `ValidationResult` objects containing validation outcomes.

**Error Handling:**
- Returns empty list on polling errors
- Logs detailed error information
- Continues simulation execution

### Resource Management

#### `cleanup() -> None`

**Description:**
Enhanced cleanup of simulation resources with proper error handling and logging.

**Cleanup Operations:**
1. Shutdown Ray distributed computing framework
2. Shutdown ThreadPoolExecutor and wait for completion
3. Record cleanup metrics and timing

**Error Handling:**
- Graceful handling of cleanup failures
- Warning logs for cleanup errors
- Ensures resources are properly released

#### `_finalize_run() -> None`

**Description:**
Finalize simulation run with comprehensive metrics collection and resource cleanup.

**Metrics Recorded:**
- `total_steps`: Total number of steps completed
- `total_runtime`: Total execution time in seconds
- `simulation_end_time`: Timestamp of completion
- `cleanup_time`: Time spent in cleanup operations

### Monitoring and Statistics

#### `get_simulation_stats() -> Dict[str, Any]`

**Description:**
Get comprehensive simulation statistics including performance metrics and current state.

**Returns:**
Dictionary containing:
- `step_count`: Current simulation step number
- `num_agents`: Total number of agents in simulation
- `threshold`: Consensus threshold for signature approval
- `use_parallel`: Whether parallel execution is enabled
- `runtime`: Total runtime since initialization
- `avg_step_time`: Average time per simulation step
- `ledger_size`: Number of entries in the simulation ledger

**Example:**
```python
stats = sim.get_simulation_stats()
print(f"Simulation Stats:")
print(f"  Steps: {stats['step_count']}")
print(f"  Agents: {stats['num_agents']}")
print(f"  Runtime: {stats['runtime']:.2f}s")
print(f"  Avg Step Time: {stats['avg_step_time']:.3f}s")
print(f"  Parallel: {stats['use_parallel']}")
```

### Configuration Integration

The Simulation class integrates with the configuration system for runtime parameter management:

```python
# Configuration keys used by Simulation:
simulation:
  use_parallel_threshold: 50    # Enable parallel execution above this threshold
  stop_on_error: false          # Whether to stop simulation on errors
database:
  path: "ledger.db"             # Database file path
  timeout: 30                   # Database connection timeout
  check_same_thread: false      # SQLite thread safety setting
```

### Error Handling and Recovery

#### Exception Types

- **ValueError**: Invalid parameters (negative agents, invalid steps)
- **KeyboardInterrupt**: User-initiated interruption
- **RuntimeError**: Critical system errors during execution
- **sqlite3.Error**: Database operation failures

#### Recovery Strategies

1. **Agent Step Failures**: Log error and continue with remaining agents
2. **Database Errors**: Retry transient errors, fail on permanent errors
3. **Resource Cleanup**: Graceful cleanup even on critical failures
4. **Parallel Execution**: Fallback to sequential execution on parallel failures

### Performance Characteristics

#### Scalability
- **Linear Scaling**: Performance scales linearly with agent count up to parallel threshold
- **Parallel Execution**: Significant performance improvements for large agent counts (>50)
- **Memory Efficient**: Optimized memory usage with connection pooling and caching

#### Monitoring Points
- Step execution time tracking
- Validation collection performance
- Consensus resolution metrics
- Resource cleanup timing

### Integration Patterns

#### With Mesa Framework
```python
from mesa.batchrunner import BatchRunner

# Use with Mesa batch runner for parameter sweeps
parameters = {"num_agents": range(10, 101, 10)}
batch_run = BatchRunner(
    Simulation,
    parameters,
    iterations=5,
    max_steps=100,
    model_reporters={"stats": lambda m: m.get_simulation_stats()}
)
```

#### With Custom Monitoring
```python
# Custom monitoring integration
class CustomMonitor:
    def record_metric(self, name: str, value: Any):
        # Custom monitoring logic
        pass

sim.monitoring = CustomMonitor()
```

### Best Practices

1. **Agent Count Selection**: Choose agent count based on available resources
   - Small simulations (≤50 agents): Sequential execution
   - Large simulations (>50 agents): Parallel execution recommended

2. **Error Handling**: Configure appropriate error handling based on use case
   - Development: Enable `stop_on_error` for debugging
   - Production: Disable `stop_on_error` for resilience

3. **Resource Management**: Always call `cleanup()` or use context managers
   ```python
   try:
       sim.run(steps=1000)
   finally:
       sim.cleanup()
   ```

4. **Monitoring**: Regularly check simulation statistics for performance optimization
   ```python
   if sim.step_count % 100 == 0:
       stats = sim.get_simulation_stats()
       if stats['avg_step_time'] > 1.0:  # Performance threshold
           logger.warning("Slow step performance detected")
   ```

### Troubleshooting

#### Common Issues

**High Memory Usage:**
- Reduce agent count or enable parallel execution
- Check database connection pool settings
- Monitor for memory leaks in custom agent implementations

**Slow Performance:**
- Enable parallel execution for large agent counts
- Check database performance and indexing
- Monitor system resource utilization

**Database Connection Errors:**
- Verify database file permissions
- Check available disk space
- Monitor connection pool exhaustion

**Ray Initialization Failures:**
- Ensure sufficient CPU cores available
- Check Ray installation and version compatibility
- Monitor system resource limits

### API Version History

- **v1.0**: Initial implementation with basic Mesa integration
- **v1.1**: Added parallel execution support
- **v1.2**: Enhanced monitoring and metrics collection
- **v1.3**: Improved error handling and resource management
- **v1.4**: Added comprehensive type hints and modern patterns