#!/usr/bin/env python3
"""
Migration script to reduce points by three digits (divide by 1000)
This script updates all existing points data to reflect the new reduced points system
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Run the points reduction migration"""
    
    # Database path
    db_path = 'asia_salman.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting points reduction migration...")
        print("This will reduce all points by three digits (divide by 1000)")
        
        # Backup current data
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_before_points_reduction_{backup_timestamp}.db"
        
        print(f"Creating backup: {backup_file}")
        backup_conn = sqlite3.connect(backup_file)
        conn.backup(backup_conn)
        backup_conn.close()
        print("Backup created successfully!")
        
        # Read and execute migration SQL
        with open('migration_reduce_points_three_digits.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            print(f"Executing statement {i}/{len(statements)}...")
            cursor.execute(statement)
            affected_rows = cursor.rowcount
            print(f"  Affected rows: {affected_rows}")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify changes
        print("\nVerifying changes...")
        
        # Check PointsRule
        cursor.execute("SELECT COUNT(*) FROM points_rule WHERE points_per_100k_rials < 1")
        rules_updated = cursor.fetchone()[0]
        print(f"PointsRule records with reduced values: {rules_updated}")
        
        # Check UserLevel
        cursor.execute("SELECT COUNT(*) FROM user_level WHERE min_points < 10")
        levels_updated = cursor.fetchone()[0]
        print(f"UserLevel records with reduced values: {levels_updated}")
        
        # Check Reward
        cursor.execute("SELECT COUNT(*) FROM reward WHERE points_required < 10")
        rewards_updated = cursor.fetchone()[0]
        print(f"Reward records with reduced values: {rewards_updated}")
        
        # Check UserPoints
        cursor.execute("SELECT COUNT(*) FROM user_points WHERE current_points < 100")
        user_points_updated = cursor.fetchone()[0]
        print(f"UserPoints records with reduced values: {user_points_updated}")
        
        # Check PointsTransaction
        cursor.execute("SELECT COUNT(*) FROM points_transaction WHERE ABS(points_amount) < 100")
        transactions_updated = cursor.fetchone()[0]
        print(f"PointsTransaction records with reduced values: {transactions_updated}")
        
        print(f"\nMigration completed! Backup saved as: {backup_file}")
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Points Reduction Migration Tool")
    print("=" * 40)
    
    # Ask for confirmation
    response = input("This will reduce all points by 1000x. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        exit(0)
    
    success = run_migration()
    if success:
        print("\n✅ Migration completed successfully!")
        print("All points have been reduced by three digits (divided by 1000)")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")
