# راهنمای رفع مشکل Static Files در Production

## مشکل
فایل‌های static (logo.png, favicon, etc.) در production با خطای 404 مواجه می‌شوند، اما لینک‌ها به تنهایی کار می‌کنند.

## علت
nginx در production نمی‌تواند فایل‌های static را پیدا کند یا route Flask به درستی کار نمی‌کند.

## راه‌حل‌های سریع

### راه‌حل 1: بررسی nginx container (اگر nginx دارید)

```bash
# بررسی وجود فایل‌ها در nginx container
docker exec -it asiasalman_nginx ls -la /usr/src/app/static/images/

# اگر فایل‌ها وجود ندارند، بررسی volume mount
docker inspect asiasalman_nginx | grep -A 10 Mounts

# بررسی nginx logs
docker logs asiasalman_nginx 2>&1 | grep -i static
```

**اگر فایل‌ها در nginx container وجود ندارند:**
1. مطمئن شوید که در `docker-compose.yaml` static folder mount شده است:
```yaml
nginx:
  volumes:
    - ./static:/usr/src/app/static:ro  # این خط باید وجود داشته باشد
```

2. Restart nginx:
```bash
docker-compose restart nginx
```

### راه‌حل 2: استفاده از Flask route (اگر nginx ندارید یا کار نمی‌کند)

Route Flask که اضافه کردیم باید کار کند. برای تست:

```bash
# تست از داخل web container
docker exec -it asiasalman_web curl http://localhost:8000/static/images/logo.png

# اگر کار کرد، مشکل از nginx است
```

**اگر Flask route کار نمی‌کند:**
1. بررسی logs:
```bash
docker logs asiasalman_web | grep -i static
```

2. Restart web container:
```bash
docker-compose restart web
```

### راه‌حل 3: بررسی nginx configuration

اگر nginx دارید، بررسی کنید که configuration درست است:

```bash
# بررسی nginx config
docker exec -it asiasalman_nginx cat /etc/nginx/conf.d/default.conf

# باید این خطوط را ببینید:
# location /static/ {
#     alias /usr/src/app/static/;
#     ...
# }
```

**اگر nginx config درست نیست:**
1. اجرای اسکریپت setup:
```bash
./setup_nginx.sh
```

2. یا دستی ایجاد کنید:
```bash
mkdir -p nginx/conf.d
# سپس فایل nginx/conf.d/default.conf را ایجاد کنید
```

3. Restart nginx:
```bash
docker-compose restart nginx
```

### راه‌حل 4: Disable nginx برای static files (موقت)

اگر nginx مشکل دارد، می‌توانید موقتاً nginx را برای static files disable کنید:

در `nginx/conf.d/default.conf`، location `/static/` را comment کنید:

```nginx
# location /static/ {
#     alias /usr/src/app/static/;
#     expires 1y;
#     add_header Cache-Control "public, immutable";
#     access_log off;
# }
```

سپس restart کنید:
```bash
docker-compose restart nginx
```

حالا Flask route static files را serve می‌کند.

## بررسی نهایی

بعد از اعمال تغییرات:

1. **تست از مرورگر:**
   - `https://www.asiasalman.com/static/images/logo.png`
   - باید تصویر نمایش داده شود

2. **تست از command line:**
```bash
curl -I https://www.asiasalman.com/static/images/logo.png
# باید HTTP 200 برگرداند
```

3. **بررسی logs:**
```bash
# nginx logs
docker logs asiasalman_nginx 2>&1 | tail -20

# web logs
docker logs asiasalman_web 2>&1 | tail -20
```

## اگر مشکل ادامه داشت

1. **بررسی permissions:**
```bash
docker exec -it asiasalman_web ls -la /usr/src/app/static/images/
# باید فایل‌ها readable باشند
```

2. **بررسی network:**
```bash
# تست ارتباط بین nginx و web
docker exec -it asiasalman_nginx ping web
```

3. **بررسی docker-compose:**
```bash
# مطمئن شوید که همه services running هستند
docker-compose ps

# مطمئن شوید که networks درست هستند
docker network inspect asiasalman_asiasalman_network
```

## تغییرات انجام شده

1. ✅ Route Flask برای `/static/<path:filename>` اضافه شد
2. ✅ Logging بهتر برای debugging
3. ✅ Cache headers اضافه شد
4. ✅ Service Worker به‌روزرسانی شد

## توصیه

**بهترین راه‌حل:** استفاده از nginx برای static files (سریع‌تر) + Flask route به عنوان fallback.

اگر nginx ندارید یا نمی‌خواهید استفاده کنید، Flask route به تنهایی کافی است.

