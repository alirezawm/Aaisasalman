# 📝 مگاپرامپت حرفه‌ای: سیستم فونت فارسی برای اپلیکیشن Android

## 📋 مقدمه

این مگاپرامپت راهنمای کامل پیاده‌سازی سیستم فونت فارسی (Vazir) در اپلیکیشن Android است که با فونت‌های استفاده شده در وب‌سایت هماهنگ باشد.

---

## 🎯 اهداف

1. **هماهنگی با وب‌سایت**: استفاده از فونت Vazir همانند وب‌سایت
2. **بهترین کیفیت**: استفاده از فونت‌های Vector برای کیفیت بالا
3. **پشتیبانی RTL**: پشتیبانی کامل از زبان فارسی و RTL
4. **بهینه‌سازی**: استفاده از فونت‌های بهینه شده برای Android
5. **Material Design 3**: تطابق با سیستم Typography در Material Design 3

---

## 📦 فونت‌های مورد نیاز

### فونت اصلی: Vazir

Vazir یک فونت فارسی منبع‌باز است که برای استفاده در وب و اپلیکیشن‌های موبایل بهینه شده است.

**لینک دانلود:**
- GitHub: https://github.com/rastikerdar/vazir-font
- CDN: https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css

**نسخه‌های مورد نیاز:**
- `Vazir-Regular.ttf` (وزن 400)
- `Vazir-Medium.ttf` (وزن 500)
- `Vazir-Bold.ttf` (وزن 700)
- `Vazir-Light.ttf` (وزن 300) - اختیاری
- `Vazir-Thin.ttf` (وزن 100) - اختیاری

---

## 📁 ساختار فایل‌ها

```
app/src/main/
├── res/
│   └── font/
│       ├── vazir_regular.ttf
│       ├── vazir_medium.ttf
│       ├── vazir_bold.ttf
│       ├── vazir_light.ttf
│       └── vazir_thin.ttf
└── java/com/asiasalman/mobile/
    └── ui/
        └── theme/
            ├── Type.kt (به‌روزرسانی)
            └── FontFamily.kt (جدید)
```

---

## 🔧 پیاده‌سازی

### مرحله 1: دانلود و قرار دادن فایل‌های فونت

1. **دانلود فونت Vazir:**
   - از GitHub: https://github.com/rastikerdar/vazir-font/releases
   - آخرین نسخه را دانلود کنید (v30.1.0 یا بالاتر)

2. **استخراج فایل‌های TTF:**
   - از پوشه `dist` فایل‌های `.ttf` را استخراج کنید
   - نام‌های فایل‌ها باید به صورت زیر باشد:
     - `Vazir-Regular.ttf`
     - `Vazir-Medium.ttf`
     - `Vazir-Bold.ttf`

3. **قرار دادن در پروژه:**
   - پوشه `app/src/main/res/font/` را ایجاد کنید (اگر وجود ندارد)
   - فایل‌های TTF را در این پوشه قرار دهید
   - نام فایل‌ها را به صورت lowercase تغییر دهید:
     - `vazir_regular.ttf`
     - `vazir_medium.ttf`
     - `vazir_bold.ttf`
     - `vazir_light.ttf` (اختیاری)
     - `vazir_thin.ttf` (اختیاری)

### مرحله 2: ایجاد FontFamily

فایل جدید `FontFamily.kt`:

```kotlin
package com.asiasalman.mobile.ui.theme

import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import com.asiasalman.mobile.R

val VazirFontFamily = FontFamily(
    Font(R.font.vazir_thin, FontWeight.Thin),
    Font(R.font.vazir_light, FontWeight.Light),
    Font(R.font.vazir_regular, FontWeight.Normal),
    Font(R.font.vazir_medium, FontWeight.Medium),
    Font(R.font.vazir_bold, FontWeight.Bold)
)

// Fallback font family (برای نسخه‌های قدیمی Android)
val PersianFontFamily = FontFamily(
    Font(R.font.vazir_regular, FontWeight.Normal),
    Font(R.font.vazir_medium, FontWeight.Medium),
    Font(R.font.vazir_bold, FontWeight.Bold)
)
```

### مرحله 3: به‌روزرسانی Typography

فایل `Type.kt` را به‌روزرسانی کنید:

```kotlin
package com.asiasalman.mobile.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val Typography = Typography(
    displayLarge = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 40.sp,
        letterSpacing = 0.sp
    ),
    displayMedium = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 36.sp,
        letterSpacing = 0.sp
    ),
    headlineLarge = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 24.sp,
        lineHeight = 32.sp,
        letterSpacing = 0.sp
    ),
    headlineMedium = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.sp
    ),
    headlineSmall = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.sp
    ),
    titleLarge = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 18.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.sp
    ),
    titleMedium = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 22.sp,
        letterSpacing = 0.15.sp
    ),
    titleSmall = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.25.sp
    ),
    bodySmall = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.4.sp
    ),
    labelLarge = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),
    labelMedium = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp
    ),
    labelSmall = TextStyle(
        fontFamily = VazirFontFamily,
        fontWeight = FontWeight.Medium,
        fontSize = 10.sp,
        lineHeight = 14.sp,
        letterSpacing = 0.5.sp
    )
)
```

---

## 📐 اندازه‌های فونت

### مقایسه با وب‌سایت

| نوع | وب‌سایت (CSS) | Android (sp) | استفاده |
|-----|---------------|--------------|---------|
| H1 | 1.5rem (24px) | 24sp | عنوان اصلی |
| H2 | 1.25rem (20px) | 20sp | عنوان فرعی |
| H3 | 1.125rem (18px) | 18sp | عنوان کوچک |
| Body | 1rem (16px) | 16sp | متن اصلی |
| Small | 0.875rem (14px) | 14sp | متن فرعی |
| Caption | 0.75rem (12px) | 12sp | توضیحات |

### Material Design 3 Typography Scale

- **Display Large**: 32sp - برای عناوین بزرگ
- **Display Medium**: 28sp - برای عناوین متوسط
- **Headline Large**: 24sp - برای سرتیترها
- **Headline Medium**: 20sp - برای عنوان بخش‌ها
- **Title Large**: 18sp - برای عنوان کارت‌ها
- **Body Large**: 16sp - برای متن اصلی
- **Body Medium**: 14sp - برای متن ثانویه
- **Label Medium**: 12sp - برای برچسب‌ها

---

## 🎨 استراتژی فونت

### 1. فونت پیش‌فرض

استفاده از `VazirFontFamily` برای همه متن‌های فارسی.

### 2. Fallback Font

در صورت عدم دسترسی به فونت Vazir، از فونت سیستم Android استفاده می‌شود:
- Samsung: SamsungOne (پشتیبانی از فارسی)
- Xiaomi: MIUI (پشتیبانی از فارسی)
- Stock Android: Roboto (پشتیبانی محدود)

### 3. بهینه‌سازی

- استفاده از فونت‌های TTF بهینه شده
- کاهش حجم فایل با استفاده از subset font
- استفاده از فونت‌های variable font (در صورت امکان)

---

## 🔄 تطابق با وب‌سایت

### CSS در وب‌سایت:

```css
body {
    font-family: 'Vazir', 'Tahoma', 'Arial', sans-serif;
    font-size: 1rem; /* 16px */
    line-height: 1.6;
}

.navbar-brand {
    font-size: 1.5rem; /* 24px */
    font-weight: bold; /* 700 */
}

.btn-primary {
    font-weight: 600; /* 500-600 */
}
```

### معادل Android:

```kotlin
// Body text
MaterialTheme.typography.bodyLarge // 16sp, Normal (400)

// Navbar brand
MaterialTheme.typography.headlineLarge // 24sp, Bold (700)

// Button text
MaterialTheme.typography.titleMedium // 16sp, Medium (500)
```

---

## 📊 وزن‌های فونت

| وزن | FontWeight | نام فایل | استفاده |
|-----|------------|----------|---------|
| 100 | Thin | vazir_thin.ttf | عناوین سبک |
| 300 | Light | vazir_light.ttf | متن‌های سبک |
| 400 | Normal | vazir_regular.ttf | متن اصلی |
| 500 | Medium | vazir_medium.ttf | دکمه‌ها، برچسب‌ها |
| 700 | Bold | vazir_bold.ttf | عناوین |

---

## 🔍 نکات مهم

### 1. RTL Support

فونت Vazir به صورت کامل از RTL پشتیبانی می‌کند و با تنظیمات RTL در `MainActivity` و `AsiaSalmanNavHost` کار می‌کند.

### 2. Letter Spacing

برای بهبود خوانایی در فارسی، letter spacing باید 0 یا منفی باشد:

```kotlin
letterSpacing = 0.sp  // برای عناوین
letterSpacing = 0.25.sp  // برای متن‌های کوچک
```

### 3. Line Height

برای متن فارسی، line height باید بیشتر باشد:

```kotlin
lineHeight = fontSize * 1.5  // برای متن اصلی
lineHeight = fontSize * 1.25  // برای عناوین
```

### 4. Font Loading

فونت‌ها به صورت lazy load می‌شوند و در اولین استفاده cache می‌شوند.

---

## 🚀 بهینه‌سازی‌ها

### 1. Subset Font

برای کاهش حجم، فقط کاراکترهای فارسی را نگه دارید:
- استفاده از ابزار fonttools
- یا استفاده از سرویس Google Fonts

### 2. Variable Font

اگر نسخه variable font موجود باشد، استفاده کنید:
- یک فایل به جای چند فایل
- وزن‌های متغیر
- حجم کمتر

### 3. Web Font Loading

برای بهینه‌سازی بیشتر، می‌توانید فونت را از CDN بارگذاری کنید (توصیه نمی‌شود برای اپلیکیشن).

---

## ✅ چک لیست پیاده‌سازی

- [ ] دانلود فونت Vazir از GitHub
- [ ] استخراج فایل‌های TTF
- [ ] ایجاد پوشه `res/font/`
- [ ] قرار دادن فایل‌های فونت در پوشه
- [ ] تغییر نام فایل‌ها به lowercase
- [ ] ایجاد فایل `FontFamily.kt`
- [ ] به‌روزرسانی `Type.kt`
- [ ] تست فونت در صفحه ورود
- [ ] تست فونت در تمام صفحات
- [ ] بررسی RTL support
- [ ] تست در اندازه‌های مختلف
- [ ] تست در dark mode

---

## 📞 منابع

- **Vazir Font**: https://github.com/rastikerdar/vazir-font
- **Material Design Typography**: https://m3.material.io/styles/typography/overview
- **Android Fonts**: https://developer.android.com/guide/topics/ui/look-and-feel/fonts-in-xml

---

## 💡 توصیه‌های نهایی

1. **همیشه از فونت Vazir استفاده کنید** برای هماهنگی با وب‌سایت
2. **تست کنید** در اندازه‌های مختلف صفحه
3. **بهینه‌سازی کنید** حجم فایل فونت را کاهش دهید
4. **Fallback** برای فونت سیستم در نظر بگیرید

---

**نکته مهم**: این مگاپرامپت شامل تمام جزئیات فنی برای پیاده‌سازی کامل سیستم فونت فارسی در اپلیکیشن Android است.

