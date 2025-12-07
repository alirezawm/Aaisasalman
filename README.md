# 🚗 Asia Salman - E-Commerce Platform

فروشگاه آنلاین قطعات خودرو با پشتیبانی کامل از API موبایل

Online Auto Parts E-Commerce Platform with Complete Mobile API Support

---

## 📋 فهرست

- [ویژگی‌ها](#ویژگی‌ها)
- [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
- [API موبایل](#api-موبایل)
- [مستندات](#مستندات)
- [توسعه](#توسعه)
- [مشارکت](#مشارکت)

---

## ✨ ویژگی‌ها

### وب‌سایت
- ✅ سیستم مدیریت محصولات
- ✅ مدیریت دسته‌بندی (بر اساس خودرو و برند)
- ✅ سبد خرید و فاکتور
- ✅ مدیریت کاربران و نقش‌ها
- ✅ پنل مدیریت کامل
- ✅ سیستم امتیازدهی و جوایز
- ✅ پشتیبانی از خریداران عمده

### API موبایل
- ✅ **29 endpoint کامل**
- ✅ احراز هویت با OTP
- ✅ مدیریت JWT Token
- ✅ مدیریت محصولات و جستجو
- ✅ مدیریت سبد خرید (نقدی و چکی)
- ✅ مدیریت سفارشات
- ✅ پروفایل کاربر
- ✅ درخواست خریدار عمده
- ✅ تنظیمات و بنرها

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.8+
- pip
- SQLite (یا دیتابیس دیگر)

### مراحل نصب

1. **کلون کردن پروژه** (یا دانلود)

```bash
git clone <repository-url>
cd asiasalman
```

2. **ایجاد محیط مجازی**

```bash
python -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate
```

3. **نصب وابستگی‌ها**

```bash
pip install -r requirements.txt
```

4. **تنظیم دیتابیس**

```bash
# ایجاد جداول (در صورت نیاز)
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

5. **اجرای سرور**

```bash
python app.py
```

سرور روی `http://localhost:5000` اجرا می‌شود.

---

## 📱 API موبایل

### Base URL

```
/api/mobile/v1
```

### مستندات کامل

- [مستندات کامل API](./API_DOCUMENTATION_COMPLETE.md)
- [راهنمای نصب API](./INSTALLATION_GUIDE.md)
- [Postman Collection](./AsiaSalman_Mobile_API.postman_collection.json)

### تست API

```bash
python test_mobile_api.py
```

یا از Postman Collection استفاده کنید.

---

## 📚 مستندات

### برای توسعه‌دهندگان

- [راهنمای توسعه](./INSTALLATION_GUIDE.md)
- [نمونه کدهای Android](./Android_Code_Samples.kt)
- [مگاپرامپت Android](./android_app_megaprompt.json)

### فایل‌های مهم

- `mobile_api.py` - تمام endpoint های API موبایل
- `app.py` - تنظیمات اصلی Flask
- `models.py` - مدل‌های دیتابیس
- `routes.py` - مسیرهای وب‌سایت

---

## 🔧 تنظیمات

### متغیرهای محیطی

یک فایل `.env` ایجاد کنید:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///asia_salman.db
FLASK_ENV=development
```

### تنظیمات JWT

در `app.py`:

```python
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
```

---

## 🧪 تست

### تست API

```bash
python test_mobile_api.py
```

### تست با Postman

1. فایل `AsiaSalman_Mobile_API.postman_collection.json` را import کنید
2. متغیر `base_url` را تنظیم کنید
3. شروع به تست کنید!

---

## 📁 ساختار پروژه

```
asiasalman/
├── app.py                 # تنظیمات اصلی Flask
├── mobile_api.py          # API موبایل (29 endpoint)
├── models.py              # مدل‌های دیتابیس
├── routes.py              # مسیرهای وب‌سایت
├── requirements.txt       # وابستگی‌های Python
├── test_mobile_api.py     # فایل تست API
├── templates/             # قالب‌های HTML
├── static/                # فایل‌های استاتیک
└── uploads/               # فایل‌های آپلود شده
```

---

## 🔒 امنیت

### نکات مهم

- ✅ از SECRET_KEY قوی استفاده کنید
- ✅ در Production از HTTPS استفاده کنید
- ✅ CORS را محدود کنید
- ✅ Rate Limiting اضافه کنید
- ✅ لاگ‌های حساس را ذخیره نکنید

---

## 📊 آمار پروژه

- **API Endpoints**: 29
- **خطوط کد API**: 1949
- **زبان**: Python (Flask)
- **دیتابیس**: SQLite
- **Authentication**: JWT + OTP

---

## 🛠️ فناوری‌ها

- **Backend**: Flask, SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **API**: RESTful
- **CORS**: Flask-CORS
- **Database**: SQLite

---

## 📱 نرم‌افزار Android

برای ساخت نرم‌افزار Android:

1. از [مگاپرامپت Android](./android_app_megaprompt.json) استفاده کنید
2. نمونه کدهای [Android](./Android_Code_Samples.kt) را ببینید
3. به API متصل شوید

---

## 🐛 عیب‌یابی

### مشکلات رایج

**سرور اجرا نمی‌شود:**
- بررسی کنید پورت 5000 آزاد است
- وابستگی‌ها را دوباره نصب کنید

**خطای دیتابیس:**
- دیتابیس را بررسی کنید
- جداول را ایجاد کنید

**خطای 401 (Unauthorized):**
- توکن را بررسی کنید
- فرمت صحیح: `Bearer {token}`

---

## 📝 تغییرات

### نسخه 1.0.0
- ✅ پیاده‌سازی کامل API موبایل
- ✅ 29 endpoint کامل
- ✅ مستندات کامل
- ✅ فایل‌های تست

---

## 👥 مشارکت

برای مشارکت:
1. Fork کنید
2. Branch ایجاد کنید
3. تغییرات را commit کنید
4. Pull Request بفرستید

---

## 📄 مجوز

[متن مجوز را اینجا اضافه کنید]

---

## 📞 تماس

- **ایمیل**: [ایمیل را اضافه کنید]
- **وب‌سایت**: [آدرس وب‌سایت]

---

## 🙏 تشکر

از تمام مشارکت‌کنندگان و کاربران تشکر می‌کنیم.

---

**آخرین به‌روزرسانی**: 2025-01-27  
**نسخه**: 1.0.0  
**وضعیت**: ✅ آماده استفاده

---

## 📚 منابع بیشتر

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [API Documentation](./API_DOCUMENTATION_COMPLETE.md)

---

**موفق باشید! 🚀**

