# راهنمای سریع شروع کار - همگام‌سازی خودکار فروشگاه
# Quick Start Guide - Shop Auto-Sync

## ⚡ شروع سریع (Quick Start)

### گام 1️⃣: راه‌اندازی اولیه

```bash
python init_shop_sync.py
```

این دستور:
- ✅ تنظیمات پیش‌فرض را ایجاد می‌کند
- ✅ صحت نصب را بررسی می‌کند
- ✅ راهنما را نمایش می‌دهد

### گام 2️⃣: اجرای برنامه

```bash
python app.py
```

🎉 **تمام!** سیستم اکنون هر 3 ساعت به صورت خودکار:
1. داده‌های تدبیر را دریافت می‌کند
2. قیمت‌ها و موجودی‌های فروشگاه را بروزرسانی می‌کند

---

## 🧪 تست سیستم (اختیاری)

```bash
python test_shop_sync.py
```

منوی تعاملی برای تست اجزای مختلف سیستم.

---

## 📊 مشاهده وضعیت

### از طریق Python:

```python
from shop_sync_service import get_shop_sync_service

with app.app_context():
    shop_sync = get_shop_sync_service()
    status = shop_sync.get_sync_status()
    
    print(status)
```

### از طریق اسکریپت تست:

```bash
python test_shop_sync.py
# انتخاب گزینه 6: نمایش وضعیت
```

---

## 🔧 دستورات مفید

### اجرای فوری همگام‌سازی (بدون انتظار 3 ساعت)

```python
from app import app
from tadbir_scheduler_service import get_scheduler

with app.app_context():
    scheduler = get_scheduler()
    
    # همگام‌سازی کامل فروشگاه
    scheduler.run_shop_sync_now('full')
```

یا از طریق اسکریپت تست:
```bash
python test_shop_sync.py
# انتخاب گزینه 4: تست همگام‌سازی کامل
```

### تغییر فاصله زمانی

```python
from app import app
from tadbir_scheduler_service import get_scheduler

with app.app_context():
    scheduler = get_scheduler()
    
    # تغییر به 6 ساعت
    scheduler.update_settings({'sync_interval': 6})
```

یا از طریق SQL:
```sql
UPDATE tadbir_sync_settings 
SET setting_value = '6' 
WHERE setting_key = 'sync_interval';
```

### غیرفعال کردن موقت

```python
from app import app
from tadbir_scheduler_service import get_scheduler

with app.app_context():
    scheduler = get_scheduler()
    
    # غیرفعال کردن
    scheduler.update_settings({'auto_sync_enabled': False})
    
    # فعال کردن مجدد
    scheduler.update_settings({'auto_sync_enabled': True})
```

---

## 📈 نظارت

### بررسی Log های آخرین همگام‌سازی

```python
from app import app
from models import TadbirSyncLog

with app.app_context():
    logs = TadbirSyncLog.query.filter(
        TadbirSyncLog.sync_type.in_([
            'shop_products', 
            'shop_inventory', 
            'shop_prices'
        ])
    ).order_by(TadbirSyncLog.started_at.desc()).limit(5).all()
    
    for log in logs:
        print(f"\n{log.sync_type}:")
        print(f"  وضعیت: {log.status}")
        print(f"  زمان: {log.started_at}")
        print(f"  موفق: {log.records_successful}")
        print(f"  ناموفق: {log.records_failed}")
```

### بررسی Scheduler

```python
from app import app
from tadbir_scheduler_service import get_scheduler

with app.app_context():
    scheduler = get_scheduler()
    status = scheduler.get_scheduler_status()
    
    print(f"در حال اجرا: {status['is_running']}")
    print(f"اجرای بعدی: {status['next_run']}")
    print(f"فاصله زمانی: {status['settings']['sync_interval']} ساعت")
    print(f"همگام‌سازی فروشگاه: {status['settings']['sync_shop']}")
```

---

## 🔍 بررسی یک محصول خاص

```python
from app import app
from models import Product, TadbirPriceCache, TadbirInventoryCache

with app.app_context():
    # کد محصول (SKU)
    sku = 'YOUR_PRODUCT_SKU'
    
    # محصول در فروشگاه
    product = Product.query.filter_by(sku=sku).first()
    if product:
        print(f"محصول: {product.name_fa}")
        print(f"موجودی: {product.stock_quantity}")
        print(f"قیمت تکی چکی: {product.retail_price_check}")
        print(f"قیمت عمده نقدی: {product.bulk_price_cash}")
        print(f"قیمت عمده چکی: {product.bulk_price_check}")
    
    # داده‌های cache تدبیر
    cache_inventory = TadbirInventoryCache.query.filter_by(
        item_code=sku
    ).first()
    
    cache_prices = TadbirPriceCache.query.filter_by(
        item_code=sku
    ).all()
    
    print(f"\nموجودی در cache: {cache_inventory.available_quantity if cache_inventory else 'نامشخص'}")
    print(f"قیمت‌ها در cache: {len(cache_prices)}")
    
    for price in cache_prices:
        print(f"  لیست {price.price_list_key}: {price.final_price}")
```

---

## ⚠️ حل مشکلات رایج

### مشکل 1: همگام‌سازی اجرا نمی‌شود

```python
from app import app
from tadbir_scheduler_service import get_scheduler

with app.app_context():
    scheduler = get_scheduler()
    
    # بررسی وضعیت
    status = scheduler.get_scheduler_status()
    print(f"در حال اجرا: {status['is_running']}")
    
    # اگر متوقف شده، راه‌اندازی مجدد
    if not status['is_running']:
        scheduler.start_scheduler()
        print("Scheduler راه‌اندازی شد")
```

### مشکل 2: Cache تدبیر خالی است

```python
from app import app
from tadbir_scheduler_service import get_scheduler

with app.app_context():
    scheduler = get_scheduler()
    
    # اجرای فوری همگام‌سازی از تدبیر
    print("همگام‌سازی محصولات از تدبیر...")
    scheduler.run_sync_now('products')
    
    print("همگام‌سازی موجودی از تدبیر...")
    scheduler.run_sync_now('inventory')
    
    print("همگام‌سازی قیمت‌ها از تدبیر...")
    scheduler.run_sync_now('prices')
    
    print("انتقال به فروشگاه...")
    scheduler.run_shop_sync_now('full')
    
    print("✓ تمام!")
```

### مشکل 3: قیمت‌ها صفر هستند

این معمولاً به این دلیل است که cache قیمت تدبیر خالی است.

```python
from app import app
from models import TadbirPriceCache

with app.app_context():
    # بررسی تعداد قیمت‌ها
    count = TadbirPriceCache.query.count()
    print(f"تعداد قیمت‌ها در cache: {count}")
    
    if count == 0:
        print("Cache خالی است! اجرای همگام‌سازی از تدبیر...")
        from tadbir_scheduler_service import get_scheduler
        scheduler = get_scheduler()
        scheduler.run_sync_now('prices')
```

---

## 📚 مستندات کامل

برای اطلاعات بیشتر:

- **[SHOP_SYNC_README.md](SHOP_SYNC_README.md)**: راهنمای جامع (فارسی)
- **[SHOP_SYNC_IMPLEMENTATION.md](SHOP_SYNC_IMPLEMENTATION.md)**: جزئیات فنی پیاده‌سازی
- **[test_shop_sync.py](test_shop_sync.py)**: نمونه‌های کد و تست

---

## 💡 نکات مهم

1. ⏰ **فاصله زمانی پیش‌فرض**: 3 ساعت
2. 🔄 **ترتیب همگام‌سازی**: تدبیر → Cache → فروشگاه
3. 💾 **پشتیبان‌گیری**: قبل از تغییرات از پایگاه داده backup بگیرید
4. 📊 **نظارت**: به طور منظم log ها را بررسی کنید
5. 🧪 **تست**: قبل از استفاده در محیط تولید، تست کنید

---

## 🎯 چک‌لیست راه‌اندازی

- [ ] اجرای `init_shop_sync.py`
- [ ] بررسی تنظیمات در پایگاه داده
- [ ] اجرای `test_shop_sync.py` برای تست
- [ ] اجرای `app.py` برای شروع
- [ ] بررسی log های اولین همگام‌سازی
- [ ] بررسی یک محصول نمونه
- [ ] تنظیم فاصله زمانی (اختیاری)

---

**✅ آماده برای استفاده!**

برای سوالات بیشتر، به مستندات کامل مراجعه کنید یا با تیم توسعه تماس بگیرید.

