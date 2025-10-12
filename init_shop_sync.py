"""
اسکریپت راه‌اندازی اولیه سیستم همگام‌سازی فروشگاه
Initialize Shop Sync System
"""

from datetime import datetime
from app import app
from models import db, TadbirSyncSettings


def init_shop_sync_settings():
    """راه‌اندازی اولیه تنظیمات همگام‌سازی فروشگاه"""
    
    print("="*60)
    print("راه‌اندازی سیستم همگام‌سازی فروشگاه")
    print("Shop Sync System Initialization")
    print("="*60)
    
    with app.app_context():
        try:
            # تنظیمات پیش‌فرض
            default_settings = [
                {
                    'key': 'auto_sync_enabled',
                    'value': 'True',
                    'description': 'فعال/غیرفعال کردن همگام‌سازی خودکار'
                },
                {
                    'key': 'sync_interval',
                    'value': '3',
                    'description': 'فاصله زمانی همگام‌سازی (ساعت)'
                },
                {
                    'key': 'sync_products',
                    'value': 'True',
                    'description': 'همگام‌سازی محصولات از تدبیر'
                },
                {
                    'key': 'sync_inventory',
                    'value': 'True',
                    'description': 'همگام‌سازی موجودی از تدبیر'
                },
                {
                    'key': 'sync_prices',
                    'value': 'True',
                    'description': 'همگام‌سازی قیمت‌ها از تدبیر'
                },
                {
                    'key': 'sync_shop',
                    'value': 'True',
                    'description': 'همگام‌سازی فروشگاه از cache تدبیر'
                },
                {
                    'key': 'batch_size',
                    'value': '1000',
                    'description': 'تعداد رکوردها در هر batch'
                },
                {
                    'key': 'retry_attempts',
                    'value': '3',
                    'description': 'تعداد تلاش مجدد در صورت خطا'
                },
                {
                    'key': 'retry_delay_seconds',
                    'value': '30',
                    'description': 'تاخیر بین تلاش‌های مجدد (ثانیه)'
                },
                {
                    'key': 'enable_incremental_sync',
                    'value': 'True',
                    'description': 'فعال کردن همگام‌سازی افزایشی'
                }
            ]
            
            print("\nبررسی و ایجاد تنظیمات...\n")
            
            created_count = 0
            updated_count = 0
            
            for setting_info in default_settings:
                # بررسی وجود تنظیمات
                existing = TadbirSyncSettings.query.filter_by(
                    setting_key=setting_info['key']
                ).first()
                
                if existing:
                    # بروزرسانی توضیحات اگر خالی باشد
                    if not existing.description and setting_info['description']:
                        existing.description = setting_info['description']
                        existing.updated_at = datetime.utcnow()
                        updated_count += 1
                        print(f"✓ بروزرسانی: {setting_info['key']} = {existing.setting_value}")
                    else:
                        print(f"○ موجود: {setting_info['key']} = {existing.setting_value}")
                else:
                    # ایجاد تنظیمات جدید
                    new_setting = TadbirSyncSettings(
                        setting_key=setting_info['key'],
                        setting_value=setting_info['value'],
                        description=setting_info['description'],
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(new_setting)
                    created_count += 1
                    print(f"✓ ایجاد: {setting_info['key']} = {setting_info['value']}")
            
            # ذخیره تغییرات
            db.session.commit()
            
            print("\n" + "="*60)
            print("خلاصه عملیات:")
            print(f"  • تنظیمات ایجاد شده: {created_count}")
            print(f"  • تنظیمات بروزرسانی شده: {updated_count}")
            print(f"  • تنظیمات موجود: {len(default_settings) - created_count - updated_count}")
            print("="*60)
            
            # نمایش تنظیمات فعلی
            print("\nتنظیمات فعلی سیستم:\n")
            
            all_settings = TadbirSyncSettings.query.order_by(
                TadbirSyncSettings.setting_key
            ).all()
            
            for setting in all_settings:
                print(f"  {setting.setting_key:30} = {setting.setting_value:10} | {setting.description}")
            
            print("\n✓ راه‌اندازی با موفقیت انجام شد!")
            
            # راهنمای استفاده
            print("\n" + "="*60)
            print("راهنمای استفاده:")
            print("="*60)
            print("""
1. برای شروع همگام‌سازی خودکار:
   - برنامه را اجرا کنید (python app.py)
   - scheduler به صورت خودکار شروع می‌شود

2. برای تست سیستم:
   python test_shop_sync.py

3. برای اجرای دستی همگام‌سازی:
   
   from tadbir_scheduler_service import get_scheduler
   scheduler = get_scheduler()
   
   # همگام‌سازی کامل فروشگاه
   scheduler.run_shop_sync_now('full')
   
   # فقط قیمت‌ها
   scheduler.run_shop_sync_now('prices')

4. برای تغییر تنظیمات:
   
   scheduler.update_settings({
       'sync_interval': 6,  # تغییر به 6 ساعت
       'sync_shop': True
   })

5. برای مشاهده وضعیت:
   
   from shop_sync_service import get_shop_sync_service
   shop_sync = get_shop_sync_service()
   status = shop_sync.get_sync_status()

برای اطلاعات بیشتر، فایل SHOP_SYNC_README.md را مطالعه کنید.
            """)
            
            return True
            
        except Exception as e:
            print(f"\n✗ خطا در راه‌اندازی: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False


def verify_installation():
    """بررسی صحت نصب و راه‌اندازی"""
    
    print("\n" + "="*60)
    print("بررسی صحت نصب")
    print("="*60 + "\n")
    
    with app.app_context():
        try:
            # بررسی جداول مورد نیاز
            print("بررسی جداول پایگاه داده:")
            
            from models import (
                TadbirSyncSettings, TadbirSyncLog, 
                TadbirProductCache, TadbirPriceCache, 
                TadbirInventoryCache, Product
            )
            
            tables = [
                ('TadbirSyncSettings', TadbirSyncSettings),
                ('TadbirSyncLog', TadbirSyncLog),
                ('TadbirProductCache', TadbirProductCache),
                ('TadbirPriceCache', TadbirPriceCache),
                ('TadbirInventoryCache', TadbirInventoryCache),
                ('Product', Product)
            ]
            
            all_ok = True
            
            for table_name, model_class in tables:
                try:
                    count = model_class.query.count()
                    print(f"  ✓ {table_name:25} ({count} رکورد)")
                except Exception as e:
                    print(f"  ✗ {table_name:25} - خطا: {str(e)}")
                    all_ok = False
            
            # بررسی تنظیمات
            print("\nبررسی تنظیمات:")
            
            required_settings = [
                'auto_sync_enabled', 'sync_interval', 'sync_products',
                'sync_inventory', 'sync_prices', 'sync_shop'
            ]
            
            for key in required_settings:
                setting = TadbirSyncSettings.query.filter_by(setting_key=key).first()
                if setting:
                    print(f"  ✓ {key:25} = {setting.setting_value}")
                else:
                    print(f"  ✗ {key:25} - موجود نیست!")
                    all_ok = False
            
            # بررسی سرویس‌ها
            print("\nبررسی سرویس‌ها:")
            
            try:
                from shop_sync_service import get_shop_sync_service
                shop_sync = get_shop_sync_service()
                print("  ✓ ShopSyncService")
            except Exception as e:
                print(f"  ✗ ShopSyncService - خطا: {str(e)}")
                all_ok = False
            
            try:
                from tadbir_sync_service import TadbirSyncService
                tadbir_sync = TadbirSyncService()
                print("  ✓ TadbirSyncService")
            except Exception as e:
                print(f"  ✗ TadbirSyncService - خطا: {str(e)}")
                all_ok = False
            
            try:
                from tadbir_scheduler_service import get_scheduler
                scheduler = get_scheduler()
                print("  ✓ TadbirSchedulerService")
            except Exception as e:
                print(f"  ✗ TadbirSchedulerService - خطا: {str(e)}")
                all_ok = False
            
            # نتیجه نهایی
            print("\n" + "="*60)
            if all_ok:
                print("✓ همه چیز آماده است!")
                print("\nمی‌توانید برنامه را اجرا کنید:")
                print("  python app.py")
            else:
                print("✗ برخی مشکلات وجود دارد.")
                print("\nلطفاً خطاهای بالا را بررسی کنید.")
            print("="*60)
            
            return all_ok
            
        except Exception as e:
            print(f"\n✗ خطا در بررسی: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """تابع اصلی"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + " سیستم همگام‌سازی خودکار فروشگاه ".center(58) + "║")
    print("║" + " Shop Auto-Sync System ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print()
    
    # راه‌اندازی تنظیمات
    success = init_shop_sync_settings()
    
    if success:
        # بررسی صحت نصب
        verify_installation()
    else:
        print("\n✗ راه‌اندازی ناموفق بود.")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

