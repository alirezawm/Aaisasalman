# 🗑️ راهنمای حذف کامل نرم‌افزار اندروید

این راهنما نحوه حذف کامل تمام فایل‌ها، پوشه‌ها و مستندات مربوط به اپلیکیشن اندروید از پروژه را توضیح می‌دهد.

## ⚠️ هشدار مهم

**این عمل غیرقابل بازگشت است!** قبل از اجرا حتماً:
- یک backup کامل از پروژه تهیه کنید
- مطمئن شوید که دیگر به اپلیکیشن اندروید نیاز ندارید
- تمام تغییرات را commit کنید

## 📋 فایل‌های مرتبط

### پوشه‌ها
- `android-app/` - پوشه اصلی اپلیکیشن اندروید

### فایل‌های مستندات
- `ANDROID_APP_MEGAPROMPT_README.md`
- `MEGAPROMPT_ANDROID_APP.json`
- `MEGAPROMPT_CLEANUP_ANDROID_AND_EXTRAS.json`

### فایل‌های اسکریپت
- `cleanup_android_and_extras.py`

## 🚀 روش استفاده

### روش 1: استفاده از اسکریپت Python (توصیه می‌شود)

#### Windows:
```bash
python delete_android_app.py
```

#### Linux/Mac:
```bash
python3 delete_android_app.py
```

#### حالت Dry Run (بدون حذف واقعی):
```bash
python delete_android_app.py --dry-run
```

### روش 2: حذف دستی

#### Windows (PowerShell):
```powershell
# حذف پوشه اصلی
Remove-Item -Recurse -Force android-app

# حذف فایل‌های مستندات
Remove-Item ANDROID_APP_MEGAPROMPT_README.md
Remove-Item MEGAPROMPT_ANDROID_APP.json
Remove-Item MEGAPROMPT_CLEANUP_ANDROID_AND_EXTRAS.json
Remove-Item cleanup_android_and_extras.py
```

#### Linux/Mac:
```bash
# حذف پوشه اصلی
rm -rf android-app/

# حذف فایل‌های مستندات
rm -f ANDROID_APP_MEGAPROMPT_README.md
rm -f MEGAPROMPT_ANDROID_APP.json
rm -f MEGAPROMPT_CLEANUP_ANDROID_AND_EXTRAS.json
rm -f cleanup_android_and_extras.py
```

## ✅ بررسی نهایی

پس از حذف، بررسی کنید که:

1. پوشه `android-app/` وجود ندارد
2. هیچ فایل `.kt` در پروژه نیست
3. هیچ فایل `.gradle*` در پروژه نیست
4. هیچ فایل `.apk` یا `.aab` در پروژه نیست

### دستورات بررسی:

#### Windows (PowerShell):
```powershell
# بررسی وجود پوشه
Test-Path android-app

# جستجوی فایل‌های .kt
Get-ChildItem -Recurse -Filter "*.kt" | Where-Object { $_.FullName -notmatch "venv|\.git" }

# جستجوی فایل‌های .gradle*
Get-ChildItem -Recurse -Filter "*.gradle*" | Where-Object { $_.FullName -notmatch "venv|\.git" }
```

#### Linux/Mac:
```bash
# بررسی وجود پوشه
test -d android-app && echo "وجود دارد" || echo "حذف شده"

# جستجوی فایل‌های .kt
find . -name "*.kt" -not -path "./venv/*" -not -path "./.git/*"

# جستجوی فایل‌های .gradle*
find . -name "*.gradle*" -not -path "./venv/*" -not -path "./.git/*"
```

## 📝 موارد اضافی برای بررسی

پس از حذف فایل‌های اندروید، ممکن است نیاز باشد:

1. **بررسی فایل `.gitignore`**: اگر قوانین مربوط به اندروید اضافه شده، حذف کنید
2. **بررسی فایل `README.md`**: اگر بخشی درباره اندروید وجود دارد، حذف کنید
3. **بررسی فایل `requirements.txt`**: اگر وابستگی‌های اندروید وجود دارد، حذف کنید
4. **بررسی فایل `docker-compose.yaml`**: اگر سرویس‌های اندروید وجود دارد، حذف کنید
5. **بررسی فایل‌های Python**: اگر import یا کدهای مرتبط با اندروید وجود دارد، حذف کنید

## 🔍 جستجوی ارجاعات به اندروید

برای اطمینان از حذف کامل، می‌توانید در فایل‌های متنی جستجو کنید:

### Windows (PowerShell):
```powershell
# جستجوی "android" در فایل‌های متنی
Select-String -Path "*.py","*.md","*.txt","*.json","*.yaml" -Pattern "android" -CaseSensitive:$false | Where-Object { $_.Path -notmatch "venv|\.git" }
```

### Linux/Mac:
```bash
# جستجوی "android" در فایل‌های متنی
grep -r -i "android" --include="*.py" --include="*.md" --include="*.txt" --include="*.json" --include="*.yaml" . | grep -v "venv" | grep -v ".git"
```

## 📊 خلاصه

این مگاپرامپت شامل:

- ✅ فایل JSON با جزئیات کامل (`MEGAPROMPT_DELETE_ANDROID_APP.json`)
- ✅ اسکریپت Python قابل اجرا (`delete_android_app.py`)
- ✅ راهنمای استفاده (این فایل)

## 🆘 پشتیبانی

اگر مشکلی پیش آمد:

1. بررسی کنید که backup تهیه کرده‌اید
2. بررسی کنید که فایل‌ها به درستی حذف شده‌اند
3. در صورت نیاز، از حالت `--dry-run` استفاده کنید تا ببینید چه فایل‌هایی حذف می‌شوند

## 📌 نکات مهم

- ⚠️ این عمل **غیرقابل بازگشت** است
- ⚠️ حتماً **backup** تهیه کنید
- ⚠️ قبل از اجرا، مطمئن شوید که دیگر به اندروید نیاز ندارید
- ✅ از حالت `--dry-run` برای بررسی استفاده کنید
- ✅ پس از حذف، بررسی نهایی انجام دهید

---

**تاریخ ایجاد**: 2025-01-28  
**نسخه**: 1.0.0


