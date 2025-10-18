#!/bin/bash

# ========================================
# اسکریپت کپی فایل‌ها به سرور لینوکس
# ========================================

SERVER_IP="192.168.1.4"
SERVER_PORT="2222"
SERVER_USER="root"
SERVER_PATH="/root/application"

echo "🚀 شروع کپی فایل‌ها به سرور..."

# کپی فایل‌های اصلی
echo "📁 کپی فایل‌های پروژه..."
scp -P $SERVER_PORT -r . $SERVER_USER@$SERVER_IP:$SERVER_PATH/

# کپی اسکریپت راه‌اندازی
echo "📄 کپی اسکریپت راه‌اندازی..."
scp -P $SERVER_PORT setup_server.sh $SERVER_USER@$SERVER_IP:/root/

# کپی آموزش‌ها
echo "📚 کپی فایل‌های آموزش..."
scp -P $SERVER_PORT آموزش_راه_اندازی_سرور_لینوکس.md $SERVER_USER@$SERVER_IP:/root/
scp -P $SERVER_PORT README_سرور_لینوکس.md $SERVER_USER@$SERVER_IP:/root/

echo "✅ کپی فایل‌ها کامل شد!"

echo ""
echo "🔧 برای راه‌اندازی در سرور، دستورات زیر را اجرا کنید:"
echo ""
echo "ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP"
echo "cd $SERVER_PATH"
echo "chmod +x /root/setup_server.sh"
echo "./setup_server.sh"
echo ""
echo "🌐 پس از راه‌اندازی، اپلیکیشن در آدرس زیر در دسترس خواهد بود:"
echo "http://$SERVER_IP:8081"
