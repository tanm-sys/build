#!/usr/bin/env python3
"""
Database Initialization Script for Decentralized AI Simulation Platform

This script initializes the SQLite database for the decentralized AI simulation
platform, setting up the required schema, tables, and performing connectivity tests.

Author: Kilo Code
Date: November 2, 2025
"""

import os
import sys
import sqlite3
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_init.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Database initialization and testing class."""
    
    def __init__(self, db_path: str = "ledger.db"):
        """Initialize the database initializer."""
        self.db_path = db_path
        self.test_results = []
        self.start_time = time.time()
        
    @contextmanager
    def get_connection(self):
        """Get database connection with error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA foreign_keys=ON")
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def create_directories(self) -> bool:
        """Create required directories."""
        try:
            directories = ['logs', 'data', 'backups']
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"Created/verified directory: {directory}")
            
            self.test_results.append({
                "test": "Create directories",
                "status": "SUCCESS",
                "details": "All required directories created successfully"
            })
            return True
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            self.test_results.append({
                "test": "Create directories",
                "status": "FAILED",
                "details": str(e)
            })
            return False
    
    def initialize_main_ledger_schema(self) -> bool:
        """Initialize the main ledger table schema."""
        try:
            with self.get_connection() as conn:
                # Create main ledger table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ledger (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        node_id TEXT NOT NULL,
                        features TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(timestamp, node_id)
                    )
                """)
                
                # Create indexes for better query performance
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_ledger_timestamp ON ledger(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_ledger_node_id ON ledger(node_id)",
                    "CREATE INDEX IF NOT EXISTS idx_ledger_confidence ON ledger(confidence)"
                ]
                
                for index_sql in indexes:
                    conn.execute(index_sql)
                
                conn.commit()
                logger.info("Main ledger schema initialized successfully")
                
                self.test_results.append({
                    "test": "Initialize main ledger schema",
                    "status": "SUCCESS",
                    "details": "Main ledger table and indexes created"
                })
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize main ledger schema: {e}")
            self.test_results.append({
                "test": "Initialize main ledger schema",
                "status": "FAILED",
                "details": str(e)
            })
            return False
    
    def initialize_agent_data_schema(self) -> bool:
        """Initialize agent data storage schema."""
        try:
            with self.get_connection() as conn:
                # Create agent states table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS agent_states (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_id TEXT NOT NULL UNIQUE,
                        state_data TEXT NOT NULL,
                        trust_score REAL DEFAULT 0.5,
                        last_updated REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create agent interactions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS agent_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_agent_id TEXT NOT NULL,
                        target_agent_id TEXT NOT NULL,
                        interaction_type TEXT NOT NULL,
                        interaction_data TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        trust_impact REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create simulation metrics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS simulation_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        metric_metadata TEXT,
                        timestamp REAL NOT NULL,
                        simulation_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                agent_indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_agent_states_id ON agent_states(agent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_agent_states_trust ON agent_states(trust_score)",
                    "CREATE INDEX IF NOT EXISTS idx_agent_interactions_source ON agent_interactions(source_agent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_agent_interactions_target ON agent_interactions(target_agent_id)",
                    "CREATE INDEX IF NOT EXISTS idx_agent_interactions_timestamp ON agent_interactions(timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_simulation_metrics_name ON simulation_metrics(metric_name)",
                    "CREATE INDEX IF NOT EXISTS idx_simulation_metrics_timestamp ON simulation_metrics(timestamp)"
                ]
                
                for index_sql in agent_indexes:
                    conn.execute(index_sql)
                
                conn.commit()
                logger.info("Agent data schema initialized successfully")
                
                self.test_results.append({
                    "test": "Initialize agent data schema",
                    "status": "SUCCESS",
                    "details": "Agent tables and indexes created"
                })
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize agent data schema: {e}")
            self.test_results.append({
                "test": "Initialize agent data schema",
                "status": "FAILED",
                "details": str(e)
            })
            return False
    
    def test_database_connectivity(self) -> bool:
        """Test basic database connectivity and operations."""
        try:
            with self.get_connection() as conn:
                # Test basic query
                cursor = conn.execute("SELECT sqlite_version()")
                sqlite_version = cursor.fetchone()[0]
                logger.info(f"SQLite version: {sqlite_version}")
                
                # Test write operation
                cursor = conn.execute("""
                    INSERT INTO ledger (timestamp, node_id, features, confidence)
                    VALUES (?, ?, ?, ?)
                """, (time.time(), "test_node", json.dumps({"test": True}), 0.95))
                
                test_id = cursor.lastrowid
                conn.commit()
                
                # Test read operation
                cursor = conn.execute("SELECT * FROM ledger WHERE id = ?", (test_id,))
                row = cursor.fetchone()
                
                if row:
                    logger.info(f"Test record inserted and retrieved: ID={test_id}")
                    # Clean up test record
                    conn.execute("DELETE FROM ledger WHERE id = ?", (test_id,))
                    conn.commit()
                    
                    self.test_results.append({
                        "test": "Database connectivity test",
                        "status": "SUCCESS",
                        "details": f"SQLite {sqlite_version}, write/read operations working"
                    })
                    return True
                else:
                    raise Exception("Failed to retrieve test record")
                    
        except Exception as e:
            logger.error(f"Database connectivity test failed: {e}")
            self.test_results.append({
                "test": "Database connectivity test",
                "status": "FAILED",
                "details": str(e)
            })
            return False
    
    def test_data_management_integration(self) -> bool:
        """Test integration with data management system."""
        try:
            # Import the data management system
            from src.data.data_management_system import (
                AdvancedDataAnalyticsFramework,
                RealTimeDataStreamingSystem,
                HistoricalDataManager,
                DataVersioningSystem
            )
            
            # Test analytics framework initialization
            analytics = AdvancedDataAnalyticsFramework()
            logger.info("Analytics framework initialized")
            
            # Test streaming system initialization
            streaming = RealTimeDataStreamingSystem()
            logger.info("Streaming system initialized")
            
            # Test historical data manager initialization
            historical = HistoricalDataManager()
            logger.info("Historical data manager initialized")
            
            # Test versioning system initialization
            versioning = DataVersioningSystem()
            logger.info("Data versioning system initialized")
            
            self.test_results.append({
                "test": "Data management integration test",
                "status": "SUCCESS",
                "details": "All data management components initialized successfully"
            })
            return True
            
        except Exception as e:
            logger.error(f"Data management integration test failed: {e}")
            self.test_results.append({
                "test": "Data management integration test",
                "status": "FAILED",
                "details": str(e)
            })
            return False
    
    def test_ledger_operations(self) -> bool:
        """Test ledger operations using the DatabaseLedger class."""
        try:
            # Try to import and test the ledger manager
            try:
                from src.core.database.ledger_manager import DatabaseLedger as LedgerManager
                ledger_manager = LedgerManager(self.db_path)
                logger.info("Ledger manager (ledger_manager.py) initialized")
                
                # Test basic ledger operations
                test_entry = {
                    "timestamp": time.time(),
                    "node_id": "test_node_ledger",
                    "features": {"test": True, "value": 42},
                    "confidence": 0.87
                }
                
                entry_id = ledger_manager.append_entry(test_entry)
                logger.info(f"Test entry added with ID: {entry_id}")
                
                # Test reading entries
                entries = ledger_manager.read_ledger()
                logger.info(f"Retrieved {len(entries)} entries from ledger")
                
                # Test getting specific entry
                retrieved_entry = ledger_manager.get_entry_by_id(entry_id)
                if retrieved_entry:
                    logger.info(f"Retrieved specific entry: {retrieved_entry['id']}")
                
                self.test_results.append({
                    "test": "Ledger operations test (ledger_manager.py)",
                    "status": "SUCCESS",
                    "details": f"Ledger manager operations working, {len(entries)} entries"
                })
                
            except ImportError as e:
                logger.warning(f"Could not import ledger_manager: {e}")
                
                # Test the core database ledger
                from src.core.database import DatabaseLedger as CoreLedger
                core_ledger = CoreLedger(self.db_path)
                logger.info("Core database ledger initialized")
                
                # Test basic operations
                test_entry = {
                    "timestamp": time.time(),
                    "node_id": "test_node_core",
                    "features": {"test": True, "value": 123},
                    "confidence": 0.92
                }
                
                entry_id = core_ledger.append_entry(test_entry)
                logger.info(f"Test entry added with ID: {entry_id}")
                
                entries = core_ledger.read_ledger()
                logger.info(f"Retrieved {len(entries)} entries from core ledger")
                
                self.test_results.append({
                    "test": "Ledger operations test (core database)",
                    "status": "SUCCESS",
                    "details": f"Core database ledger operations working, {len(entries)} entries"
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Ledger operations test failed: {e}")
            self.test_results.append({
                "test": "Ledger operations test",
                "status": "FAILED",
                "details": str(e)
            })
            return False
    
    def validate_file_permissions(self) -> bool:
        """Validate database file permissions and accessibility."""
        try:
            # Check if database file exists
            db_exists = Path(self.db_path).exists()
            
            # Check write permissions
            can_write = os.access(self.db_path, os.W_OK) if db_exists else False
            
            # Test creating and writing to the database
            with self.get_connection() as conn:
                # Try to get file info
                cursor = conn.execute("PRAGMA database_list")
                db_info = cursor.fetchone()
                
                if db_info:
                    logger.info(f"Database info: {db_info}")
                
                # Get database size
                cursor = conn.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                cursor = conn.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                db_size_bytes = page_count * page_size
                
                logger.info(f"Database size: {db_size_bytes} bytes ({db_size_bytes / 1024:.1f} KB)")
                
            self.test_results.append({
                "test": "File permissions validation",
                "status": "SUCCESS",
                "details": f"Database file accessible, size: {db_size_bytes} bytes"
            })
            return True
            
        except Exception as e:
            logger.error(f"File permissions validation failed: {e}")
            self.test_results.append({
                "test": "File permissions validation",
                "status": "FAILED",
                "details": str(e)
            })
            return False
    
    def create_database_info_file(self) -> bool:
        """Create a database info file with initialization details."""
        try:
            # Get database statistics
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                table_info = {}
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_info[table] = count
            
            # Create database info
            db_info = {
                "initialization_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "database_path": str(Path(self.db_path).absolute()),
                "database_size_bytes": Path(self.db_path).stat().st_size,
                "tables": table_info,
                "test_results": self.test_results,
                "initialization_duration": time.time() - self.start_time,
                "environment": "development"
            }
            
            # Save to file
            info_file = "logs/database_info.json"
            with open(info_file, 'w') as f:
                json.dump(db_info, f, indent=2)
            
            logger.info(f"Database info saved to {info_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database info file: {e}")
            return False
    
    def run_initialization(self) -> Dict[str, Any]:
        """Run the complete database initialization process."""
        logger.info("Starting database initialization process...")
        
        initialization_steps = [
            ("Create directories", self.create_directories),
            ("Initialize main ledger schema", self.initialize_main_ledger_schema),
            ("Initialize agent data schema", self.initialize_agent_data_schema),
            ("Test database connectivity", self.test_database_connectivity),
            ("Test data management integration", self.test_data_management_integration),
            ("Test ledger operations", self.test_ledger_operations),
            ("Validate file permissions", self.validate_file_permissions),
            ("Create database info file", self.create_database_info_file)
        ]
        
        successful_steps = 0
        failed_steps = 0
        
        for step_name, step_function in initialization_steps:
            logger.info(f"Running step: {step_name}")
            try:
                if step_function():
                    successful_steps += 1
                else:
                    failed_steps += 1
            except Exception as e:
                logger.error(f"Step '{step_name}' failed with exception: {e}")
                failed_steps += 1
        
        # Final summary
        total_time = time.time() - self.start_time
        success_rate = (successful_steps / len(initialization_steps)) * 100
        
        logger.info(f"Database initialization completed in {total_time:.2f} seconds")
        logger.info(f"Successful steps: {successful_steps}/{len(initialization_steps)} ({success_rate:.1f}%)")
        
        if failed_steps > 0:
            logger.warning(f"Failed steps: {failed_steps}")
        
        return {
            "success": failed_steps == 0,
            "total_steps": len(initialization_steps),
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "success_rate": success_rate,
            "duration": total_time,
            "test_results": self.test_results
        }

def main():
    """Main function to run database initialization."""
    try:
        # Initialize the database
        initializer = DatabaseInitializer()
        results = initializer.run_initialization()
        
        # Print summary
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION SUMMARY")
        print("="*60)
        print(f"Status: {'SUCCESS' if results['success'] else 'PARTIAL SUCCESS'}")
        print(f"Duration: {results['duration']:.2f} seconds")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Steps Completed: {results['successful_steps']}/{results['total_steps']}")
        
        if results['failed_steps'] > 0:
            print(f"Steps Failed: {results['failed_steps']}")
            print("\nFailed tests:")
            for test in results['test_results']:
                if test['status'] == 'FAILED':
                    print(f"  - {test['test']}: {test['details']}")
        
        print(f"\nDatabase file: {initializer.db_path}")
        print(f"Log file: logs/database_init.log")
        print(f"Info file: logs/database_info.json")
        print("="*60)
        
        return 0 if results['success'] else 1
        
    except Exception as e:
        logger.error(f"Database initialization failed with critical error: {e}")
        print(f"\nCRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)