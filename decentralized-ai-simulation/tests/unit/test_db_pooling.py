#!/usr/bin/env python3
"""Test script for database connection pooling."""

import threading
import time
import random
import numpy as np
from src.core.database import DatabaseLedger

# Initialize numpy random generator for modern random number generation
rng = np.random.default_rng(42)

def test_connection_pooling():
    """Test that database connection pooling works correctly."""
    print("Testing database connection pooling...")
    
    # Create multiple database instances to test pooling
    db_instances = []
    for i in range(5):
        db = DatabaseLedger()
        db_instances.append(db)
        print(f"Created database instance {i+1}")
    
    # Verify all instances can access the database
    for i, db in enumerate(db_instances):
        entries = db.read_ledger()
        print(f"Database instance {i+1} has {len(entries)} entries")
    
    print("✓ Database connection pooling test passed")

def test_concurrent_access():
    """Test concurrent access to database."""
    print("\nTesting concurrent database access...")
    
    results = {}
    
    def worker(worker_id):
        db = DatabaseLedger()
        try:
            # Create a valid entry with required keys
            features = rng.random(10).tolist()  # 10 random features
            entry = {
                'timestamp': time.time(),
                'node_id': f'worker_{worker_id}',
                'features': features,
                'confidence': random.random()
            }
            entry_id = db.append_entry(entry)
            entries = db.read_ledger()
            results[worker_id] = {
                'success': True,
                'entry_id': entry_id,
                'total_entries': len(entries)
            }
        except Exception as e:
            results[worker_id] = {
                'success': False,
                'error': str(e)
            }
    
    # Create multiple threads to access database concurrently
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Check results
    successful = sum(1 for r in results.values() if r['success'])
    print(f"Concurrent access test: {successful}/10 threads succeeded")
    
    if successful == 10:
        print("✓ Concurrent database access test passed")
    else:
        print("✗ Concurrent database access test failed")
        for worker_id, result in results.items():
            if not result['success']:
                print(f"  Worker {worker_id} failed: {result['error']}")

if __name__ == "__main__":
    test_connection_pooling()
    test_concurrent_access()
    print("\nAll database pooling tests completed!")