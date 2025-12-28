# 🔨 راهنمای ساخت APK

## روش 1: استفاده از Gradle Wrapper (پیشنهادی)

### در Windows:
```bash
cd android_app
gradlew.bat assembleDebug
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

## روش 2: ساخت APK Release

### در Windows:
```bash
gradlew.bat assembleRelease
```

### در Linux/Mac:
```bash
./gradlew assembleRelease
```

### خروجی:
APK در مسیر زیر ساخته می‌شود:
```
app/build/outputs/apk/release/app-release.apk
```

**نکته**: برای Release APK نیاز به keystore دارید. برای تست می‌توانید از Debug APK استفاده کنید.

## روش 3: استفاده از Android Studio

1. پروژه را در Android Studio باز کنید
2. `Build > Build Bundle(s) / APK(s) > Build APK(s)`
3. منتظر بمانید تا build کامل شود
4. APK در مسیر `app/build/outputs/apk/debug/` قرار می‌گیرد

## روش 4: ساخت APK Bundle (برای Google Play)

```bash
# Windows
gradlew.bat bundleRelease

# Linux/Mac
./gradlew bundleRelease
```

## 🔧 تنظیمات قبل از Build

### 1. بررسی Java
```bash
java -version
```
باید Java 17 یا بالاتر نصب باشد.

### 2. تنظیم JAVA_HOME (در صورت نیاز)
```bash
# Windows
set JAVA_HOME=C:\Program Files\Java\jdk-17

# Linux/Mac
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
```

### 3. تنظیم API_BASE_URL
فایل `app/build.gradle` را باز کنید و `API_BASE_URL` را تنظیم کنید.

## 🐛 رفع مشکلات

### خطای "Gradle wrapper not found"
- مطمئن شوید که فایل `gradlew` یا `gradlew.bat` در root پروژه وجود دارد
- مطمئن شوید که `gradle/wrapper/gradle-wrapper.jar` وجود دارد

### خطای "JAVA_HOME not set"
```bash
# Windows
set JAVA_HOME=C:\Program Files\Java\jdk-17

# Linux/Mac
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
```

### خطای "SDK not found"
- Android SDK را نصب کنید
- `ANDROID_HOME` را تنظیم کنید:
```bash
# Windows
set ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk

# Linux/Mac
export ANDROID_HOME=$HOME/Android/Sdk
```

### خطای Build
```bash
# Clean و Rebuild
gradlew.bat clean
gradlew.bat assembleDebug
```

## 📱 نصب APK روی دستگاه

### روش 1: ADB
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### روش 2: انتقال دستی
1. APK را به دستگاه Android منتقل کنید
2. File Manager را باز کنید
3. روی APK کلیک کنید و نصب کنید
4. در صورت نیاز "Install from Unknown Sources" را فعال کنید

## ✅ چک‌لیست قبل از Build

- [ ] Java 17+ نصب است
- [ ] Android SDK نصب است
- [ ] `gradlew` یا `gradlew.bat` موجود است
- [ ] `gradle-wrapper.jar` موجود است
- [ ] `API_BASE_URL` تنظیم شده است
- [ ] پروژه بدون خطا sync شده است

---

**موفق باشید! 🎉**

