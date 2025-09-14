from mesa import Model
import ray
from multiprocessing import Pool
from agents import AnomalyAgent
from database import DatabaseLedger
import random
import time
from logging_setup import get_logger
from config_loader import get_config
from monitoring import get_monitoring

logger = get_logger(__name__)


class Simulation(Model):
    """
    Main simulation class inheriting from mesa.Model.
    Manages agents, ledger, scheduling, and consensus.
    Supports scalability with Ray or multiprocessing for large agent counts.
    Uses AgentSet API for agent activation in Mesa 3.0+.
    """

    def __init__(self, num_agents: int = 100, seed=None):
        """
        Initialize the simulation model.

        Args:
            num_agents (int): Number of agents in the simulation.
            seed (int, optional): Random seed for reproducibility.
        """
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.ledger = DatabaseLedger()
        self.validations = {}  # Collect validations per signature ID
        self.threshold = num_agents // 2 + 1  # Majority consensus threshold

        # Create agents manually and store in list
        self.node_agents = []
        for _ in range(num_agents):
            agent = AnomalyAgent(self)
            self.node_agents.append(agent)

        # Initialize monitoring
        self.monitoring = get_monitoring()
        self.monitoring.record_metric('agent_count', num_agents)

        # Scalability setup - disable for basic run
        self.use_parallel = False  # Set to True for >50 agents after testing
        if self.use_parallel:
            if ray.is_initialized():
                ray.shutdown()
            ray.init(ignore_reinit_error=True)
            logger.info(f"Using Ray for parallel execution with {num_agents} agents")

    def agent_step(self, agent):
        """
        Wrapper for agent step to enable parallel execution.

        Args:
            agent: The AnomalyAgent instance.
        """
        agent.step()

    def agent_poll(self, agent):
        """
        Wrapper for agent poll_and_validate to enable parallel execution.

        Args:
            agent: The AnomalyAgent instance.

        Returns:
            list: Validations from the agent.
        """
        return agent.poll_and_validate()

    def step(self):
        """
        Execute one simulation step: agent actions, polling, consensus.
        Uses parallel execution if self.use_parallel is True.
        """
        step_start = time.time()
        try:
            # Phase 1: Agents generate traffic, detect, broadcast signatures
            if self.use_parallel:
                # Use Ray for parallel agent steps
                futures = [ray.remote(self.agent_step).remote(agent) for agent in self.node_agents]
                ray.get(futures)
            else:
                # Shuffle agents manually for sequential execution
                random.shuffle(self.node_agents)
                for agent in self.node_agents:
                    agent.step()

            # Phase 2: Agents poll and validate new signatures
            all_validations = {}
            if self.use_parallel:
                # Parallel poll with multiprocessing fallback
                with Pool() as pool:
                    poll_results = pool.map(self.agent_poll, self.node_agents)
            else:
                poll_results = [self.agent_poll(agent) for agent in self.node_agents]

            for vals in poll_results:
                for v in vals:
                    sid = v['sig_id']
                    if sid not in all_validations:
                        all_validations[sid] = []
                    all_validations[sid].append(v['valid'])

            # Phase 3: Resolve consensus and update agents
            self.resolve_consensus(all_validations)
            
            # Record metrics
            self.monitoring.record_metric('step_duration', time.time() - step_start)
            self.monitoring.record_metric('validation_count', len(all_validations))
            
        except Exception as e:
            logger.error(f"Error during simulation step: {e}")
            self.monitoring.record_metric('error_count', 1)
            raise

    def resolve_consensus(self, all_validations: dict):
        """
        Resolve consensus for signatures based on validations.
        If majority agrees, update all agents with the confirmed signature.

        Args:
            all_validations (dict): Dict of sig_id to list of bool validations.
        """
        for sig_id, val_list in all_validations.items():
            num_valid = sum(1 for valid in val_list if valid)
            if num_valid >= self.threshold:
                sig = self.ledger.get_entry_by_id(sig_id)
                if sig:
                    # Update all agents (parallel if needed)
                    if self.use_parallel:
                        futures = [
                            ray.remote(
                                lambda a, s: a.update_model_and_blacklist(s)
                            ).remote(agent, sig)
                            for agent in self.node_agents
                        ]
                        ray.get(futures)
                    else:
                        for agent in self.node_agents:
                            agent.update_model_and_blacklist(sig)
                    logger.info(f"Consensus reached for sig {sig_id} ({num_valid}/{len(val_list)} votes), all agents updated")
                    self.monitoring.record_metric('consensus_reached', 1)
                    self.monitoring.record_metric('consensus_votes', num_valid)

    def run(self, steps: int = 100):
        """
        Run the simulation for a number of steps.

        Args:
            steps (int): Number of simulation steps to run.
        """
        for i in range(steps):
            try:
                self.step()
                logger.info(f"Completed step {i+1}/{steps}")
            except Exception as e:
                logger.error(f"Error in step {i+1}: {e}")
                # Optionally, break or continue based on severity
                if get_config('simulation.stop_on_error', False):
                    raise

    def __del__(self):
        """
        Cleanup Ray initialization on destruction.
        """
        try:
            if hasattr(self, 'use_parallel') and self.use_parallel and ray.is_initialized():
                ray.shutdown()
                logger.info("Ray shutdown completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
