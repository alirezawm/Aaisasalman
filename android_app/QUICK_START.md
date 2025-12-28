# 🚀 راهنمای سریع شروع - نرم‌افزار اندروید آسیا سلمان

## ⚡ شروع سریع (5 دقیقه)

### 1. باز کردن پروژه
```bash
# در Android Studio:
File > Open > android_app
```

### 2. تنظیم API URL
فایل `app/build.gradle` را باز کنید و خط 25 را پیدا کنید:
```gradle
buildConfigField "String", "API_BASE_URL", '"https://your-domain.com/api/mobile/v1"'
```
آدرس سرور خود را جایگزین کنید.

### 3. Sync و Run
- `File > Sync Project with Gradle Files`
- یک دستگاه یا Emulator متصل کنید
- دکمه Run را بزنید

## 📋 چک‌لیست قبل از Build

- [ ] Android Studio Hedgehog یا بالاتر نصب است
- [ ] JDK 17 نصب است
- [ ] Android SDK 34 نصب است
- [ ] API_BASE_URL تنظیم شده است
- [ ] یک دستگاه Android یا Emulator آماده است

## 🔍 تست اولیه

1. **Splash Screen**: باید نمایش داده شود و بعد از 2 ثانیه به Login برود
2. **Login**: شماره تلفن وارد کنید و OTP را دریافت کنید
3. **OTP Verification**: کد را وارد کنید
4. **Main Screen**: باید با Bottom Navigation نمایش داده شود

## 🐛 رفع مشکلات رایج

### خطای "Cannot resolve symbol"
- `File > Invalidate Caches / Restart`
- `Build > Clean Project`
- `Build > Rebuild Project`

### خطای API Connection
- بررسی کنید که `API_BASE_URL` درست است
- برای HTTP (نه HTTPS) باید `usesCleartextTraffic="true"` در Manifest باشد
- بررسی کنید که سرور در دسترس است

### خطای Gradle Sync
- `File > Settings > Build > Gradle`
- Gradle JDK را روی JDK 17 تنظیم کنید

## 📱 تست روی دستگاه واقعی

1. Settings > Developer Options را فعال کنید
2. USB Debugging را فعال کنید
3. دستگاه را با USB متصل کنید
4. در Android Studio دستگاه را انتخاب کنید
5. Run کنید

## 🎯 مراحل بعدی

پس از اینکه اپلیکیشن اجرا شد:
1. UI components را تکمیل کنید (Adapters, Detail pages)
2. Room Database را اضافه کنید
3. Push Notifications را پیاده‌سازی کنید
4. تست کنید و باگ‌ها را رفع کنید

---

**موفق باشید! 🎉**

