"""
Initialize Tadbir Accounting System Configuration
اسکریپت راه‌اندازی تنظیمات سیستم حسابداری تدبیر
"""

from models import db, TadbirSyncSettings
from app import app
from datetime import datetime

def init_tadbir_settings():
    """Initialize default Tadbir settings"""
    
    default_settings = [
        {
            'setting_key': 'api_url',
            'setting_value': 'http://5.202.90.240:8085',
            'description': 'آدرس پایه API تدبیر'
        },
        {
            'setting_key': 'api_username',
            'setting_value': 'Asia@tadbir.biz',
            'description': 'نام کاربری API تدبیر'
        },
        {
            'setting_key': 'api_password',
            'setting_value': 'Asia@tadbir.biz',
            'description': 'رمز عبور API تدبیر'
        },
        {
            'setting_key': 'api_timeout',
            'setting_value': '300',
            'description': 'زمان انتظار API به ثانیه'
        },
        {
            'setting_key': 'retry_attempts',
            'setting_value': '3',
            'description': 'تعداد تلاش مجدد'
        },
        {
            'setting_key': 'auto_sync_enabled',
            'setting_value': 'true',
            'description': 'فعال‌سازی همگام‌سازی خودکار'
        },
        {
            'setting_key': 'sync_interval',
            'setting_value': '3',
            'description': 'فاصله زمانی همگام‌سازی به ساعت'
        },
        {
            'setting_key': 'batch_size',
            'setting_value': '1000',
            'description': 'اندازه دسته برای همگام‌سازی'
        },
        {
            'setting_key': 'enable_incremental_sync',
            'setting_value': 'true',
            'description': 'فعال‌سازی همگام‌سازی افزایشی'
        },
        {
            'setting_key': 'sync_products',
            'setting_value': 'true',
            'description': 'همگام‌سازی کالاها'
        },
        {
            'setting_key': 'sync_inventory',
            'setting_value': 'true',
            'description': 'همگام‌سازی موجودی'
        },
        {
            'setting_key': 'sync_prices',
            'setting_value': 'true',
            'description': 'همگام‌سازی قیمت‌ها'
        },
        {
            'setting_key': 'default_markup_percentage',
            'setting_value': '10',
            'description': 'درصد اضافی پیش‌فرض'
        },
        {
            'setting_key': 'price_rounding',
            'setting_value': 'round',
            'description': 'نوع گرد کردن قیمت'
        },
        {
            'setting_key': 'currency_format',
            'setting_value': 'هزار تومان',
            'description': 'فرمت نمایش ارز'
        },
        {
            'setting_key': 'sync_notifications',
            'setting_value': 'true',
            'description': 'اعلان همگام‌سازی'
        },
        {
            'setting_key': 'error_notifications',
            'setting_value': 'true',
            'description': 'اعلان خطاها'
        },
        {
            'setting_key': 'price_change_notifications',
            'setting_value': 'false',
            'description': 'اعلان تغییرات قیمت'
        },
        {
            'setting_key': 'inventory_alerts',
            'setting_value': 'true',
            'description': 'هشدارهای موجودی'
        }
    ]
    
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            
            # Initialize settings
            for setting_data in default_settings:
                existing_setting = TadbirSyncSettings.query.filter_by(
                    setting_key=setting_data['setting_key']
                ).first()
                
                if not existing_setting:
                    setting = TadbirSyncSettings(
                        setting_key=setting_data['setting_key'],
                        setting_value=setting_data['setting_value'],
                        description=setting_data['description'],
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(setting)
                    print(f"Added setting: {setting_data['setting_key']}")
                else:
                    print(f"Setting already exists: {setting_data['setting_key']}")
            
            db.session.commit()
            print("Tadbir settings initialized successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing Tadbir settings: {str(e)}")
            raise

if __name__ == '__main__':
    init_tadbir_settings()
