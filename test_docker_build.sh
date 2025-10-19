#!/bin/bash

# ========================================
# اسکریپت تست Docker build
# ========================================

set -e

echo "🔧 تست Docker build..."

# کپی فایل‌های اصلاح شده
echo "📁 کپی فایل‌های اصلاح شده..."
cp Dockerfile.fixed Dockerfile
cp requirements.fixed.txt requirements.txt

# ساخت Docker image
echo "🐳 ساخت Docker image..."
docker build -t asiasalman:test .

# تست اجرای container
echo "🚀 تست اجرای container..."
docker run --rm -d --name asiasalman_test -p 8081:8000 asiasalman:test

# انتظار برای راه‌اندازی
echo "⏳ انتظار برای راه‌اندازی..."
sleep 30

# تست سلامت
echo "🏥 تست سلامت اپلیکیشن..."
if curl -f http://localhost:8081/health >/dev/null 2>&1; then
    echo "✅ اپلیکیشن با موفقیت راه‌اندازی شد!"
    echo "🌐 آدرس: http://localhost:8081"
else
    echo "❌ اپلیکیشن راه‌اندازی نشد!"
    echo "📋 لاگ‌های container:"
    docker logs asiasalman_test
fi

# پاک کردن container تست
echo "🧹 پاک کردن container تست..."
docker stop asiasalman_test 2>/dev/null || true
docker rm asiasalman_test 2>/dev/null || true

echo "✅ تست کامل شد!"
