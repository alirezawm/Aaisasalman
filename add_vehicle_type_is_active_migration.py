#!/usr/bin/env python3
"""
Migration script to add is_active column to vehicle_type table
This script adds the is_active column with default value True to all existing records
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
    """Run the migration to add is_active column to vehicle_type table"""
    
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
        if check_column_exists(cursor, 'vehicle_type', 'is_active'):
            print("Column 'is_active' already exists in vehicle_type table.")
            print("Migration not needed.")
            conn.close()
            return True
        
        print("Starting migration to add is_active column to vehicle_type table...")
        
        # Backup current data
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_before_vehicle_type_is_active_{backup_timestamp}.db"
        
        print(f"Creating backup: {backup_file}")
        backup_conn = sqlite3.connect(backup_file)
        conn.backup(backup_conn)
        backup_conn.close()
        print("Backup created successfully!")
        
        # Add the is_active column with default value True
        print("Adding is_active column to vehicle_type table...")
        try:
            cursor.execute("""
                ALTER TABLE vehicle_type 
                ADD COLUMN is_active BOOLEAN DEFAULT 1
            """)
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower() or "duplicate column name" in str(e).lower():
                print("Column 'is_active' already exists. Skipping column addition.")
                # Column already exists, which is fine - we'll just update existing records
            else:
                raise
        
        # Update all existing records to have is_active = True (in case default didn't apply)
        print("Updating existing records to set is_active = True...")
        cursor.execute("""
            UPDATE vehicle_type 
            SET is_active = 1 
            WHERE is_active IS NULL
        """)
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify changes
        print("\nVerifying changes...")
        cursor.execute("SELECT COUNT(*) FROM vehicle_type WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM vehicle_type")
        total_count = cursor.fetchone()[0]
        print(f"Total vehicle types: {total_count}")
        print(f"Active vehicle types: {active_count}")
        
        # Verify column exists
        if check_column_exists(cursor, 'vehicle_type', 'is_active'):
            print("✓ Column 'is_active' successfully added to vehicle_type table")
        else:
            print("✗ ERROR: Column 'is_active' was not added!")
            conn.close()
            return False
        
        conn.close()
        print("\nMigration completed successfully!")
        print(f"Backup saved as: {backup_file}")
        return True
        
    except sqlite3.OperationalError as e:
        error_msg = str(e).lower()
        if "duplicate column" in error_msg or "duplicate column name" in error_msg:
            print(f"INFO: Column 'is_active' already exists in vehicle_type table.")
            print("Migration not needed - column is already present.")
            # Still update any NULL values to be safe
            try:
                cursor.execute("""
                    UPDATE vehicle_type 
                    SET is_active = 1 
                    WHERE is_active IS NULL
                """)
                conn.commit()
                print("Updated any NULL is_active values to True.")
            except Exception as update_error:
                print(f"Note: Could not update NULL values: {update_error}")
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
    print("Vehicle Type is_active Column Migration")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    if success:
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("You can now use the vehicle_type.is_active filter in your code.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("Please check the error messages above and try again.")
        print("=" * 60)
        sys.exit(1)

