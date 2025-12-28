"""
Simple migration script to add discount_type and priority fields
Uses sqlite3 directly to avoid import issues
"""

import sqlite3
import os
from pathlib import Path

# Find database path - match app.py logic exactly
if 'DATABASE_DIR' in os.environ:
    DATABASE_DIR = os.environ.get('DATABASE_DIR')
else:
    # Auto-detect: if running in /root/, use /root/data/, otherwise use ../data/
    project_root = Path(__file__).parent
    if str(project_root).startswith('/root/'):
        DATABASE_DIR = '/root/data'
    else:
        DATABASE_DIR = str(project_root.parent / 'data')

# Create directory if it doesn't exist
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATABASE_DIR, 'asia_salman.db')

# Fallback to instance directory
if not os.path.exists(DATABASE_PATH):
    project_root = Path(__file__).parent
    instance_path = os.path.join(project_root, 'instance', 'asia_salman.db')
    if os.path.exists(instance_path):
        DATABASE_PATH = instance_path

print("=" * 60)
print("Discount Migration Script")
print("=" * 60)
print(f"Database path: {DATABASE_PATH}")

if not os.path.exists(DATABASE_PATH):
    print(f"\n[ERROR] Database file not found at: {DATABASE_PATH}")
    print("Please check the database path.")
    exit(1)

try:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(product_discount)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\nCurrent columns: {columns}")
    
    # Add discount_type column if it doesn't exist
    if 'discount_type' not in columns:
        print("\nAdding discount_type column...")
        cursor.execute("""
            ALTER TABLE product_discount 
            ADD COLUMN discount_type VARCHAR(20) DEFAULT 'daily'
        """)
        # Update existing records
        cursor.execute("""
            UPDATE product_discount 
            SET discount_type = 'daily' 
            WHERE discount_type IS NULL
        """)
        print("[OK] discount_type column added successfully")
    else:
        print("[OK] discount_type column already exists")
    
    # Add priority column if it doesn't exist
    if 'priority' not in columns:
        print("\nAdding priority column...")
        cursor.execute("""
            ALTER TABLE product_discount 
            ADD COLUMN priority INTEGER DEFAULT 0
        """)
        print("[OK] priority column added successfully")
    else:
        print("[OK] priority column already exists")
    
    # Create indexes
    print("\nCreating indexes...")
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_discount_type 
            ON product_discount(discount_type)
        """)
        print("[OK] Index on discount_type created")
    except Exception as e:
        print(f"[WARNING] Index on discount_type: {e}")
    
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_discount_active_type 
            ON product_discount(is_active, discount_type)
        """)
        print("[OK] Index on is_active, discount_type created")
    except Exception as e:
        print(f"[WARNING] Index on is_active, discount_type: {e}")
    
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_discount_priority 
            ON product_discount(priority DESC)
        """)
        print("[OK] Index on priority created")
    except Exception as e:
        print(f"[WARNING] Index on priority: {e}")
    
    # Commit changes
    conn.commit()
    print("\n[OK] Migration completed successfully!")
    
    # Verify columns
    cursor.execute("PRAGMA table_info(product_discount)")
    columns_after = [row[1] for row in cursor.fetchall()]
    print(f"\nColumns after migration: {columns_after}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("You can now use the discount management system.")
    print("=" * 60)
    
except sqlite3.Error as e:
    print(f"\n[ERROR] SQLite error: {str(e)}")
    if conn:
        conn.rollback()
        conn.close()
    exit(1)
except Exception as e:
    print(f"\n[ERROR] Error during migration: {str(e)}")
    import traceback
    traceback.print_exc()
    if conn:
        conn.rollback()
        conn.close()
    exit(1)

