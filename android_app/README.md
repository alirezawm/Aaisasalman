# Asia Salman Auto Parts - Android Application

## 📱 نرم‌افزار اندروید قطعات خودرو آسیا سلمان

این پروژه شامل نرم‌افزار اندروید کامل برای سایت قطعات خودرو آسیا سلمان است.

## 🚀 ویژگی‌ها

- ✅ طراحی مدرن با Material Design 3
- ✅ انیمیشن‌های جذاب
- ✅ سازگار با تمام نسخه‌های اندروید (5.0+)
- ✅ پشتیبانی کامل از RTL
- ✅ حالت آفلاین
- ✅ موتور جستجوی حرفه‌ای
- ✅ سبد خرید با تفکیک نقدی/چکی
- ✅ پروفایل کامل کاربر
- ✅ درخواست خریدار عمده
- ✅ اعلان‌های Push

## 📋 پیش‌نیازها

- Android Studio Hedgehog | 2023.1.1 یا بالاتر
- JDK 17
- Android SDK 34
- Gradle 8.1+

## 🔧 نصب و راه‌اندازی

1. پروژه را در Android Studio باز کنید
2. فایل `app/build.gradle` را باز کرده و `API_BASE_URL` را به آدرس سرور خود تغییر دهید:
   ```gradle
   buildConfigField "String", "API_BASE_URL", '"https://your-domain.com/api/mobile/v1"'
   ```
3. Sync Project with Gradle Files
4. Run the app

## 📁 ساختار پروژه

```
app/src/main/java/com/asiasalman/autoparts/
├── data/
│   ├── model/          # Data models
│   ├── remote/         # API service
│   ├── local/          # Room database
│   └── repository/     # Repositories
├── ui/
│   ├── splash/         # Splash screen
│   ├── auth/           # Authentication
│   ├── main/           # Main activity
│   ├── home/           # Home screen
│   ├── shop/           # Shop screen
│   ├── cart/           # Cart screen
│   └── profile/        # Profile screen
├── di/                 # Dependency Injection
└── util/               # Utilities
```

## 🔌 API Endpoints

تمام API endpoints در فایل `ApiService.kt` تعریف شده‌اند و با سرور شما ارتباط برقرار می‌کنند.

## 📝 TODO

- [ ] تکمیل UI برای تمام صفحات
- [ ] اضافه کردن Room Database برای cache
- [ ] پیاده‌سازی Push Notifications
- [ ] اضافه کردن Unit Tests
- [ ] بهینه‌سازی تصاویر
- [ ] اضافه کردن Analytics

## 📄 License

Copyright © 2024 Asia Salman Auto Parts

