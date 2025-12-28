#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست برای بررسی مشکل static files
"""

import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_static_files():
    """بررسی وجود فایل‌های static"""
    
    # پیدا کردن مسیر static folder
    project_root = Path(__file__).parent
    static_folder = project_root / 'static'
    images_folder = static_folder / 'images'
    
    print("=" * 60)
    print("بررسی فایل‌های Static")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print(f"Static folder: {static_folder}")
    print(f"Images folder: {images_folder}")
    print()
    
    # بررسی وجود پوشه‌ها
    if not static_folder.exists():
        print(f"❌ پوشه static وجود ندارد: {static_folder}")
        return False
    
    if not images_folder.exists():
        print(f"❌ پوشه images وجود ندارد: {images_folder}")
        return False
    
    print("✅ پوشه‌ها وجود دارند")
    print()
    
    # لیست فایل‌های مورد نیاز
    required_files = [
        'logo.png',
        'favicon-16x16.png',
        'favicon-32x32.png',
        'favicon-48x48.png',
        'favicon-64x64.png',
        'favicon-128x128.png',
        'favicon.ico',
        'photo_5460656944265162587_w.jpg'
    ]
    
    print("بررسی فایل‌های مورد نیاز:")
    print("-" * 60)
    
    all_exist = True
    for filename in required_files:
        file_path = images_folder / filename
        if file_path.exists() and file_path.is_file():
            size = file_path.stat().st_size
            print(f"✅ {filename:40s} ({size:,} bytes)")
        else:
            print(f"❌ {filename:40s} (NOT FOUND)")
            all_exist = False
    
    print()
    print("=" * 60)
    
    if all_exist:
        print("✅ همه فایل‌ها موجود هستند")
        return True
    else:
        print("❌ برخی فایل‌ها موجود نیستند")
        return False

def test_flask_route():
    """تست route Flask برای static files"""
    print()
    print("=" * 60)
    print("تست Route Flask")
    print("=" * 60)
    
    try:
        # Import Flask app
        sys.path.insert(0, str(Path(__file__).parent))
        from app import app
        
        with app.app_context():
            static_folder = app.static_folder
            print(f"Flask static_folder: {static_folder}")
            
            if static_folder:
                static_path = Path(static_folder)
                if not static_path.is_absolute():
                    # Convert to absolute path
                    project_root = Path(__file__).parent
                    static_path = project_root / static_path
                
                print(f"Absolute static path: {static_path}")
                print(f"Exists: {static_path.exists()}")
                
                # Test a file
                test_file = static_path / 'images' / 'logo.png'
                print(f"Test file (logo.png): {test_file}")
                print(f"Test file exists: {test_file.exists()}")
                
                return static_path.exists()
            else:
                print("❌ static_folder تنظیم نشده است")
                return False
                
    except Exception as e:
        print(f"❌ خطا در تست Flask: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print()
    file_check = test_static_files()
    print()
    flask_check = test_flask_route()
    print()
    print("=" * 60)
    if file_check and flask_check:
        print("✅ همه چیز درست است!")
        sys.exit(0)
    else:
        print("❌ مشکلاتی وجود دارد")
        sys.exit(1)

