#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script
Moves database from project directory to external data directory
"""

import os
import shutil
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def migrate_database():
    """Move database from old location to new external location"""
    
    # Determine old and new paths
    project_root = Path(__file__).parent
    data_dir = project_root.parent / 'data'
    
    old_locations = [
        project_root / 'instance' / 'asia_salman.db',
        project_root / 'asia_salman.db',
    ]
    
    new_db_path = data_dir / 'asia_salman.db'
    
    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)
    print(f"[OK] Data directory created: {data_dir}")
    
    # Search for database in old locations
    found_db = None
    for old_path in old_locations:
        if old_path.exists():
            found_db = old_path
            print(f"[OK] Database found: {found_db}")
            break
    
    if not found_db:
        print("[WARNING] No database found in old locations.")
        if new_db_path.exists():
            print(f"[OK] Database already exists in new location: {new_db_path}")
            return True
        else:
            print("[INFO] Database will be created when the application runs.")
            return True
    
    # Check if database exists in new location
    if new_db_path.exists():
        response = input(f"[WARNING] Database already exists in new location: {new_db_path}\n"
                        f"Do you want to replace it with the old database? (y/n): ")
        if response.lower() != 'y':
            print("[CANCELLED] Migration cancelled.")
            return False
        # Backup existing database
        import time
        backup_path = data_dir / f"asia_salman_backup_before_migration_{int(time.time())}.db"
        shutil.copy2(new_db_path, backup_path)
        print(f"[OK] Backup created: {backup_path}")
    
    # Move database
    try:
        print(f"[INFO] Moving database from {found_db} to {new_db_path}...")
        shutil.copy2(found_db, new_db_path)
        print(f"[OK] Database moved successfully: {new_db_path}")
        
        # Move WAL and SHM files if they exist
        wal_files = [
            (found_db.parent / f"{found_db.name}-wal", data_dir / f"{new_db_path.name}-wal"),
            (found_db.parent / f"{found_db.name}-shm", data_dir / f"{new_db_path.name}-shm"),
        ]
        
        for old_wal, new_wal in wal_files:
            if old_wal.exists():
                shutil.copy2(old_wal, new_wal)
                print(f"[OK] File {old_wal.name} moved")
        
        # Optionally delete old files (skip in non-interactive mode)
        try:
            response = input(f"Do you want to delete old database files? (y/n): ")
        except (EOFError, KeyboardInterrupt):
            print("[INFO] Running in non-interactive mode. Old files kept.")
            response = 'n'
        
        if response.lower() == 'y':
            try:
                found_db.unlink()
                print(f"[OK] Old file deleted: {found_db}")
                
                # Delete old WAL and SHM files
                for old_wal, _ in wal_files:
                    if old_wal.exists():
                        old_wal.unlink()
                        print(f"[OK] Old file deleted: {old_wal}")
            except Exception as e:
                print(f"[WARNING] Error deleting old files: {e}")
        
        print("\n[SUCCESS] Database migration completed successfully!")
        print(f"[INFO] New database path: {new_db_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration to External Directory")
    print("=" * 60)
    migrate_database()

