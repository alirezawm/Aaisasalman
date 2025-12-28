# ✅ Gradle Wrapper اضافه شد!

## 📦 فایل‌های اضافه شده

- ✅ `gradlew` - Script برای Linux/Mac
- ✅ `gradlew.bat` - Script برای Windows
- ✅ `gradle/wrapper/gradle-wrapper.jar` - JAR فایل Gradle Wrapper
- ✅ `gradle/wrapper/gradle-wrapper.properties` - تنظیمات Wrapper

## 🚀 ساخت APK

### در Windows (PowerShell یا CMD):
```bash
cd android_app
.\gradlew.bat assembleDebug
```

### در Linux/Mac:
```bash
cd android_app
chmod +x gradlew
./gradlew assembleDebug
```

### خروجی:
APK در مسیر زیر ساخته می‌شود:
```
app/build/outputs/apk/debug/app-debug.apk
```

## 📱 نصب APK

### روش 1: با ADB
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### روش 2: انتقال دستی
1. فایل `app-debug.apk` را به دستگاه Android منتقل کنید
2. File Manager را باز کنید
3. روی APK کلیک کنید و نصب کنید

## 🔧 دستورات مفید

### Clean Project:
```bash
# Windows
.\gradlew.bat clean

# Linux/Mac
./gradlew clean
```

### Build و Install:
```bash
# Windows
.\gradlew.bat installDebug

# Linux/Mac
./gradlew installDebug
```

### Build Release:
```bash
# Windows
.\gradlew.bat assembleRelease

# Linux/Mac
./gradlew assembleRelease
```

### مشاهده Tasks:
```bash
# Windows
.\gradlew.bat tasks

# Linux/Mac
./gradlew tasks
```

## ✅ چک‌لیست

- [x] `gradlew` / `gradlew.bat` موجود است
- [x] `gradle-wrapper.jar` دانلود شده
- [x] `gradle-wrapper.properties` تنظیم شده
- [ ] Java 17+ نصب است
- [ ] Android SDK نصب است

## 🐛 رفع مشکلات

### اگر خطای "Permission denied" گرفتید (Linux/Mac):
```bash
chmod +x gradlew
```

### اگر خطای Java گرفتید:
```bash
# بررسی Java
java -version

# باید Java 17 یا بالاتر باشد
```

### اگر خطای SDK گرفتید:
- Android SDK را نصب کنید
- `ANDROID_HOME` را تنظیم کنید

## 📖 راهنمای کامل

برای راهنمای کامل ساخت APK، فایل `BUILD_APK.md` را مطالعه کنید.

---

**حالا می‌توانید APK بسازید! 🎉**

