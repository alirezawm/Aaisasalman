# راهنمای رفع مشکل خطای 500 در جستجو

## مشکل
در سرور لینوکس هنگام جستجو خطای 500 رخ می‌دهد.

## علل احتمالی
1. **مشکل در encoding متن فارسی**
2. **مشکل در توابع SQLAlchemy**
3. **مشکل در اتصال دیتابیس**
4. **مشکل در تنظیمات سرور**

## راه‌های رفع مشکل

### 1. بررسی لاگ‌های خطا
```bash
# بررسی لاگ‌های Flask
tail -f /var/log/your-app/error.log

# یا اگر از systemd استفاده می‌کنید
journalctl -u your-app-service -f
```

### 2. اجرای تست debug
فایل `test_search_debug.py` را در سرور اجرا کنید:
```bash
cd /path/to/your/app
python test_search_debug.py
```

### 3. بررسی تنظیمات دیتابیس
اطمینان حاصل کنید که دیتابیس از UTF-8 پشتیبانی می‌کند:
```sql
-- بررسی encoding دیتابیس
SHOW VARIABLES LIKE 'character_set%';
SHOW VARIABLES LIKE 'collation%';
```

### 4. بررسی تنظیمات Python
```bash
# بررسی encoding سیستم
python -c "import sys; print(sys.getdefaultencoding())"
python -c "import locale; print(locale.getpreferredencoding())"
```

### 5. تست دستی جستجو
```python
# در Python shell
from app import app
from routes import normalize_fa_text, normalize_sql_expr
from models import Product
import models

with app.app_context():
    # تست normalize
    test_text = "تست جستجو"
    normalized = normalize_fa_text(test_text)
    print(f"Normalized: {normalized}")
    
    # تست جستجو
    products = Product.query.filter(
        models.db.or_(
            Product.name.contains(normalized),
            Product.name_fa.contains(normalized)
        )
    ).limit(5).all()
    
    print(f"Found {len(products)} products")
```

## تغییرات اعمال شده

### 1. بهبود Error Handling
- اضافه شدن try-catch در توابع جستجو
- Fallback به جستجوی ساده در صورت خطا
- لاگ کردن خطاها

### 2. بهبود API Search
- اضافه شدن error handling کامل
- بازگشت خطای مناسب به کاربر

### 3. تست Debug
- فایل `test_search_debug.py` برای تست کامل

## دستورات مفید برای سرور

### بررسی وضعیت سرویس
```bash
# اگر از systemd استفاده می‌کنید
systemctl status your-app-service
systemctl restart your-app-service

# اگر از supervisor استفاده می‌کنید
supervisorctl status your-app
supervisorctl restart your-app
```

### بررسی لاگ‌ها
```bash
# لاگ‌های سیستم
journalctl -u your-app-service --since "1 hour ago"

# لاگ‌های nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### بررسی منابع سیستم
```bash
# حافظه و CPU
htop
free -h
df -h

# بررسی process ها
ps aux | grep python
```

## نکات مهم

1. **Encoding**: مطمئن شوید که تمام فایل‌ها با UTF-8 ذخیره شده‌اند
2. **Locale**: تنظیمات locale سرور باید از UTF-8 پشتیبانی کند
3. **Database**: دیتابیس باید با UTF-8 تنظیم شده باشد
4. **Python**: نسخه Python باید از Unicode پشتیبانی کند

## تماس با پشتیبانی
اگر مشکل حل نشد، لاگ‌های خطا و خروجی `test_search_debug.py` را ارسال کنید.
