"""
Migration script to add discount_type and priority fields to product_discount table
"""

from app import app
from models import db
from sqlalchemy import text

def run_migration():
    """Run migration to add discount_type and priority columns"""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('product_discount')]
            
            print("Checking existing columns...")
            print(f"Current columns: {columns}")
            
            # Add discount_type column if it doesn't exist
            if 'discount_type' not in columns:
                print("\nAdding discount_type column...")
                db.session.execute(text("""
                    ALTER TABLE product_discount 
                    ADD COLUMN discount_type VARCHAR(20) DEFAULT 'daily'
                """))
                # Update existing records
                db.session.execute(text("""
                    UPDATE product_discount 
                    SET discount_type = 'daily' 
                    WHERE discount_type IS NULL
                """))
                print("✅ discount_type column added successfully")
            else:
                print("✅ discount_type column already exists")
            
            # Add priority column if it doesn't exist
            if 'priority' not in columns:
                print("\nAdding priority column...")
                db.session.execute(text("""
                    ALTER TABLE product_discount 
                    ADD COLUMN priority INTEGER DEFAULT 0
                """))
                print("✅ priority column added successfully")
            else:
                print("✅ priority column already exists")
            
            # Create indexes
            print("\nCreating indexes...")
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_product_discount_type 
                    ON product_discount(discount_type)
                """))
                print("✅ Index on discount_type created")
            except Exception as e:
                print(f"⚠️  Index on discount_type may already exist: {e}")
            
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_product_discount_active_type 
                    ON product_discount(is_active, discount_type)
                """))
                print("✅ Index on is_active, discount_type created")
            except Exception as e:
                print(f"⚠️  Index on is_active, discount_type may already exist: {e}")
            
            try:
                db.session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_product_discount_priority 
                    ON product_discount(priority DESC)
                """))
                print("✅ Index on priority created")
            except Exception as e:
                print(f"⚠️  Index on priority may already exist: {e}")
            
            # Commit changes
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
            # Verify columns
            inspector = db.inspect(db.engine)
            columns_after = [col['name'] for col in inspector.get_columns('product_discount')]
            print(f"\nColumns after migration: {columns_after}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("Discount Migration Script")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    if success:
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("You can now use the discount management system.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Migration failed. Please check the error messages above.")
        print("=" * 60)

