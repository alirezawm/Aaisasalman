"""
Helper script to restart the application and clear database locks
"""
import os
import sys
import time
import sqlite3
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def close_database_connections():
    """Close all database connections and clear locks"""
    from database_path import get_database_path
    db_path = get_database_path()
    
    if not db_path.exists():
        print("Database file not found. Creating new instance.")
        return
    
    try:
        # Connect and immediately close to clear any locks
        conn = sqlite3.connect(str(db_path), timeout=1)
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.commit()
        conn.close()
        print("[OK] Database connections closed successfully")
        
        # Enable WAL mode
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.commit()
        conn.close()
        print("[OK] WAL mode enabled")
        
    except sqlite3.OperationalError as e:
        print(f"[WARNING] Could not access database: {e}")
        print("Database may be locked by another process.")
        print("\nPlease:")
        print("1. Close all other Python processes accessing the database")
        print("2. Close any database browser tools (DB Browser for SQLite, etc.)")
        print("3. Wait a moment and try again")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    return True

def check_wal_files():
    """Check for WAL files that might indicate active transactions"""
    from database_path import get_database_path
    db_path = get_database_path()
    wal_path = db_path.parent / f"{db_path.name}-wal"
    shm_path = db_path.parent / f"{db_path.name}-shm"
    
    print("\nChecking database files:")
    print(f"  Database: {db_path.exists()} - {db_path}")
    print(f"  WAL file: {wal_path.exists()} - {wal_path}")
    print(f"  SHM file: {shm_path.exists()} - {shm_path}")
    
    if wal_path.exists():
        size = wal_path.stat().st_size
        print(f"  WAL size: {size} bytes")

def main():
    print("=" * 60)
    print("Database Lock Resolver and Application Restart Helper")
    print("=" * 60)
    print()
    
    # Check current state
    check_wal_files()
    print()
    
    # Try to close connections
    print("Attempting to clear database locks...")
    if close_database_connections():
        print("\n[SUCCESS] Database is ready!")
        print("\nYou can now restart your Flask application:")
        print("  python app.py")
    else:
        print("\n[FAILED] Could not clear database locks.")
        print("\nTroubleshooting steps:")
        print("1. Stop the Flask development server (Ctrl+C)")
        print("2. Check for other Python processes:")
        print("   - Windows: tasklist | findstr python")
        print("   - Linux/Mac: ps aux | grep python")
        print("3. Close any database viewer applications")
        print("4. Run this script again")
        print("5. If the problem persists, restart your computer")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()

