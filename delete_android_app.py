#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مگاپرامپت حذف کامل نرم‌افزار اندروید - آسیا سلمان

این اسکریپت تمام فایل‌ها، پوشه‌ها، مستندات و ارجاعات مربوط به 
اپلیکیشن اندروید را به طور کامل از پروژه حذف می‌کند.

⚠️ هشدار: این عمل غیرقابل بازگشت است!
"""

import os
import shutil
import glob
from pathlib import Path
from typing import List, Tuple

# رنگ‌های ترمینال
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """چاپ هدر با استایل"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")

def print_success(text: str):
    """چاپ پیام موفقیت"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """چاپ پیام خطا"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    """چاپ هشدار"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    """چاپ اطلاعات"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

# پوشه‌های مرتبط با اندروید
ANDROID_DIRS = [
    'android-app',
]

# فایل‌های مستندات و پیکربندی
ANDROID_FILES = [
    'ANDROID_APP_MEGAPROMPT_README.md',
    'MEGAPROMPT_ANDROID_APP.json',
    'MEGAPROMPT_CLEANUP_ANDROID_AND_EXTRAS.json',
    'cleanup_android_and_extras.py',
]

# الگوهای فایل برای جستجو
ANDROID_PATTERNS = [
    '**/*.apk',
    '**/*.aab',
    '**/*.keystore',
    '**/*.jks',
    '**/*.kt',
    '**/*.gradle.kts',
    '**/AndroidManifest.xml',
    '**/gradlew',
    '**/gradlew.bat',
    '**/gradle-wrapper.jar',
    '**/gradle-wrapper.properties',
]

# پوشه‌هایی که باید نادیده گرفته شوند
IGNORE_DIRS = ['venv', '.git', '__pycache__', '.pytest_cache', 'node_modules']

def should_ignore(path: str) -> bool:
    """بررسی اینکه آیا مسیر باید نادیده گرفته شود"""
    path_str = str(path).replace('\\', '/')
    return any(ignore_dir in path_str for ignore_dir in IGNORE_DIRS)

def delete_directory(dir_path: str) -> Tuple[bool, str]:
    """حذف یک پوشه"""
    if not os.path.exists(dir_path):
        return False, "پوشه وجود ندارد"
    
    try:
        shutil.rmtree(dir_path)
        return True, f"پوشه {dir_path}/ حذف شد"
    except Exception as e:
        return False, f"خطا در حذف {dir_path}: {e}"

def delete_file(file_path: str) -> Tuple[bool, str]:
    """حذف یک فایل"""
    if not os.path.exists(file_path):
        return False, "فایل وجود ندارد"
    
    try:
        os.remove(file_path)
        return True, f"فایل {file_path} حذف شد"
    except Exception as e:
        return False, f"خطا در حذف {file_path}: {e}"

def find_files_by_patterns(patterns: List[str]) -> List[str]:
    """جستجوی فایل‌ها بر اساس الگوها"""
    found_files = []
    
    for pattern in patterns:
        for file_path in glob.glob(pattern, recursive=True):
            if should_ignore(file_path):
                continue
            
            if os.path.isfile(file_path):
                found_files.append(file_path)
    
    return found_files

def verify_deletion() -> Tuple[bool, List[str]]:
    """بررسی نهایی حذف"""
    issues = []
    
    # بررسی پوشه android-app
    if os.path.exists('android-app'):
        issues.append("❌ پوشه android-app/ هنوز وجود دارد!")
    
    # بررسی فایل‌های .kt
    kt_files = find_files_by_patterns(['**/*.kt'])
    if kt_files:
        issues.append(f"⚠ {len(kt_files)} فایل .kt یافت شد (اولین 5 مورد):")
        for f in kt_files[:5]:
            issues.append(f"  - {f}")
    
    # بررسی فایل‌های .gradle*
    gradle_files = find_files_by_patterns(['**/*.gradle*'])
    if gradle_files:
        issues.append(f"⚠ {len(gradle_files)} فایل .gradle* یافت شد (اولین 5 مورد):")
        for f in gradle_files[:5]:
            issues.append(f"  - {f}")
    
    # بررسی فایل‌های APK
    apk_files = find_files_by_patterns(['**/*.apk', '**/*.aab'])
    if apk_files:
        issues.append(f"⚠ {len(apk_files)} فایل APK/AAB یافت شد:")
        for f in apk_files:
            issues.append(f"  - {f}")
    
    return len(issues) == 0, issues

def delete_android_app(dry_run: bool = False) -> bool:
    """حذف کامل نرم‌افزار اندروید"""
    print_header("حذف کامل نرم‌افزار اندروید - آسیا سلمان")
    
    if dry_run:
        print_warning("حالت DRY RUN فعال است - هیچ فایلی حذف نمی‌شود")
        print()
    
    deleted_count = 0
    errors = []
    
    # حذف پوشه‌ها
    print_info("در حال حذف پوشه‌ها...")
    for dir_path in ANDROID_DIRS:
        if os.path.exists(dir_path):
            if dry_run:
                print_warning(f"[DRY RUN] پوشه {dir_path}/ حذف می‌شود")
            else:
                success, message = delete_directory(dir_path)
                if success:
                    print_success(message)
                    deleted_count += 1
                else:
                    print_error(message)
                    errors.append(message)
        else:
            print_warning(f"پوشه {dir_path}/ یافت نشد")
    
    # حذف فایل‌ها
    print()
    print_info("در حال حذف فایل‌ها...")
    for file_path in ANDROID_FILES:
        if os.path.exists(file_path):
            if dry_run:
                print_warning(f"[DRY RUN] فایل {file_path} حذف می‌شود")
            else:
                success, message = delete_file(file_path)
                if success:
                    print_success(message)
                    deleted_count += 1
                else:
                    print_error(message)
                    errors.append(message)
    
    # جستجو و حذف فایل‌های با الگوهای خاص
    print()
    print_info("در حال جستجوی فایل‌های مرتبط...")
    found_files = find_files_by_patterns(ANDROID_PATTERNS)
    
    if found_files:
        print_info(f"{len(found_files)} فایل مرتبط یافت شد")
        for file_path in found_files:
            if dry_run:
                print_warning(f"[DRY RUN] فایل {file_path} حذف می‌شود")
            else:
                success, message = delete_file(file_path)
                if success:
                    print_success(message)
                    deleted_count += 1
                else:
                    print_error(message)
                    errors.append(message)
    else:
        print_success("هیچ فایل مرتبط دیگری یافت نشد")
    
    # بررسی نهایی
    print()
    print_header("بررسی نهایی")
    
    if not dry_run:
        success, issues = verify_deletion()
        
        if success:
            print_success("همه فایل‌های اندروید با موفقیت حذف شدند!")
        else:
            print_error("برخی فایل‌ها هنوز وجود دارند:")
            for issue in issues:
                print_warning(issue)
        
        # خلاصه
        print()
        print_header("خلاصه")
        print_info(f"تعداد موارد حذف شده: {deleted_count}")
        if errors:
            print_error(f"تعداد خطاها: {len(errors)}")
            for error in errors:
                print_error(f"  - {error}")
        
        return success
    else:
        print_info("در حالت DRY RUN، بررسی نهایی انجام نشد")
        return True

def main():
    """تابع اصلی"""
    import sys
    
    # بررسی آرگومان‌ها
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
    
    # نمایش هشدار
    print()
    print_warning("⚠️  هشدار: این عمل غیرقابل بازگشت است!")
    print_warning("⚠️  تمام فایل‌ها و پوشه‌های مرتبط با اندروید حذف می‌شوند!")
    print()
    
    if not dry_run:
        response = input("آیا مطمئن هستید که می‌خواهید ادامه دهید؟ (yes/no): ")
        if response.lower() not in ['yes', 'y', 'بله', 'ب']:
            print_info("عملیات لغو شد")
            return
    
    # اجرای حذف
    success = delete_android_app(dry_run=dry_run)
    
    if success:
        print()
        print_success("✅ عملیات با موفقیت انجام شد!")
    else:
        print()
        print_error("❌ برخی خطاها رخ داد. لطفاً بررسی کنید.")
        sys.exit(1)

if __name__ == '__main__':
    main()


