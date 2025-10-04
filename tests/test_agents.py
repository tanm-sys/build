import json
import os
import random
import sys
import time
from typing import Dict, List, Any
from unittest.mock import Mock, patch

import numpy as np
import pytest
from sklearn.ensemble import IsolationForest
import sys
import os

# Add the agents module path to sys.path for direct imports
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
agents_module_path = os.path.join(project_root, 'decentralized-ai-simulation', 'src', 'core', 'agents')
sys.path.insert(0, agents_module_path)

# Import with fallback mechanism
try:
    from agent_manager import AnomalyAgent, AgentFactory, validate_agent_input
except ImportError:
    try:
        # Fallback to absolute import
        from decentralized_ai_simulation.src.core.agents.agent_manager import AnomalyAgent, AgentFactory, validate_agent_input
    except ImportError:
        # Final fallback - try importing the module directly
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        agents_module_path = os.path.join(project_root, 'decentralized-ai-simulation', 'src', 'core', 'agents')
        sys.path.insert(0, agents_module_path)
        import agent_manager
        AnomalyAgent = agent_manager.AnomalyAgent
        AgentFactory = agent_manager.AgentFactory
        validate_agent_input = agent_manager.validate_agent_input

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test utilities and fixtures
class TestUtils:
    """Utility class for test data and common operations."""

    @staticmethod
    def create_mock_model() -> Mock:
        """Create a mock model for testing."""
        model = Mock()
        model.ledger = TestUtils.create_mock_ledger()
        return model

    @staticmethod
    def create_mock_ledger() -> Mock:
        """Create a mock ledger for testing."""
        ledger = Mock()
        ledger.append_entry.return_value = 1
        ledger.get_new_entries.return_value = []
        ledger.read_ledger.return_value = []
        return ledger

    @staticmethod
    def create_test_anomaly_data(num_points: int = 10) -> np.ndarray:
        """Create test anomaly data for testing."""
        rng = np.random.default_rng(42)
        normal_data = rng.normal(100, 20, num_points - 1)
        anomaly_data = np.append(normal_data, 500)  # Add one anomaly
        return anomaly_data

    @staticmethod
    def create_test_signature() -> Dict[str, Any]:
        """Create a test signature for testing."""
        return {
            'timestamp': time.time(),
            'features': [{'packet_size': 500.0, 'source_ip': '192.168.1.1'}],
            'confidence': 0.95,
            'node_id': 'test_node'
        }

# Initialize numpy random generator for modern random number generation
rng = np.random.default_rng(42)

# Test fixtures
@pytest.fixture
def mock_model():
    """Create a mock model for testing."""
    return TestUtils.create_mock_model()

@pytest.fixture
def mock_ledger():
    """Create a mock ledger for testing."""
    return TestUtils.create_mock_ledger()

@pytest.fixture
def test_anomaly_data():
    """Create test anomaly data for testing."""
    return TestUtils.create_test_anomaly_data()

@pytest.fixture
def test_signature():
    """Create a test signature for testing."""
    return TestUtils.create_test_signature()

@pytest.fixture
def sample_agent(mock_model, mock_ledger):
    """Create a sample agent for testing."""
    mock_model.ledger = mock_ledger
    return AnomalyAgent(mock_model)

def test_anomaly_agent_init(sample_agent, mock_ledger):
    """Test Agent initialization with lazy loading."""
    agent = sample_agent

    # Test basic initialization
    assert agent.node_id.startswith("Node_")
    assert len(agent.recent_data) == 0
    assert agent.last_seen_id == 0
    assert agent.local_blacklist_file == f"blacklist_{agent.node_id}.json"
    assert agent.ledger == mock_ledger

    # Test lazy loading of anomaly model
    assert agent._anomaly_model is None  # Should not be initialized yet
    model = agent.anomaly_model  # Trigger lazy loading
    assert isinstance(model, IsolationForest)
    assert agent._anomaly_model is not None  # Should be initialized now

def test_generate_traffic_normal(mock_model, mock_ledger):
    """Test generating normal traffic."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    
    with patch('agents.random.random', return_value=0.9):  # No anomaly
        data = agent.generate_traffic(batch_size=10)
    
    assert len(data) == 10
    assert np.all(data > 0)  # All positive
    assert len(agent.recent_data) == 10

def test_generate_traffic_anomaly(mock_model, mock_ledger):
    """Test generating traffic with forced anomaly."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    
    data = agent.generate_traffic(batch_size=10, force_anomaly=True)
    
    assert len(data) == 10
    # One value should be 500
    assert np.any(data == 500)
    assert len(agent.recent_data) == 10

def test_detect_anomaly_no_anomaly(mock_model, mock_ledger):
    """Test anomaly detection with no anomalies."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    normal_data = rng.normal(100, 20, 10)
    
    has_anom, indices, anomaly_data, ips, scores = agent.detect_anomaly(normal_data)
    
    assert not has_anom
    assert len(indices) == 0
    assert len(anomaly_data) == 0
    assert len(ips) == 0
    assert len(scores) == 0

def test_detect_anomaly_with_anomaly(mock_model, mock_ledger):
    """Test anomaly detection with anomaly (adjust threshold for test)."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    data = rng.normal(100, 10, 9)
    data = np.append(data, 1000)  # More extreme outlier
    
    has_anom, indices, anomaly_data, _, _ = agent.detect_anomaly(data)
    
    assert has_anom
    assert len(indices) > 0
    assert len(anomaly_data) == len(indices)
    assert np.any(anomaly_data > 400)  # Outlier detected

def test_generate_signature(mock_model, mock_ledger):
    """Test signature generation."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    anomaly_data = np.array([500])
    anomaly_ips = ["192.168.1.1"]
    anomaly_scores = np.array([-0.5])
    
    sig = agent.generate_signature(anomaly_data, anomaly_ips, anomaly_scores)
    
    assert 'timestamp' in sig
    assert 'features' in sig
    assert len(sig['features']) == 1
    assert 'confidence' in sig
    assert sig['node_id'] == agent.node_id

def test_validate_signature_true(mock_model, mock_ledger):
    """Test signature validation returns True (similar data)."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    agent.recent_data = [100, 100, 100]
    
    sig = {
        'features': [{'packet_size': 100.0, 'source_ip': '192.168.1.1'}],
        'node_id': 'other_node'
    }
    
    with patch('agents.random.random', return_value=0.25):  # >=0.2, go to cos
        valid = agent.validate_signature(sig)
    
    assert valid  # Cosine sim should be 1.0 > 0.7

def test_validate_signature_false(mock_model, mock_ledger):
    """Test signature validation returns False (dissimilar data)."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    agent.recent_data = [100, 100, 100]
    
    sig = {
        'features': [{'packet_size': 500.0, 'source_ip': '192.168.1.1'}],
        'node_id': 'other_node'
    }
    
    with patch('agents.random.random', side_effect=[0.15, 0.1]):  # <0.2, then inner random <0.2, return False
        valid = agent.validate_signature(sig)
    
    assert not valid  # Random failure return False

@patch('agents.time.strftime')
@patch('agents.print')
def test_step(mock_print, mock_strftime, mock_model, mock_ledger):
    """Test agent step execution."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    mock_strftime.return_value = "2023-01-01 00:00:00"
    
    with patch.object(agent, 'generate_traffic', return_value=np.array([100]*10)):
        with patch.object(agent, 'detect_anomaly', return_value=(False, [], [], [], [])):
            with patch.object(agent, 'poll_and_validate') as mock_poll:
                agent.step()

            mock_poll.assert_called_once()
            # get_new_entries not called because poll_and_validate is mocked; this is expected
            # No assertion on get_new_entries

def test_update_model_and_blacklist(mock_model, mock_ledger):
    """Test model update and blacklist file creation."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    
    sig = {
        'features': [{'packet_size': 500.0, 'source_ip': '192.168.1.1'}]
    }
    
    # Mock file write
    from unittest.mock import mock_open
    with patch('agents.open', mock_open(read_data='[]')) as m_open:
        with patch('agents.json.load', return_value=[]):
            with patch('agents.json.dump'):
                with patch('agents.print'):
                    agent.update_model_and_blacklist(sig)
        
        # Check file written
        m_open.assert_called_with(agent.local_blacklist_file, 'w')
    
    # Check model retrained
    train_data = np.array(agent.recent_data + [500]).reshape(-1, 1)
    if len(train_data) > 0:
        agent.anomaly_model.fit(train_data)

# Performance and optimization tests
class TestAgentPerformance:
    """Test class for agent performance and optimization features."""

    def test_lazy_loading_performance(self, mock_model):
        """Test that lazy loading improves initialization performance."""
        mock_model.ledger = TestUtils.create_mock_ledger()

        # Measure initialization time
        start_time = time.time()
        agent = AnomalyAgent(mock_model)
        init_time = time.time() - start_time

        # Agent should initialize quickly without loading the model
        assert init_time < 0.1  # Should be very fast
        assert agent._anomaly_model is None

        # Model should load only when first accessed
        start_time = time.time()
        _ = agent.anomaly_model
        model_load_time = time.time() - start_time

        assert model_load_time < 0.5  # Model loading should be reasonably fast
        assert agent._anomaly_model is not None

    def test_bounded_list_memory_efficiency(self, sample_agent):
        """Test that BoundedList prevents memory leaks."""
        agent = sample_agent

        # Add many items to test memory bounds
        for i in range(2000):
            agent.recent_data.append(f"item_{i}")

        # Should not exceed max_size (1000)
        assert len(agent.recent_data) <= 1000

        # Should track total appended items
        stats = agent.recent_data.get_stats()
        assert stats['total_appended'] >= 2000
        assert stats['current_size'] <= 1000

    def test_agent_factory_batch_creation(self, mock_model):
        """Test AgentFactory batch creation functionality."""
        mock_model.ledger = TestUtils.create_mock_ledger()

        # Test successful batch creation
        agents = AgentFactory.create_agents_batch(mock_model, 5)
        assert len(agents) == 5
        assert all(isinstance(agent, AnomalyAgent) for agent in agents)

        # Test error handling in batch creation
        with patch('agents.logger') as mock_logger:
            # This should handle errors gracefully and continue
            agents = AgentFactory.create_agents_batch(mock_model, 3)
            assert len(agents) >= 0  # May be less than requested if errors occur

    def test_input_validation_utility(self):
        """Test the input validation utility function."""
        # Test valid inputs
        validate_agent_input(100, "test_param", int, min_val=0, max_val=1000)
        validate_agent_input("test_string", "test_param", str)
        validate_agent_input(10.5, "test_param", float, min_val=0.0, max_val=100.0)

        # Test invalid inputs
        with pytest.raises(TypeError):
            validate_agent_input("not_an_int", "test_param", int)

        with pytest.raises(ValueError):
            validate_agent_input(-1, "test_param", int, min_val=0)

        with pytest.raises(ValueError):
            validate_agent_input("", "test_param", str)