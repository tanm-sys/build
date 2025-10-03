"""
Main entrypoint for the decentralized AI simulation.
Imports and runs the modular simulation for anomaly detection.
"""

from simulation import Simulation
import os
import json
import argparse
import subprocess
from logging_setup import get_logger
from config_loader import get_config

logger = get_logger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decentralized AI Simulation')
    parser.add_argument('--ui', action='store_true', help='Launch Streamlit UI instead of running headless simulation')
    args = parser.parse_args()

    if args.ui:
        # Launch Streamlit UI
        subprocess.run(['./venv/bin/streamlit', 'run', 'streamlit_app.py'])
    else:
        # Run headless simulation
        num_agents = get_config('simulation.default_agents', 100)
        steps = get_config('simulation.default_steps', 10)
        logger.info(f"Starting decentralized AI simulation with {num_agents} agents for {steps} steps...")
        
        try:
            model = Simulation(num_agents=num_agents)
            model.run(steps=steps)
            
            # Final state
            logger.info("Simulation completed.")
            ledger = model.ledger
            entries = ledger.read_ledger()
            logger.info(f"Shared ledger: {len(entries)} entries")
            
            total_threats = 0
            for i in range(num_agents):
                blacklist_file = f"blacklist_Node_{i}.json"
                if os.path.exists(blacklist_file):
                    try:
                        with open(blacklist_file, 'r') as f:
                            bl = json.load(f)
                        total_threats += len(bl)
                        logger.info(f"Node {i} blacklist: {len(bl)} signatures")
                        os.remove(blacklist_file)  # Clean up after reporting
                    except Exception as e:
                        logger.error(f"Error processing blacklist file {blacklist_file}: {e}")
            
            logger.info(f"Final state: All nodes share {total_threats} threat signatures.")
            
            # Clean up ledger db if in development mode
            if get_config('environment') == 'development':
                db_path = get_config('database.path', 'ledger.db')
                if os.path.exists(db_path):
                    os.remove(db_path)
                    logger.info("Cleaned up ledger database")
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise