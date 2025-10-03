from mesa import Model
from typing import List, Dict, Any, Optional, Tuple, Callable
import asyncio
import ray
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor, as_completed
from .agents import AnomalyAgent, ValidationResult
from .database import DatabaseLedger
import random
import time
from src.utils.logging_setup import get_logger
from src.config.config_loader import get_config
from src.utils.monitoring import get_monitoring
import functools

logger = get_logger(__name__)


class Simulation(Model):
    """
    Enhanced simulation class with modern patterns and optimizations.

    Manages agents, ledger, scheduling, and consensus with improved type safety,
    async support, and better resource management.
    """

    def __init__(self, num_agents: int = 100, seed: Optional[int] = None) -> None:
        """
        Initialize the simulation model with enhanced configuration.

        Args:
            num_agents: Number of agents in the simulation.
            seed: Random seed for reproducibility.
        """
        super().__init__(seed=seed)

        # Validate inputs
        if num_agents <= 0:
            raise ValueError("Number of agents must be positive")
        if num_agents > get_config('simulation.use_parallel_threshold', 50):
            logger.info(f"Large agent count ({num_agents}) detected, consider enabling parallel execution")

        self.num_agents: int = num_agents
        self.ledger: DatabaseLedger = DatabaseLedger()
        self.validations: Dict[int, List[bool]] = {}
        self.threshold: int = num_agents // 2 + 1
        self.step_count: int = 0
        self.start_time: float = time.time()

        # Create agents with enhanced initialization
        self.node_agents: List[AnomalyAgent] = []
        self._initialize_agents()

        # Initialize monitoring and metrics
        self.monitoring = get_monitoring()
        self.monitoring.record_metric('agent_count', num_agents)
        self.monitoring.record_metric('simulation_start_time', self.start_time)

        # Scalability configuration
        self.use_parallel: bool = num_agents > get_config('simulation.use_parallel_threshold', 50)
        self.executor: Optional[ThreadPoolExecutor] = None

        if self.use_parallel:
            self._initialize_parallel_execution()

        logger.info(f"Initialized simulation with {num_agents} agents, parallel={self.use_parallel}")

    def _initialize_agents(self) -> None:
        """Initialize agents with proper error handling."""
        for i in range(self.num_agents):
            try:
                agent = AnomalyAgent(self)
                self.node_agents.append(agent)
            except Exception as e:
                logger.error(f"Failed to initialize agent {i}: {e}")
                raise

    def _initialize_parallel_execution(self) -> None:
        """Initialize parallel execution resources."""
        try:
            if ray.is_initialized():
                ray.shutdown()

            ray.init(ignore_reinit_error=True, num_cpus=min(self.num_agents, 8))
            self.executor = ThreadPoolExecutor(max_workers=min(self.num_agents, 8))

            logger.info(f"Initialized parallel execution for {self.num_agents} agents")

        except Exception as e:
            logger.warning(f"Failed to initialize parallel execution, falling back to sequential: {e}")
            self.use_parallel = False

    def agent_step(self, agent: AnomalyAgent) -> None:
        """
        Wrapper for agent step to enable parallel execution with error handling.

        Args:
            agent: The AnomalyAgent instance to step.
        """
        try:
            agent.step()
        except Exception as e:
            logger.error(f"Error in agent {agent.node_id} step: {e}")
            # Continue with other agents rather than failing entire simulation

    def agent_poll(self, agent: AnomalyAgent) -> List[ValidationResult]:
        """
        Wrapper for agent poll_and_validate with enhanced error handling.

        Args:
            agent: The AnomalyAgent instance to poll.

        Returns:
            List of ValidationResult objects from the agent.
        """
        try:
            return agent.poll_and_validate()
        except Exception as e:
            logger.error(f"Error polling agent {agent.node_id}: {e}")
            return []

    def _execute_agent_steps_parallel(self) -> None:
        """Execute agent steps in parallel using available execution method."""
        if self.use_parallel and ray.is_initialized():
            # Use Ray for distributed execution
            futures = [
                ray.remote(self.agent_step).remote(agent)
                for agent in self.node_agents
            ]
            ray.get(futures)
        elif self.use_parallel and self.executor:
            # Use ThreadPoolExecutor for concurrent execution
            futures = [
                self.executor.submit(self.agent_step, agent)
                for agent in self.node_agents
            ]
            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    future.result()  # Will raise exception if agent step failed
                except Exception as e:
                    logger.error(f"Agent step failed in thread pool: {e}")
        else:
            # Sequential execution with shuffling for fairness
            shuffled_agents = self.node_agents.copy()
            random.shuffle(shuffled_agents)
            for agent in shuffled_agents:
                self.agent_step(agent)

    def _collect_validations_parallel(self) -> Dict[int, List[bool]]:
        """Collect validations from all agents in parallel."""
        if self.use_parallel and ray.is_initialized():
            # Use Ray for distributed validation collection
            futures = [
                ray.remote(self.agent_poll).remote(agent)
                for agent in self.node_agents
            ]
            poll_results = ray.get(futures)
        elif self.use_parallel and self.executor:
            # Use ThreadPoolExecutor for concurrent validation
            futures = [
                self.executor.submit(self.agent_poll, agent)
                for agent in self.node_agents
            ]
            poll_results = [future.result() for future in as_completed(futures)]
        else:
            # Sequential validation collection
            poll_results = [self.agent_poll(agent) for agent in self.node_agents]

        # Aggregate validations
        all_validations = {}
        for validation_list in poll_results:
            for validation in validation_list:
                sig_id = validation.signature_id
                if sig_id not in all_validations:
                    all_validations[sig_id] = []
                all_validations[sig_id].append(validation.is_valid)

        return all_validations

    def step(self) -> None:
        """
        Execute one simulation step with enhanced parallel processing and monitoring.

        Uses optimized parallel execution strategies based on configuration and
        available resources.
        """
        step_start = time.time()
        self.step_count += 1

        try:
            # Phase 1: Execute agent steps in parallel or sequential
            self._execute_agent_steps_parallel()

            # Phase 2: Collect validations from all agents
            all_validations = self._collect_validations_parallel()

            # Phase 3: Resolve consensus and update agents
            self.resolve_consensus(all_validations)

            # Record comprehensive metrics
            step_duration = time.time() - step_start
            self.monitoring.record_metric('step_duration', step_duration)
            self.monitoring.record_metric('validation_count', len(all_validations))
            self.monitoring.record_metric('step_count', self.step_count)

            # Log progress periodically
            if self.step_count % 10 == 0:
                elapsed = time.time() - self.start_time
                logger.info(f"Completed step {self.step_count}, "
                          f"avg step time: {elapsed/self.step_count:.2f}s, "
                          f"validations: {len(all_validations)}")

        except Exception as e:
            logger.error(f"Error during simulation step {self.step_count}: {e}")
            self.monitoring.record_metric('error_count', 1)
            self.monitoring.record_metric('last_error_step', self.step_count)
            raise

    def resolve_consensus(self, all_validations: Dict[int, List[bool]]) -> None:
        """
        Resolve consensus for signatures with enhanced parallel processing.

        Args:
            all_validations: Dict mapping signature_id to list of boolean validations.
        """
        if not all_validations:
            return

        for sig_id, val_list in all_validations.items():
            if not val_list:
                continue

            num_valid = sum(1 for valid in val_list if valid)
            consensus_reached = num_valid >= self.threshold

            if consensus_reached:
                try:
                    # Retrieve signature from ledger
                    signature_entry = self.ledger.get_entry_by_id(sig_id)
                    if not signature_entry:
                        logger.warning(f"Signature {sig_id} not found in ledger")
                        continue

                    # Update all agents with confirmed signature
                    self._update_agents_with_signature(signature_entry)

                    logger.info(f"Consensus reached for signature {sig_id} "
                              f"({num_valid}/{len(val_list)} votes)")

                    # Record consensus metrics
                    self.monitoring.record_metric('consensus_reached', 1)
                    self.monitoring.record_metric('consensus_votes', num_valid)
                    self.monitoring.record_metric('consensus_rate', num_valid / len(val_list))

                except Exception as e:
                    logger.error(f"Error processing consensus for signature {sig_id}: {e}")
                    self.monitoring.record_metric('consensus_error', 1)

    def _update_agents_with_signature(self, signature_entry: Dict[str, Any]) -> None:
        """Update all agents with a confirmed signature using parallel processing."""
        try:
            if self.use_parallel and ray.is_initialized():
                # Use Ray for distributed agent updates
                update_func = ray.remote(lambda agent, sig: agent.update_model_and_blacklist_from_dict(sig))
                futures = [
                    update_func.remote(agent, signature_entry)
                    for agent in self.node_agents
                ]
                ray.get(futures)

            elif self.use_parallel and self.executor:
                # Use ThreadPoolExecutor for concurrent updates
                futures = [
                    self.executor.submit(self._update_single_agent, agent, signature_entry)
                    for agent in self.node_agents
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Agent update failed: {e}")

            else:
                # Sequential agent updates
                for agent in self.node_agents:
                    try:
                        self._update_single_agent(agent, signature_entry)
                    except Exception as e:
                        logger.error(f"Failed to update agent {agent.node_id}: {e}")

        except Exception as e:
            logger.error(f"Error in parallel agent updates: {e}")
            raise

    def _update_single_agent(self, agent: AnomalyAgent, signature_entry: Dict[str, Any]) -> None:
        """Update a single agent with signature data."""
        # This would need to be implemented in the agent class
        # For now, we'll use the existing method
        agent.update_model_and_blacklist_from_dict(signature_entry)

    def run(self, steps: int = 100) -> None:
        """
        Run the simulation for a specified number of steps with enhanced monitoring.

        Args:
            steps: Number of simulation steps to run.

        Raises:
            ValueError: If steps is not a positive integer.
        """
        if not isinstance(steps, int) or steps <= 0:
            raise ValueError("Steps must be a positive integer")

        logger.info(f"Starting simulation run for {steps} steps with {self.num_agents} agents")

        try:
            for step_num in range(1, steps + 1):
                self.step()

                # Log progress at intervals
                if step_num % max(1, steps // 10) == 0:
                    progress = step_num / steps
                    elapsed = time.time() - self.start_time
                    eta = (elapsed / progress) - elapsed if progress > 0 else 0

                    logger.info(f"Simulation progress: {progress:.1%} "
                              f"({step_num}/{steps}), "
                              f"elapsed: {elapsed:.1f}s, "
                              f"ETA: {eta:.1f}s")

        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Simulation run failed at step {self.step_count}: {e}")
            if get_config('simulation.stop_on_error', False):
                raise
        finally:
            self._finalize_run()

    def _finalize_run(self) -> None:
        """Finalize simulation run with comprehensive metrics."""
        total_time = time.time() - self.start_time

        logger.info(f"Simulation completed: {self.step_count} steps in {total_time:.2f}s")
        logger.info(f"Average step time: {total_time/self.step_count:.3f}s")

        # Record final metrics
        self.monitoring.record_metric('total_steps', self.step_count)
        self.monitoring.record_metric('total_runtime', total_time)
        self.monitoring.record_metric('simulation_end_time', time.time())

        # Cleanup resources
        self.cleanup()

    def cleanup(self) -> None:
        """Enhanced cleanup of simulation resources."""
        logger.info("Cleaning up simulation resources")

        try:
            # Shutdown Ray if initialized
            if ray.is_initialized():
                ray.shutdown()
                logger.debug("Ray shutdown completed")
        except Exception as e:
            logger.warning(f"Error shutting down Ray: {e}")

        try:
            # Shutdown thread pool executor
            if self.executor:
                self.executor.shutdown(wait=True)
                logger.debug("Thread pool executor shutdown completed")
        except Exception as e:
            logger.warning(f"Error shutting down thread pool: {e}")

        # Record cleanup metrics
        self.monitoring.record_metric('cleanup_time', time.time())

    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get comprehensive simulation statistics."""
        return {
            'step_count': self.step_count,
            'num_agents': self.num_agents,
            'threshold': self.threshold,
            'use_parallel': self.use_parallel,
            'runtime': time.time() - self.start_time,
            'avg_step_time': (time.time() - self.start_time) / max(1, self.step_count),
            'ledger_size': len(self.ledger.read_ledger()) if self.ledger else 0
        }

    def __del__(self) -> None:
        """Enhanced destructor with proper resource cleanup."""
        try:
            self.cleanup()
        except Exception as e:
            logger.error(f"Error during simulation cleanup: {e}")
