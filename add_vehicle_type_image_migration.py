#!/usr/bin/env python3
"""
Migration script to add image column to vehicle_type table
This script adds the image column to store image filenames for the UI
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

def find_database():
    """Find the database file"""
    db_paths = [
        'instance/asia_salman.db',
        'asia_salman.db',
        'instance/asiasalman.db',
        'asiasalman.db'
    ]
    
    for path in db_paths:
        if os.path.exists(path):
            return path
    
    return None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    except Exception as e:
        # If PRAGMA fails, try a different approach
        try:
            # Try to select the column - if it exists, this will work
            cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT 1")
            return True
        except:
            return False

def run_migration():
    """Run the migration to add image column to vehicle_type table"""
    
    # Find database
    db_path = find_database()
    
    if not db_path:
        print("ERROR: Database file not found!")
        print("Searched paths:")
        for path in ['instance/asia_salman.db', 'asia_salman.db', 'instance/asiasalman.db', 'asiasalman.db']:
            print(f"  - {path}")
        return False
    
    print(f"Found database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        if check_column_exists(cursor, 'vehicle_type', 'image'):
            print("Column 'image' already exists in vehicle_type table.")
            print("Migration not needed.")
            conn.close()
            return True
        
        print("Starting migration to add image column to vehicle_type table...")
        
        # Backup current data
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_before_vehicle_type_image_{backup_timestamp}.db"
        
        print(f"Creating backup: {backup_file}")
        backup_conn = sqlite3.connect(backup_file)
        conn.backup(backup_conn)
        backup_conn.close()
        print("Backup created successfully!")
        
        # Add the image column
        print("Adding image column to vehicle_type table...")
        try:
            cursor.execute("""
                ALTER TABLE vehicle_type 
                ADD COLUMN image VARCHAR(255)
            """)
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower() or "duplicate column name" in str(e).lower():
                print("Column 'image' already exists. Skipping column addition.")
                conn.close()
                return True
            else:
                raise
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify changes
        print("\nVerifying changes...")
        if check_column_exists(cursor, 'vehicle_type', 'image'):
            print("✓ Column 'image' successfully added to vehicle_type table")
        else:
            print("✗ ERROR: Column 'image' was not added!")
            conn.close()
            return False
        
        conn.close()
        print("\nMigration completed successfully!")
        print(f"Backup saved as: {backup_file}")
        return True
        
    except sqlite3.OperationalError as e:
        error_msg = str(e).lower()
        if "duplicate column" in error_msg or "duplicate column name" in error_msg:
            print(f"INFO: Column 'image' already exists in vehicle_type table.")
            print("Migration not needed - column is already present.")
            conn.close()
            return True
        else:
            print(f"ERROR: Database operation failed: {e}")
            print("\nPossible causes:")
            print("1. Database is locked by another process")
            print("2. Insufficient permissions")
            print("3. Database file is corrupted")
            return False
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Vehicle Type Image Column Migration")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    if success:
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("You can now use the vehicle_type.image field in your code.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("Please check the error messages above and try again.")
        print("=" * 60)
        sys.exit(1)

