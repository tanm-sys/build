import pytest
import tempfile
import os
from src.core.database import DatabaseLedger

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    # Close all database connections before deleting the file
    from src.core.database import close_db_connection
    close_db_connection()
    os.unlink(path)

def test_database_ledger_init(temp_db):
    """Test DatabaseLedger initialization and table creation."""
    ledger = DatabaseLedger(db_file=temp_db)
    
    assert ledger.db_file == temp_db
    # Verify table created by checking schema
    import sqlite3
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ledger'")
        assert cursor.fetchone() is not None

def test_append_entry(temp_db):
    """Test appending an entry and returning ID."""
    ledger = DatabaseLedger(db_file=temp_db)
    entry = {
        'timestamp': 123.45,
        'node_id': 'Node_1',
        'features': [{'packet_size': 500.0, 'source_ip': '192.168.1.1'}],
        'confidence': 0.8
    }
    
    entry_id = ledger.append_entry(entry)
    
    assert isinstance(entry_id, int)
    assert entry_id > 0
    
    # Verify inserted
    entries = ledger.read_ledger()
    assert len(entries) == 1
    inserted = entries[0]
    assert inserted['id'] == entry_id
    assert inserted['timestamp'] == pytest.approx(123.45)
    assert inserted['node_id'] == 'Node_1'
    assert inserted['confidence'] == pytest.approx(0.8)
    assert inserted['features'] == entry['features']

def test_read_ledger(temp_db):
    """Test reading all entries from ledger."""
    ledger = DatabaseLedger(db_file=temp_db)
    
    # Append two entries
    entry1 = {'timestamp': 1.0, 'node_id': 'Node_1', 'features': [], 'confidence': 0.5}
    entry2 = {'timestamp': 2.0, 'node_id': 'Node_2', 'features': [], 'confidence': 0.6}
    ledger.append_entry(entry1)
    id2 = ledger.append_entry(entry2)
    
    entries = ledger.read_ledger()
    
    assert len(entries) == 2
    assert entries[0]['id'] == 1
    assert entries[1]['id'] == id2
    assert entries[0]['timestamp'] == pytest.approx(1.0)
    assert entries[1]['timestamp'] == pytest.approx(2.0)

def test_get_new_entries(temp_db):
    """Test getting new entries after last seen ID."""
    ledger = DatabaseLedger(db_file=temp_db)
    
    entry1 = {'timestamp': 1.0, 'node_id': 'Node_1', 'features': [], 'confidence': 0.5}
    entry2 = {'timestamp': 2.0, 'node_id': 'Node_2', 'features': [], 'confidence': 0.6}
    id1 = ledger.append_entry(entry1)
    id2 = ledger.append_entry(entry2)
    
    # No new after id2
    new = ledger.get_new_entries(id2)
    assert len(new) == 0
    
    # New after id1
    new = ledger.get_new_entries(id1)
    assert len(new) == 1
    assert new[0]['id'] == id2
    
    # New after 0
    new = ledger.get_new_entries(0)
    assert len(new) == 2

def test_thread_safety_append(temp_db):
    """Test thread-safe append (basic, since lock is used)."""
    ledger = DatabaseLedger(db_file=temp_db)
    
    # Simulate concurrent appends
    import threading
    entries = [
        {'timestamp': 1.0, 'node_id': 'Node_1', 'features': [], 'confidence': 0.5},
        {'timestamp': 2.0, 'node_id': 'Node_2', 'features': [], 'confidence': 0.6}
    ]
    
    def append_entry(i):
        ledger.append_entry(entries[i])
    
    threads = [threading.Thread(target=append_entry, args=(i,)) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    read_entries = ledger.read_ledger()
    assert len(read_entries) == 2  # Both inserted without corruption