#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت استخراج تصویر PNG از فایل SVG
Extract PNG image from SVG file
"""

import re
import base64
import os

def extract_png_from_svg(svg_file_path):
    """استخراج تصویر PNG از فایل SVG"""
    print(f"در حال خواندن فایل SVG: {svg_file_path}")
    
    # خواندن فایل SVG
    with open(svg_file_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # جستجوی base64 encoded image
    pattern = r'data:image/png;base64,([A-Za-z0-9+/=]+)'
    match = re.search(pattern, svg_content)
    
    if not match:
        print("❌ تصویر PNG در فایل SVG یافت نشد!")
        return None
    
    base64_data = match.group(1)
    print(f"✅ داده base64 یافت شد (طول: {len(base64_data)} کاراکتر)")
    
    # دیکد کردن base64
    try:
        png_data = base64.b64decode(base64_data)
        print(f"✅ تصویر PNG استخراج شد (حجم: {len(png_data)} بایت)")
        return png_data
    except Exception as e:
        print(f"❌ خطا در دیکد کردن base64: {e}")
        return None

def save_png(png_data, output_path):
    """ذخیره تصویر PNG"""
    try:
        with open(output_path, 'wb') as f:
            f.write(png_data)
        print(f"✅ تصویر با موفقیت در {output_path} ذخیره شد")
        return True
    except Exception as e:
        print(f"❌ خطا در ذخیره فایل: {e}")
        return False

def main():
    svg_file = "New Text Document.txt"
    output_file = "app_icon.png"
    
    if not os.path.exists(svg_file):
        print(f"❌ فایل {svg_file} یافت نشد!")
        return
    
    # استخراج PNG
    png_data = extract_png_from_svg(svg_file)
    
    if png_data:
        # ذخیره PNG
        save_png(png_data, output_file)
        print(f"\n🎉 تصویر آیکون با موفقیت استخراج شد: {output_file}")
        print(f"📁 می‌توانید از این فایل برای آیکون اپلیکیشن استفاده کنید.")

if __name__ == "__main__":
    main()

