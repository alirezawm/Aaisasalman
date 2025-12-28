# راهنمای راه‌اندازی پروژه Android

## مراحل نصب

### 1. نصب Android Studio
- Android Studio Hedgehog | 2023.1.1 یا بالاتر را دانلود و نصب کنید
- JDK 17 را نصب کنید

### 2. باز کردن پروژه
1. Android Studio را باز کنید
2. گزینه "Open" را انتخاب کنید
3. پوشه `android_app` را انتخاب کنید
4. منتظر بمانید تا Gradle sync انجام شود

### 3. تنظیم API Base URL
1. فایل `app/build.gradle` را باز کنید
2. خط زیر را پیدا کنید:
   ```gradle
   buildConfigField "String", "API_BASE_URL", '"https://your-domain.com/api/mobile/v1"'
   ```
3. `your-domain.com` را با آدرس سرور خود جایگزین کنید

### 4. ساخت و اجرا
1. یک دستگاه Android یا Emulator متصل کنید
2. دکمه Run را بزنید یا `Shift + F10` را فشار دهید
3. منتظر بمانید تا اپلیکیشن build و install شود

## ساختار پروژه

پروژه به صورت MVVM طراحی شده است:
- **Model**: Data classes در پوشه `data/model`
- **View**: Activities و Fragments در پوشه `ui`
- **ViewModel**: ViewModels در پوشه `ui`

## نکات مهم

- تمام API calls نیاز به Base URL دارند که باید در `build.gradle` تنظیم شود
- برای استفاده از API، باید JWT token در `TokenManager` ذخیره شود
- پروژه از Hilt برای Dependency Injection استفاده می‌کند

## مشکلات رایج

### خطای Gradle Sync
- File > Invalidate Caches / Restart را اجرا کنید
- Build > Clean Project را اجرا کنید
- دوباره Build > Rebuild Project را اجرا کنید

### خطای API Connection
- مطمئن شوید که `API_BASE_URL` درست تنظیم شده است
- بررسی کنید که سرور در دسترس است
- برای HTTP (نه HTTPS) باید `usesCleartextTraffic="true"` در Manifest باشد

