package com.asiasalman.mobile.ui.theme

import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import com.asiasalman.mobile.R

/**
 * فونت‌های فارسی برای اپلیکیشن
 * استفاده از فونت Vazirmatn برای هماهنگی با وب‌سایت
 */

// فونت Vazirmatn با وزن‌های موجود
// Android به صورت خودکار نام فایل‌ها را normalize می‌کند: Vazirmatn-Bold.ttf → vazirmatn_bold
val VazirmatnFontFamily = FontFamily(
    Font(R.font.vazirmatn_regular, FontWeight.Normal),
    Font(R.font.vazirmatn_medium, FontWeight.Medium),
    Font(R.font.vazirmatn_bold, FontWeight.Bold)
)

// برای استفاده در Typography
val AppFontFamily = VazirmatnFontFamily

