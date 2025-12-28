"""
Migration script to create ProductDiscount tables
"""

from app import app
from models import db, ProductDiscount, ProductDiscountProduct
from datetime import datetime

def create_discount_tables():
    """Create ProductDiscount and ProductDiscountProduct tables"""
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'product_discount' in tables and 'product_discount_products' in tables:
                print("✅ جداول تخفیفات با موفقیت ایجاد شدند!")
                print(f"   - product_discount")
                print(f"   - product_discount_products")
                return True
            else:
                print("❌ خطا در ایجاد جداول")
                return False
                
        except Exception as e:
            print(f"❌ خطا: {str(e)}")
            return False

if __name__ == '__main__':
    print("شروع migration برای جداول تخفیفات...")
    create_discount_tables()
    print("Migration تکمیل شد!")

