#!/usr/bin/env python3
"""Test script for caching mechanisms."""

import time
from src.core.database import DatabaseLedger

def test_caching_mechanisms():
    """Test the caching mechanisms in the database ledger."""
    print("Testing caching mechanisms...")
    
    # Create a database instance
    db = DatabaseLedger()
    
    # Add some test entries
    print("Adding test entries...")
    entry1 = {
        'timestamp': time.time(),
        'node_id': 'test_node_1',
        'features': [{'packet_size': 100.0, 'source_ip': '192.168.1.1'}],
        'confidence': 0.95
    }
    
    entry2 = {
        'timestamp': time.time() + 1,
        'node_id': 'test_node_2',
        'features': [{'packet_size': 200.0, 'source_ip': '192.168.1.2'}],
        'confidence': 0.85
    }
    
    id1 = db.append_entry(entry1)
    id2 = db.append_entry(entry2)
    print(f"Added entries with IDs {id1} and {id2}")
    
    # Test ledger caching
    print("\nTesting ledger caching...")
    start_time = time.time()
    entries1 = db.read_ledger()
    first_read_time = time.time() - start_time
    
    start_time = time.time()
    entries2 = db.read_ledger()
    second_read_time = time.time() - start_time
    
    print(f"First read time: {first_read_time:.6f}s")
    print(f"Second read time: {second_read_time:.6f}s")
    print(f"Performance improvement: {first_read_time/second_read_time:.2f}x" if second_read_time > 0 else "Cached read")
    print(f"Entry count: {len(entries1)} (should be {len(entries2)})")
    
    # Test entry caching
    print("\nTesting entry caching...")
    start_time = time.time()
    entry_first = db.get_entry_by_id(id1)
    first_get_time = time.time() - start_time
    
    start_time = time.time()
    _ = db.get_entry_by_id(id1)  # Second call should be cached
    second_get_time = time.time() - start_time
    
    print(f"First get time: {first_get_time:.6f}s")
    print(f"Second get time: {second_get_time:.6f}s")
    print(f"Performance improvement: {first_get_time/second_get_time:.2f}x" if second_get_time > 0 else "Cached get")
    print(f"Entry retrieved: {entry_first is not None}")
    
    # Test cache invalidation
    print("\nTesting cache invalidation...")
    entry3 = {
        'timestamp': time.time() + 2,
        'node_id': 'test_node_3',
        'features': [{'packet_size': 300.0, 'source_ip': '192.168.1.3'}],
        'confidence': 0.75
    }
    
    # Read cached entries
    cached_entries = db.read_ledger()
    cached_count = len(cached_entries)
    
    # Add new entry (should invalidate cache)
    _ = db.append_entry(entry3)
    
    # Read entries again (should get fresh data)
    fresh_entries = db.read_ledger()
    fresh_count = len(fresh_entries)
    
    print(f"Cached entry count: {cached_count}")
    print(f"Fresh entry count: {fresh_count}")
    print(f"Cache invalidated: {cached_count != fresh_count}")
    
    print("✓ Caching mechanisms test completed")

if __name__ == "__main__":
    test_caching_mechanisms()