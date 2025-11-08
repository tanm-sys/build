import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.core.agents import AnomalyAgent, TrafficData, AnomalySignature
from sklearn.ensemble import IsolationForest
import random
import time
import json

# Initialize numpy random generator for modern random number generation
rng = np.random.default_rng(42)

@pytest.fixture
def mock_model():
    model = Mock()
    model.ledger = Mock()
    model.ledger.append_entry.return_value = 1
    model.ledger.get_new_entries.return_value = []
    model.ledger.read_ledger.return_value = []
    return model

@pytest.fixture
def mock_ledger():
    ledger = Mock()
    ledger.append_entry.return_value = 1
    ledger.get_new_entries.return_value = []
    ledger.read_ledger.return_value = []
    return ledger

def test_anomaly_agent_init(mock_model):
    """Test Agent initialization."""
    agent = AnomalyAgent(mock_model)
    
    assert agent.node_id.startswith("Node_")
    assert isinstance(agent.anomaly_model, IsolationForest)
    assert len(agent.recent_data) == 0  # BoundedList starts empty
    assert agent.last_seen_id == 0
    assert agent.local_blacklist_file == f"blacklist_{agent.node_id}.json"
    assert agent.ledger == mock_model.ledger
    assert agent.model is mock_model

def test_generate_traffic_normal(mock_model):
    """Test generating normal traffic."""
    agent = AnomalyAgent(mock_model)
    
    with patch('random.random', return_value=0.9):  # No anomaly
        traffic_data = agent.generate_traffic(batch_size=10)
    
    assert isinstance(traffic_data, TrafficData)
    assert len(traffic_data.data) == 10
    assert np.all(traffic_data.data > 0)  # All positive
    assert len(agent.recent_data) == 10

def test_generate_traffic_anomaly(mock_model):
    """Test generating traffic with forced anomaly."""
    agent = AnomalyAgent(mock_model)
    
    traffic_data = agent.generate_traffic(batch_size=10, force_anomaly=True)
    
    assert isinstance(traffic_data, TrafficData)
    assert len(traffic_data.data) == 10
    assert traffic_data.has_anomaly  # Should have anomaly
    assert len(agent.recent_data) == 10

def test_detect_anomaly_no_anomaly(mock_model):
    """Test anomaly detection with no anomalies."""
    agent = AnomalyAgent(mock_model)
    normal_data = TrafficData(data=rng.normal(100, 20, 10))
    
    has_anom, indices, anomaly_data, ips, scores = agent.detect_anomaly(normal_data)
    
    assert not has_anom
    assert len(indices) == 0
    assert len(anomaly_data) == 0
    assert len(ips) == 0
    assert len(scores) == 0

def test_detect_anomaly_with_anomaly(mock_model):
    """Test anomaly detection with anomaly (adjust threshold for test)."""
    agent = AnomalyAgent(mock_model)
    # Create data with clear anomaly
    data = rng.normal(100, 10, 9)
    data = np.append(data, 1000)  # More extreme outlier
    
    traffic_data = TrafficData(data=data)
    has_anom, indices, anomaly_data, ips, scores = agent.detect_anomaly(traffic_data)
    
    assert has_anom
    assert len(indices) > 0
    assert len(anomaly_data) == len(indices)
    assert np.any(anomaly_data > 400)  # Outlier detected

def test_generate_signature(mock_model):
    """Test signature generation."""
    agent = AnomalyAgent(mock_model)
    anomaly_data = np.array([500])
    anomaly_ips = ["192.168.1.1"]
    anomaly_scores = np.array([-0.5])
    
    sig = agent.generate_signature(anomaly_data, anomaly_ips, anomaly_scores)
    
    assert isinstance(sig, AnomalySignature)
    assert sig.timestamp > 0
    assert len(sig.features) == 1
    assert sig.confidence > 0
    assert sig.node_id == agent.node_id

def test_validate_signature_true(mock_model):
    """Test signature validation returns True (similar data)."""
    agent = AnomalyAgent(mock_model)
    agent.recent_data.extend([100, 100, 100])
    
    sig = {
        'features': [{'packet_size': 100.0, 'source_ip': '192.168.1.1'}],
        'node_id': 'other_node'
    }
    
    with patch('random.random', return_value=0.25):  # >=0.2, go to cos
        valid = agent.validate_signature(sig)
    
    # Validation should succeed based on similarity
    assert valid  # Cosine sim should be high for similar data

def test_validate_signature_false(mock_model):
    """Test signature validation returns False (dissimilar data)."""
    agent = AnomalyAgent(mock_model)
    agent.recent_data.extend([100, 100, 100])
    
    sig = {
        'features': [{'packet_size': 500.0, 'source_ip': '192.168.1.1'}],
        'node_id': 'other_node'
    }
    
    with patch('random.random', side_effect=[0.15, 0.1]):  # <0.2, then inner random <0.2, return False
        valid = agent.validate_signature(sig)
    
    assert not valid  # Random failure return False

@patch('time.strftime')
@patch('random.random')
def test_step(mock_random, mock_strftime, mock_model):
    """Test agent step execution."""
    agent = AnomalyAgent(mock_model)
    mock_strftime.return_value = "2023-01-01 00:00:00"
    mock_random.return_value = 0.9  # Normal traffic
    
    with patch.object(agent, 'generate_traffic') as mock_gen:
        # Mock normal traffic (no anomaly)
        mock_gen.return_value = TrafficData(data=np.array([100]*10), has_anomaly=False)
        
        # Should not raise any exceptions
        agent.step()
        
        # Verify generate_traffic was called
        mock_gen.assert_called_once()

@patch('time.strftime')
@patch('random.random')
def test_step_with_anomaly(mock_random, mock_strftime, mock_model):
    """Test agent step execution with anomaly."""
    agent = AnomalyAgent(mock_model)
    mock_strftime.return_value = "2023-01-01 00:00:00"
    mock_random.return_value = 0.9  # Normal traffic
    
    with patch.object(agent, 'generate_traffic') as mock_gen:
        # Mock traffic with anomaly
        mock_gen.return_value = TrafficData(
            data=np.array([100, 500, 100]), 
            has_anomaly=True, 
            anomaly_indices=[1]
        )
        
        with patch.object(agent, 'poll_and_validate') as mock_poll:
            agent.step()
            
            # Verify poll_and_validate was called
            mock_poll.assert_called_once()

def test_update_model_and_blacklist(mock_model):
    """Test model update and blacklist file creation."""
    agent = AnomalyAgent(mock_model)
    
    # Add some data to recent_data for model training
    agent.recent_data.extend([100, 100, 100])
    
    sig = AnomalySignature(
        timestamp=time.time(),
        features=[{'packet_size': 500.0, 'source_ip': '192.168.1.1'}],
        confidence=0.8,
        node_id='other_node'
    )
    
    # Mock file operations
    with patch('builtins.open', create=True) as mock_open:
        with patch('json.dump') as mock_json_dump:
            with patch('json.load', return_value=[]):
                with patch('os.path.exists', return_value=False):
                    agent.update_model_and_blacklist(sig)
        
        # Verify files were opened for writing
        assert mock_open.call_count >= 1
        # Verify JSON dump was called for blacklist update
        mock_json_dump.assert_called()

def test_bounded_list_functionality(mock_model):
    """Test BoundedList functionality and integration."""
    from src.core.agents import BoundedList
    
    # Test BoundedList creation
    bounded_list = BoundedList(max_size=3)
    assert len(bounded_list) == 0
    assert not bounded_list.is_full()
    
    # Test append and extend
    bounded_list.extend([1, 2, 3])
    assert len(bounded_list) == 3
    assert bounded_list.is_full()
    
    # Test capacity limit
    bounded_list.append(4)
    assert len(bounded_list) == 3  # Should still be 3 (oldest removed)
    
    # Test conversion to list
    assert bounded_list.tolist() == [2, 3, 4]
    
    # Test iteration
    items = list(bounded_list)
    assert items == [2, 3, 4]

def test_agent_cache_functionality(mock_model):
    """Test agent validation cache functionality."""
    agent = AnomalyAgent(mock_model)
    agent.recent_data.extend([100, 100, 100])
    
    sig = {
        'features': [{'packet_size': 100.0, 'source_ip': '192.168.1.1'}],
        'node_id': 'other_node'
    }
    
    # First validation - cache miss
    result1 = agent.validate_signature(sig)
    
    # Check cache stats
    stats = agent.get_cache_stats()
    assert stats['cache_hits'] == 0
    assert stats['cache_misses'] >= 1
    
    # Second validation - should be cache hit
    result2 = agent.validate_signature(sig)
    
    # Check updated cache stats
    stats = agent.get_cache_stats()
    assert stats['cache_hits'] >= 1

def test_agent_cleanup(mock_model):
    """Test agent cleanup functionality."""
    agent = AnomalyAgent(mock_model)
    
    # Add some data
    agent.recent_data.extend([100, 200, 300])
    
    # Verify data exists
    assert len(agent.recent_data) > 0
    
    # Call cleanup
    agent.cleanup()
    
    # Verify data is cleared
    assert len(agent.recent_data) == 0
    
    # Verify model is reset (will be recreated on next access)
    assert agent._anomaly_model is None

def test_error_handling_invalid_inputs(mock_model):
    """Test error handling for invalid inputs."""
    agent = AnomalyAgent(mock_model)
    
    # Test invalid batch_size
    with pytest.raises(ValueError):
        agent.generate_traffic(batch_size=-1)
    
    with pytest.raises(ValueError):
        agent.generate_traffic(batch_size=0)
    
    # Test invalid force_anomaly type
    with pytest.raises(ValueError):
        agent.generate_traffic(force_anomaly="invalid")

def test_signature_generation_edge_cases(mock_model):
    """Test signature generation with edge cases."""
    agent = AnomalyAgent(mock_model)
    
    # Test empty anomaly data
    with pytest.raises(ValueError):
        agent.generate_signature(np.array([]), [], np.array([]))
    
    # Test mismatched array lengths
    with pytest.raises(ValueError):
        agent.generate_signature(
            np.array([100, 200]), 
            ["192.168.1.1"], 
            np.array([-0.5])
        )

def test_anomaly_detection_empty_data(mock_model):
    """Test anomaly detection with empty data."""
    agent = AnomalyAgent(mock_model)
    
    empty_traffic = TrafficData(data=np.array([]))
    
    has_anom, indices, anomaly_data, ips, scores = agent.detect_anomaly(empty_traffic)
    
    assert not has_anom
    assert len(indices) == 0
    assert len(anomaly_data) == 0
    assert len(ips) == 0
    assert len(scores) == 0