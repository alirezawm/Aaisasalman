# پیاده‌سازی سیستم همگام‌سازی خودکار فروشگاه
# Shop Auto-Sync Implementation Summary

## 📅 تاریخ پیاده‌سازی
اکتبر 2025

---

## 🎯 هدف

ایجاد یک سیستم خودکار برای همگام‌سازی اطلاعات فروشگاه (قیمت‌ها، موجودی‌ها و اطلاعات محصولات) با cache تدبیر هر 3 ساعت.

---

## 📦 فایل‌های ایجاد شده

### 1. `shop_sync_service.py`
سرویس اصلی همگام‌سازی فروشگاه

**ویژگی‌ها:**
- `sync_shop_prices()`: همگام‌سازی قیمت‌های فروشگاه از cache تدبیر
- `sync_shop_inventory()`: همگام‌سازی موجودی‌های فروشگاه از cache تدبیر
- `sync_shop_products()`: همگام‌سازی اطلاعات محصولات (is_active, description_fa, name_fa)
- `full_shop_sync()`: همگام‌سازی کامل (قیمت + موجودی + اطلاعات)
- `get_sync_status()`: دریافت وضعیت آخرین همگام‌سازی‌ها

**جریان داده:**
```
TadbirProductCache → Product (is_active, description_fa, name_fa)
TadbirInventoryCache → Product.stock_quantity
TadbirPriceCache → Product.retail_price_* و Product.bulk_price_*
```

### 2. `test_shop_sync.py`
اسکریپت تست کامل سیستم

**قابلیت‌ها:**
- تست همگام‌سازی قیمت‌ها
- تست همگام‌سازی موجودی‌ها
- تست همگام‌سازی اطلاعات محصولات
- تست همگام‌سازی کامل
- تست scheduler
- نمایش وضعیت
- اجرای تمام تست‌ها به صورت یکجا

### 3. `SHOP_SYNC_README.md`
مستندات کامل سیستم (فارسی)

**محتویات:**
- معرفی و ویژگی‌ها
- معماری سیستم
- نحوه کار
- تنظیمات
- راهنمای استفاده
- راهنمای تست
- عیب‌یابی
- سوالات متداول

### 4. `init_shop_sync.py`
اسکریپت راه‌اندازی اولیه

**عملکرد:**
- ایجاد تنظیمات پیش‌فرض در پایگاه داده
- بررسی صحت نصب
- تست سرویس‌ها
- نمایش راهنمای استفاده

---

## 🔧 فایل‌های تغییر یافته

### `tadbir_scheduler_service.py`

**تغییرات:**

1. **Import جدید:**
```python
from shop_sync_service import get_shop_sync_service
```

2. **تنظیمات جدید در `__init__`:**
```python
self.shop_sync_service = get_shop_sync_service()

self.default_settings = {
    # ... تنظیمات قبلی
    'sync_shop': True  # جدید
}
```

3. **بروزرسانی `_sync_job`:**
افزودن بخش همگام‌سازی فروشگاه بعد از همگام‌سازی تدبیر:
```python
# ========== بخش دوم: همگام‌سازی فروشگاه با cache تدبیر ==========
if sync_shop:
    shop_products_log = self.shop_sync_service.sync_shop_products()
    shop_inventory_log = self.shop_sync_service.sync_shop_inventory()
    shop_prices_log = self.shop_sync_service.sync_shop_prices()
```

4. **متد جدید `run_shop_sync_now`:**
برای اجرای فوری همگام‌سازی فروشگاه

5. **بروزرسانی `get_scheduler_status`:**
افزودن تنظیم `sync_shop` به خروجی status

---

## 🗄️ تغییرات پایگاه داده

### تنظیمات جدید در `TadbirSyncSettings`

| کلید | مقدار پیش‌فرض | توضیحات |
|------|--------------|---------|
| `sync_shop` | `True` | فعال/غیرفعال همگام‌سازی فروشگاه |

### نوع‌های جدید در `TadbirSyncLog.sync_type`

- `shop_products`: همگام‌سازی اطلاعات محصولات فروشگاه
- `shop_inventory`: همگام‌سازی موجودی‌های فروشگاه
- `shop_prices`: همگام‌سازی قیمت‌های فروشگاه

---

## 🔄 جریان کار سیستم

### مرحله 1: همگام‌سازی با تدبیر (هر 3 ساعت)

```
[Scheduler] --3h--> [TadbirSyncService]
                           |
                           ├─> sync_products() --> TadbirProductCache
                           ├─> sync_inventory() --> TadbirInventoryCache
                           └─> sync_prices() --> TadbirPriceCache
```

### مرحله 2: همگام‌سازی فروشگاه (بلافاصله بعد از مرحله 1)

```
[Scheduler] --> [ShopSyncService]
                      |
                      ├─> sync_shop_products() --> Product (info)
                      ├─> sync_shop_inventory() --> Product.stock_quantity
                      └─> sync_shop_prices() --> Product.prices
```

### نتیجه نهایی

```
TadbirProductCache ──┐
TadbirInventoryCache ├──> ShopSyncService ──> Product (در فروشگاه)
TadbirPriceCache ────┘
```

---

## 📊 نگاشت داده‌ها

### قیمت‌ها

| Cache تدبیر | فروشگاه |
|-------------|---------|
| لیست 13 (چکی) | `retail_price_check` (تکی) |
| لیست 13 (چکی) | `retail_price_cash` (تکی - برای سازگاری) |
| لیست 13 (چکی) | `bulk_price_check` (عمده) |
| لیست 14 (نقدی) | `bulk_price_cash` (عمده) |

**نکته**: قیمت‌ها در تدبیر به ریال است و به هزار ریال تبدیل می‌شود.

### موجودی

| Cache تدبیر | فروشگاه |
|-------------|---------|
| `TadbirInventoryCache.available_quantity` | `Product.stock_quantity` |

### اطلاعات محصولات

| Cache تدبیر | فروشگاه |
|-------------|---------|
| `TadbirProductCache.is_active` | `Product.is_active` |
| `TadbirProductCache.description` | `Product.description_fa` (اگر خالی باشد) |
| `TadbirProductCache.description` | `Product.name_fa` (اگر خالی باشد - 200 کاراکتر اول) |

---

## 🚀 راه‌اندازی

### گام 1: اجرای اسکریپت راه‌اندازی

```bash
python init_shop_sync.py
```

این اسکریپت:
- تنظیمات پیش‌فرض را در پایگاه داده ایجاد می‌کند
- صحت نصب را بررسی می‌کند
- راهنمای استفاده را نمایش می‌دهد

### گام 2: اجرای برنامه

```bash
python app.py
```

Scheduler به صورت خودکار شروع می‌شود و هر 3 ساعت:
1. داده‌های تدبیر را به cache منتقل می‌کند
2. داده‌های cache را به فروشگاه منتقل می‌کند

### گام 3: تست سیستم (اختیاری)

```bash
python test_shop_sync.py
```

---

## 📝 استفاده

### اجرای فوری همگام‌سازی فروشگاه

```python
from tadbir_scheduler_service import get_scheduler

scheduler = get_scheduler()

# همگام‌سازی کامل
scheduler.run_shop_sync_now('full')

# فقط قیمت‌ها
scheduler.run_shop_sync_now('prices')

# فقط موجودی
scheduler.run_shop_sync_now('inventory')

# فقط اطلاعات محصولات
scheduler.run_shop_sync_now('products')
```

### مشاهده وضعیت

```python
from shop_sync_service import get_shop_sync_service

shop_sync = get_shop_sync_service()
status = shop_sync.get_sync_status()

print(f"آخرین همگام‌سازی قیمت‌ها: {status['last_prices_sync']}")
print(f"آخرین همگام‌سازی موجودی: {status['last_inventory_sync']}")
print(f"تعداد محصولات فعال: {status['shop_stats']['active_products']}")
```

### تغییر تنظیمات

```python
from tadbir_scheduler_service import get_scheduler

scheduler = get_scheduler()

# تغییر فاصله زمانی به 6 ساعت
scheduler.update_settings({'sync_interval': 6})

# غیرفعال کردن همگام‌سازی فروشگاه
scheduler.update_settings({'sync_shop': False})
```

---

## ✅ مزایا

1. **خودکار**: نیازی به مداخله دستی نیست
2. **قابل اعتماد**: گزارش‌دهی کامل و مدیریت خطا
3. **قابل تنظیم**: هر بخش را می‌توان جداگانه کنترل کرد
4. **کارآمد**: استفاده از cache برای کاهش بار شبکه
5. **شفاف**: log های کامل برای رصد عملیات
6. **قابل تست**: اسکریپت تست جامع
7. **مستند**: مستندات کامل فارسی

---

## 🔍 نظارت و گزارش‌دهی

### 1. بررسی Log های همگام‌سازی

```python
from models import TadbirSyncLog

# آخرین همگام‌سازی‌های فروشگاه
logs = TadbirSyncLog.query.filter(
    TadbirSyncLog.sync_type.in_([
        'shop_products', 
        'shop_inventory', 
        'shop_prices'
    ])
).order_by(TadbirSyncLog.started_at.desc()).limit(10).all()

for log in logs:
    print(f"{log.sync_type}: {log.status}")
    print(f"  موفق: {log.records_successful}")
    print(f"  ناموفق: {log.records_failed}")
    if log.error_message:
        print(f"  خطا: {log.error_message}")
```

### 2. بررسی وضعیت Scheduler

```python
from tadbir_scheduler_service import get_scheduler

scheduler = get_scheduler()
status = scheduler.get_scheduler_status()

print(f"در حال اجرا: {status['is_running']}")
print(f"اجرای بعدی: {status['next_run']}")
print(f"همگام‌سازی فروشگاه فعال: {status['settings']['sync_shop']}")
```

### 3. بررسی آمار فروشگاه

```python
from shop_sync_service import get_shop_sync_service

shop_sync = get_shop_sync_service()
status = shop_sync.get_sync_status()

print(f"تعداد کل محصولات: {status['shop_stats']['total_products']}")
print(f"تعداد محصولات فعال: {status['shop_stats']['active_products']}")
```

---

## 🐛 عیب‌یابی رایج

### مشکل: همگام‌سازی اجرا نمی‌شود

**راه‌حل:**
```python
from tadbir_scheduler_service import get_scheduler

scheduler = get_scheduler()

# بررسی وضعیت
print(scheduler.get_scheduler_status())

# راه‌اندازی مجدد
if not scheduler._is_running:
    scheduler.start_scheduler()
```

### مشکل: قیمت‌ها بروزرسانی نمی‌شوند

**راه‌حل:**
```python
# 1. بررسی cache قیمت تدبیر
from models import TadbirPriceCache
prices = TadbirPriceCache.query.count()
print(f"تعداد قیمت‌ها در cache: {prices}")

# 2. اجرای همگام‌سازی تدبیر
from tadbir_scheduler_service import get_scheduler
scheduler = get_scheduler()
scheduler.run_sync_now('prices')

# 3. اجرای همگام‌سازی فروشگاه
scheduler.run_shop_sync_now('prices')
```

### مشکل: موجودی‌ها بروزرسانی نمی‌شوند

**راه‌حل:**
```python
# 1. بررسی cache موجودی تدبیر
from models import TadbirInventoryCache
inventory = TadbirInventoryCache.query.count()
print(f"تعداد موجودی‌ها در cache: {inventory}")

# 2. اجرای همگام‌سازی
from tadbir_scheduler_service import get_scheduler
scheduler = get_scheduler()
scheduler.run_sync_now('inventory')
scheduler.run_shop_sync_now('inventory')
```

---

## 📚 مستندات بیشتر

برای اطلاعات تکمیلی، به فایل‌های زیر مراجعه کنید:

- **`SHOP_SYNC_README.md`**: راهنمای جامع کاربری (فارسی)
- **`test_shop_sync.py`**: نمونه‌های استفاده و تست
- **`init_shop_sync.py`**: راه‌اندازی و تنظیمات اولیه

---

## ⚠️ نکات مهم

1. **قبل از تغییرات**: همیشه نسخه پشتیبان از پایگاه داده تهیه کنید
2. **تست**: قبل از استفاده در محیط تولید، سیستم را تست کنید
3. **نظارت**: به طور منظم log ها را بررسی کنید
4. **تنظیمات**: فاصله زمانی را بر اساس نیاز خود تنظیم کنید

---

## 📞 پشتیبانی

برای گزارش مشکلات یا سوالات:
- فایل log ها را بررسی کنید
- اسکریپت تست را اجرا کنید
- با تیم توسعه تماس بگیرید

---

**تاریخ آخرین بروزرسانی**: اکتبر 2025  
**نسخه**: 1.0.0

