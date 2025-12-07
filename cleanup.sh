#!/bin/bash
# اسکریپت پاک‌سازی سریع پروژه
# استفاده: ./cleanup.sh [--execute]

set -e

# رنگ‌ها برای خروجی
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# بررسی حالت اجرا
DRY_RUN=true
if [[ "$1" == "--execute" ]]; then
    DRY_RUN=false
    echo -e "${RED}⚠️  توجه: این حالت فایل‌ها را واقعاً حذف می‌کند!${NC}"
    read -p "آیا مطمئن هستید؟ (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "عملیات لغو شد."
        exit 0
    fi
else
    echo -e "${YELLOW}حالت Dry Run: هیچ فایلی حذف نمی‌شود${NC}"
    echo "برای حذف واقعی فایل‌ها، از فلگ --execute استفاده کنید."
    echo ""
fi

# تابع برای حذف فایل‌ها
delete_files() {
    local pattern=$1
    local description=$2
    
    echo -e "${GREEN}در حال پاک‌سازی: $description${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        find . -name "$pattern" -not -path "./venv/*" -not -path "./.git/*" -type f | while read file; do
            echo "  [DRY RUN] حذف می‌شد: $file"
        done
    else
        find . -name "$pattern" -not -path "./venv/*" -not -path "./.git/*" -type f -delete
        echo "  ✓ حذف شد"
    fi
}

# تابع برای حذف دایرکتوری‌ها
delete_dirs() {
    local pattern=$1
    local description=$2
    
    echo -e "${GREEN}در حال پاک‌سازی: $description${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        find . -name "$pattern" -not -path "./venv/*" -not -path "./.git/*" -type d | while read dir; do
            echo "  [DRY RUN] حذف می‌شد: $dir"
        done
    else
        find . -name "$pattern" -not -path "./venv/*" -not -path "./.git/*" -type d -exec rm -rf {} + 2>/dev/null || true
        echo "  ✓ حذف شد"
    fi
}

echo "=========================================="
echo "شروع پاک‌سازی پروژه"
echo "=========================================="
echo ""

# 1. حذف فایل‌های مگاپرامپت
delete_files "*megaprompt*.json" "فایل‌های مگاپرامپت"

# 2. حذف فایل‌های بکاپ
delete_files "*.backup" "فایل‌های .backup"
delete_files "*.old" "فایل‌های .old"
delete_files "*.bak" "فایل‌های .bak"

# 3. حذف فایل‌های تکراری
if [ "$DRY_RUN" = false ]; then
    [ -f "Dockerfile.fixed" ] && rm -f "Dockerfile.fixed" && echo "✓ Dockerfile.fixed حذف شد"
    [ -f "requirements.fixed.txt" ] && rm -f "requirements.fixed.txt" && echo "✓ requirements.fixed.txt حذف شد"
    [ -f "project_analysis_megaprompt.txt" ] && rm -f "project_analysis_megaprompt.txt" && echo "✓ project_analysis_megaprompt.txt حذف شد"
else
    [ -f "Dockerfile.fixed" ] && echo "  [DRY RUN] حذف می‌شد: Dockerfile.fixed"
    [ -f "requirements.fixed.txt" ] && echo "  [DRY RUN] حذف می‌شد: requirements.fixed.txt"
    [ -f "project_analysis_megaprompt.txt" ] && echo "  [DRY RUN] حذف می‌شد: project_analysis_megaprompt.txt"
fi

# 4. حذف دایرکتوری‌های کش
delete_dirs "__pycache__" "دایرکتوری‌های __pycache__"
delete_files "*.pyc" "فایل‌های .pyc"
delete_files "*.pyo" "فایل‌های .pyo"

# 5. حذف فایل‌های موقت
delete_files "*.log" "فایل‌های لاگ"
delete_files "*.tmp" "فایل‌های موقت"
delete_files "*.temp" "فایل‌های temp"
delete_files ".DS_Store" "فایل‌های .DS_Store"
delete_files "Thumbs.db" "فایل‌های Thumbs.db"

# 6. حذف دایرکتوری‌های بکاپ (با احتیاط)
if [ "$DRY_RUN" = false ]; then
    if [ -d "backups" ]; then
        read -p "آیا می‌خواهید دایرکتوری backups را حذف کنید؟ (yes/no): " confirm_backups
        if [[ "$confirm_backups" == "yes" ]]; then
            rm -rf backups
            echo "✓ دایرکتوری backups حذف شد"
        fi
    fi
    
    if [ -d "archive" ]; then
        read -p "آیا می‌خواهید دایرکتوری archive را حذف کنید؟ (yes/no): " confirm_archive
        if [[ "$confirm_archive" == "yes" ]]; then
            rm -rf archive
            echo "✓ دایرکتوری archive حذف شد"
        fi
    fi
else
    [ -d "backups" ] && echo "  [DRY RUN] حذف می‌شد: backups/"
    [ -d "archive" ] && echo "  [DRY RUN] حذف می‌شد: archive/"
fi

echo ""
echo "=========================================="
echo "پاک‌سازی کامل شد!"
echo "=========================================="

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo -e "${YELLOW}برای اجرای واقعی پاک‌سازی، دستور زیر را اجرا کنید:${NC}"
    echo "  ./cleanup.sh --execute"
fi

