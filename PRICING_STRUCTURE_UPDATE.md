# به‌روزرسانی ساختار قیمت‌گذاری سیستم تدبیر

## تاریخ: 11 اکتبر 2025

## توضیح مشکل قبلی

قبل از این به‌روزرسانی، سیستم به اشتباه فرض می‌کرد که خریدار تکی هم قیمت نقدی دارد.

## ساختار صحیح قیمت‌گذاری از تدبیر

### لیست‌های قیمت در تدبیر:
- **لیست 13**: قیمت چکی (برای تکی و عمده)
- **لیست 14**: قیمت نقدی (retail_cash - فقط برای خریدار عمده)

### انواع خریدار:

#### 1. خریدار تکی (Retail Buyer)
- ✅ **فقط قیمت چکی** (`retail_check` - لیست 13)
- ❌ قیمت نقدی ندارد

#### 2. خریدار عمده (Bulk Buyer - تایید شده)
- ✅ قیمت **نقدی عمده** (`bulk_cash` - لیست 14)
- ✅ قیمت **چکی عمده** (`bulk_check` - لیست 13)

#### 3. خریدار عمده در انتظار تایید
- ✅ **فقط قیمت چکی تکی** (`retail_check` - لیست 13)

## تغییرات انجام شده

### 1. فایل: `tadbir_api_service.py`
```python
# قبل:
self.price_categories = {
    'retail_cash': {'price_list_key': 14, ...},  # ❌ اشتباه بود
    'retail_check': {'price_list_key': 13, ...},
    'bulk_cash': {'price_list_key': 14, ...},
    'bulk_check': {'price_list_key': 13, ...}
}

# بعد:
self.price_categories = {
    'retail_check': {'price_list_key': 13, ...},  # ✅ فقط چکی برای تکی
    'bulk_cash': {'price_list_key': 14, ...},
    'bulk_check': {'price_list_key': 13, ...}
}
```

### 2. فایل: `tadbir_sync_service.py`

#### تابع `_get_price_type`:
```python
# قبل:
if price_list_key == 14:
    return 'retail_cash'  # ❌ اشتباه

# بعد:
if price_list_key == 14:
    return 'bulk_cash'  # ✅ صحیح - فقط برای عمده
```

#### تابع `sync_prices_to_products`:
```python
# قبل:
product.retail_price_cash = base_price_cash * markup_cash  # ❌ اشتباه

# بعد:
product.retail_price_check = base_price_check * markup_check  # ✅ چکی خرده
product.retail_price_cash = base_price_check * markup_check  # برای سازگاری با کد قدیمی
product.bulk_price_cash = base_price_cash * (markup_cash - 0.02)  # نقدی عمده
product.bulk_price_check = base_price_check * (markup_check - 0.02)  # چکی عمده
```

### 3. تمپلیت‌ها

#### فایل‌های اصلاح شده:
- `templates/shop.html`
- `templates/category_products.html`
- `templates/brand_products.html`
- `templates/product_detail.html`

#### تغییرات:
- ❌ حذف دکمه "نقدی" برای خریدار تکی
- ✅ نمایش فقط دکمه "قیمت چکی" برای خریدار تکی
- ✅ نمایش هر دو دکمه "نقدی عمده" و "چکی عمده" برای خریدار عمده تایید شده
- ✅ اصلاح محاسبه صرفه‌جویی بر اساس قیمت چکی

## نتیجه

### خریدار تکی می‌بیند:
```
┌──────────────────────┐
│   قیمت چکی           │
│   1,999,250 ریال     │
└──────────────────────┘
```

### خریدار عمده می‌بیند:
```
┌──────────────┬──────────────┐
│  نقدی عمده   │  چکی عمده    │
│ 1,869,307    │ 2,099,175    │
│    ریال      │    ریال      │
└──────────────┴──────────────┘
صرفه‌جویی چکی: 100,075 ریال
```

## توجه مهم برای توسعه‌دهندگان

1. فیلد `retail_price_cash` در مدل `Product` همچنان وجود دارد برای سازگاری با کد قدیمی
2. این فیلد اکنون همان مقدار `retail_price_check` را دارد
3. در UI، این فیلد دیگر به خریدار تکی نمایش داده نمی‌شود
4. تنها خریدار عمده می‌تواند قیمت نقدی (`bulk_cash`) ببیند

## بررسی نهایی

✅ سرویس تدبیر اصلاح شد
✅ سرویس همگام‌سازی اصلاح شد
✅ تمام تمپلیت‌ها اصلاح شدند
✅ محاسبات صرفه‌جویی اصلاح شد
✅ سند به‌روزرسانی ایجاد شد

## دستور اجرای مجدد همگام‌سازی

پس از این تغییرات، برای به‌روزرسانی قیمت‌ها:

```python
from tadbir_sync_service import TadbirSyncService

sync_service = TadbirSyncService()

# همگام‌سازی قیمت‌ها
sync_service.sync_prices()

# اعمال قیمت‌ها به محصولات
sync_service.sync_prices_to_products()
```

یا از پنل ادمین:
**حسابداری تدبیر → همگام‌سازی دستی → همگام‌سازی قیمت‌ها**

