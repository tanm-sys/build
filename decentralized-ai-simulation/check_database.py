#!/usr/bin/env python3
"""
Database Structure Verification Script
"""

import sqlite3
import sys
import os

def check_database_structure():
    """Check the database structure and content."""
    try:
        conn = sqlite3.connect('ledger.db')
        cursor = conn.cursor()
        
        print("=== DATABASE STRUCTURE VERIFICATION ===\n")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n=== TABLE DETAILS ===\n")
        
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("  Columns:")
            for col in columns:
                print(f"    {col[1]} ({col[2]}) - {'PK' if col[5] else 'Not PK'}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Row count: {count}")
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            
            if indexes:
                print("  Indexes:")
                for idx in indexes:
                    print(f"    {idx[1]} ({idx[2]})")
            
            print()
        
        # Show sample data from main tables
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            
            if rows:
                print(f"Sample data from {table_name}:")
                for i, row in enumerate(rows, 1):
                    print(f"  Row {i}: {row}")
                print()
        
        conn.close()
        print("Database structure verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error checking database structure: {e}")
        return False

if __name__ == "__main__":
    check_database_structure()