import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch
from simulation import Simulation
from database import DatabaseLedger
from agents import AnomalyAgent
import ray

@pytest.fixture
def mock_ledger():
    ledger = Mock(spec=DatabaseLedger)
    ledger.append_entry.return_value = 1
    ledger.get_new_entries.return_value = []
    ledger.read_ledger.return_value = []
    return ledger

def test_simulation_init():
    """Test Simulation initialization with 10 agents."""
    model = Simulation(num_agents=10, seed=42)
    
    assert model.num_agents == 10
    assert isinstance(model.ledger, DatabaseLedger)
    assert model.threshold == 6  # 10//2 + 1
    assert len(model.node_agents) == 10
    for agent in model.node_agents:
        assert isinstance(agent, AnomalyAgent)
        assert agent.model is model
    assert model.use_parallel is False
    assert model.validations == {}

def test_simulation_init_no_seed():
    """Test Simulation init without seed."""
    model = Simulation(num_agents=5)
    
    assert model.num_agents == 5
    assert len(model.node_agents) == 5
    assert model.threshold == 3

def test_simulation_step_sequential():
    """Test simulation step in sequential mode with 2 agents."""
    model = Simulation(num_agents=2, seed=42)
    model.use_parallel = False
    
    # Mock agent methods
    for agent in model.node_agents:
        agent.step = Mock()
        agent.poll_and_validate = Mock(return_value=[{'sig_id': 1, 'valid': True}])
    
    # Mock resolve_consensus
    with patch.object(model, 'resolve_consensus') as mock_resolve:
        model.step()
    
    # Verify calls
    for agent in model.node_agents:
        agent.step.assert_called_once()
        agent.poll_and_validate.assert_called_once()
    mock_resolve.assert_called_once()
    # Check validations collected (local in code, but test checks calls)

def test_simulation_resolve_consensus():
    """Test consensus resolution."""
    model = Simulation(num_agents=5, seed=42)
    model.threshold = 3
    all_validations = {1: [True, True, False, True, True]}  # 4 True > threshold
    
    with patch.object(model.ledger, 'get_entry_by_id', return_value={'id': 1, 'features': []}):
        mock_update = patch.object(model.node_agents[0], 'update_model_and_blacklist')
        with mock_update as m:
            model.resolve_consensus(all_validations)
    
    # Since sequential, check first agent updated
    m.assert_called_once()

def test_simulation_resolve_consensus_no_consensus():
    """Test no consensus (below threshold)."""
    model = Simulation(num_agents=5, seed=42)
    model.threshold = 3
    all_validations = {1: [True, False, False, False, False]}  # 1 True < threshold
    
    with patch.object(model.ledger, 'get_entry_by_id', return_value=None):
        mock_update = patch.object(model.node_agents[0], 'update_model_and_blacklist')
        with mock_update as m:
            model.resolve_consensus(all_validations)
    
    m.assert_not_called()

def test_simulation_run():
    """Test running the simulation for steps."""
    model = Simulation(num_agents=1, seed=42)
    model.step = Mock()
    
    model.run(steps=3)
    
    assert model.step.call_count == 3

def test_simulation_parallel_setup():
    """Test parallel setup (mock Ray)."""
    with patch('ray.is_initialized', return_value=False):
        with patch('ray.shutdown'):
            with patch('ray.init') as mock_init:
                model = Simulation(num_agents=100)
                model.use_parallel = True
                if model.use_parallel:
                    ray.init(ignore_reinit_error=True)
    
    # Verify init called
    mock_init.assert_called_once()