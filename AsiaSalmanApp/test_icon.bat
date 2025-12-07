@echo off
REM اسکریپت تست آیکون اپلیکیشن Asia Salman
REM این اسکریپت آیکون را در مرورگر نمایش می‌دهد

echo ========================================
echo   تست آیکون اپلیکیشن Asia Salman
echo ========================================
echo.

echo [1] باز کردن پیش‌نمایش HTML...
start "" "preview_icon.html"
echo ✓ پیش‌نمایش در مرورگر باز شد
echo.

echo [2] بررسی فایل XML...
if exist "app\src\main\res\drawable\ic_launcher_foreground.xml" (
    echo ✓ فایل ic_launcher_foreground.xml موجود است
) else (
    echo ✗ فایل ic_launcher_foreground.xml یافت نشد!
)

if exist "app\src\main\res\mipmap-anydpi-v26\ic_launcher.xml" (
    echo ✓ فایل ic_launcher.xml موجود است
) else (
    echo ✗ فایل ic_launcher.xml یافت نشد!
)
echo.

echo [3] بررسی رنگ‌ها...
findstr /C:"#D92027" "app\src\main\res\values\colors.xml" >nul
if %errorlevel% equ 0 (
    echo ✓ رنگ primary (#D92027) تنظیم شده است
) else (
    echo ✗ رنگ primary یافت نشد!
)
echo.

echo ========================================
echo   تست کامل شد!
echo ========================================
echo.
echo برای مشاهده آیکون:
echo 1. فایل preview_icon.html در مرورگر باز شده است
echo 2. برای تست روی دستگاه، APK را build کنید:
echo    gradlew assembleDebug
echo.
pause





