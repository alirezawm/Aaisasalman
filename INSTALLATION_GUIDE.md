# 📖 راهنمای نصب و راه‌اندازی API موبایل

## 📋 پیش‌نیازها

### نرم‌افزارهای مورد نیاز:
- Python 3.8 یا بالاتر
- pip (Python Package Manager)
- یک ویرایشگر کد (VS Code، PyCharm، و...)
- Postman (برای تست API - اختیاری)

---

## 🚀 مراحل نصب

### مرحله 1: بررسی Python

```bash
python --version
# یا
python3 --version
```

باید نسخه 3.8 یا بالاتر باشد.

---

### مرحله 2: نصب وابستگی‌ها

در دایرکتوری پروژه، فایل `requirements.txt` را بررسی کنید. اگر وجود ندارد، این وابستگی‌ها را نصب کنید:

```bash
pip install flask flask-jwt-extended flask-cors flask-login sqlalchemy
```

یا اگر فایل requirements.txt وجود دارد:

```bash
pip install -r requirements.txt
```

---

### مرحله 3: تنظیمات

#### 3.1 بررسی فایل `app.py`

اطمینان حاصل کنید که:
- `SECRET_KEY` تنظیم شده است
- `JWT_SECRET_KEY` تنظیم شده است
- دیتابیس در دسترس است

#### 3.2 تنظیم Base URL (برای تست)

در فایل `test_mobile_api.py`، Base URL را تنظیم کنید:

```python
BASE_URL = "http://localhost:5000/api/mobile/v1"
```

---

### مرحله 4: راه‌اندازی دیتابیس

اطمینان حاصل کنید که دیتابیس ایجاد شده است:

```bash
# اگر از SQLite استفاده می‌کنید، فایل دیتابیس باید موجود باشد
# یا از دستورات Flask-Migrate استفاده کنید
```

---

### مرحله 5: اجرای سرور

```bash
python app.py
```

یا:

```bash
flask run
```

سرور باید روی `http://localhost:5000` اجرا شود.

---

## 🧪 تست API

### روش 1: استفاده از فایل تست

```bash
python test_mobile_api.py
```

این فایل تمام endpoint ها را به صورت خودکار تست می‌کند.

### روش 2: استفاده از Postman

1. فایل `AsiaSalman_Mobile_API.postman_collection.json` را در Postman import کنید
2. متغیرهای محیط را تنظیم کنید:
   - `base_url`: `http://localhost:5000/api/mobile/v1`
3. شروع به تست کنید!

### روش 3: استفاده از curl

```bash
# ارسال OTP
curl -X POST http://localhost:5000/api/mobile/v1/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "09123456789"}'
```

---

## 🔧 تنظیمات پیشرفته

### تنظیم JWT

در فایل `app.py`:

```python
app.config['JWT_SECRET_KEY'] = 'your-super-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
```

### تنظیم CORS

```python
CORS(app, resources={r"/api/mobile/*": {"origins": "*"}})
```

برای production، origins را محدود کنید:

```python
CORS(app, resources={r"/api/mobile/*": {"origins": ["https://yourdomain.com"]}})
```

---

## 🐛 عیب‌یابی

### مشکل: سرور اجرا نمی‌شود

**راه‌حل:**
1. بررسی کنید که پورت 5000 آزاد است
2. وابستگی‌ها را دوباره نصب کنید
3. لاگ خطاها را بررسی کنید

### مشکل: خطای دیتابیس

**راه‌حل:**
1. بررسی کنید که دیتابیس ایجاد شده است
2. اتصال به دیتابیس را بررسی کنید
3. جداول را ایجاد کنید

### مشکل: خطای 401 (Unauthorized)

**راه‌حل:**
1. بررسی کنید که توکن در header ارسال می‌شود
2. فرمت توکن درست است: `Bearer {token}`
3. توکن منقضی نشده باشد

### مشکل: خطای 404 (Not Found)

**راه‌حل:**
1. URL را بررسی کنید
2. Base URL را بررسی کنید
3. مطمئن شوید که Blueprint ثبت شده است

---

## 📱 اتصال Android

برای اتصال نرم‌افزار Android به API:

1. Base URL را در Android تنظیم کنید:
   ```kotlin
   const val BASE_URL = "https://www.asiasalman.com/api/mobile/v1/"
   ```

2. از Retrofit استفاده کنید:
   ```kotlin
   val retrofit = Retrofit.Builder()
       .baseUrl(BASE_URL)
       .addConverterFactory(GsonConverterFactory.create())
       .build()
   ```

3. توکن را در هر درخواست اضافه کنید:
   ```kotlin
   @Header("Authorization") token: String = "Bearer $accessToken"
   ```

---

## 🔒 امنیت در Production

### نکات مهم:

1. **SECRET_KEY**: باید یک رشته تصادفی قوی باشد
2. **JWT_SECRET_KEY**: باید متفاوت از SECRET_KEY باشد
3. **HTTPS**: حتماً از HTTPS استفاده کنید
4. **CORS**: Origins را محدود کنید
5. **Rate Limiting**: محدودیت درخواست اضافه کنید
6. **Logging**: لاگ‌های حساس را ذخیره نکنید

---

## 📚 منابع بیشتر

- [مستندات Flask](https://flask.palletsprojects.com/)
- [مستندات Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [مستندات API](./API_DOCUMENTATION_COMPLETE.md)

---

## ✅ چک‌لیست نصب

- [ ] Python نصب شده است
- [ ] وابستگی‌ها نصب شده‌اند
- [ ] دیتابیس ایجاد شده است
- [ ] تنظیمات انجام شده است
- [ ] سرور اجرا می‌شود
- [ ] تست‌ها موفق هستند
- [ ] Postman Collection کار می‌کند

---

**آخرین به‌روزرسانی**: اکنون  
**نسخه**: 1.0.0

