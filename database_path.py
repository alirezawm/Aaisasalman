"""
Utility module for database path resolution
Provides consistent database path across all scripts
"""
import os
from pathlib import Path

def get_database_path():
    """
    Get the database path using the same logic as app.py
    Returns the path to asia_salman.db in the external data directory
    Priority: 1. DATABASE_DIR env var, 2. /root/data/ (server), 3. ../data/ (local)
    """
    # Use environment variable DATABASE_DIR if set
    if 'DATABASE_DIR' in os.environ:
        database_dir = os.environ.get('DATABASE_DIR')
    else:
        # Auto-detect: if running in /root/, use /root/data/, otherwise use ../data/
        project_root = Path(__file__).parent
        if str(project_root).startswith('/root/'):
            database_dir = '/root/data'
        else:
            database_dir = str(project_root.parent / 'data')
    
    os.makedirs(database_dir, exist_ok=True)
    database_path = os.path.join(database_dir, 'asia_salman.db')
    return Path(database_path)

def find_database():
    """
    Find database file in old or new locations (for migration compatibility)
    Returns Path object or None
    """
    project_root = Path(__file__).parent
    
    # Check new location first
    new_path = get_database_path()
    if new_path.exists():
        return new_path
    
    # Check old locations for backward compatibility
    old_locations = [
        project_root / 'instance' / 'asia_salman.db',
        project_root / 'asia_salman.db',
        project_root / 'instance' / 'asiasalman.db',
        project_root / 'asiasalman.db',
    ]
    
    for old_path in old_locations:
        if old_path.exists():
            return old_path
    
    return None

