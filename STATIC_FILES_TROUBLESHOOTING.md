# راهنمای رفع مشکل Static Files (404 Errors)

## مشکل
فایل‌های static (logo.png, favicon, etc.) با خطای 404 مواجه می‌شوند.

## علل احتمالی

### 1. نبود nginx در docker-compose.yaml
در `docker-compose.yaml` فعلی، nginx service وجود ندارد. باید اضافه شود.

### 2. عدم دسترسی nginx به static files
nginx container باید به فایل‌های static دسترسی داشته باشد.

### 3. مسیر نادرست در nginx configuration
nginx باید مسیر صحیح static files را داشته باشد.

## راه‌حل‌ها

### راه‌حل 1: اضافه کردن nginx به docker-compose.yaml (توصیه می‌شود)

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: asiasalman_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./static:/usr/src/app/static:ro  # مهم: mount static folder
      - ./uploads:/usr/src/app/uploads:ro  # مهم: mount uploads folder
      - ./ssl_certs:/etc/nginx/ssl:ro
    depends_on:
      - web
    networks:
      - asiasalman_network
```

### راه‌حل 2: استفاده از Flask route (fallback)
اگر nginx نتواند فایل را پیدا کند، Flask route که اضافه کردیم به عنوان fallback عمل می‌کند.

### راه‌حل 3: Proxy static files از Flask
اگر نمی‌خواهید nginx را اضافه کنید، می‌توانید تمام static files را از Flask serve کنید.

## مراحل بررسی و رفع مشکل

### مرحله 1: بررسی وجود فایل‌ها در container

```bash
# بررسی فایل‌ها در web container
docker exec -it asiasalman_web ls -la /usr/src/app/static/images/

# بررسی وجود logo.png
docker exec -it asiasalman_web ls -la /usr/src/app/static/images/logo.png

# بررسی favicon files
docker exec -it asiasalman_web ls -la /usr/src/app/static/images/favicon*.png
```

### مرحله 2: بررسی nginx container (اگر وجود دارد)

```bash
# بررسی nginx container
docker ps | grep nginx

# اگر nginx container وجود دارد، بررسی کنید
docker exec -it asiasalman_nginx ls -la /usr/src/app/static/images/
```

### مرحله 3: بررسی nginx configuration

```bash
# بررسی nginx config
cat nginx/conf.d/default.conf

# بررسی اینکه آیا static folder mount شده است
docker inspect asiasalman_nginx | grep -A 10 Mounts
```

### مرحله 4: تست دسترسی مستقیم

```bash
# تست از داخل web container
docker exec -it asiasalman_web curl http://localhost:8000/static/images/logo.png

# تست از داخل nginx container (اگر وجود دارد)
docker exec -it asiasalman_nginx curl http://web:8000/static/images/logo.png
```

### مرحله 5: بررسی logs

```bash
# بررسی nginx logs
docker logs asiasalman_nginx

# بررسی web logs
docker logs asiasalman_web | grep -i static
```

## راه‌حل سریع

### اگر nginx ندارید:
1. route Flask که اضافه کردیم (`/static/<path:filename>`) باید کار کند
2. مطمئن شوید که فایل‌ها در container وجود دارند
3. restart کنید: `docker-compose restart web`

### اگر nginx دارید:
1. مطمئن شوید که static folder mount شده است
2. nginx configuration را بررسی کنید
3. restart کنید: `docker-compose restart nginx web`

## بررسی نهایی

بعد از اعمال تغییرات، این URL ها را تست کنید:

```
https://www.asiasalman.com/static/images/logo.png
https://www.asiasalman.com/static/images/favicon-32x32.png
https://www.asiasalman.com/manifest.json
```

همه باید کار کنند.

