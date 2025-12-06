#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت ساده پاک‌سازی - فقط فایل‌های اصلی پروژه
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# دایرکتوری‌های محافظت شده
PROTECTED_DIRS = ['venv', '.venv', 'static', 'templates', 'uploads', 'instance', 
                  'ssl', 'services', 'scripts', '.git', '__pycache__']

# فایل‌های محافظت شده
PROTECTED_FILES = ['app.py', 'routes.py', 'models.py', 'requirements.txt', 
                   'docker-compose.yaml', 'Dockerfile', '.env']

def is_protected(path):
    """بررسی اینکه مسیر محافظت شده است یا نه"""
    path_str = str(path)
    path_parts = path.parts
    
    # بررسی دایرکتوری‌های محافظت شده
    for protected in PROTECTED_DIRS:
        if protected in path_parts:
            return True
    
    # بررسی فایل‌های محافظت شده
    for protected in PROTECTED_FILES:
        if path.name == protected:
            return True
    
    return False

def cleanup_megaprompts():
    """حذف فایل‌های مگاپرامپت"""
    print("🔍 در حال جستجوی فایل‌های مگاپرامپت...")
    patterns = ['*megaprompt*.json', 'detection_rebuild_report_*.json', 
                'project_analysis_megaprompt.json', 'project_analysis_megaprompt.txt']
    
    deleted = 0
    for pattern in patterns:
        for file_path in Path('.').rglob(pattern):
            if not is_protected(file_path) and file_path.is_file():
                try:
                    file_path.unlink()
                    print(f"  ✓ حذف شد: {file_path}")
                    deleted += 1
                except Exception as e:
                    print(f"  ✗ خطا در حذف {file_path}: {e}")
    
    print(f"✅ {deleted} فایل مگاپرامپت حذف شد\n")
    return deleted

def cleanup_backup_files():
    """حذف فایل‌های بکاپ"""
    print("🔍 در حال جستجوی فایل‌های بکاپ...")
    patterns = ['*.backup', '*.old', '*.bak', 'routes.py.backup', 
                'brand_vehicle_detector.py.old', 'requirements.fixed.txt', 
                'Dockerfile.fixed']
    
    deleted = 0
    for pattern in patterns:
        for file_path in Path('.').rglob(pattern):
            if not is_protected(file_path) and file_path.is_file():
                try:
                    file_path.unlink()
                    print(f"  ✓ حذف شد: {file_path}")
                    deleted += 1
                except Exception as e:
                    print(f"  ✗ خطا در حذف {file_path}: {e}")
    
    print(f"✅ {deleted} فایل بکاپ حذف شد\n")
    return deleted

def cleanup_backup_dirs():
    """حذف دایرکتوری‌های بکاپ"""
    print("🔍 در حال جستجوی دایرکتوری‌های بکاپ...")
    dirs_to_check = ['backups', 'archive']
    
    deleted = 0
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir() and not is_protected(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"  ✓ حذف شد: {dir_path}/")
                deleted += 1
            except Exception as e:
                print(f"  ✗ خطا در حذف {dir_path}: {e}")
    
    print(f"✅ {deleted} دایرکتوری بکاپ حذف شد\n")
    return deleted

def cleanup_cache():
    """حذف فایل‌های کش (فقط در ریشه پروژه، نه venv)"""
    print("🔍 در حال جستجوی فایل‌های کش...")
    
    deleted = 0
    
    # حذف __pycache__ در ریشه پروژه
    for cache_dir in Path('.').rglob('__pycache__'):
        if not is_protected(cache_dir) and cache_dir.is_dir():
            # بررسی که در venv نیست
            if 'venv' not in cache_dir.parts and '.venv' not in cache_dir.parts:
                try:
                    shutil.rmtree(cache_dir)
                    print(f"  ✓ حذف شد: {cache_dir}/")
                    deleted += 1
                except Exception as e:
                    print(f"  ✗ خطا در حذف {cache_dir}: {e}")
    
    # حذف فایل‌های .pyc و .pyo
    for pattern in ['*.pyc', '*.pyo']:
        for file_path in Path('.').rglob(pattern):
            if not is_protected(file_path) and file_path.is_file():
                if 'venv' not in file_path.parts and '.venv' not in file_path.parts:
                    try:
                        file_path.unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"  ✗ خطا در حذف {file_path}: {e}")
    
    print(f"✅ {deleted} فایل/دایرکتوری کش حذف شد\n")
    return deleted

def cleanup_temp_files():
    """حذف فایل‌های موقت"""
    print("🔍 در حال جستجوی فایل‌های موقت...")
    patterns = ['*.log', '*.tmp', '*.temp', '.DS_Store', 'Thumbs.db', '.coverage']
    
    deleted = 0
    for pattern in patterns:
        for file_path in Path('.').rglob(pattern):
            if not is_protected(file_path) and file_path.is_file():
                if 'venv' not in file_path.parts and '.venv' not in file_path.parts:
                    try:
                        file_path.unlink()
                        deleted += 1
                    except Exception as e:
                        print(f"  ✗ خطا در حذف {file_path}: {e}")
    
    print(f"✅ {deleted} فایل موقت حذف شد\n")
    return deleted

def main():
    """تابع اصلی"""
    print("="*60)
    print("شروع پاک‌سازی پروژه")
    print("="*60)
    print()
    
    total_deleted = 0
    
    # اجرای مراحل پاک‌سازی
    total_deleted += cleanup_megaprompts()
    total_deleted += cleanup_backup_files()
    total_deleted += cleanup_backup_dirs()
    total_deleted += cleanup_cache()
    total_deleted += cleanup_temp_files()
    
    print("="*60)
    print(f"✅ پاک‌سازی کامل شد! تعداد کل فایل‌های حذف شده: {total_deleted}")
    print("="*60)

if __name__ == "__main__":
    main()

