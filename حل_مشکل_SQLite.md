# 🔧 حل مشکل SQLite در Docker Build

## 🚨 مشکل
خطای `pysqlite3` در هنگام ساخت Docker image:
```
fatal error: sqlite3.h: No such file or directory
```

## ✅ راه‌حل

### 1. استفاده از فایل‌های اصلاح شده

فایل‌های زیر برای حل مشکل ایجاد شده‌اند:

- **`Dockerfile.fixed`** - Dockerfile اصلاح شده با SQLite headers
- **`requirements.fixed.txt`** - requirements.txt بدون pysqlite3
- **`test_docker_build.sh`** - اسکریپت تست Docker build

### 2. مراحل حل مشکل

#### مرحله 1: کپی فایل‌های اصلاح شده
```bash
cp Dockerfile.fixed Dockerfile
cp requirements.fixed.txt requirements.txt
```

#### مرحله 2: تست Docker build
```bash
chmod +x test_docker_build.sh
./test_docker_build.sh
```

#### مرحله 3: راه‌اندازی کامل
```bash
chmod +x setup_server.sh
./setup_server.sh
```

## 🔍 تغییرات اعمال شده

### Dockerfile
- اضافه کردن `libsqlite3-dev` و `sqlite3` در build stage
- اضافه کردن `libsqlite3-0` و `sqlite3` در production stage

### requirements.txt
- حذف `pysqlite3==0.5.2`
- حذف `pysqlite3-binary==0.5.2.post2`
- استفاده از SQLite built-in Python 3.11

## 🧪 تست

### تست محلی
```bash
# ساخت image
docker build -t asiasalman:test .

# اجرای container
docker run --rm -d --name test -p 8081:8000 asiasalman:test

# تست سلامت
curl http://localhost:8081/health
```

### تست در سرور
```bash
# اتصال به سرور
ssh -p 2222 root@192.168.1.4

# کپی فایل‌ها
scp -P 2222 Dockerfile.fixed root@192.168.1.4:/root/application/
scp -P 2222 requirements.fixed.txt root@192.168.1.4:/root/application/

# در سرور
cd /root/application
cp Dockerfile.fixed Dockerfile
cp requirements.fixed.txt requirements.txt
docker-compose build --no-cache
docker-compose up -d
```

## 📋 بررسی نهایی

پس از راه‌اندازی، موارد زیر را بررسی کنید:

1. **وضعیت container ها**:
   ```bash
   docker-compose ps
   ```

2. **سلامت اپلیکیشن**:
   ```bash
   curl http://192.168.1.4:8081/health
   ```

3. **لاگ‌ها**:
   ```bash
   docker-compose logs
   ```

## ⚠️ نکات مهم

1. **SQLite built-in**: Python 3.11 خودش sqlite3 دارد، نیازی به pysqlite3 نیست
2. **Headers**: فقط برای build نیاز است، runtime فقط library کافی است
3. **Performance**: SQLite built-in بهینه‌تر از pysqlite3 است

## 🔄 بازگشت به حالت قبلی

اگر نیاز به بازگشت دارید:

```bash
# بازگردانی فایل‌های اصلی
git checkout Dockerfile
git checkout requirements.txt

# یا استفاده از backup
cp Dockerfile.backup Dockerfile
cp requirements.txt.backup requirements.txt
```

---

**✅ مشکل SQLite حل شد!**

اکنون می‌توانید Docker build را بدون مشکل انجام دهید.
