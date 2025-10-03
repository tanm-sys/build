# API Usage Examples and Troubleshooting

## Overview

This document provides comprehensive usage examples, practical patterns, and troubleshooting guidance for the core API modules in the decentralized AI simulation system. It includes real-world scenarios, best practices, and solutions to common issues.

## Simulation Module Examples

### Basic Simulation Setup

```python
from simulation import Simulation
import time

# Example 1: Basic simulation with 20 agents
def basic_simulation_example():
    """Demonstrate basic simulation setup and execution."""
    print("=== Basic Simulation Example ===")

    # Initialize simulation
    sim = Simulation(num_agents=20, seed=42)

    # Run simulation for 50 steps
    start_time = time.time()
    sim.run(steps=50)
    end_time = time.time()

    # Get final statistics
    stats = sim.get_simulation_stats()
    print(f"Simulation completed in {end_time - start_time".2f"}s")
    print(f"Final stats: {stats}")

    # Cleanup resources
    sim.cleanup()

# Example 2: Large-scale simulation with monitoring
def large_scale_simulation_example():
    """Demonstrate large-scale simulation with performance monitoring."""
    print("=== Large-Scale Simulation Example ===")

    # Create large simulation (will use parallel execution)
    sim = Simulation(num_agents=100, seed=123)

    try:
        # Monitor progress during execution
        for step in range(100):
            sim.step()

            # Check performance every 10 steps
            if step % 10 == 0:
                stats = sim.get_simulation_stats()
                print(f"Step {step}: {stats['avg_step_time']".3f"}s avg, "
                      f"Ledger size: {stats['ledger_size']}")

    except KeyboardInterrupt:
        print("Simulation interrupted by user")
    finally:
        sim.cleanup()
```

### Custom Simulation with Monitoring

```python
from simulation import Simulation
from monitoring import get_monitoring

class MonitoredSimulation(Simulation):
    """Custom simulation with enhanced monitoring."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_monitoring = get_monitoring()

    def step(self):
        """Override step with custom monitoring."""
        step_start = time.time()
        super().step()
        step_duration = time.time() - step_start

        # Custom metrics
        self.custom_monitoring.record_metric('custom_step_duration', step_duration)
        if step_duration > 1.0:
            self.custom_monitoring.record_metric('slow_steps', 1)
```

## Agent Module Examples

### Agent Lifecycle Management

```python
from agents import AnomalyAgent, TrafficData
import numpy as np

# Example 1: Manual agent operations
def agent_operations_example():
    """Demonstrate manual agent operations and data flow."""
    print("=== Agent Operations Example ===")

    # Create mock simulation model
    class MockModel:
        def __init__(self):
            from database import DatabaseLedger
            self.ledger = DatabaseLedger()

    # Create agent
    model = MockModel()
    agent = AnomalyAgent(model)

    print(f"Created agent: {agent.node_id}")

    # Generate traffic and detect anomalies
    traffic = agent.generate_traffic(batch_size=50, force_anomaly=True)
    print(f"Generated traffic: {len(traffic.data)} points, "
          f"anomaly: {traffic.has_anomaly}")

    # Detect anomalies
    has_anomaly, indices, data, ips, scores = agent.detect_anomaly(traffic)

    if has_anomaly:
        print(f"Detected anomalies at indices: {indices}")
        print(f"Anomaly IPs: {ips}")
        print(f"Anomaly scores: {scores}")

        # Generate and broadcast signature
        signature = agent.generate_signature(data, ips, scores)
        print(f"Generated signature with confidence: {signature.confidence".3f"}")

        agent.broadcast_signature(signature)
        print(f"Broadcast signature ID: {signature.signature_id}")
```

### Batch Processing Example

```python
# Example 2: Batch signature processing
def batch_processing_example():
    """Demonstrate efficient batch processing of signatures."""
    print("=== Batch Processing Example ===")

    model = MockModel()
    agent = AnomalyAgent(model)

    signatures = []
    validation_results = []

    # Generate multiple signatures
    for i in range(5):
        traffic = agent.generate_traffic(force_anomaly=True)
        has_anomaly, indices, data, ips, scores = agent.detect_anomaly(traffic)

        if has_anomaly:
            signature = agent.generate_signature(data, ips, scores)
            agent.broadcast_signature(signature)
            signatures.append(signature)

    print(f"Generated {len(signatures)} signatures")

    # Batch validation
    for signature in signatures:
        # Simulate other agents validating our signatures
        pass

    # Check cache performance
    cache_stats = agent.get_cache_stats()
    print(f"Cache performance: {cache_stats['hit_rate_percent']".1f"}% hit rate")
```

### Model Retraining Workflow

```python
# Example 3: Model retraining with new data
def model_retraining_example():
    """Demonstrate model retraining with confirmed signatures."""
    print("=== Model Retraining Example ===")

    model = MockModel()
    agent = AnomalyAgent(model)

    # Generate initial training data
    for _ in range(10):
        traffic = agent.generate_traffic()
        agent.step()  # This will train on any detected anomalies

    print("Initial training completed")

    # Simulate receiving confirmed signature from consensus
    confirmed_signature = type('MockSignature', (), {
        'timestamp': time.time(),
        'features': [{'packet_size': 600, 'source_ip': '192.168.1.200'}],
        'confidence': 0.9,
        'node_id': 'External_Node'
    })()

    # Update model with confirmed signature
    agent.update_model_and_blacklist(confirmed_signature)
    print("Model updated with confirmed signature")
```

## Database Module Examples

### Database Operations and Queries

```python
from database import DatabaseLedger, get_db_connection
import json

# Example 1: Comprehensive database operations
def database_operations_example():
    """Demonstrate comprehensive database operations."""
    print("=== Database Operations Example ===")

    # Create ledger
    ledger = DatabaseLedger()

    # Prepare sample entries
    entries = []
    for i in range(5):
        entry = {
            'timestamp': time.time() + i,
            'node_id': f'Node_{i % 3}',
            'features': [
                {'packet_size': 100 + i * 50, 'source_ip': f'192.168.1.{100 + i}'}
            ],
            'confidence': 0.5 + (i * 0.1)
        }
        entries.append(entry)

    # Batch insert entries
    entry_ids = []
    for entry in entries:
        entry_id = ledger.append_entry(entry)
        entry_ids.append(entry_id)
        print(f"Inserted entry {entry_id}: {entry['node_id']}")

    # Query operations
    print(f"\nTotal entries in ledger: {len(ledger.read_ledger())}")

    # Get entries by node
    node_entries = ledger.get_entries_by_node('Node_0', limit=2)
    print(f"Recent entries for Node_0: {len(node_entries)}")

    # Get specific entry
    entry = ledger.get_entry_by_id(entry_ids[0])
    if entry:
        print(f"Entry {entry_ids[0]}: {json.dumps(entry, indent=2)}")
```

### Connection Pool Management

```python
# Example 2: Connection pool usage patterns
def connection_pool_example():
    """Demonstrate proper connection pool usage."""
    print("=== Connection Pool Example ===")

    from database import get_connection_pool, get_db_connection

    # Get connection pool info
    pool = get_connection_pool()
    print(f"Pool max connections: {pool.config.max_connections}")

    # Pattern 1: Context manager (recommended)
    print("Using context manager:")
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM ledger")
        count = cursor.fetchone()[0]
        print(f"Current ledger entries: {count}")

    # Pattern 2: Manual connection management
    print("Manual connection management:")
    conn = pool.get_connection()
    try:
        cursor = conn.execute("SELECT node_id, COUNT(*) FROM ledger GROUP BY node_id")
        node_counts = cursor.fetchall()
        for node_id, count in node_counts:
            print(f"  {node_id}: {count} entries")
    finally:
        # Connection automatically managed by pool
        pass
```

### Performance Monitoring

```python
# Example 3: Database performance monitoring
def performance_monitoring_example():
    """Demonstrate database performance monitoring."""
    print("=== Performance Monitoring Example ===")

    ledger = DatabaseLedger()

    # Populate with test data
    for i in range(100):
        entry = {
            'timestamp': time.time() + i,
            'node_id': f'Node_{i % 10}',
            'features': [{'packet_size': 100 + i, 'source_ip': f'192.168.1.{i}'}],
            'confidence': 0.5 + (i % 5) * 0.1
        }
        ledger.append_entry(entry)

    # Test query performance
    import time

    # Full ledger read
    start = time.time()
    all_entries = ledger.read_ledger()
    read_time = time.time() - start
    print(f"Full ledger read ({len(all_entries)} entries): {read_time".3f"}s")

    # Node-specific query
    start = time.time()
    node_entries = ledger.get_entries_by_node('Node_0')
    query_time = time.time() - start
    print(f"Node query ({len(node_entries)} entries): {query_time".3f"}s")

    # New entries polling
    start = time.time()
    new_entries = ledger.get_new_entries(50)
    poll_time = time.time() - start
    print(f"New entries poll: {poll_time".3f"}s ({len(new_entries)} entries)")
```

## Integration Examples

### Complete Workflow Integration

```python
# Example 1: Complete simulation workflow
def complete_workflow_example():
    """Demonstrate complete workflow from simulation to consensus."""
    print("=== Complete Workflow Example ===")

    # Initialize components
    sim = Simulation(num_agents=5, seed=42)

    # Run simulation with monitoring
    for step in range(10):
        sim.step()

        # Monitor progress
        if step % 3 == 0:
            stats = sim.get_simulation_stats()
            print(f"Step {step}: {stats['step_count']} total, "
                  f"ledger size: {stats['ledger_size']}")

    # Analyze final results
    final_stats = sim.get_simulation_stats()
    print(f"\nFinal Statistics:")
    print(f"  Total steps: {final_stats['step_count']}")
    print(f"  Runtime: {final_stats['runtime']".2f"}s")
    print(f"  Avg step time: {final_stats['avg_step_time']".3f"}s")

    # Cleanup
    sim.cleanup()
```

### Multi-Agent Coordination

```python
# Example 2: Multi-agent coordination patterns
def multi_agent_coordination_example():
    """Demonstrate coordination between multiple agents."""
    print("=== Multi-Agent Coordination Example ===")

    # Create multiple agents with shared ledger
    class SharedModel:
        def __init__(self):
            from database import DatabaseLedger
            self.ledger = DatabaseLedger()

    model = SharedModel()
    agents = [AnomalyAgent(model) for _ in range(3)]

    print(f"Created {len(agents)} agents:")
    for agent in agents:
        print(f"  {agent.node_id}")

    # Simulate coordinated operation
    for round_num in range(3):
        print(f"\n--- Round {round_num + 1} ---")

        # Each agent generates traffic and potentially signatures
        for agent in agents:
            traffic = agent.generate_traffic(force_anomaly=True)
            has_anomaly, indices, data, ips, scores = agent.detect_anomaly(traffic)

            if has_anomaly:
                signature = agent.generate_signature(data, ips, scores)
                agent.broadcast_signature(signature)
                print(f"{agent.node_id}: Broadcast signature {signature.signature_id}")

        # All agents validate new signatures
        for agent in agents:
            validations = agent.poll_and_validate()
            print(f"{agent.node_id}: Validated {len(validations)} signatures")
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Simulation Issues

**Problem:** High memory usage during large simulations
```python
# Solution: Enable parallel execution and monitor resource usage
sim = Simulation(num_agents=200)  # Automatically uses parallel execution
stats = sim.get_simulation_stats()

# Monitor memory-intensive operations
if stats['avg_step_time'] > 2.0:
    print("Warning: High step latency detected")
    # Consider reducing agent count or optimizing detection thresholds
```

**Problem:** Slow simulation performance
```python
# Solution: Check configuration and enable appropriate execution mode
from config_loader import get_config

# Verify parallel execution is enabled for large agent counts
parallel_threshold = get_config('simulation.use_parallel_threshold', 50)
print(f"Parallel threshold: {parallel_threshold}")

# Force parallel execution if needed
sim.use_parallel = True
sim._initialize_parallel_execution()
```

#### Agent Issues

**Problem:** Low anomaly detection accuracy
```python
# Solution: Adjust detection parameters and retrain models
agent = AnomalyAgent(model)

# Lower threshold for more sensitive detection
agent.anomaly_threshold = -0.1  # Default: -0.05

# Ensure sufficient training data
if len(agent.recent_data) < agent.min_data_points:
    print("Warning: Insufficient training data")
    # Generate more training traffic
    for _ in range(10):
        traffic = agent.generate_traffic(batch_size=100)
        agent.detect_anomaly(traffic)  # Train model
```

**Problem:** Validation cache issues
```python
# Solution: Monitor and manage cache performance
agent = AnomalyAgent(model)

# Check cache statistics
stats = agent.get_cache_stats()
if stats['hit_rate_percent'] < 50:
    print("Low cache hit rate - consider cache tuning")
    # Cache will automatically manage size, but you can monitor

# Manual cache inspection if needed
print(f"Cache size: {stats['cache_size']}")
print(f"Hit rate: {stats['hit_rate_percent']:.1f}%")
```

#### Database Issues

**Problem:** Database connection errors
```python
# Solution: Proper connection management and error handling
from database import get_db_connection

try:
    with get_db_connection() as conn:
        # Database operations
        pass
except Exception as e:
    print(f"Database error: {e}")
    # Check if it's a transient error
    if "locked" in str(e).lower() or "busy" in str(e).lower():
        print("Transient error - operation can be retried")
    else:
        print("Persistent error - check database configuration")
```

**Problem:** Slow database queries
```python
# Solution: Optimize queries and check indexes
ledger = DatabaseLedger()

# Use appropriate query methods
start = time.time()

# Instead of reading entire ledger for new data:
# ledger.read_ledger()  # Avoid for large datasets

# Use targeted queries:
new_entries = ledger.get_new_entries(last_seen_id)
node_entries = ledger.get_entries_by_node(node_id, limit=100)

query_time = time.time() - start
print(f"Query time: {query_time:.3f}s")
```

### Performance Optimization Patterns

#### Memory Optimization

```python
# Pattern 1: Efficient data handling
def memory_efficient_processing():
    """Process large datasets without memory spikes."""

    # Use generators for large result sets
    def process_entries_batch(entries, batch_size=100):
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            yield process_batch(batch)

    # Process in batches
    all_entries = ledger.read_ledger()
    for processed_batch in process_entries_batch(all_entries):
        # Handle processed batch
        pass
```

#### Parallel Processing Optimization

```python
# Pattern 2: Optimal parallel execution
def optimize_parallel_execution():
    """Optimize parallel processing configuration."""

    # Check system capabilities
    import multiprocessing
    cpu_count = multiprocessing.cpu_count()
    print(f"Available CPUs: {cpu_count}")

    # Configure based on available resources
    if cpu_count > 4:
        # Use Ray for better distributed processing
        sim = Simulation(num_agents=100)
        # Ray will be automatically configured
    else:
        # Use ThreadPool for smaller systems
        sim = Simulation(num_agents=50)
        # Will use ThreadPoolExecutor

    return sim
```

### Debugging Patterns

#### Comprehensive Logging Setup

```python
import logging

def setup_debug_logging():
    """Set up comprehensive logging for debugging."""

    # Configure detailed logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create logger for debugging
    logger = logging.getLogger('debug_example')

    # Example usage in custom code
    sim = Simulation(num_agents=10)
    logger.info(f"Created simulation with {sim.num_agents} agents")

    return logger
```

#### Diagnostic Information Collection

```python
def collect_diagnostic_info():
    """Collect comprehensive diagnostic information."""

    from simulation import Simulation
    from agents import AnomalyAgent
    from database import DatabaseLedger

    sim = Simulation(num_agents=5)
    agent = AnomalyAgent(sim)
    ledger = DatabaseLedger()

    # Collect system information
    diagnostics = {
        'simulation': sim.get_simulation_stats(),
        'agent_cache': agent.get_cache_stats(),
        'ledger_size': len(ledger.read_ledger()),
        'timestamp': time.time()
    }

    # Save or log diagnostics
    print("=== Diagnostic Information ===")
    for category, data in diagnostics.items():
        print(f"{category}: {data}")

    return diagnostics
```

### Best Practices Summary

#### Error Handling Best Practices

1. **Always use context managers for database operations**
   ```python
   # Good
   with get_db_connection() as conn:
       # Database operations

   # Avoid
   conn = get_connection_pool().get_connection()
   # Risk of connection leaks
   ```

2. **Implement proper cleanup in all scenarios**
   ```python
   # Good
   try:
       sim.run(steps=100)
   except KeyboardInterrupt:
       print("Interrupted by user")
   finally:
       sim.cleanup()

   # Avoid
   sim.run(steps=100)
   # May leave resources allocated
   ```

3. **Validate all inputs before processing**
   ```python
   # Good
   if not isinstance(entry, dict) or 'timestamp' not in entry:
       raise ValueError("Invalid entry format")

   # Avoid
   ledger.append_entry(malformed_data)  # Will fail later
   ```

#### Performance Best Practices

1. **Use appropriate execution modes for agent count**
   ```python
   # Small simulations: Sequential is fine
   sim = Simulation(num_agents=10)

   # Large simulations: Parallel execution
   sim = Simulation(num_agents=100)  # Auto-enables parallel
   ```

2. **Monitor cache performance**
   ```python
   # Regular cache monitoring
   if step % 100 == 0:
       stats = agent.get_cache_stats()
       if stats['hit_rate_percent'] < 70:
           print("Cache performance degraded")
   ```

3. **Batch operations when possible**
   ```python
   # Batch multiple operations
   entries = prepare_multiple_entries()
   for entry in entries:
       ledger.append_entry(entry)
   ```

## Advanced Use Cases and Demonstrations

### Research and Development Scenarios

#### Scenario 1: Algorithm Comparison Study
```python
# Example: Comparing different anomaly detection algorithms
from simulation import Simulation
from agents import AnomalyAgent
import pandas as pd
import matplotlib.pyplot as plt

def algorithm_comparison_study():
    """Compare performance of different ML algorithms in distributed setting."""
    print("=== Algorithm Comparison Study ===")

    # Test different agent configurations
    configurations = [
        {"name": "Isolation Forest", "contamination": 0.1},
        {"name": "Isolation Forest", "contamination": 0.05},
        {"name": "Local Outlier Factor", "contamination": 0.1, "algorithm": "LOF"},
    ]

    results = []

    for config in configurations:
        print(f"\nTesting configuration: {config['name']}")

        # Create custom agent class for this configuration
        class CustomAnomalyAgent(AnomalyAgent):
            def __init__(self, model, **kwargs):
                super().__init__(model, **kwargs)
                self.algorithm_config = config

        # Run simulation with this configuration
        sim = Simulation(num_agents=20, seed=42)

        # Override agents with custom configuration
        for agent in sim.node_agents:
            agent.algorithm_config = config

        # Run simulation
        sim.run(steps=100)

        # Collect results
        stats = sim.get_simulation_stats()
        results.append({
            'algorithm': config['name'],
            'config': config,
            'runtime': stats['runtime'],
            'avg_step_time': stats['avg_step_time'],
            'ledger_size': stats['ledger_size']
        })

        sim.cleanup()

    # Analyze and visualize results
    results_df = pd.DataFrame(results)
    print("\n=== Results Summary ===")
    print(results_df.to_string(index=False))

    return results_df
```

#### Scenario 2: Scalability Testing
```python
# Example: Testing system scalability across different agent counts
def scalability_testing():
    """Test system performance across different scales."""
    print("=== Scalability Testing ===")

    agent_counts = [10, 25, 50, 100, 200]
    results = []

    for num_agents in agent_counts:
        print(f"\nTesting with {num_agents} agents...")

        start_time = time.time()

        # Create simulation
        sim = Simulation(num_agents=num_agents, seed=42)

        # Run for fixed number of steps
        steps = 50 if num_agents <= 50 else 25  # Fewer steps for larger simulations
        sim.run(steps=steps)

        # Record metrics
        runtime = time.time() - start_time
        stats = sim.get_simulation_stats()

        results.append({
            'agents': num_agents,
            'steps': steps,
            'total_runtime': runtime,
            'avg_step_time': stats['avg_step_time'],
            'ledger_size': stats['ledger_size'],
            'parallel_used': stats['use_parallel']
        })

        print(f"Completed in {runtime:.2f}s ({stats['avg_step_time']:.3f}s avg step)")
        sim.cleanup()

    # Return results for analysis
    return pd.DataFrame(results)
```

### Educational Applications

#### Interactive Learning Environment
```python
# Example: Interactive web-based learning environment
import streamlit as st
from simulation import Simulation
import plotly.graph_objects as go
import time

def create_learning_environment():
    """Create an interactive learning environment for students."""
    print("=== Interactive Learning Environment ===")

    st.title("Decentralized AI Simulation - Learning Environment")
    st.sidebar.header("Simulation Controls")

    # Sidebar controls
    num_agents = st.sidebar.slider("Number of Agents", 5, 50, 10)
    steps = st.sidebar.slider("Simulation Steps", 10, 200, 50)
    anomaly_rate = st.sidebar.slider("Anomaly Rate", 0.01, 0.2, 0.05)

    if st.sidebar.button("Run Simulation"):
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Create and run simulation
        sim = Simulation(num_agents=num_agents, seed=42)

        with st.expander("Simulation Progress", expanded=True):
            progress_container = st.container()

        # Run simulation step by step for visualization
        for step in range(steps):
            start_time = time.time()
            sim.step()
            step_time = time.time() - start_time

            # Update progress
            progress = (step + 1) / steps
            progress_bar.progress(progress)

            # Get current stats
            stats = sim.get_simulation_stats()

            # Update status
            status_text.text(f"Step {step + 1}/{steps} - "
                           f"Avg: {stats['avg_step_time']:.3f}s, "
                           f"Ledger: {stats['ledger_size']} entries")

            # Real-time metrics display
            with progress_container:
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Step", stats['step_count'])
                col2.metric("Avg Step Time", f"{stats['avg_step_time']:.3f}s")
                col3.metric("Ledger Size", stats['ledger_size'])

            time.sleep(0.1)  # Small delay for visualization

        # Final results
        st.success("Simulation completed!")

        # Display final statistics
        final_stats = sim.get_simulation_stats()
        st.subheader("Final Results")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Steps", final_stats['step_count'])
        col2.metric("Total Runtime", f"{final_stats['runtime']:.2f}s")
        col3.metric("Avg Step Time", f"{final_stats['avg_step_time']:.3f}s")
        col4.metric("Ledger Entries", final_stats['ledger_size'])

        sim.cleanup()

    return sim if 'sim' in locals() else None
```

#### Curriculum Integration Example
```python
# Example: University course integration
def university_course_integration():
    """Example integration for computer science courses."""
    print("=== University Course Integration ===")

    # Week 1: Basic concepts
    def week1_basic_concepts():
        """Introduction to decentralized AI concepts."""
        st.header("Week 1: Basic Concepts")

        st.markdown("""
        **Learning Objectives:**
        - Understand decentralized AI principles
        - Learn about anomaly detection
        - Explore consensus mechanisms
        """)

        # Simple demonstration
        if st.button("Run Basic Demo"):
            sim = Simulation(num_agents=5, seed=42)
            sim.run(steps=20)

            stats = sim.get_simulation_stats()
            st.json(stats)

            sim.cleanup()

    # Week 2: Agent behavior
    def week2_agent_behavior():
        """Deep dive into agent behavior and configuration."""
        st.header("Week 2: Agent Behavior")

        # Interactive agent configuration
        contamination = st.slider("Contamination Rate", 0.01, 0.5, 0.1)
        threshold = st.slider("Detection Threshold", -1.0, 1.0, -0.05)

        if st.button("Test Agent Configuration"):
            # Custom agent with specific configuration
            class ConfigurableAgent(AnomalyAgent):
                def __init__(self, model):
                    super().__init__(model)
                    self.contamination = contamination
                    self.threshold = threshold

            st.info(f"Testing with contamination={contamination}, threshold={threshold}")

    # Week 3: Performance analysis
    def week3_performance_analysis():
        """Performance analysis and optimization."""
        st.header("Week 3: Performance Analysis")

        # Comparative analysis
        sizes = [10, 25, 50]
        results = []

        for size in sizes:
            sim = Simulation(num_agents=size, seed=42)
            sim.run(steps=30)

            stats = sim.get_simulation_stats()
            results.append({
                'agents': size,
                'runtime': stats['runtime'],
                'avg_step': stats['avg_step_time']
            })

            sim.cleanup()

        # Display results
        st.line_chart(pd.DataFrame(results).set_index('agents'))

    return {
        'week1': week1_basic_concepts,
        'week2': week2_agent_behavior,
        'week3': week3_performance_analysis
    }
```

### Production Deployment Patterns

#### Enterprise Deployment Example
```python
# Example: Enterprise-grade deployment with monitoring
import logging
from monitoring import get_monitoring
import json

def enterprise_deployment():
    """Enterprise-grade deployment with comprehensive monitoring."""
    print("=== Enterprise Deployment ===")

    # Configure enterprise logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/enterprise_simulation.log'),
            logging.StreamHandler()
        ]
    )

    # Initialize monitoring
    monitoring = get_monitoring()
    monitoring.record_metric('deployment_start', time.time())

    # Production configuration
    config = {
        'simulation': {
            'num_agents': 100,
            'steps': 1000,
            'parallel_threshold': 50,
            'checkpoint_interval': 100
        },
        'database': {
            'connection_pool_size': 20,
            'timeout': 60,
            'retry_attempts': 3
        },
        'monitoring': {
            'health_check_interval': 30,
            'metrics_retention_days': 7,
            'alert_thresholds': {
                'max_step_time': 2.0,
                'max_memory_usage': 80,
                'min_consensus_rate': 0.7
            }
        }
    }

    # Save configuration
    with open('config/production.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("Production configuration saved")

    # Initialize simulation with production settings
    sim = Simulation(num_agents=config['simulation']['num_agents'], seed=42)

    # Production monitoring setup
    class ProductionMonitor:
        def __init__(self, monitoring, config):
            self.monitoring = monitoring
            self.config = config
            self.start_time = time.time()

        def check_health(self, sim):
            """Production health checks."""
            stats = sim.get_simulation_stats()

            # Check step time
            if stats['avg_step_time'] > self.config['monitoring']['alert_thresholds']['max_step_time']:
                monitoring.record_metric('alert_step_time', stats['avg_step_time'])

            # Check ledger growth
            if stats['ledger_size'] > 10000:  # Example threshold
                monitoring.record_metric('alert_ledger_size', stats['ledger_size'])

            return stats

    monitor = ProductionMonitor(monitoring, config)

    # Production run with monitoring
    try:
        for step in range(config['simulation']['steps']):
            sim.step()

            # Health check every 50 steps
            if step % 50 == 0:
                health = monitor.check_health(sim)
                print(f"Step {step}: Health OK - {health['avg_step_time']:.3f}s avg")

                # Checkpoint if configured
                if step % config['simulation']['checkpoint_interval'] == 0:
                    print(f"Checkpoint at step {step}")

    except Exception as e:
        logging.error(f"Production simulation failed: {e}")
        monitoring.record_metric('simulation_failure', 1)
        raise
    finally:
        sim.cleanup()
        monitoring.record_metric('deployment_end', time.time())

    return sim
```

#### Microservices Integration Pattern
```python
# Example: Integration with microservices architecture
from flask import Flask, jsonify, request
import threading
import queue

def microservices_integration():
    """Integration pattern for microservices architecture."""
    print("=== Microservices Integration ===")

    app = Flask(__name__)

    # Shared simulation state
    simulation_state = {
        'simulation': None,
        'is_running': False,
        'step_count': 0,
        'results_queue': queue.Queue()
    }

    @app.route('/api/simulation/start', methods=['POST'])
    def start_simulation():
        """Start a new simulation."""
        if simulation_state['is_running']:
            return jsonify({'error': 'Simulation already running'}), 409

        data = request.get_json()
        num_agents = data.get('num_agents', 50)
        steps = data.get('steps', 100)

        # Start simulation in background thread
        def run_simulation():
            try:
                sim = Simulation(num_agents=num_agents, seed=42)
                simulation_state['simulation'] = sim
                simulation_state['is_running'] = True

                for step in range(steps):
                    sim.step()
                    simulation_state['step_count'] = step + 1

                    # Report progress
                    if step % 10 == 0:
                        stats = sim.get_simulation_stats()
                        simulation_state['results_queue'].put({
                            'step': step,
                            'stats': stats
                        })

                simulation_state['is_running'] = False
                sim.cleanup()

            except Exception as e:
                simulation_state['is_running'] = False
                simulation_state['results_queue'].put({
                    'error': str(e)
                })

        thread = threading.Thread(target=run_simulation)
        thread.daemon = True
        thread.start()

        return jsonify({'message': 'Simulation started', 'steps': steps})

    @app.route('/api/simulation/status', methods=['GET'])
    def get_simulation_status():
        """Get current simulation status."""
        if not simulation_state['simulation']:
            return jsonify({'status': 'No simulation running'})

        stats = simulation_state['simulation'].get_simulation_stats()
        return jsonify({
            'status': 'running' if simulation_state['is_running'] else 'completed',
            'step_count': simulation_state['step_count'],
            'stats': stats
        })

    @app.route('/api/simulation/results', methods=['GET'])
    def get_simulation_results():
        """Get simulation results."""
        results = []
        while not simulation_state['results_queue'].empty():
            try:
                result = simulation_state['results_queue'].get_nowait()
                results.append(result)
            except queue.Empty:
                break

        return jsonify({'results': results})

    @app.route('/api/simulation/stop', methods=['POST'])
    def stop_simulation():
        """Stop the current simulation."""
        if simulation_state['simulation'] and simulation_state['is_running']:
            simulation_state['simulation'].cleanup()
            simulation_state['is_running'] = False
            return jsonify({'message': 'Simulation stopped'})

        return jsonify({'message': 'No simulation to stop'})

    return app
```

### Edge Computing Implementations

#### Resource-Constrained Deployment
```python
# Example: Deployment on edge devices with limited resources
import psutil
import os

def edge_computing_deployment():
    """Optimized deployment for edge computing environments."""
    print("=== Edge Computing Deployment ===")

    # Detect system resources
    memory = psutil.virtual_memory()
    cpu_count = os.cpu_count() or 1

    print(f"System Resources: {memory.total // (1024**3)}GB RAM, {cpu_count} CPUs")

    # Adaptive configuration based on available resources
    if memory.total < 2 * (1024**3):  # Less than 2GB RAM
        config = {
            'simulation': {
                'num_agents': min(10, cpu_count * 2),
                'steps': 50,
                'parallel_threshold': 5,
                'enable_ray': False
            },
            'database': {
                'connection_pool_size': 2,
                'cache_size': 10
            },
            'monitoring': {
                'health_check_interval': 60,
                'enable_detailed_metrics': False
            }
        }
    else:  # More resources available
        config = {
            'simulation': {
                'num_agents': min(25, cpu_count * 3),
                'steps': 100,
                'parallel_threshold': 10,
                'enable_ray': cpu_count >= 4
            },
            'database': {
                'connection_pool_size': 5,
                'cache_size': 50
            },
            'monitoring': {
                'health_check_interval': 30,
                'enable_detailed_metrics': True
            }
        }

    print(f"Adaptive configuration: {config['simulation']['num_agents']} agents")

    # Create simulation with resource-optimized settings
    sim = Simulation(num_agents=config['simulation']['num_agents'], seed=42)

    # Resource monitoring during execution
    def monitor_resources():
        """Monitor system resources during simulation."""
        while sim.step_count < config['simulation']['steps']:
            memory_usage = psutil.virtual_memory().percent
            cpu_usage = psutil.cpu_percent(interval=1)

            if memory_usage > 80:
                print(f"Warning: High memory usage ({memory_usage}%)")
                break

            if cpu_usage > 90:
                print(f"Warning: High CPU usage ({cpu_usage}%)")
                time.sleep(1)  # Brief pause to reduce load

            time.sleep(5)

    # Start resource monitoring in background thread
    monitor_thread = threading.Thread(target=monitor_resources)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Run simulation
    sim.run(steps=config['simulation']['steps'])

    # Final resource check
    final_memory = psutil.virtual_memory().percent
    final_cpu = psutil.cpu_percent(interval=1)

    print(f"Final resource usage - Memory: {final_memory}%, CPU: {final_cpu}%")

    sim.cleanup()

    return config
```

#### IoT Device Simulation
```python
# Example: Simulating IoT device networks
def iot_device_simulation():
    """Simulation of IoT device network with constrained resources."""
    print("=== IoT Device Simulation ===")

    # IoT device characteristics
    iot_devices = [
        {'id': 'sensor_1', 'type': 'temperature', 'location': 'building_a'},
        {'id': 'sensor_2', 'type': 'humidity', 'location': 'building_a'},
        {'id': 'sensor_3', 'type': 'motion', 'location': 'building_b'},
        {'id': 'sensor_4', 'type': 'temperature', 'location': 'building_b'},
        {'id': 'gateway_1', 'type': 'gateway', 'location': 'building_a'},
        {'id': 'gateway_2', 'type': 'gateway', 'location': 'building_b'}
    ]

    # Create specialized agents for IoT devices
    class IoTSensorAgent(AnomalyAgent):
        def __init__(self, model, device_info):
            super().__init__(model)
            self.device_info = device_info
            self.node_id = device_info['id']
            self.device_type = device_info['type']

            # IoT-specific configuration
            self.battery_level = 100
            self.signal_strength = 85
            self.data_rate = 10  # packets per step

        def generate_traffic(self, batch_size=None, force_anomaly=False):
            """Generate IoT-specific traffic patterns."""
            if batch_size is None:
                batch_size = self.data_rate

            # Simulate battery drain
            self.battery_level = max(0, self.battery_level - 0.1)

            # Generate location and device-specific patterns
            base_traffic = super().generate_traffic(batch_size, force_anomaly)

            # Add IoT-specific metadata
            for packet in base_traffic.data:
                packet.update({
                    'device_type': self.device_type,
                    'location': self.device_info['location'],
                    'battery_level': self.battery_level,
                    'signal_strength': self.signal_strength
                })

            return base_traffic

    # Create IoT simulation
    sim = Simulation(num_agents=len(iot_devices), seed=42)

    # Replace default agents with IoT agents
    for i, agent in enumerate(sim.node_agents):
        iot_agent = IoTSensorAgent(sim, iot_devices[i])
        sim.node_agents[i] = iot_agent

    print(f"Created IoT simulation with {len(iot_devices)} devices")

    # Run IoT-specific simulation
    for step in range(100):
        sim.step()

        # IoT-specific monitoring
        if step % 20 == 0:
            low_battery_devices = []
            for agent in sim.node_agents:
                if isinstance(agent, IoTSensorAgent) and agent.battery_level < 20:
                    low_battery_devices.append(agent.node_id)

            if low_battery_devices:
                print(f"Low battery warning: {low_battery_devices}")

    # IoT analytics
    final_stats = sim.get_simulation_stats()
    print(f"\nIoT Simulation Results:")
    print(f"  Total steps: {final_stats['step_count']}")
    print(f"  Ledger entries: {final_stats['ledger_size']}")
    print(f"  Runtime: {final_stats['runtime']:.2f}s")

    # Device-specific statistics
    device_stats = {}
    for agent in sim.node_agents:
        if isinstance(agent, IoTSensorAgent):
            device_stats[agent.node_id] = {
                'type': agent.device_type,
                'battery_level': agent.battery_level,
                'packets_sent': agent.data_rate * final_stats['step_count']
            }

    print(f"\nDevice Statistics:")
    for device_id, stats in device_stats.items():
        print(f"  {device_id}: {stats['type']}, "
              f"Battery: {stats['battery_level']:.1f}%, "
              f"Packets: {stats['packets_sent']}")

    sim.cleanup()

    return device_stats
```

## Hands-On Code Examples with Detailed Explanations

### Complete Working Examples

#### Example 1: Basic Simulation with Detailed Monitoring
```python
"""
Complete working example: Basic simulation setup with comprehensive monitoring
and visualization. This example demonstrates the full lifecycle of a simulation
from initialization through execution to results analysis.
"""

import time
import json
from datetime import datetime
from simulation import Simulation
from monitoring import get_monitoring
import matplotlib.pyplot as plt

def comprehensive_simulation_example():
    """
    Complete simulation example with detailed monitoring and analysis.

    This function demonstrates:
    1. Simulation initialization with custom configuration
    2. Real-time monitoring during execution
    3. Progress tracking and performance metrics
    4. Results analysis and visualization
    5. Resource cleanup and reporting
    """
    print("🚀 Starting Comprehensive Simulation Example")
    print("=" * 60)

    # Configuration for the example
    config = {
        'simulation': {
            'num_agents': 25,
            'steps': 100,
            'seed': 42,
            'parallel_threshold': 20
        },
        'monitoring': {
            'progress_interval': 10,  # Log progress every 10 steps
            'detailed_metrics': True
        }
    }

    print(f"📋 Configuration: {json.dumps(config, indent=2)}")

    # Initialize monitoring
    monitoring = get_monitoring()
    start_time = time.time()

    # Step 1: Initialize simulation
    print("
🔧 Step 1: Initializing simulation..."    sim_start = time.time()
    sim = Simulation(
        num_agents=config['simulation']['num_agents'],
        seed=config['simulation']['seed']
    )
    sim_init_time = time.time() - sim_start

    print(f"   ✓ Simulation initialized in {sim_init_time:.3f}s")
    print(f"   ✓ Agents: {sim.num_agents}")
    print(f"   ✓ Parallel execution: {sim.use_parallel}")
    print(f"   ✓ Consensus threshold: {sim.threshold}")

    # Step 2: Execute simulation with monitoring
    print("
⚡ Step 2: Running simulation..."    execution_start = time.time()

    # Monitoring data collection
    step_times = []
    ledger_sizes = []
    validation_counts = []

    try:
        for step in range(config['simulation']['steps']):
            # Execute one step
            step_start = time.time()
            sim.step()
            step_time = time.time() - step_start
            step_times.append(step_time)

            # Collect metrics every 10 steps
            if step % config['monitoring']['progress_interval'] == 0:
                stats = sim.get_simulation_stats()
                ledger_sizes.append(stats['ledger_size'])

                # Get validation count from monitoring
                validation_count = monitoring.get_metric('validation_count', 0)
                validation_counts.append(validation_count)

                # Progress report
                progress = (step + 1) / config['simulation']['steps']
                elapsed = time.time() - execution_start
                eta = (elapsed / progress) - elapsed if progress > 0 else 0

                print(f"   📊 Step {step + 1"3d"}/{config['simulation']['steps']"3d"} "
                      f"({progress".1%"}) - "
                      f"Step: {step_time".3f"}s, "
                      f"Ledger: {stats['ledger_size']"3d"}, "
                      f"ETA: {eta".1f"}s")

    except KeyboardInterrupt:
        print("
⏹️  Simulation interrupted by user"        interrupted = True
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
        raise
    else:
        interrupted = False

    execution_time = time.time() - execution_start

    # Step 3: Analyze results
    print("
📈 Step 3: Analyzing results..."
    final_stats = sim.get_simulation_stats()

    print("   📋 Final Statistics:"    print(f"      Total steps: {final_stats['step_count']}")
    print(f"      Total runtime: {final_stats['runtime']".3f"}s")
    print(f"      Average step time: {final_stats['avg_step_time']".3f"}s")
    print(f"      Final ledger size: {final_stats['ledger_size']}")
    print(f"      Parallel execution used: {final_stats['use_parallel']}")

    # Performance analysis
    if step_times:
        avg_step_time = sum(step_times) / len(step_times)
        max_step_time = max(step_times)
        min_step_time = min(step_times)

        print("
   ⚡ Performance Analysis:"        print(f"      Average step time: {avg_step_time".3f"}s")
        print(f"      Fastest step: {min_step_time".3f"}s")
        print(f"      Slowest step: {max_step_time".3f"}s")
        print(f"      Steps monitored: {len(step_times)}")

    # Step 4: Visualization (optional)
    print("
📊 Step 4: Generating visualizations..."
    try:
        # Simple performance chart
        plt.figure(figsize=(10, 6))

        # Plot step times
        if step_times:
            plt.subplot(2, 2, 1)
            plt.plot(step_times, 'b-', alpha=0.7)
            plt.title('Step Execution Times')
            plt.xlabel('Step Number')
            plt.ylabel('Time (seconds)')
            plt.grid(True, alpha=0.3)

        # Plot ledger growth
        if ledger_sizes:
            plt.subplot(2, 2, 2)
            plt.plot(range(0, len(ledger_sizes) * config['monitoring']['progress_interval'],
                         config['monitoring']['progress_interval']),
                    ledger_sizes, 'g-', marker='o')
            plt.title('Ledger Size Growth')
            plt.xlabel('Step Number')
            plt.ylabel('Ledger Entries')
            plt.grid(True, alpha=0.3)

        # Plot validation counts
        if validation_counts:
            plt.subplot(2, 2, 3)
            plt.bar(range(len(validation_counts)), validation_counts, color='orange', alpha=0.7)
            plt.title('Validation Activity')
            plt.xlabel('Progress Interval')
            plt.ylabel('Validations')
            plt.grid(True, alpha=0.3)

        # Summary statistics
        plt.subplot(2, 2, 4)
        summary_data = ['Init', 'Execution', 'Total']
        summary_times = [sim_init_time, execution_time, time.time() - start_time]
        plt.pie(summary_times, labels=summary_data, autopct='%1.1f%%')
        plt.title('Time Distribution')

        plt.tight_layout()
        plt.savefig('simulation_analysis.png', dpi=150, bbox_inches='tight')
        print("   ✓ Visualization saved as 'simulation_analysis.png'")

    except ImportError:
        print("   ⚠️  Matplotlib not available for visualization")
    except Exception as e:
        print(f"   ⚠️  Visualization error: {e}")

    # Step 5: Cleanup and reporting
    print("
🧹 Step 5: Cleanup and final reporting..."
    cleanup_start = time.time()
    sim.cleanup()
    cleanup_time = time.time() - cleanup_start

    print(f"   ✓ Cleanup completed in {cleanup_time:.3f"}s")

    # Final summary
    total_time = time.time() - start_time
    print("
🎉 Simulation completed successfully!"    print(f"   Total execution time: {total_time:.3f".3f"conds")
    print(f"   Simulation efficiency: {final_stats['step_count']/total_time".2f"} steps/second")

    if not interrupted:
        print("   Status: Completed all requested steps")
    else:
        print("   Status: Interrupted by user")

    # Return comprehensive results
    results = {
        'configuration': config,
        'execution_stats': final_stats,
        'performance_metrics': {
            'total_time': total_time,
            'execution_time': execution_time,
            'init_time': sim_init_time,
            'cleanup_time': cleanup_time,
            'avg_step_time': avg_step_time if step_times else 0,
            'steps_per_second': final_stats['step_count'] / total_time if total_time > 0 else 0
        },
        'monitoring_data': {
            'step_times': step_times,
            'ledger_sizes': ledger_sizes,
            'validation_counts': validation_counts
        },
        'success': not interrupted,
        'timestamp': datetime.now().isoformat()
    }

    # Save results to file
    with open('simulation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("   ✓ Results saved to 'simulation_results.json'")

    return results

# Run the example
if __name__ == "__main__":
    results = comprehensive_simulation_example()
```

#### Example 2: Custom Agent Development
```python
"""
Advanced example: Creating custom agents with specialized behavior.
This demonstrates how to extend the base agent functionality for specific use cases.
"""

from agents import AnomalyAgent, TrafficData
from simulation import Simulation
import numpy as np
from typing import List, Dict, Any
import random

class CustomSecurityAgent(AnomalyAgent):
    """
    Custom agent with specialized security monitoring capabilities.

    This example demonstrates:
    1. Extending base agent functionality
    2. Adding domain-specific detection logic
    3. Implementing custom signature generation
    4. Specialized model training and updates
    """

    def __init__(self, model, security_domain: str = "network"):
        """
        Initialize custom security agent.

        Args:
            model: The simulation model
            security_domain: Specialized security domain focus
        """
        super().__init__(model)
        self.security_domain = security_domain
        self.domain_expertise = 0.0  # Domain knowledge level
        self.specialized_patterns = []  # Domain-specific patterns
        self.detection_history = []  # Track detection performance

        print(f"🔒 Initialized {security_domain} security agent: {self.node_id}")

    def generate_traffic(self, batch_size: int = 50, force_anomaly: bool = False) -> TrafficData:
        """
        Generate domain-specific traffic patterns.

        This override demonstrates how to create specialized traffic
        that reflects real-world scenarios in the chosen security domain.
        """
        # Base traffic generation
        traffic = super().generate_traffic(batch_size, force_anomaly)

        # Add domain-specific characteristics
        if self.security_domain == "web":
            # Web-specific patterns
            for packet in traffic.data:
                packet.update({
                    'http_method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                    'user_agent': self._generate_user_agent(),
                    'endpoint': self._generate_endpoint(),
                    'content_type': random.choice(['application/json', 'text/html', 'application/xml'])
                })

        elif self.security_domain == "network":
            # Network-specific patterns
            for packet in traffic.data:
                packet.update({
                    'protocol': random.choice(['TCP', 'UDP', 'ICMP']),
                    'port': random.choice([80, 443, 22, 3389, random.randint(1024, 65535)]),
                    'ttl': random.randint(64, 255),
                    'flags': self._generate_tcp_flags()
                })

        elif self.security_domain == "iot":
            # IoT-specific patterns
            for packet in traffic.data:
                packet.update({
                    'device_type': random.choice(['sensor', 'actuator', 'gateway']),
                    'battery_level': random.randint(0, 100),
                    'signal_strength': random.randint(0, 100),
                    'firmware_version': f"v{random.randint(1, 5)}.{random.randint(0, 9)}"
                })

        return traffic

    def _generate_user_agent(self) -> str:
        """Generate realistic user agent strings."""
        browsers = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        return random.choice(browsers)

    def _generate_endpoint(self) -> str:
        """Generate realistic API endpoints."""
        endpoints = ['/api/users', '/api/data', '/api/auth', '/api/reports', '/api/admin']
        return random.choice(endpoints)

    def _generate_tcp_flags(self) -> str:
        """Generate realistic TCP flag combinations."""
        flags = ['SYN', 'ACK', 'PSH', 'URG', 'FIN', 'RST']
        return ''.join(random.sample(flags, random.randint(1, 3)))

    def detect_anomaly(self, traffic: TrafficData) -> tuple:
        """
        Enhanced anomaly detection with domain expertise.

        This demonstrates how to combine base detection with
        domain-specific rules and expertise.
        """
        # Base anomaly detection
        has_anomaly, indices, data, ips, scores = super().detect_anomaly(traffic)

        # Apply domain-specific rules
        if self.security_domain == "web":
            # Web-specific anomaly rules
            web_anomalies = self._detect_web_anomalies(traffic)
            if web_anomalies:
                has_anomaly = True
                indices.extend([i for i, _ in web_anomalies])
                scores.extend([score for _, score in web_anomalies])

        elif self.security_domain == "network":
            # Network-specific anomaly rules
            network_anomalies = self._detect_network_anomalies(traffic)
            if network_anomalies:
                has_anomaly = True
                indices.extend([i for i, _ in network_anomalies])
                scores.extend([score for _, score in network_anomalies])

        # Update detection history
        self.detection_history.append({
            'timestamp': time.time(),
            'has_anomaly': has_anomaly,
            'anomalies_detected': len(indices) if has_anomaly else 0,
            'domain': self.security_domain
        })

        return has_anomaly, list(set(indices)), data, ips, scores

    def _detect_web_anomalies(self, traffic: TrafficData) -> List[tuple]:
        """Detect web-specific anomalies."""
        anomalies = []

        for i, packet in enumerate(traffic.data):
            # Rule 1: Unusual HTTP methods in combination
            if packet.get('http_method') == 'DELETE' and packet.get('packet_size', 0) > 1000:
                anomalies.append((i, 0.8))

            # Rule 2: Suspicious user agents
            user_agent = packet.get('user_agent', '')
            if 'bot' in user_agent.lower() or 'crawler' in user_agent.lower():
                anomalies.append((i, 0.7))

            # Rule 3: Admin endpoints with large payloads
            if 'admin' in packet.get('endpoint', '') and packet.get('packet_size', 0) > 500:
                anomalies.append((i, 0.9))

        return anomalies

    def _detect_network_anomalies(self, traffic: TrafficData) -> List[tuple]:
        """Detect network-specific anomalies."""
        anomalies = []

        for i, packet in enumerate(traffic.data):
            # Rule 1: Unusual port activity
            port = packet.get('port', 0)
            if port in [22, 3389] and packet.get('packet_size', 0) > 10000:  # SSH/RDP with large data
                anomalies.append((i, 0.8))

            # Rule 2: Low TTL with high packet count (potential routing anomaly)
            if packet.get('ttl', 255) < 32 and packet.get('packet_size', 0) < 100:
                anomalies.append((i, 0.6))

            # Rule 3: SYN flood indicators
            if packet.get('flags', '') == 'SYN' and packet.get('packet_size', 0) == 40:
                anomalies.append((i, 0.7))

        return anomalies

    def generate_signature(self, anomaly_data: List[Dict], anomaly_ips: List[str],
                          anomaly_scores: List[float]) -> 'ThreatSignature':
        """
        Generate domain-specific threat signatures.

        This demonstrates how to create specialized signatures
        that include domain-relevant metadata and analysis.
        """
        # Base signature generation
        signature = super().generate_signature(anomaly_data, anomaly_ips, anomaly_scores)

        # Add domain-specific signature data
        signature.domain = self.security_domain
        signature.expertise_level = self.domain_expertise
        signature.domain_patterns = self._extract_domain_patterns(anomaly_data)
        signature.risk_assessment = self._assess_domain_risk(anomaly_data, anomaly_scores)

        # Update agent expertise based on signature quality
        if signature.confidence > 0.8:
            self.domain_expertise = min(1.0, self.domain_expertise + 0.01)

        return signature

    def _extract_domain_patterns(self, anomaly_data: List[Dict]) -> Dict[str, Any]:
        """Extract domain-specific patterns from anomaly data."""
        patterns = {
            'packet_sizes': [p.get('packet_size', 0) for p in anomaly_data],
            'protocols': list(set(p.get('protocol', 'unknown') for p in anomaly_data)),
            'ports': list(set(p.get('port', 0) for p in anomaly_data))
        }

        if self.security_domain == "web":
            patterns.update({
                'http_methods': list(set(p.get('http_method', 'unknown') for p in anomaly_data)),
                'endpoints': list(set(p.get('endpoint', 'unknown') for p in anomaly_data))
            })

        return patterns

    def _assess_domain_risk(self, anomaly_data: List[Dict], scores: List[float]) -> Dict[str, Any]:
        """Assess domain-specific risk levels."""
        avg_score = sum(scores) / len(scores) if scores else 0

        risk_factors = {
            'overall_risk': 'high' if avg_score > 0.8 else 'medium' if avg_score > 0.5 else 'low',
            'confidence_level': avg_score,
            'affected_components': len(set(p.get('endpoint', p.get('port', 'unknown'))
                                         for p in anomaly_data))
        }

        return risk_factors

def demonstrate_custom_agents():
    """
    Demonstrate the use of custom agents in a simulation.

    This function shows how to:
    1. Create agents with different specializations
    2. Run comparative analysis
    3. Evaluate domain-specific performance
    """
    print("🔬 Custom Agent Demonstration")
    print("=" * 50)

    # Create simulation with custom agents
    sim = Simulation(num_agents=15, seed=42)

    # Replace some agents with custom security agents
    custom_agents = []
    for i in range(5):  # Replace 5 agents with custom ones
        domain = random.choice(['web', 'network', 'iot'])
        custom_agent = CustomSecurityAgent(sim, domain)
        sim.node_agents[i] = custom_agent
        custom_agents.append(custom_agent)

    print(f"Created {len(custom_agents)} custom security agents:")
    for agent in custom_agents:
        print(f"  • {agent.node_id}: {agent.security_domain} security")

    # Run simulation
    print("
🚀 Running simulation with custom agents..."    sim.run(steps=50)

    # Analyze custom agent performance
    print("
📊 Custom Agent Performance Analysis:"
    for agent in custom_agents:
        history = agent.detection_history
        if history:
            total_detections = sum(h['anomalies_detected'] for h in history)
            avg_detections = total_detections / len(history)

            print(f"  {agent.node_id} ({agent.security_domain}):")
            print(f"    • Expertise level: {agent.domain_expertise".3f"}")
            print(f"    • Total detections: {total_detections}")
            print(f"    • Average detections per step: {avg_detections".2f"}")

    # Cleanup
    sim.cleanup()

    return custom_agents

# Run the custom agent demonstration
if __name__ == "__main__":
    custom_agents = demonstrate_custom_agents()
```

## Technology Stack Alignment and Best Practices

### Current Technology Stack (October 2025)

All examples in this documentation are designed to work with the current technology stack:

#### Core Technologies
- **Python 3.8+**: All examples use modern Python features and type hints
- **Mesa Framework 3.3.0**: Agent-based modeling with enhanced scheduling capabilities
- **Ray 2.45.0**: Distributed computing with advanced dashboard and cluster management
- **SQLite**: Embedded database with WAL mode for high concurrency
- **Streamlit 1.39.0**: Interactive web interface with modern UI components

#### Machine Learning & Data Processing
- **NumPy 2.1.3**: High-performance array operations and mathematical functions
- **Pandas 2.2.3**: Data manipulation with enhanced performance optimizations
- **Scikit-learn 1.7.2**: Machine learning algorithms with improved accuracy
- **NetworkX 3.5**: Network analysis for complex topology modeling

#### Visualization & Monitoring
- **Plotly 6.3.1**: Advanced interactive data visualization
- **Matplotlib**: Statistical plotting and chart generation
- **Prometheus Integration**: Enterprise monitoring and alerting
- **Grafana Compatibility**: Dashboard visualization and metrics display

### Version Compatibility Matrix

| Component | Version | Compatibility | Example Usage |
|-----------|---------|---------------|---------------|
| Python | 3.8-3.12 | ✅ Full | All examples |
| Mesa | 3.3.0 | ✅ Full | `from mesa import Model` |
| Ray | 2.45.0 | ✅ Full | `ray.init()` patterns |
| SQLite | 3.40+ | ✅ Full | WAL mode examples |
| Streamlit | 1.39.0 | ✅ Full | Web UI examples |

### Environment Setup Verification

#### Pre-flight Checks
```python
# Example: Verify environment compatibility before running examples
import sys
import platform
from packaging import version

def verify_environment():
    """Verify that the current environment is compatible with examples."""
    print("🔍 Environment Verification")
    print("=" * 40)

    # Python version check
    python_version = sys.version_info
    print(f"Python: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version compatible")

    # Required packages check
    required_packages = {
        'mesa': '3.3.0',
        'ray': '2.45.0',
        'numpy': '2.1.0',
        'pandas': '2.2.0',
        'scikit-learn': '1.7.0'
    }

    missing_packages = []
    incompatible_packages = []

    for package, min_version in required_packages.items():
        try:
            module = __import__(package)
            package_version = getattr(module, '__version__', 'unknown')

            if version.parse(package_version) < version.parse(min_version):
                incompatible_packages.append(f"{package} {package_version} < {min_version}")
            else:
                print(f"✅ {package}: {package_version}")

        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    if incompatible_packages:
        print(f"⚠️  Incompatible packages: {', '.join(incompatible_packages)}")
        print("Consider updating packages for best compatibility")

    # System resources check
    import psutil
    memory = psutil.virtual_memory()
    cpu_count = psutil.cpu_count() or 1

    print(f"\n🖥️  System Resources:")
    print(f"   CPU cores: {cpu_count}")
    print(f"   Memory: {memory.total // (1024**3)}GB")

    if cpu_count < 2:
        print("⚠️  Limited CPU cores - parallel examples may be slower")
    if memory.total < 4 * (1024**3):
        print("⚠️  Limited memory - consider reducing agent count in examples")

    print("✅ Environment verification completed")
    return len(missing_packages) == 0

# Run verification before examples
if __name__ == "__main__":
    ready = verify_environment()
    if ready:
        print("\n🚀 Ready to run examples!")
    else:
        print("\n❌ Please fix environment issues before running examples")
```

### Modern Python Patterns Used

#### Type Hints and Modern Syntax
```python
# All examples use modern Python patterns:
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path
import asyncio
from dataclasses import dataclass

# Example with full type annotations
@dataclass
class SimulationConfig:
    """Modern configuration using dataclasses."""
    num_agents: int
    steps: int
    parallel_threshold: int = 50
    enable_monitoring: bool = True
    output_dir: Path = Path("./output")

def modern_simulation_example(config: SimulationConfig) -> Dict[str, Any]:
    """Example using modern Python patterns."""
    # Using pathlib for cross-platform paths
    output_path = config.output_dir / "results.json"

    # Using f-strings for formatting
    print(f"Running simulation with {config.num_agents} agents")

    # Using type hints throughout
    sim: Simulation = Simulation(num_agents=config.num_agents)

    # Modern async patterns (where applicable)
    # asyncio.run(run_simulation_async(sim, config.steps))

    return {"status": "completed", "config": config}
```

#### Resource Management with Context Managers
```python
# All examples use proper resource management:
from contextlib import contextmanager

@contextmanager
def managed_simulation(num_agents: int, steps: int):
    """Context manager for proper resource management."""
    sim = None
    try:
        sim = Simulation(num_agents=num_agents)
        yield sim
        # Run simulation within context
        sim.run(steps=steps)
    finally:
        if sim:
            sim.cleanup()

# Usage example:
def safe_simulation_example():
    """Example using proper resource management."""
    with managed_simulation(num_agents=50, steps=100) as sim:
        # Simulation automatically cleaned up on exit
        stats = sim.get_simulation_stats()
        print(f"Simulation completed: {stats}")

    # Resources are guaranteed to be cleaned up
    print("✓ Resources properly cleaned up")
```

### Cross-Platform Compatibility

#### Path Handling
```python
# All examples use cross-platform path handling:
from pathlib import Path

def cross_platform_example():
    """Example with cross-platform compatibility."""
    # Use pathlib for all file operations
    base_dir = Path(__file__).parent
    output_dir = base_dir / "output"
    logs_dir = base_dir / "logs"

    # Create directories safely
    output_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    # Cross-platform file paths
    results_file = output_dir / "results.json"
    log_file = logs_dir / "simulation.log"

    print(f"Output file: {results_file}")
    print(f"Log file: {log_file}")

    return results_file, log_file
```

#### Platform-Specific Adaptations
```python
# Examples adapt to different platforms:
import platform
import os

def platform_adaptive_example():
    """Example that adapts to different operating systems."""

    system = platform.system().lower()

    if system == "windows":
        # Windows-specific configurations
        config = {
            'parallel_workers': min(4, os.cpu_count() or 1),
            'memory_limit': "2GB",
            'temp_dir': os.environ.get('TEMP', 'C:\\Temp')
        }
    elif system == "linux":
        # Linux-specific configurations
        config = {
            'parallel_workers': os.cpu_count() or 4,
            'memory_limit': "4GB",
            'temp_dir': '/tmp'
        }
    elif system == "darwin":  # macOS
        # macOS-specific configurations
        config = {
            'parallel_workers': min(8, (os.cpu_count() or 1) * 2),
            'memory_limit': "8GB",
            'temp_dir': '/tmp'
        }
    else:
        # Default configuration
        config = {
            'parallel_workers': 4,
            'memory_limit': "2GB",
            'temp_dir': '/tmp'
        }

    print(f"Platform: {platform.system()}")
    print(f"Adaptive config: {config}")

    return config
```

### Performance Optimization Patterns

#### Memory-Efficient Processing
```python
# Examples use memory-efficient patterns:
import gc
from typing import Iterator, Generator

def memory_efficient_example():
    """Example demonstrating memory-efficient processing."""

    def process_large_dataset_batch(data: List[Dict], batch_size: int = 100) -> Iterator[Dict]:
        """Process large datasets in batches to control memory usage."""
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            # Process batch and yield results
            yield process_batch(batch)

            # Explicit garbage collection for large datasets
            if i % 1000 == 0:
                gc.collect()

    # Usage with large simulation results
    sim = Simulation(num_agents=100)
    sim.run(steps=1000)

    # Process results in batches
    all_entries = sim.ledger.read_ledger()

    print(f"Processing {len(all_entries)} entries in batches...")

    for batch_result in process_large_dataset_batch(all_entries):
        # Handle each batch result
        print(f"Processed batch with {len(batch_result)} results")

    sim.cleanup()
```

#### CPU-Efficient Parallel Processing
```python
# Examples optimize CPU usage based on available resources:
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

def cpu_optimized_example():
    """Example with CPU-optimized processing."""

    # Detect optimal worker count
    cpu_count = mp.cpu_count()
    optimal_workers = max(1, cpu_count - 1)  # Leave one core free

    print(f"Detected {cpu_count} CPUs, using {optimal_workers} workers")

    # Use ProcessPoolExecutor for CPU-intensive tasks
    def cpu_intensive_task(agent_data: Dict) -> Dict:
        """Simulate CPU-intensive processing."""
        # This would be actual processing in real scenarios
        return {
            'agent_id': agent_data['id'],
            'processed': True,
            'result': f"processed_{agent_data['id']}"
        }

    # Example usage with multiple agents
    agent_data_list = [{'id': i} for i in range(50)]

    with ProcessPoolExecutor(max_workers=optimal_workers) as executor:
        # Process agents in parallel
        results = list(executor.map(cpu_intensive_task, agent_data_list))

    print(f"Processed {len(results)} agents in parallel")

    return results
```

### Error Handling and Resilience

#### Comprehensive Error Handling
```python
# All examples include comprehensive error handling:
import logging
from functools import wraps

def with_error_handling(operation_name: str):
    """Decorator for consistent error handling across examples."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"❌ Error in {operation_name}: {e}")
                logging.error(f"Error in {operation_name}", exc_info=True)
                raise
        return wrapper
    return decorator

@with_error_handling("simulation_example")
def resilient_simulation_example():
    """Example with comprehensive error handling."""

    # Multiple layers of error handling
    try:
        # 1. Input validation
        num_agents = 50
        if not isinstance(num_agents, int) or num_agents <= 0:
            raise ValueError("Invalid number of agents")

        # 2. Resource initialization with error handling
        sim = None
        try:
            sim = Simulation(num_agents=num_agents, seed=42)
        except Exception as e:
            print(f"Failed to initialize simulation: {e}")
            raise

        # 3. Execution with progress monitoring
        max_retries = 3
        for attempt in range(max_retries):
            try:
                sim.run(steps=100)
                break  # Success, exit retry loop
            except KeyboardInterrupt:
                print("Simulation interrupted by user")
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(1)  # Brief delay before retry
                else:
                    print(f"All {max_retries} attempts failed")
                    raise

    except Exception as e:
        print(f"Simulation failed: {e}")
        return None
    finally:
        # 4. Guaranteed cleanup
        if sim:
            try:
                sim.cleanup()
            except Exception as cleanup_error:
                print(f"Warning: Cleanup error: {cleanup_error}")

    return sim
```

This comprehensive guide provides practical examples and troubleshooting strategies for effective use of the decentralized AI simulation API. Use these patterns as starting points and adapt them to your specific use cases.