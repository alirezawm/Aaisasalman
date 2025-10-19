#!/usr/bin/env python3
"""
Database lock fix utility
This script helps resolve SQLite database lock issues
"""

import os
import sys
import time
import sqlite3
from pathlib import Path

def check_database_locks(db_path):
    """Check if database files are locked"""
    print(f"Checking database locks for: {db_path}")
    
    # Check main database file
    if os.path.exists(db_path):
        try:
            # Try to open in exclusive mode
            conn = sqlite3.connect(db_path, timeout=1)
            conn.execute("PRAGMA journal_mode")
            conn.close()
            print("[OK] Main database is accessible")
        except sqlite3.OperationalError as e:
            print(f"[ERROR] Main database is locked: {e}")
            return False
    else:
        print("[ERROR] Main database file not found")
        return False
    
    # Check WAL file
    wal_path = f"{db_path}-wal"
    if os.path.exists(wal_path):
        print(f"[OK] WAL file exists: {os.path.getsize(wal_path)} bytes")
    else:
        print("[INFO] No WAL file found")
    
    # Check SHM file
    shm_path = f"{db_path}-shm"
    if os.path.exists(shm_path):
        print(f"[OK] SHM file exists: {os.path.getsize(shm_path)} bytes")
    else:
        print("[INFO] No SHM file found")
    
    return True

def checkpoint_database(db_path):
    """Checkpoint the WAL file to reduce lock contention"""
    print(f"Checkpointing database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        
        # Get WAL info before checkpoint
        wal_info = conn.execute("PRAGMA wal_checkpoint").fetchone()
        print(f"WAL info before checkpoint: {wal_info}")
        
        # Perform checkpoint
        result = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        print(f"Checkpoint result: {result}")
        
        # Get WAL info after checkpoint
        wal_info_after = conn.execute("PRAGMA wal_checkpoint").fetchone()
        print(f"WAL info after checkpoint: {wal_info_after}")
        
        conn.close()
        print("[OK] Database checkpoint completed successfully")
        return True
        
    except sqlite3.OperationalError as e:
        print(f"[ERROR] Database checkpoint failed: {e}")
        return False

def optimize_database(db_path):
    """Apply database optimizations"""
    print(f"Optimizing database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        
        # Apply optimizations
        optimizations = [
            ("PRAGMA journal_mode=WAL", "Set WAL mode"),
            ("PRAGMA busy_timeout=30000", "Set busy timeout"),
            ("PRAGMA synchronous=NORMAL", "Set synchronous mode"),
            ("PRAGMA cache_size=10000", "Set cache size"),
            ("PRAGMA temp_store=MEMORY", "Set temp store to memory"),
            ("PRAGMA mmap_size=268435456", "Set memory mapping size"),
        ]
        
        for pragma, description in optimizations:
            try:
                conn.execute(pragma)
                print(f"[OK] {description}")
            except Exception as e:
                print(f"[ERROR] {description} failed: {e}")
        
        conn.close()
        print("[OK] Database optimization completed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database optimization failed: {e}")
        return False

def main():
    """Main function"""
    print("SQLite Database Lock Fix Utility")
    print("=" * 40)
    
    # Find database file
    db_paths = [
        "instance/asia_salman.db",
        "asia_salman.db",
        "instance/asiasalman.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("[ERROR] No database file found")
        print("Searched paths:")
        for path in db_paths:
            print(f"  - {path}")
        return 1
    
    print(f"Found database: {db_path}")
    print()
    
    # Check current status
    if not check_database_locks(db_path):
        print("\nDatabase is currently locked. Attempting to resolve...")
        
        # Wait a bit and try again
        print("Waiting 5 seconds...")
        time.sleep(5)
        
        if not check_database_locks(db_path):
            print("Database is still locked. You may need to:")
            print("1. Stop all Python processes accessing the database")
            print("2. Wait for any long-running transactions to complete")
            print("3. Restart your application")
            return 1
    
    print()
    
    # Checkpoint database
    if checkpoint_database(db_path):
        print("[OK] Database checkpoint successful")
    else:
        print("[ERROR] Database checkpoint failed")
    
    print()
    
    # Optimize database
    if optimize_database(db_path):
        print("[OK] Database optimization successful")
    else:
        print("[ERROR] Database optimization failed")
    
    print()
    print("Database maintenance completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
