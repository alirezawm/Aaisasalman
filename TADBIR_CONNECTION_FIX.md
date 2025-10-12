# راهنمای رفع مشکل اتصال به تدبیر
## Tadbir Connection Fix Guide

## تشخیص مشکل

تست‌های انجام شده نشان می‌دهند:

### ✅ موارد صحیح:
- سرور تدبیر در `http://5.202.90.240:8085` در دسترس است
- پورت 8085 باز و قابل دسترسی است
- API تدبیر در حال کار است

### ❌ مشکلات:
- نام کاربری یا رمز عبور صحیح نیست
- API خطای `invalid_grant` برمی‌گرداند
- تمام endpoint ها کد وضعیت 503 برمی‌گردانند (Service Unavailable)

## علت اصلی مشکل

احراز هویت ناموفق است. نام کاربری و رمز عبور فعلی:
```
Username: Asia@tadbir.biz
Password: Asia@tadbir.biz
```

این اطلاعات توسط API تدبیر رد می‌شود.

## راه‌حل

### گام ۱: دریافت اطلاعات صحیح

با مدیر سرور تدبیر تماس بگیرید و اطلاعات صحیح را دریافت کنید:
- نام کاربری صحیح (Username)
- رمز عبور صحیح (Password)
- آدرس API (در حال حاضر: http://5.202.90.240:8085)

### گام ۲: ایجاد فایل .env

در پوشه اصلی پروژه (`D:\site4\site4`) فایلی به نام `.env` ایجاد کنید:

```env
# Tadbir API Configuration
TADBIR_API_URL=http://5.202.90.240:8085
TADBIR_USERNAME=نام_کاربری_صحیح_اینجا
TADBIR_PASSWORD=رمز_عبور_صحیح_اینجا
TADBIR_TIMEOUT=300
TADBIR_RETRY_ATTEMPTS=3

# Sync Configuration
SYNC_INTERVAL_HOURS=3
BATCH_SIZE=1000
ENABLE_INCREMENTAL_SYNC=True
```

### گام ۳: نصب python-dotenv (در صورت نیاز)

```bash
pip install python-dotenv
```

### گام ۴: به‌روزرسانی پایگاه داده

اطلاعات احراز هویت را در پایگاه داده ذخیره کنید:

```bash
python setup_tadbir_credentials.py
```

این اسکریپت از شما نام کاربری و رمز عبور صحیح را می‌خواهد.

### گام ۵: تست اتصال

پس از تنظیم اطلاعات صحیح، اتصال را تست کنید:

```bash
python test_tadbir_simple.py
```

## تست دستی با curl (اختیاری)

می‌توانید با ابزار curl یا Postman هم تست کنید:

```bash
curl -X POST http://5.202.90.240:8085/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=نام_کاربری&password=رمز_عبور"
```

اگر اطلاعات صحیح باشند، باید یک توکن دریافت کنید:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## رفع مشکلات احتمالی

### 1. خطای "invalid_grant"
- نام کاربری یا رمز عبور اشتباه است
- حساب کاربری قفل شده است
- با مدیر تدبیر تماس بگیرید

### 2. خطای "Connection refused"
- سرور تدبیر خاموش است
- آدرس IP یا پورت اشتباه است
- فایروال اتصال را مسدود می‌کند

### 3. خطای "Timeout"
- سرور تدبیر خیلی کند است
- مشکل شبکه وجود دارد
- Timeout را افزایش دهید (در .env)

## تماس با پشتیبانی

در صورت ادامه مشکل:

1. **مدیر سرور تدبیر**: 
   - بررسی کنید که حساب فعال است
   - نام کاربری و رمز عبور را تایید کنید
   - دسترسی‌های لازم را بررسی کنید

2. **فایل‌های Log**:
   - بررسی کنید: `tadbir_test_*.json`
   - بررسی کنید: `tadbir_auth_test_*.json`

3. **اطلاعات سرور**:
   - IP: 5.202.90.240
   - Port: 8085
   - API Endpoint: /token

## گزارش‌های تست

تمام تست‌ها در فایل‌های JSON ذخیره می‌شوند:
- `tadbir_test_YYYYMMDD_HHMMSS.json`
- `tadbir_auth_test_YYYYMMDD_HHMMSS.json`

این فایل‌ها را برای بررسی بیشتر نگه دارید.

