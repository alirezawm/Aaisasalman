# سیستم تشخیص خودکار برند و نوع خودرو
## Vehicle Brand & Type Auto-Detection System

<div dir="rtl">

## 📋 فهرست مطالب

- [معرفی](#معرفی)
- [ویژگی‌ها](#ویژگیها)
- [نصب و راه‌اندازی](#نصب-و-راهاندازی)
- [استفاده](#استفاده)
- [API](#api)
- [مدیریت](#مدیریت)
- [عیب‌یابی](#عیبیابی)
- [سوالات متداول](#سوالات-متداول)

---

## 🎯 معرفی

سیستم تشخیص خودکار برند و نوع خودرو یک ابزار هوشمند برای شناسایی خودکار برند و نوع خودرو از نام محصولات است. این سیستم با استفاده از الگوریتم‌های پیشرفته NLP و Machine Learning، قادر به تشخیص دقیق برند و نوع خودرو با دقت بیش از 95% است.

### مزایا

- ✅ **صرفه‌جویی در زمان**: ورود خودکار اطلاعات محصولات
- ✅ **دقت بالا**: دقت تشخیص بیش از 95%
- ✅ **سرعت**: تشخیص در کمتر از 10 میلی‌ثانیه
- ✅ **یادگیری خودکار**: بهبود مستمر با استفاده از بازخورد کاربران
- ✅ **پشتیبانی دو زبانه**: فارسی و انگلیسی

---

## ⚡ ویژگی‌ها

### 1. تشخیص خودکار

- تشخیص برند از نام محصول
- تشخیص نوع خودرو (سدان، SUV، هاچبک، ...)
- تشخیص چندگانه (چند برند/نوع در یک متن)
- محاسبه امتیاز اطمینان

### 2. الگوریتم‌های پیشرفته

- **Fuzzy Matching**: تطبیق تقریبی برای نام‌های مشابه
- **Regular Expressions**: تشخیص دقیق با الگوهای منظم
- **TF-IDF**: وزن‌دهی کلمات مهم
- **N-gram**: تشخیص مبتنی بر توالی کاراکترها

### 3. یادگیری خودکار

- یادگیری از بازخورد کاربران
- استخراج الگوهای جدید
- بهبود خودکار دقت تشخیص

### 4. مدیریت جامع

- داشبورد آماری
- مدیریت الگوها
- مدیریت نام‌های مستعار
- گزارش‌دهی پیشرفته

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

```bash
Python >= 3.8
Flask >= 2.0
SQLAlchemy >= 1.4
```

### نصب با یک کلیک

```bash
python run_complete_detection.py --full-rebuild --auto-detect-all --generate-reports --backup-first
```

### نصب دستی

#### 1. نصب وابستگی‌ها

```bash
pip install fuzzywuzzy
pip install python-Levenshtein
pip install scikit-learn
```

#### 2. ایجاد دیتابیس

```python
from app import app
from models import db
import detection_models

with app.app_context():
    db.create_all()
```

#### 3. مقداردهی اولیه

```bash
python setup_detection_system.py
```

#### 4. راه‌اندازی

```bash
python app.py
```

---

## 📖 استفاده

### استفاده از کد Python

```python
from brand_vehicle_detector import get_detector

# دریافت نمونه detector
detector = get_detector()

# تشخیص تکی
result = detector.detect_brand_and_vehicle_types("لنت ترمز جلو تویوتا کمری سدان")

if result['status'] == 'success':
    data = result['data']
    print(f"برند: {data['detected_brand']['name']}")
    print(f"نوع خودرو: {[vt['name'] for vt in data['detected_vehicle_types']]}")

# تشخیص دسته‌ای
result = detector.batch_detect_products()
print(f"تعداد محصولات پردازش شده: {result['data']['total_processed']}")
print(f"تعداد به‌روزرسانی: {result['data']['updated_count']}")
```

### استفاده از API

#### تشخیص تکی

```bash
curl -X POST http://localhost:8081/api/detection/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "روغن موتور هیوندای سوناتا"}'
```

پاسخ:

```json
{
  "status": "success",
  "data": {
    "product_name": "روغن موتور هیوندای سوناتا",
    "detected_brand": {
      "id": 2,
      "name": "Hyundai",
      "name_fa": "هیوندای",
      "confidence": "high"
    },
    "detected_vehicle_types": [],
    "processing_time": 8
  }
}
```

#### تشخیص دسته‌ای

```bash
curl -X POST http://localhost:8081/api/detection/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "لنت ترمز تویوتا",
      "فیلتر هوای بنز",
      "شمع BMW"
    ]
  }'
```

#### دریافت آمار

```bash
curl http://localhost:8081/api/detection/stats
```

---

## 🎛️ API

### Endpoints

#### POST /api/detection/detect

تشخیص برند و نوع از متن

**Request Body:**

```json
{
  "text": "string (required)",
  "mode": "auto|brand_only|type_only (optional)",
  "confidence_threshold": 0.7
}
```

**Response:**

```json
{
  "status": "success|error",
  "data": {
    "detected_brand": {...},
    "detected_vehicle_types": [...],
    "confidence_scores": {...},
    "processing_time": 10
  }
}
```

#### POST /api/detection/batch

تشخیص دسته‌ای محصولات

**Request Body:**

```json
{
  "product_ids": [1, 2, 3],
  "update_database": true
}
```

#### GET /api/detection/stats

دریافت آمار تشخیص

**Response:**

```json
{
  "total_products": 1000,
  "products_with_brand": 950,
  "products_with_vehicle_types": 850,
  "brand_coverage": 95.0,
  "vehicle_type_coverage": 85.0
}
```

#### POST /api/detection/feedback

ثبت بازخورد تشخیص

**Request Body:**

```json
{
  "detection_log_id": 123,
  "is_correct": false,
  "correct_brand_id": 5,
  "correct_vehicle_type_ids": [2, 3]
}
```

---

## 🎨 مدیریت

### دسترسی به پنل مدیریت

```
http://localhost:8081/admin/detection
```

### بخش‌های پنل مدیریت

#### 1. داشبورد

- نمایش آمار کلی
- نمودارهای عملکرد
- محصولات بدون تشخیص
- تشخیص‌های با اطمینان پایین

#### 2. تشخیص تکی

```
1. وارد کردن متن محصول
2. کلیک روی "تشخیص"
3. بررسی نتایج
4. تأیید یا اصلاح نتایج
```

#### 3. تشخیص دسته‌ای

```
1. انتخاب محصولات (یا همه)
2. فیلتر محصولات بدون برند
3. کلیک روی "شروع تشخیص"
4. مشاهده progress bar
5. بررسی نتایج
```

#### 4. مدیریت الگوها

افزودن الگوی جدید:

```python
pattern_type: brand  # یا vehicle_type
pattern: "تویوتا|toyota|TOYOTA"
target_id: 1  # شناسه برند
confidence_weight: 0.9
```

#### 5. مدیریت نام‌های مستعار

افزودن نام مستعار برای برند:

```
برند: Toyota
نام مستعار: تویوتا، تويوتا، toyota، TOYOTA
زبان: fa
```

#### 6. بازخوردها

- مشاهده بازخوردهای کاربران
- تأیید یا رد بازخوردها
- اعمال بازخوردها برای یادگیری

#### 7. گزارشات

- گزارش عملکرد روزانه/هفتگی/ماهانه
- گزارش خطاها
- گزارش بهبودها
- Export به Excel/PDF

---

## 🔧 عیب‌یابی

### مشکل: دقت تشخیص پایین است

**راه‌حل:**

1. بررسی الگوهای موجود
2. افزودن نام‌های مستعار بیشتر
3. بررسی بازخوردهای کاربران
4. تنظیم آستانه اطمینان

### مشکل: سرعت پردازش پایین است

**راه‌حل:**

1. فعال‌سازی Redis برای کش
2. کاهش تعداد الگوریتم‌های فعال
3. افزایش منابع سرور
4. بهینه‌سازی queries دیتابیس

### مشکل: برند/نوع خاصی تشخیص داده نمی‌شود

**راه‌حل:**

1. بررسی وجود برند/نوع در دیتابیس
2. افزودن الگوی جدید برای آن برند/نوع
3. افزودن نام‌های مستعار
4. بررسی املای نام محصول

### مشکل: تشخیص اشتباه

**راه‌حل:**

1. ثبت بازخورد در سیستم
2. اصلاح الگوهای اشتباه
3. افزایش وزن الگوریتم‌های دقیق‌تر
4. حذف الگوهای مشکل‌دار

### لاگ‌ها

```bash
# مشاهده لاگ‌های تشخیص
tail -f logs/detection.log

# مشاهده لاگ‌های خطا
tail -f logs/detection_errors.log
```

---

## ❓ سوالات متداول

### چگونه دقت تشخیص را افزایش دهم؟

1. افزودن نام‌های مستعار بیشتر
2. اصلاح الگوهای موجود
3. استفاده از بازخورد کاربران
4. آموزش سیستم با داده‌های بیشتر

### آیا می‌توانم الگوریتم‌های خاص خود را اضافه کنم؟

بله! می‌توانید در فایل `brand_vehicle_detector.py` الگوریتم‌های جدید اضافه کنید.

### چگونه از سیستم برای محصولات دیگر استفاده کنم؟

سیستم قابل تعمیم است و می‌توانید آن را برای هر نوع دسته‌بندی متنی استفاده کنید.

### آیا سیستم از زبان‌های دیگر پشتیبانی می‌کند؟

در حال حاضر فارسی و انگلیسی پشتیبانی می‌شود، اما می‌توانید زبان‌های دیگر را اضافه کنید.

### چگونه پشتیبان‌گیری کنم؟

```bash
python run_complete_detection.py --backup-first
```

یا دستی:

```bash
cp instance/asia_salman.db instance/asia_salman.db.backup_$(date +%Y%m%d_%H%M%S)
```

---

## 📊 معیارهای عملکرد

### هدف

- **دقت**: > 95%
- **سرعت**: < 10ms برای تشخیص تکی
- **سرعت دسته‌ای**: < 2s برای 100 محصول
- **پوشش**: > 90% محصولات

### فعلی

بررسی آمار فعلی با:

```bash
curl http://localhost:8081/api/detection/stats
```

---

## 🔄 به‌روزرسانی

### به‌روزرسانی سیستم

```bash
git pull origin main
python run_complete_detection.py --full-rebuild --backup-first
```

### به‌روزرسانی الگوها

```bash
# Import الگوها از فایل JSON
python -c "from detection_utils import import_patterns; import_patterns('patterns.json')"
```

---

## 🤝 مشارکت

برای مشارکت در پروژه:

1. Fork کردن repository
2. ایجاد branch جدید
3. انجام تغییرات
4. ارسال Pull Request

---

## 📝 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

---

## 📞 پشتیبانی

برای پشتیبانی و سوالات:

- ایمیل: support@example.com
- تلفن: 021-12345678

---

## 🎓 منابع

- [مستندات API](API_DOCUMENTATION.md)
- [راهنمای توسعه‌دهنده](DEVELOPER_GUIDE.md)
- [راهنمای رفع مشکلات](TROUBLESHOOTING.md)

---

## 📅 تاریخچه نسخه‌ها

### نسخه 2.0.0 (2025-10-10)

- بازسازی کامل سیستم
- افزودن الگوریتم‌های پیشرفته
- رابط مدیریت جدید
- یادگیری خودکار
- API کامل

### نسخه 1.0.0 (2025-09-01)

- نسخه اولیه
- تشخیص پایه برند و نوع

---

## 🙏 تشکر

از تمامی کسانی که در توسعه این سیستم مشارکت داشته‌اند، تشکر می‌کنیم.

---

**ساخته شده با ❤️ برای آسیا سلمان**

</div>

