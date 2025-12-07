# 📥 راهنمای دانلود و نصب فونت Vazir

## 🔗 لینک دانلود

**GitHub Releases:**
https://github.com/rastikerdar/vazir-font/releases

**مستقیم:**
- آخرین نسخه: v30.1.0 یا بالاتر

## 📋 مراحل نصب

### 1. دانلود فونت

از لینک بالا آخرین نسخه را دانلود کنید.

### 2. استخراج فایل‌ها

از فایل ZIP دانلود شده، فایل‌های `.ttf` را از پوشه `dist` استخراج کنید:
- `Vazir-Regular.ttf`
- `Vazir-Medium.ttf`
- `Vazir-Bold.ttf`
- `Vazir-Light.ttf` (اختیاری)
- `Vazir-Thin.ttf` (اختیاری)

### 3. ایجاد پوشه font

در پروژه Android:
```
app/src/main/res/font/
```

اگر این پوشه وجود ندارد، آن را ایجاد کنید.

### 4. تغییر نام فایل‌ها

نام فایل‌ها باید به صورت **lowercase** و با **underline** باشند:

- `Vazir-Regular.ttf` → `vazir_regular.ttf`
- `Vazir-Medium.ttf` → `vazir_medium.ttf`
- `Vazir-Bold.ttf` → `vazir_bold.ttf`
- `Vazir-Light.ttf` → `vazir_light.ttf`
- `Vazir-Thin.ttf` → `vazir_thin.ttf`

### 5. قرار دادن در پروژه

فایل‌های تغییر نام یافته را در پوشه `app/src/main/res/font/` قرار دهید.

### 6. فعال‌سازی در کد

بعد از قرار دادن فایل‌ها، فایل `FontFamily.kt` را ویرایش کنید:

```kotlin
val VazirFontFamily = FontFamily(
    Font(R.font.vazir_thin, FontWeight.Thin),
    Font(R.font.vazir_light, FontWeight.Light),
    Font(R.font.vazir_regular, FontWeight.Normal),
    Font(R.font.vazir_medium, FontWeight.Medium),
    Font(R.font.vazir_bold, FontWeight.Bold)
)

val AppFontFamily = VazirFontFamily
```

## ✅ چک لیست

- [ ] فونت را از GitHub دانلود کردم
- [ ] فایل‌های TTF را استخراج کردم
- [ ] پوشه `res/font/` را ایجاد کردم
- [ ] نام فایل‌ها را به lowercase تغییر دادم
- [ ] فایل‌ها را در پوشه قرار دادم
- [ ] `FontFamily.kt` را به‌روزرسانی کردم
- [ ] پروژه را build کردم
- [ ] فونت را در اپلیکیشن تست کردم

## 📝 ساختار نهایی

```
app/src/main/res/font/
├── vazir_regular.ttf
├── vazir_medium.ttf
├── vazir_bold.ttf
├── vazir_light.ttf (اختیاری)
└── vazir_thin.ttf (اختیاری)
```

---

**نکته**: تا زمانی که فایل‌های فونت اضافه نشوند، از فونت پیش‌فرض سیستم استفاده می‌شود.

