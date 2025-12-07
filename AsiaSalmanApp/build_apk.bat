@echo off
echo ==========================================
echo    Asia Salman Android Build Script
echo ==========================================

:: Set Java Home
set JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
set PATH=%JAVA_HOME%\bin;%PATH%

:: Set Android SDK
set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
set PATH=%ANDROID_HOME%\platform-tools;%PATH%

echo.
echo Java Home: %JAVA_HOME%
echo Android SDK: %ANDROID_HOME%
echo.

:: Check if Java exists
java -version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Java not found. Please install JDK 17 or higher.
    pause
    exit /b 1
)

echo.
echo Building Debug APK...
echo.

:: Build using gradlew
call gradlew.bat assembleDebug --no-daemon

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Build failed!
    echo.
    echo Please open the project in Android Studio and try:
    echo   1. Wait for Gradle sync to complete
    echo   2. Go to Build ^> Build Bundle(s) / APK(s) ^> Build APK(s)
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo    Build Successful!
echo ==========================================
echo.
echo APK Location:
echo   app\build\outputs\apk\debug\app-debug.apk
echo.

:: Open the output folder
explorer app\build\outputs\apk\debug\

pause

