# سیستم همگام‌سازی خودکار فروشگاه
# Shop Auto-Sync System

## 📋 فهرست مطالب

1. [معرفی](#معرفی)
2. [معماری سیستم](#معماری-سیستم)
3. [نحوه کار](#نحوه-کار)
4. [تنظیمات](#تنظیمات)
5. [استفاده](#استفاده)
6. [تست](#تست)
7. [عیب‌یابی](#عیب‌یابی)

---

## معرفی

این سیستم به صورت خودکار اطلاعات فروشگاه (قیمت‌ها، موجودی‌ها و اطلاعات محصولات) را از cache تدبیر بروزرسانی می‌کند.

### ویژگی‌های کلیدی

- ✅ **همگام‌سازی خودکار هر 3 ساعت**
- ✅ **بروزرسانی قیمت‌ها** (تکی و عمده، نقدی و چکی)
- ✅ **بروزرسانی موجودی‌ها** از انبار تدبیر
- ✅ **بروزرسانی اطلاعات محصولات** (وضعیت فعال/غیرفعال، توضیحات و...)
- ✅ **قابل تنظیم** (می‌توان هر بخش را جداگانه فعال/غیرفعال کرد)
- ✅ **گزارش‌دهی کامل** (ثبت تمام عملیات در پایگاه داده)

---

## معماری سیستم

### جریان داده

```
┌─────────────────┐
│  تدبیر API      │
│  Tadbir API     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tadbir Cache   │  ◄── همگام‌سازی هر 3 ساعت
│  (Database)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Shop Sync      │  ◄── همگام‌سازی فروشگاه
│  Service        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Shop Products  │  ◄── محصولات فروشگاه
│  (Database)     │
└─────────────────┘
```

### مراحل همگام‌سازی

**مرحله 1: همگام‌سازی با تدبیر** (توسط `TadbirSyncService`)
1. دریافت محصولات از Tadbir API → ذخیره در `TadbirProductCache`
2. دریافت موجودی‌ها از Tadbir API → ذخیره در `TadbirInventoryCache`
3. دریافت قیمت‌ها از Tadbir API → ذخیره در `TadbirPriceCache`

**مرحله 2: همگام‌سازی فروشگاه** (توسط `ShopSyncService`)
1. بروزرسانی اطلاعات محصولات از `TadbirProductCache` → `Product`
2. بروزرسانی موجودی‌ها از `TadbirInventoryCache` → `Product.stock_quantity`
3. بروزرسانی قیمت‌ها از `TadbirPriceCache` → `Product.retail_price_*` و `Product.bulk_price_*`

---

## نحوه کار

### 1. همگام‌سازی قیمت‌ها

سیستم قیمت‌های زیر را از cache تدبیر دریافت و به محصولات فروشگاه اعمال می‌کند:

- **لیست قیمت 13 (چکی)**: برای خریدار تکی و عمده
  - `Product.retail_price_check` = قیمت چکی تکی
  - `Product.bulk_price_check` = قیمت چکی عمده
  
- **لیست قیمت 14 (نقدی)**: فقط برای خریدار عمده
  - `Product.bulk_price_cash` = قیمت نقدی عمده

**نکته مهم**: قیمت‌های تدبیر به ریال است و قبل از ذخیره به هزار ریال تبدیل می‌شود.

### 2. همگام‌سازی موجودی

- موجودی از فیلد `available_quantity` در `TadbirInventoryCache` دریافت می‌شود
- مستقیماً به `Product.stock_quantity` اعمال می‌شود
- کد انبار پیش‌فرض: `10`

### 3. همگام‌سازی اطلاعات محصولات

- وضعیت فعال/غیرفعال (`is_active`)
- توضیحات فارسی (`description_fa`) - فقط اگر خالی باشد
- نام فارسی (`name_fa`) - فقط اگر خالی باشد

---

## تنظیمات

### تنظیمات پایگاه داده

تنظیمات در جدول `TadbirSyncSettings` ذخیره می‌شوند:

| کلید | مقدار پیش‌فرض | توضیحات |
|------|--------------|---------|
| `auto_sync_enabled` | `True` | فعال/غیرفعال کردن همگام‌سازی خودکار |
| `sync_interval` | `3` | فاصله زمانی همگام‌سازی (ساعت) |
| `sync_products` | `True` | همگام‌سازی محصولات از تدبیر |
| `sync_inventory` | `True` | همگام‌سازی موجودی از تدبیر |
| `sync_prices` | `True` | همگام‌سازی قیمت‌ها از تدبیر |
| `sync_shop` | `True` | همگام‌سازی فروشگاه از cache |

### تغییر تنظیمات

#### از طریق کد Python:

```python
from tadbir_scheduler_service import get_scheduler

scheduler = get_scheduler()

# تغییر فاصله زمانی به 6 ساعت
scheduler.update_settings({'sync_interval': 6})

# غیرفعال کردن همگام‌سازی خودکار
scheduler.update_settings({'auto_sync_enabled': False})

# فعال کردن فقط همگام‌سازی قیمت‌ها
scheduler.update_settings({
    'sync_products': False,
    'sync_inventory': False,
    'sync_prices': True,
    'sync_shop': True
})
```

#### از طریق پایگاه داده:

```sql
-- تغییر فاصله زمانی به 6 ساعت
UPDATE tadbir_sync_settings 
SET setting_value = '6' 
WHERE setting_key = 'sync_interval';

-- غیرفعال کردن همگام‌سازی فروشگاه
UPDATE tadbir_sync_settings 
SET setting_value = 'False' 
WHERE setting_key = 'sync_shop';
```

---

## استفاده

### راه‌اندازی خودکار

سیستم به صورت خودکار با اجرای برنامه راه‌اندازی می‌شود (`app.py`):

```python
# در app.py
from tadbir_scheduler_service import get_scheduler

scheduler = get_scheduler()
scheduler.start_scheduler()
```

### اجرای دستی

#### 1. همگام‌سازی کامل فروشگاه

```python
from shop_sync_service import get_shop_sync_service

shop_sync = get_shop_sync_service()
sync_logs = shop_sync.full_shop_sync()

# بررسی نتایج
for sync_type, log in sync_logs.items():
    print(f"{sync_type}: {log.status}")
    print(f"  موفق: {log.records_successful}")
    print(f"  ناموفق: {log.records_failed}")
```

#### 2. همگام‌سازی فقط قیمت‌ها

```python
from shop_sync_service import get_shop_sync_service

shop_sync = get_shop_sync_service()
sync_log = shop_sync.sync_shop_prices()

print(f"وضعیت: {sync_log.status}")
print(f"تعداد بروزرسانی شده: {sync_log.records_successful}")
```

#### 3. همگام‌سازی فقط موجودی

```python
from shop_sync_service import get_shop_sync_service

shop_sync = get_shop_sync_service()
sync_log = shop_sync.sync_shop_inventory()

print(f"وضعیت: {sync_log.status}")
print(f"تعداد بروزرسانی شده: {sync_log.records_successful}")
```

#### 4. اجرای فوری از طریق Scheduler

```python
from tadbir_scheduler_service import get_scheduler

scheduler = get_scheduler()

# همگام‌سازی کامل فروشگاه
sync_logs = scheduler.run_shop_sync_now('full')

# فقط قیمت‌ها
price_log = scheduler.run_shop_sync_now('prices')

# فقط موجودی
inventory_log = scheduler.run_shop_sync_now('inventory')

# فقط اطلاعات محصولات
products_log = scheduler.run_shop_sync_now('products')
```

### مشاهده وضعیت

```python
from shop_sync_service import get_shop_sync_service

shop_sync = get_shop_sync_service()
status = shop_sync.get_sync_status()

print("آخرین همگام‌سازی قیمت‌ها:")
print(f"  وضعیت: {status['last_prices_sync']['status']}")
print(f"  زمان: {status['last_prices_sync']['started_at']}")
print(f"  تعداد موفق: {status['last_prices_sync']['records_successful']}")

print("\nآمار فروشگاه:")
print(f"  کل محصولات: {status['shop_stats']['total_products']}")
print(f"  محصولات فعال: {status['shop_stats']['active_products']}")
```

---

## تست

### اجرای اسکریپت تست

```bash
python test_shop_sync.py
```

منوی تست:
1. تست همگام‌سازی قیمت‌ها
2. تست همگام‌سازی موجودی
3. تست همگام‌سازی اطلاعات محصولات
4. تست همگام‌سازی کامل
5. تست Scheduler
6. نمایش وضعیت
7. اجرای همه تست‌ها

### تست‌های دستی

#### تست 1: بررسی Cache تدبیر

```python
from models import TadbirProductCache, TadbirPriceCache, TadbirInventoryCache

# تعداد محصولات در cache
print(f"محصولات: {TadbirProductCache.query.count()}")

# تعداد قیمت‌ها در cache
print(f"قیمت‌ها: {TadbirPriceCache.query.count()}")

# تعداد موجودی‌ها در cache
print(f"موجودی‌ها: {TadbirInventoryCache.query.count()}")
```

#### تست 2: بررسی بروزرسانی یک محصول خاص

```python
from models import Product, TadbirPriceCache, TadbirInventoryCache

# انتخاب یک محصول
product = Product.query.filter_by(sku='YOUR_SKU').first()

print(f"محصول: {product.name_fa}")
print(f"موجودی فعلی: {product.stock_quantity}")
print(f"قیمت چکی تکی: {product.retail_price_check}")
print(f"قیمت نقدی عمده: {product.bulk_price_cash}")

# بررسی cache تدبیر
cache_inventory = TadbirInventoryCache.query.filter_by(
    item_code=product.sku
).first()

cache_prices = TadbirPriceCache.query.filter_by(
    item_code=product.sku
).all()

print(f"\nموجودی در cache: {cache_inventory.available_quantity if cache_inventory else 'نامشخص'}")
print(f"تعداد قیمت‌ها در cache: {len(cache_prices)}")

# اجرای همگام‌سازی
from shop_sync_service import get_shop_sync_service
shop_sync = get_shop_sync_service()
shop_sync.full_shop_sync()

# بررسی مجدد
from sqlalchemy import inspect
inspect(product).session.refresh(product)

print(f"\nبعد از همگام‌سازی:")
print(f"موجودی: {product.stock_quantity}")
print(f"قیمت چکی تکی: {product.retail_price_check}")
print(f"قیمت نقدی عمده: {product.bulk_price_cash}")
```

---

## عیب‌یابی

### مشکل: همگام‌سازی انجام نمی‌شود

**راه‌حل:**

1. بررسی وضعیت scheduler:
```python
from tadbir_scheduler_service import get_scheduler
scheduler = get_scheduler()
status = scheduler.get_scheduler_status()
print(f"در حال اجرا: {status['is_running']}")
print(f"همگام‌سازی فروشگاه فعال: {status['settings']['sync_shop']}")
```

2. بررسی تنظیمات:
```sql
SELECT * FROM tadbir_sync_settings;
```

3. راه‌اندازی مجدد scheduler:
```python
from tadbir_scheduler_service import get_scheduler
scheduler = get_scheduler()
scheduler.stop_scheduler()
scheduler.start_scheduler()
```

### مشکل: قیمت‌ها بروزرسانی نمی‌شوند

**علل احتمالی:**
- Cache قیمت تدبیر خالی است
- محصول در cache تدبیر وجود ندارد
- مشکل در تبدیل واحد (ریال به هزار ریال)

**راه‌حل:**

1. بررسی cache قیمت:
```python
from models import TadbirPriceCache

prices = TadbirPriceCache.query.filter_by(item_code='YOUR_SKU').all()
for price in prices:
    print(f"لیست {price.price_list_key}: {price.final_price}")
```

2. اجرای همگام‌سازی تدبیر اول:
```python
from tadbir_scheduler_service import get_scheduler
scheduler = get_scheduler()
scheduler.run_sync_now('prices')  # همگام‌سازی قیمت‌ها از تدبیر
scheduler.run_shop_sync_now('prices')  # همگام‌سازی فروشگاه
```

### مشکل: موجودی‌ها بروزرسانی نمی‌شوند

**راه‌حل:**

1. بررسی cache موجودی:
```python
from models import TadbirInventoryCache

inventory = TadbirInventoryCache.query.filter_by(
    item_code='YOUR_SKU',
    stock_code='10'
).first()

if inventory:
    print(f"موجودی: {inventory.available_quantity}")
else:
    print("محصول در cache موجودی وجود ندارد")
```

2. همگام‌سازی موجودی از تدبیر:
```python
from tadbir_scheduler_service import get_scheduler
scheduler = get_scheduler()
scheduler.run_sync_now('inventory')  # از تدبیر
scheduler.run_shop_sync_now('inventory')  # به فروشگاه
```

### مشکل: خطا در log ها

**بررسی log ها:**

```python
from models import TadbirSyncLog

# آخرین همگام‌سازی‌های فروشگاه
logs = TadbirSyncLog.query.filter(
    TadbirSyncLog.sync_type.in_(['shop_products', 'shop_inventory', 'shop_prices'])
).order_by(TadbirSyncLog.started_at.desc()).limit(10).all()

for log in logs:
    print(f"\n{log.sync_type}:")
    print(f"  وضعیت: {log.status}")
    print(f"  زمان: {log.started_at}")
    if log.error_message:
        print(f"  خطا: {log.error_message}")
```

### مشکل: scheduler متوقف می‌شود

**راه‌حل:**

1. بررسی thread:
```python
import threading
print(f"Thread های فعال: {threading.active_count()}")
for thread in threading.enumerate():
    print(f"  - {thread.name}")
```

2. راه‌اندازی مجدد:
```python
from tadbir_scheduler_service import get_scheduler
scheduler = get_scheduler()

if scheduler._is_running:
    scheduler.stop_scheduler()
    
scheduler.start_scheduler()
```

---

## سوالات متداول

### چرا هر 3 ساعت؟

این فاصله زمانی تعادل خوبی بین:
- بروز بودن اطلاعات فروشگاه
- کاهش بار بر سرور تدبیر
- کاهش ترافیک شبکه

می‌توانید این مقدار را تغییر دهید (نگاه کنید به بخش [تنظیمات](#تنظیمات)).

### آیا می‌توان فقط قیمت‌ها را همگام‌سازی کرد؟

بله، می‌توانید هر بخش را جداگانه فعال/غیرفعال کنید:

```python
from tadbir_scheduler_service import get_scheduler
scheduler = get_scheduler()

scheduler.update_settings({
    'sync_products': False,  # غیرفعال
    'sync_inventory': False,  # غیرفعال
    'sync_prices': True,  # فعال
    'sync_shop': True  # فعال
})
```

### چه اتفاقی می‌افتد اگر scheduler خطا بگیرد؟

- خطا ثبت می‌شود در `TadbirSyncLog`
- scheduler ادامه می‌دهد و در دفعه بعد دوباره تلاش می‌کند
- می‌توانید log ها را بررسی کنید (نگاه کنید به بخش [عیب‌یابی](#عیب‌یابی))

### آیا می‌توان همگام‌سازی را دستی اجرا کرد؟

بله، نگاه کنید به بخش [استفاده - اجرای دستی](#اجرای-دستی).

---

## پشتیبانی و توسعه

### فایل‌های مرتبط

- `shop_sync_service.py`: سرویس اصلی همگام‌سازی فروشگاه
- `tadbir_scheduler_service.py`: سرویس زمان‌بندی
- `tadbir_sync_service.py`: سرویس همگام‌سازی با تدبیر
- `test_shop_sync.py`: اسکریپت تست

### نسخه

- نسخه فعلی: 1.0.0
- تاریخ: اکتبر 2025

### تماس

برای گزارش مشکلات یا پیشنهادات، لطفاً با تیم توسعه تماس بگیرید.

---

**نکته مهم**: همیشه قبل از تغییر تنظیمات، یک نسخه پشتیبان از پایگاه داده تهیه کنید.

