#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت حرفه‌ای پاک‌سازی پروژه
این اسکریپت تمام فایل‌های اضافی، کدهای استفاده نشده و فایل‌های بکاپ را شناسایی و حذف می‌کند
"""

import os
import shutil
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import hashlib

class ProjectCleaner:
    def __init__(self, project_root: str = ".", dry_run: bool = True, interactive: bool = True):
        self.project_root = Path(project_root).resolve()
        self.dry_run = dry_run
        self.interactive = interactive
        self.deleted_files = []
        self.deleted_dirs = []
        self.errors = []
        self.protected_patterns = [
            "app.py", "routes.py", "models.py", "requirements.txt",
            "docker-compose.yaml", "Dockerfile", ".env", ".git"
        ]
        self.protected_dirs = [
            "static", "templates", "uploads", "instance", "ssl", "services", "scripts", "venv", ".git"
        ]
        
    def log(self, message: str, level: str = "INFO"):
        """لاگ کردن پیام‌ها"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def is_protected(self, file_path: Path) -> bool:
        """بررسی اینکه فایل محافظت شده است یا نه"""
        file_str = str(file_path)
        path_parts = file_path.parts
        
        # بررسی دایرکتوری‌های محافظت شده (با بررسی دقیق‌تر)
        for protected_dir in self.protected_dirs:
            # بررسی دقیق‌تر برای venv
            if protected_dir in ['venv', '.venv']:
                if 'venv' in path_parts or '.venv' in path_parts:
                    return True
            elif protected_dir in path_parts:
                return True
                
        # بررسی فایل‌های محافظت شده
        for protected_pattern in self.protected_patterns:
            if file_path.name == protected_pattern or protected_pattern in file_str:
                return True
                
        return False
        
    def find_files_by_pattern(self, patterns: List[str]) -> List[Path]:
        """پیدا کردن فایل‌ها بر اساس الگو"""
        found_files = []
        
        for pattern in patterns:
            for file_path in self.project_root.rglob(pattern):
                if not self.is_protected(file_path):
                    found_files.append(file_path)
                    
        return found_files
        
    def find_directories_by_pattern(self, patterns: List[str]) -> List[Path]:
        """پیدا کردن دایرکتوری‌ها بر اساس الگو"""
        found_dirs = []
        
        for pattern in patterns:
            for dir_path in self.project_root.rglob(pattern):
                if not self.is_protected(dir_path):
                    found_dirs.append(dir_path)
                    
        return found_dirs
        
    def delete_file(self, file_path: Path) -> bool:
        """حذف فایل"""
        try:
            if not self.dry_run:
                file_path.unlink()
            self.deleted_files.append(str(file_path))
            self.log(f"حذف فایل: {file_path}", "DELETE")
            return True
        except Exception as e:
            self.errors.append(f"خطا در حذف {file_path}: {str(e)}")
            self.log(f"خطا در حذف {file_path}: {str(e)}", "ERROR")
            return False
            
    def delete_directory(self, dir_path: Path) -> bool:
        """حذف دایرکتوری"""
        try:
            if not self.dry_run:
                shutil.rmtree(dir_path)
            self.deleted_dirs.append(str(dir_path))
            self.log(f"حذف دایرکتوری: {dir_path}", "DELETE")
            return True
        except Exception as e:
            self.errors.append(f"خطا در حذف {dir_path}: {str(e)}")
            self.log(f"خطا در حذف {dir_path}: {str(e)}", "ERROR")
            return False
            
    def confirm_deletion(self, items: List[Path], item_type: str = "فایل") -> bool:
        """درخواست تأیید از کاربر"""
        if not self.interactive:
            return True
            
        print(f"\n{'='*60}")
        print(f"تعداد {item_type}های پیدا شده: {len(items)}")
        if len(items) <= 20:
            for item in items[:20]:
                print(f"  - {item}")
        else:
            for item in items[:10]:
                print(f"  - {item}")
            print(f"  ... و {len(items) - 10} مورد دیگر")
        print(f"{'='*60}")
        
        response = input(f"آیا می‌خواهید این {item_type}ها را حذف کنید؟ (y/n): ")
        return response.lower() in ['y', 'yes', 'بله', 'ب']
        
    def cleanup_megaprompt_files(self):
        """حذف فایل‌های مگاپرامپت"""
        self.log("شروع پاک‌سازی فایل‌های مگاپرامپت...")
        patterns = [
            "*megaprompt*.json",
            "*_megaprompt.json",
            "detection_rebuild_report_*.json",
            "project_analysis_megaprompt.json",
            "project_analysis_megaprompt.txt"
        ]
        
        files = self.find_files_by_pattern(patterns)
        if files and self.confirm_deletion(files, "فایل مگاپرامپت"):
            for file_path in files:
                self.delete_file(file_path)
                
    def cleanup_backup_files(self):
        """حذف فایل‌های بکاپ"""
        self.log("شروع پاک‌سازی فایل‌های بکاپ...")
        patterns = [
            "*.backup",
            "*.old",
            "*.bak",
            "*_backup.*",
            "*_old.*",
            "requirements.fixed.txt",
            "Dockerfile.fixed"
        ]
        
        files = self.find_files_by_pattern(patterns)
        if files and self.confirm_deletion(files, "فایل بکاپ"):
            for file_path in files:
                self.delete_file(file_path)
                
    def cleanup_backup_directories(self):
        """حذف دایرکتوری‌های بکاپ"""
        self.log("شروع پاک‌سازی دایرکتوری‌های بکاپ...")
        dirs_to_check = [
            self.project_root / "backups",
            self.project_root / "archive"
        ]
        
        existing_dirs = [d for d in dirs_to_check if d.exists() and d.is_dir()]
        if existing_dirs and self.confirm_deletion(existing_dirs, "دایرکتوری بکاپ"):
            for dir_path in existing_dirs:
                self.delete_directory(dir_path)
                
    def cleanup_cache_directories(self):
        """حذف دایرکتوری‌های کش"""
        self.log("شروع پاک‌سازی دایرکتوری‌های کش...")
        patterns = ["__pycache__", ".pytest_cache", ".mypy_cache", "htmlcov"]
        
        dirs = self.find_directories_by_pattern(patterns)
        # همچنین فایل‌های .pyc و .pyo
        pyc_files = list(self.project_root.rglob("*.pyc")) + list(self.project_root.rglob("*.pyo"))
        
        all_items = dirs + pyc_files
        if all_items and self.confirm_deletion(all_items, "فایل/دایرکتوری کش"):
            for item in dirs:
                self.delete_directory(item)
            for item in pyc_files:
                if not self.is_protected(item):
                    self.delete_file(item)
                    
    def cleanup_temporary_files(self):
        """حذف فایل‌های موقت"""
        self.log("شروع پاک‌سازی فایل‌های موقت...")
        patterns = [
            "*.log",
            "*.tmp",
            "*.temp",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db",
            ".coverage"
        ]
        
        files = self.find_files_by_pattern(patterns)
        if files and self.confirm_deletion(files, "فایل موقت"):
            for file_path in files:
                self.delete_file(file_path)
                
    def cleanup_old_database_backups(self):
        """حذف بکاپ‌های قدیمی دیتابیس"""
        self.log("شروع پاک‌سازی بکاپ‌های قدیمی دیتابیس...")
        patterns = ["*.db.backup", "*.db.old"]
        
        files = self.find_files_by_pattern(patterns)
        # همچنین فایل‌های db در دایرکتوری backups
        backup_db_files = list((self.project_root / "backups").rglob("*.db")) if (self.project_root / "backups").exists() else []
        
        all_files = files + backup_db_files
        if all_files and self.confirm_deletion(all_files, "بکاپ دیتابیس"):
            for file_path in all_files:
                if not self.is_protected(file_path):
                    self.delete_file(file_path)
                    
    def cleanup_unused_imports(self):
        """حذف import های استفاده نشده"""
        self.log("شروع پاک‌سازی import های استفاده نشده...")
        
        if self.dry_run:
            self.log("حالت dry-run: import های استفاده نشده شناسایی می‌شوند اما حذف نمی‌شوند", "INFO")
            return
            
        try:
            # استفاده از autoflake برای حذف import های استفاده نشده
            result = subprocess.run(
                ["autoflake", "--in-place", "--remove-all-unused-imports", "--recursive", 
                 str(self.project_root), "--exclude", "venv"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log("import های استفاده نشده با موفقیت حذف شدند", "SUCCESS")
            else:
                self.log(f"خطا در حذف import ها: {result.stderr}", "WARNING")
        except FileNotFoundError:
            self.log("autoflake نصب نیست. برای نصب: pip install autoflake", "WARNING")
        except Exception as e:
            self.log(f"خطا در حذف import ها: {str(e)}", "ERROR")
            
    def format_code(self):
        """فرمت کردن کد با black"""
        self.log("شروع فرمت کردن کد...")
        
        if self.dry_run:
            self.log("حالت dry-run: کد فرمت نمی‌شود", "INFO")
            return
            
        try:
            result = subprocess.run(
                ["black", str(self.project_root), "--exclude", "venv"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log("کد با موفقیت فرمت شد", "SUCCESS")
            else:
                self.log(f"خطا در فرمت کردن کد: {result.stderr}", "WARNING")
        except FileNotFoundError:
            self.log("black نصب نیست. برای نصب: pip install black", "WARNING")
        except Exception as e:
            self.log(f"خطا در فرمت کردن کد: {str(e)}", "ERROR")
            
    def sort_imports(self):
        """مرتب‌سازی import ها با isort"""
        self.log("شروع مرتب‌سازی import ها...")
        
        if self.dry_run:
            self.log("حالت dry-run: import ها مرتب نمی‌شوند", "INFO")
            return
            
        try:
            result = subprocess.run(
                ["isort", str(self.project_root), "--skip", "venv"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.log("import ها با موفقیت مرتب شدند", "SUCCESS")
            else:
                self.log(f"خطا در مرتب‌سازی import ها: {result.stderr}", "WARNING")
        except FileNotFoundError:
            self.log("isort نصب نیست. برای نصب: pip install isort", "WARNING")
        except Exception as e:
            self.log(f"خطا در مرتب‌سازی import ها: {str(e)}", "ERROR")
            
    def generate_report(self) -> Dict:
        """ایجاد گزارش نهایی"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "deleted_files_count": len(self.deleted_files),
            "deleted_dirs_count": len(self.deleted_dirs),
            "errors_count": len(self.errors),
            "deleted_files": self.deleted_files,
            "deleted_directories": self.deleted_dirs,
            "errors": self.errors
        }
        
        # محاسبه فضای آزاد شده
        total_size = 0
        for file_path in self.deleted_files:
            try:
                path = Path(file_path)
                if path.exists():
                    total_size += path.stat().st_size
            except:
                pass
                
        report["freed_space_mb"] = round(total_size / (1024 * 1024), 2)
        
        return report
        
    def save_report(self, report: Dict):
        """ذخیره گزارش در فایل"""
        report_file = self.project_root / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        self.log(f"گزارش در {report_file} ذخیره شد", "INFO")
        
    def print_summary(self, report: Dict):
        """چاپ خلاصه گزارش"""
        print("\n" + "="*60)
        print("خلاصه پاک‌سازی")
        print("="*60)
        print(f"حالت: {'Dry Run (شبیه‌سازی)' if self.dry_run else 'اجرای واقعی'}")
        print(f"تعداد فایل‌های حذف شده: {report['deleted_files_count']}")
        print(f"تعداد دایرکتوری‌های حذف شده: {report['deleted_dirs_count']}")
        print(f"فضای آزاد شده: {report['freed_space_mb']} MB")
        print(f"تعداد خطاها: {report['errors_count']}")
        print("="*60)
        
        if report['errors']:
            print("\nخطاها:")
            for error in report['errors']:
                print(f"  - {error}")
                
    def run_full_cleanup(self):
        """اجرای کامل پاک‌سازی"""
        self.log("شروع فرآیند پاک‌سازی کامل پروژه...")
        self.log(f"دایرکتوری پروژه: {self.project_root}")
        self.log(f"حالت: {'Dry Run' if self.dry_run else 'اجرای واقعی'}")
        
        if self.dry_run:
            print("\n⚠️  توجه: در حالت Dry Run هیچ فایلی حذف نمی‌شود!")
            print("برای حذف واقعی فایل‌ها، از فلگ --execute استفاده کنید.\n")
        
        # اجرای مراحل پاک‌سازی
        self.cleanup_megaprompt_files()
        self.cleanup_backup_files()
        self.cleanup_backup_directories()
        self.cleanup_cache_directories()
        self.cleanup_temporary_files()
        self.cleanup_old_database_backups()
        
        # بهینه‌سازی کد (فقط در حالت اجرای واقعی)
        if not self.dry_run:
            self.cleanup_unused_imports()
            self.format_code()
            self.sort_imports()
        
        # ایجاد گزارش
        report = self.generate_report()
        self.save_report(report)
        self.print_summary(report)
        
        self.log("پاک‌سازی با موفقیت انجام شد!", "SUCCESS")


def main():
    """تابع اصلی"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="اسکریپت پاک‌سازی حرفه‌ای پروژه",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="اجرای واقعی پاک‌سازی (به صورت پیش‌فرض dry-run است)"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="غیرفعال کردن حالت تعاملی (بدون درخواست تأیید)"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="مسیر ریشه پروژه (پیش‌فرض: دایرکتوری فعلی)"
    )
    
    args = parser.parse_args()
    
    cleaner = ProjectCleaner(
        project_root=args.project_root,
        dry_run=not args.execute,
        interactive=not args.non_interactive
    )
    
    try:
        cleaner.run_full_cleanup()
    except KeyboardInterrupt:
        print("\n\nپاک‌سازی توسط کاربر متوقف شد.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nخطای غیرمنتظره: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

