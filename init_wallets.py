"""
اسکریپت ایجاد کیف پول برای کاربران موجود
این اسکریپت کیف پول را برای تمام کاربرانی که هنوز کیف پول ندارند ایجاد می‌کند
"""

from app import app
from models import db, User, Wallet

def init_wallets():
    """ایجاد کیف پول برای کاربران موجود"""
    with app.app_context():
        # دریافت تمام کاربران
        users = User.query.all()
        created_count = 0
        existing_count = 0
        
        for user in users:
            # بررسی وجود کیف پول
            if not user.wallet:
                wallet = Wallet(user_id=user.id, balance=0)
                db.session.add(wallet)
                created_count += 1
                print(f"کیف پول برای کاربر {user.username} ({user.full_name}) ایجاد شد.")
            else:
                existing_count += 1
        
        # ذخیره تغییرات
        db.session.commit()
        
        print(f"\n=== خلاصه ===")
        print(f"کیف پول‌های جدید ایجاد شده: {created_count}")
        print(f"کیف پول‌های موجود: {existing_count}")
        print(f"جمع کل کاربران: {len(users)}")
        print("\nعملیات با موفقیت انجام شد!")

if __name__ == '__main__':
    init_wallets()

