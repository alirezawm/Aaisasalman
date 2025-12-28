# راهنمای پاک کردن Cache و رفع مشکل Static Files

## مشکل
اگر فایل‌های static (logo.png, favicon, etc.) با خطای 404 مواجه می‌شوند اما لینک‌ها به تنهایی کار می‌کنند، مشکل از cache مرورگر یا Service Worker است.

## راه‌حل‌های سریع

### راه‌حل 1: Hard Refresh مرورگر

**Chrome/Edge (Windows):**
- `Ctrl + Shift + R` یا `Ctrl + F5`

**Chrome/Edge (Mac):**
- `Cmd + Shift + R`

**Firefox:**
- `Ctrl + Shift + R` (Windows) یا `Cmd + Shift + R` (Mac)

**Safari:**
- `Cmd + Option + R`

### راه‌حل 2: Clear Cache مرورگر

**Chrome/Edge:**
1. `F12` برای باز کردن Developer Tools
2. راست کلیک روی دکمه Refresh
3. انتخاب "Empty Cache and Hard Reload"

**Firefox:**
1. `Ctrl + Shift + Delete` (Windows) یا `Cmd + Shift + Delete` (Mac)
2. انتخاب "Cache" و "Clear Now"

### راه‌حل 3: Unregister Service Worker

1. باز کردن Developer Tools (`F12`)
2. رفتن به تب "Application" (Chrome) یا "Storage" (Firefox)
3. در سمت چپ، کلیک روی "Service Workers"
4. کلیک روی "Unregister" برای هر Service Worker فعال

یا در Console مرورگر این کد را اجرا کنید:

```javascript
navigator.serviceWorker.getRegistrations().then(function(registrations) {
    for(let registration of registrations) {
        registration.unregister();
    }
    console.log('All Service Workers unregistered');
    window.location.reload();
});
```

### راه‌حل 4: Clear All Cache

**Chrome/Edge:**
1. Developer Tools (`F12`)
2. تب "Application"
3. "Clear storage" در سمت چپ
4. تیک زدن "Cache storage" و "Service Workers"
5. کلیک روی "Clear site data"

**Firefox:**
1. Developer Tools (`F12`)
2. تب "Storage"
3. راست کلیک روی "Cache Storage"
4. "Delete All"

## تغییرات انجام شده

1. **Service Worker به‌روزرسانی شد:**
   - Cache name به `asiasalman-v2` تغییر کرد
   - Strategy برای static files به "Network First" تغییر کرد
   - Cache قدیمی به صورت خودکار پاک می‌شود

2. **Route Flask برای static files:**
   - Route `/static/<path:filename>` به عنوان fallback اضافه شد

## تست بعد از Clear Cache

بعد از پاک کردن cache، این URL ها را تست کنید:

```
https://www.asiasalman.com/static/images/logo.png
https://www.asiasalman.com/static/images/favicon-32x32.png
https://www.asiasalman.com/manifest.json
```

همه باید کار کنند.

## اگر مشکل ادامه داشت

1. بررسی کنید که فایل‌ها در container وجود دارند:
```bash
docker exec -it asiasalman_web ls -la /usr/src/app/static/images/logo.png
```

2. بررسی logs:
```bash
docker logs asiasalman_web | grep -i static
docker logs asiasalman_nginx | grep -i static
```

3. Restart containers:
```bash
docker-compose restart web nginx
```

