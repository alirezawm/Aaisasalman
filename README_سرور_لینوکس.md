# 🚀 راهنمای سریع راه‌اندازی پروژه آسیا سلمان در سرور لینوکس

## 📋 مشخصات سرور
- **IP**: 192.168.1.4
- **پورت**: 8081
- **مسیر**: `/root/application/`
- **Git**: https://git.agarvand.ir/Alirezawm/asiasalman.git
- **SSH**: پورت 2222

## ⚡ راه‌اندازی خودکار (توصیه شده)

### 1. اتصال به سرور
```bash
ssh -p 2222 root@192.168.1.4
```

### 2. دانلود و اجرای اسکریپت
```bash
# دانلود اسکریپت
wget https://raw.githubusercontent.com/your-repo/setup_server.sh -O setup_server.sh

# یا کپی کردن محتویات فایل setup_server.sh و ایجاد آن در سرور
nano setup_server.sh
# محتویات فایل را کپی کنید

# قابل اجرا کردن
chmod +x setup_server.sh

# اجرای اسکریپت
./setup_server.sh
```

## 🔧 راه‌اندازی دستی

اگر می‌خواهید مرحله به مرحله راه‌اندازی کنید، فایل `آموزش_راه_اندازی_سرور_لینوکس.md` را مطالعه کنید.

## 📊 دستورات مدیریت

پس از راه‌اندازی، از دستورات زیر استفاده کنید:

```bash
# بررسی وضعیت
/root/manage.sh status

# راه‌اندازی
/root/manage.sh start

# توقف
/root/manage.sh stop

# راه‌اندازی مجدد
/root/manage.sh restart

# مشاهده لاگ‌ها
/root/manage.sh logs

# به‌روزرسانی
/root/manage.sh update

# پشتیبان‌گیری
/root/manage.sh backup

# پاک‌سازی
/root/manage.sh clean

# مانیتورینگ
/root/monitor.sh
```

## 🌐 دسترسی به اپلیکیشن

- **صفحه اصلی**: http://192.168.1.4:8081
- **پنل مدیریت**: http://192.168.1.4:8081/admin
- **بررسی سلامت**: http://192.168.1.4:8081/health

## ⚠️ نکات مهم

1. **پاک‌سازی کامل**: این اسکریپت تمام سایت‌های قبلی را پاک می‌کند
2. **فایروال**: فقط پورت‌های 2222 (SSH) و 8081 (اپلیکیشن) باز می‌مانند
3. **پشتیبان‌گیری**: پشتیبان‌گیری خودکار روزانه تنظیم شده است
4. **امنیت**: حتماً SECRET_KEY را در فایل `.env` تغییر دهید

## 🔍 عیب‌یابی

```bash
# بررسی وضعیت کلی
/root/manage.sh status

# بررسی لاگ‌ها
/root/manage.sh logs

# بررسی منابع سیستم
/root/monitor.sh

# راه‌اندازی مجدد
/root/manage.sh restart
```

## 📞 پشتیبانی

در صورت بروز مشکل:
1. ابتدا `/root/manage.sh status` را اجرا کنید
2. لاگ‌ها را با `/root/manage.sh logs` بررسی کنید
3. در صورت نیاز `/root/manage.sh restart` را اجرا کنید

---

**🎉 اپلیکیشن آسیا سلمان آماده استفاده است!**
