#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script for Server
Moves database to /root/data/ directory
"""

import os
import shutil
import sys
from pathlib import Path

# Fix encoding for console
if sys.platform != 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def migrate_database_server():
    """Move database to /root/data/ directory on server"""
    
    # Target directory for server
    target_dir = Path('/root/data')
    target_db = target_dir / 'asia_salman.db'
    
    # Find project root (assuming script is in project root)
    project_root = Path(__file__).parent
    
    # Old database locations to check
    old_locations = [
        project_root / 'instance' / 'asia_salman.db',
        project_root / 'asia_salman.db',
        project_root / 'instance' / 'asiasalman.db',
        project_root / 'asiasalman.db',
        Path('/root/application/instance/asia_salman.db'),
        Path('/root/application/asia_salman.db'),
    ]
    
    # Create target directory
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Target directory created: {target_dir}")
    except PermissionError:
        print(f"[ERROR] Permission denied. Run with sudo or as root user.")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to create target directory: {e}")
        return False
    
    # Find database in old locations
    found_db = None
    for old_path in old_locations:
        if old_path.exists():
            found_db = old_path
            print(f"[OK] Database found: {found_db}")
            break
    
    if not found_db:
        print("[WARNING] No database found in old locations.")
        if target_db.exists():
            print(f"[OK] Database already exists in target location: {target_db}")
            return True
        else:
            print("[INFO] Database will be created when the application runs.")
            return True
    
    # Check if database exists in target location
    if target_db.exists():
        response = input(f"[WARNING] Database already exists in target location: {target_db}\n"
                        f"Do you want to replace it with the old database? (y/n): ")
        if response.lower() != 'y':
            print("[CANCELLED] Migration cancelled.")
            return False
        # Backup existing database
        import time
        backup_path = target_dir / f"asia_salman_backup_before_migration_{int(time.time())}.db"
        shutil.copy2(target_db, backup_path)
        print(f"[OK] Backup created: {backup_path}")
    
    # Move database
    try:
        print(f"[INFO] Moving database from {found_db} to {target_db}...")
        shutil.copy2(found_db, target_db)
        
        # Set proper permissions (read/write for owner, read for group/others)
        os.chmod(target_db, 0o644)
        print(f"[OK] Database moved successfully: {target_db}")
        
        # Move WAL and SHM files if they exist
        wal_files = [
            (found_db.parent / f"{found_db.name}-wal", target_dir / f"{target_db.name}-wal"),
            (found_db.parent / f"{found_db.name}-shm", target_dir / f"{target_db.name}-shm"),
        ]
        
        for old_wal, new_wal in wal_files:
            if old_wal.exists():
                shutil.copy2(old_wal, new_wal)
                os.chmod(new_wal, 0o644)
                print(f"[OK] File {old_wal.name} moved")
        
        # Optionally delete old files
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
        print(f"[INFO] New database path: {target_db}")
        print(f"[INFO] Make sure to restart your application after migration.")
        return True
        
    except PermissionError:
        print(f"[ERROR] Permission denied. Make sure you have write access to {target_dir}")
        print("[INFO] Try running with: sudo python migrate_database_server.py")
        return False
    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration to /root/data/ (Server)")
    print("=" * 60)
    
    if os.geteuid() != 0 and str(Path('/root/data')).startswith('/root/'):
        print("[WARNING] You may need root permissions to write to /root/data/")
        print("[INFO] If migration fails, try: sudo python migrate_database_server.py")
        print()
    
    migrate_database_server()

