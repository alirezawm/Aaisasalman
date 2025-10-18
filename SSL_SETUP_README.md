# 🔒 راهنمای راه‌اندازی SSL برای دامنه asiasalman.com

## ✅ کارهای انجام شده

### 1. ایجاد پوشه SSL
- پوشه `ssl/` در ریشه پروژه ایجاد شد
- گواهی‌های SSL در این پوشه قرار گرفتند

### 2. فایل‌های گواهی SSL
```
ssl/
├── cert.pem          # گواهی کامل (fullchain)
├── key.pem           # کلید خصوصی
└── cert.pfx          # گواهی در فرمت PFX
```

### 3. پیکربندی Nginx
- پیکربندی HTTPS در `nginx/conf.d/default.conf` فعال شد
- دامنه‌های `asiasalman.com` و `www.asiasalman.com` پیکربندی شدند
- Redirect خودکار از HTTP به HTTPS اضافه شد
- تنظیمات امنیتی SSL بهینه شد

### 4. پیکربندی Docker Compose
- پوشه `ssl/` به container nginx mount شد
- Volume غیرضروری `ssl_certs` حذف شد

## 🚀 راه‌اندازی

### 1. راه‌اندازی سرویس‌ها
```bash
docker-compose up -d
```

### 2. بررسی وضعیت SSL
```bash
# بررسی وضعیت container ها
docker-compose ps

# بررسی لاگ nginx
docker-compose logs nginx

# تست SSL
curl -I https://asiasalman.com
```

## 🔧 تنظیمات SSL

### ویژگی‌های امنیتی فعال شده:
- **TLS 1.2 و 1.3**: فقط پروتکل‌های امن
- **HSTS**: اجباری کردن HTTPS
- **Cipher Suites**: الگوریتم‌های رمزنگاری قوی
- **Security Headers**: هدرهای امنیتی اضافی

### پورت‌های فعال:
- **80**: HTTP (redirect به HTTPS)
- **443**: HTTPS

## 🔍 عیب‌یابی

### مشکلات رایج:

1. **خطای SSL Certificate**
   ```bash
   # بررسی وجود فایل‌ها
   ls -la ssl/
   
   # بررسی محتوای گواهی
   openssl x509 -in ssl/cert.pem -text -noout
   ```

2. **خطای Nginx Configuration**
   ```bash
   # تست پیکربندی nginx
   docker-compose exec nginx nginx -t
   ```

3. **مشکل در Mount کردن فایل‌ها**
   ```bash
   # بررسی mount در container
   docker-compose exec nginx ls -la /etc/nginx/ssl/
   ```

## 📝 نکات مهم

- گواهی‌های SSL باید برای دامنه `asiasalman.com` صادر شده باشند
- فایل‌های گواهی باید در فرمت PEM باشند
- کلید خصوصی باید محافظت شود و دسترسی محدود داشته باشد
- برای تولید، گواهی‌ها باید از یک CA معتبر دریافت شوند

## 🔄 به‌روزرسانی گواهی

برای به‌روزرسانی گواهی‌های SSL:

1. فایل‌های جدید را در پوشه `ssl/` قرار دهید
2. نام فایل‌ها باید `cert.pem` و `key.pem` باشند
3. nginx را restart کنید:
   ```bash
   docker-compose restart nginx
   ```

## 📞 پشتیبانی

در صورت بروز مشکل، لاگ‌های nginx را بررسی کنید:
```bash
docker-compose logs nginx
```
