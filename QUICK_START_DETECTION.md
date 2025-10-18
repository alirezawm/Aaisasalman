# 🚀 راهنمای سریع شروع کار
# Quick Start Guide - Vehicle Detection System

<div dir="rtl">

## شروع سریع با یک کلیک ⚡

### گام 1: اجرای اسکریپت نصب

```bash
python run_complete_detection.py --full-rebuild --auto-detect-all --generate-reports --backup-first --verbose
```

این دستور به صورت خودکار:

- ✅ تمام پیش‌نیازها را بررسی می‌کند
- ✅ نسخه پشتیبان می‌گیرد
- ✅ وابستگی‌های لازم را نصب می‌کند
- ✅ دیتابیس را راه‌اندازی می‌کند
- ✅ داده‌های اولیه را وارد می‌کند
- ✅ تمام محصولات را تشخیص می‌دهد
- ✅ گزارش کامل ایجاد می‌کند

### گام 2: بررسی نتایج

پس از اتمام، فایل گزارش در این مسیر ایجاد می‌شود:

```
detection_rebuild_report_20251010_HHMMSS.json
```

---

## استفاده از API 📡

### مثال 1: تشخیص تکی

```python
import requests

response = requests.post(
    'http://localhost:8081/api/detection/detect',
    json={'text': 'لنت ترمز جلو تویوتا کمری سدان'}
)

result = response.json()
print(result)
```

خروجی:

```json
{
  "status": "success",
  "data": {
    "detected_brand": {
      "id": 1,
      "name": "Toyota",
      "name_fa": "تویوتا"
    },
    "detected_vehicle_types": [
      {
        "id": 1,
        "name": "sedan"
      }
    ],
    "processing_time": 8
  }
}
```

### مثال 2: تشخیص دسته‌ای

```python
from brand_vehicle_detector import get_detector

detector = get_detector()
result = detector.batch_detect_products()

print(f"✓ پردازش شده: {result['data']['total_processed']}")
print(f"✓ به‌روزرسانی: {result['data']['updated_count']}")
```

---

## مثال‌های کاربردی 💡

### مثال 1: تشخیص و ذخیره

```python
from app import app
from brand_vehicle_detector import get_detector
from models import db, Product

detector = get_detector()

with app.app_context():
    # دریافت محصولات بدون برند
    products = Product.query.filter_by(brand_id=None).all()
    
    for product in products:
        result = detector.detect_brand_and_vehicle_types(product.name)
        
        if result['status'] == 'success':
            data = result['data']
            
            # ذخیره برند
            if data['detected_brand']:
                product.brand_id = data['detected_brand']['id']
                print(f"✓ {product.name} -> {data['detected_brand']['name']}")
    
    db.session.commit()
    print(f"\n✅ تکمیل شد! {len(products)} محصول پردازش شد.")
```

### مثال 2: تشخیص با فیلتر اطمینان

```python
def detect_with_confidence(text, min_confidence=0.8):
    detector = get_detector()
    result = detector.detect_brand_and_vehicle_types(text)
    
    if result['status'] == 'success':
        data = result['data']
        
        # فیلتر بر اساس اطمینان
        if data['detected_brand']:
            confidence = data['detected_brand'].get('confidence', 'high')
            if confidence != 'high':
                return None
        
        return data
    
    return None

# استفاده
result = detect_with_confidence("روغن موتور هیوندا")
if result:
    print(f"برند: {result['detected_brand']['name']}")
else:
    print("تشخیص با اطمینان بالا ممکن نیست")
```

### مثال 3: گزارش عملکرد

```python
from brand_vehicle_detector import get_detector

detector = get_detector()
stats = detector.get_detection_stats()

print("=" * 50)
print("📊 آمار تشخیص")
print("=" * 50)
print(f"کل محصولات: {stats['total_products']}")
print(f"با برند: {stats['products_with_brand']}")
print(f"با نوع: {stats['products_with_vehicle_types']}")
print(f"پوشش برند: {stats['brand_coverage']}%")
print(f"پوشش نوع: {stats['vehicle_type_coverage']}%")
print("=" * 50)
```

---

## تست سریع ✅

### تست 1: بررسی نصب

```bash
python -c "from brand_vehicle_detector import get_detector; d = get_detector(); print('✅ سیستم آماده است!')"
```

### تست 2: تست تشخیص

```python
from brand_vehicle_detector import get_detector

detector = get_detector()

test_cases = [
    "لنت ترمز تویوتا کمری",
    "فیلتر هوای هیوندای سوناتا",
    "روغن موتور بنز E کلاس",
    "شمع BMW سری 3",
    "باتری پژو 206 سدان"
]

print("🧪 تست تشخیص\n")

for text in test_cases:
    result = detector.detect_brand_and_vehicle_types(text)
    if result['status'] == 'success':
        data = result['data']
        brand = data['detected_brand']['name'] if data['detected_brand'] else 'نامشخص'
        print(f"✓ {text[:30]:30} -> برند: {brand}")
    else:
        print(f"✗ {text[:30]:30} -> خطا")

print("\n✅ تست تکمیل شد!")
```

---

## نکات مهم ⚠️

### 1. پشتیبان‌گیری

همیشه قبل از تغییرات بزرگ، نسخه پشتیبان بگیرید:

```bash
cp instance/asia_salman.db instance/asia_salman.db.backup_$(date +%Y%m%d_%H%M%S)
```

### 2. بهینه‌سازی عملکرد

برای عملکرد بهتر، Redis را فعال کنید:

```bash
pip install redis
redis-server
```

### 3. مانیتورینگ

لاگ‌ها را بررسی کنید:

```bash
tail -f logs/detection.log
```

---

## حل مشکلات سریع 🔧

### مشکل: ModuleNotFoundError

```bash
pip install fuzzywuzzy python-Levenshtein scikit-learn
```

### مشکل: دیتابیس قفل است

```bash
# بستن اتصالات و restart
python app.py
```

### مشکل: دقت پایین

1. افزودن نام‌های مستعار بیشتر
2. بررسی املای نام محصولات
3. اصلاح الگوهای تشخیص

---

## دستورات مفید 📝

```bash
# نمایش آمار
curl http://localhost:8081/api/detection/stats

# تشخیص تکی
curl -X POST http://localhost:8081/api/detection/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "لنت ترمز تویوتا"}'

# تشخیص دسته‌ای همه محصولات
python -c "from brand_vehicle_detector import get_detector; from app import app; app.app_context().push(); get_detector().batch_detect_products()"

# Refresh کش
python -c "from brand_vehicle_detector import get_detector; from app import app; app.app_context().push(); get_detector().refresh_cache()"

# نمایش آمار در ترمینال
python -c "from brand_vehicle_detector import get_detector; from app import app; import json; app.app_context().push(); print(json.dumps(get_detector().get_detection_stats(), indent=2, ensure_ascii=False))"
```

---

## منابع بیشتر 📚

- [مستندات کامل](README_DETECTION.md)
- [مگاپرامپت](brand_vehicle_detection_complete_rebuild_megaprompt.json)
- [API Documentation](API_DOCUMENTATION.md)

---

## چک‌لیست نصب ✓

- [ ] Python 3.8+ نصب است
- [ ] وابستگی‌ها نصب شدند
- [ ] دیتابیس ایجاد شد
- [ ] داده‌های اولیه وارد شدند
- [ ] تست‌ها موفق بودند
- [ ] محصولات تشخیص داده شدند
- [ ] گزارش تولید شد

---

## پشتیبانی 💬

اگر به کمک نیاز دارید:

1. ابتدا [README کامل](README_DETECTION.md) را مطالعه کنید
2. [مسائل رایج](TROUBLESHOOTING.md) را بررسی کنید
3. با پشتیبانی تماس بگیرید

---

**موفق باشید! 🎉**

</div>

---

# English Quick Start

## One-Click Start

```bash
python run_complete_detection.py --full-rebuild --auto-detect-all --generate-reports --backup-first --verbose
```

This command automatically:

- ✅ Checks all prerequisites
- ✅ Creates backup
- ✅ Installs dependencies
- ✅ Sets up database
- ✅ Imports initial data
- ✅ Detects all products
- ✅ Generates complete report

## Quick Test

```python
from brand_vehicle_detector import get_detector

detector = get_detector()
result = detector.detect_brand_and_vehicle_types("Toyota Camry brake pad")

print(result)
# Output: {'status': 'success', 'data': {...}}
```

## API Usage

```bash
curl -X POST http://localhost:8081/api/detection/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Toyota Camry brake pad"}'
```

## Useful Commands

```bash
# View stats
curl http://localhost:8081/api/detection/stats

# Batch detect all products
python -c "from brand_vehicle_detector import get_detector; from app import app; app.app_context().push(); get_detector().batch_detect_products()"

# Refresh cache
python -c "from brand_vehicle_detector import get_detector; from app import app; app.app_context().push(); get_detector().refresh_cache()"
```

---

**Good Luck! 🚀**

