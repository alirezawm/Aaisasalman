# 🚀 راهنمای استقرار (Deployment Guide)

## 📋 مقدمه

این راهنما به شما کمک می‌کند تا پروژه Asia Salman را در محیط Production استقرار دهید.

---

## 🔒 پیش‌نیازها برای Production

### 1. امنیت

#### تغییر کلیدهای امنیتی
```bash
# در فایل .env
SECRET_KEY=<یک رشته تصادفی قوی>
JWT_SECRET_KEY=<یک رشته تصادفی دیگر>
```

برای تولید کلید:
```python
import secrets
print(secrets.token_hex(32))
```

#### تنظیمات HTTPS
- استفاده از HTTPS اجباری است
- گواهینامه SSL نصب کنید
- در `app.py`:
```python
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PREFERRED_URL_SCHEME'] = 'https'
```

#### محدود کردن CORS
```python
CORS(app, resources={
    r"/api/mobile/*": {
        "origins": ["https://yourdomain.com", "https://app.yourdomain.com"]
    }
})
```

---

## 🖥️ گزینه‌های استقرار

### گزینه 1: استفاده از Gunicorn

#### نصب Gunicorn
```bash
pip install gunicorn
```

#### اجرا
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### با فایل تنظیمات
```bash
gunicorn -c gunicorn_config.py app:app
```

### گزینه 2: استفاده از uWSGI

#### نصب
```bash
pip install uwsgi
```

#### اجرا
```bash
uwsgi --http :5000 --wsgi-file app.py --callable app
```

### گزینه 3: استفاده از Docker

#### ایجاد Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### ساخت و اجرا
```bash
docker build -t asiasalman-api .
docker run -p 5000:5000 asiasalman-api
```

---

## ☁️ استقرار روی سرورهای ابری

### Heroku

#### 1. ایجاد فایل `Procfile`
```
web: gunicorn app:app
```

#### 2. ایجاد `runtime.txt`
```
python-3.9.0
```

#### 3. Deploy
```bash
heroku create asiasalman-api
git push heroku main
```

### DigitalOcean

#### استفاده از App Platform
1. به App Platform بروید
2. پروژه را به GitHub متصل کنید
3. تنظیمات را انجام دهید
4. Deploy کنید

### AWS (EC2)

#### مراحل:
1. ایجاد EC2 Instance
2. نصب Python و وابستگی‌ها
3. تنظیم Nginx به عنوان Reverse Proxy
4. استفاده از systemd برای مدیریت

---

## 🔧 تنظیمات Nginx

### فایل تنظیمات Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 نظارت و Logging

### تنظیم Logging

در `app.py`:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/asiasalman.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### استفاده از Monitoring Tools

- **Sentry**: برای ردیابی خطاها
- **New Relic**: برای Performance Monitoring
- **Prometheus + Grafana**: برای Metrics

---

## 🔄 Backup و Restore

### Backup دیتابیس

```bash
# SQLite
cp asia_salman.db backups/asia_salman_$(date +%Y%m%d).db

# PostgreSQL
pg_dump asiasalman > backup_$(date +%Y%m%d).sql
```

### Restore

```bash
# SQLite
cp backups/asia_salman_YYYYMMDD.db asia_salman.db

# PostgreSQL
psql asiasalman < backup_YYYYMMDD.sql
```

---

## ⚡ بهینه‌سازی Performance

### 1. Caching

استفاده از Redis:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379'})
```

### 2. Database Indexing

اطمینان حاصل کنید که Indexes مناسب ایجاد شده‌اند.

### 3. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## 🧪 تست قبل از Deploy

### چک‌لیست:

- [ ] تمام تست‌ها موفق هستند
- [ ] Performance Test انجام شده
- [ ] Security Test انجام شده
- [ ] Backup گرفته شده
- [ ] Documentation به‌روز است
- [ ] Environment Variables تنظیم شده
- [ ] Logging فعال است

---

## 🚨 عیب‌یابی در Production

### بررسی Logs

```bash
# Gunicorn logs
tail -f logs/gunicorn.log

# Application logs
tail -f logs/asiasalman.log

# Nginx logs
tail -f /var/log/nginx/error.log
```

### مشکلات رایج

**خطای 502 Bad Gateway:**
- بررسی کنید Gunicorn اجرا می‌شود
- پورت را بررسی کنید

**خطای Database Locked:**
- Timeout را افزایش دهید
- Connection Pool را بررسی کنید

**مشکل Memory:**
- تعداد Worker ها را کاهش دهید
- Cache را بهینه کنید

---

## 📝 چک‌لیست استقرار

- [ ] Environment Variables تنظیم شده
- [ ] SECRET_KEY تغییر یافته
- [ ] HTTPS فعال شده
- [ ] CORS محدود شده
- [ ] Logging فعال است
- [ ] Backup تنظیم شده
- [ ] Monitoring تنظیم شده
- [ ] Performance بهینه شده
- [ ] Security Test انجام شده
- [ ] Documentation به‌روز است

---

## 🔐 امنیت در Production

### نکات مهم:

1. ✅ استفاده از HTTPS
2. ✅ محدود کردن CORS
3. ✅ استفاده از کلیدهای قوی
4. ✅ Rate Limiting
5. ✅ Input Validation
6. ✅ SQL Injection Prevention
7. ✅ XSS Prevention
8. ✅ CSRF Protection

---

## 📞 پشتیبانی

در صورت مشکل:
1. Logs را بررسی کنید
2. مستندات را مطالعه کنید
3. Issue ایجاد کنید

---

**موفق باشید! 🚀**

