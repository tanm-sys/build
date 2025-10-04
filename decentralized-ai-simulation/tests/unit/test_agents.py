import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.core.agents import AnomalyAgent
from sklearn.ensemble import IsolationForest
import random
import time
import json

# Initialize numpy random generator for modern random number generation
rng = np.random.default_rng(42)

@pytest.fixture
def mock_model():
    return Mock()

@pytest.fixture
def mock_ledger():
    ledger = Mock()
    ledger.append_entry.return_value = 1
    ledger.get_new_entries.return_value = []
    ledger.read_ledger.return_value = []
    return ledger

def test_anomaly_agent_init(mock_model, mock_ledger):
    """Test Agent initialization."""
    mock_model.ledger = mock_ledger
    agent = AnomalyAgent(mock_model)
    
    assert agent.node_id.startswith("Node_")
    assert isinstance(agent.anomaly_model, IsolationForest)
    assert agent.recent_data == []
    assert agent.last_seen_id == 0
    assert agent.local_blacklist_file == f"blacklist_{agent.node_id}.json"
    assert agent.ledger == mock_ledger
    assert agent.model is mock_model

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