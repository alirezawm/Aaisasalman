#!/bin/bash
# Script برای راه‌اندازی Meilisearch

echo "=========================================="
echo "راه‌اندازی Meilisearch"
echo "=========================================="
echo ""

# بررسی وجود Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker نصب نشده است!"
    echo "لطفاً ابتدا Docker را نصب کنید."
    exit 1
fi

# بررسی وجود docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose نصب نشده است!"
    echo "لطفاً ابتدا docker-compose را نصب کنید."
    exit 1
fi

echo "✓ Docker و docker-compose در دسترس هستند"
echo ""

# بررسی اجرای Meilisearch
if docker ps | grep -q meilisearch; then
    echo "⚠ Meilisearch در حال اجرا است"
    echo "آیا می‌خواهید restart کنید؟ (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Restart کردن Meilisearch..."
        docker-compose -f docker-compose.meilisearch.yml restart
    else
        echo "Meilisearch در حال اجرا است. هیچ کاری انجام نشد."
        exit 0
    fi
else
    echo "شروع Meilisearch..."
    docker-compose -f docker-compose.meilisearch.yml up -d
fi

echo ""
echo "صبر می‌کنیم تا Meilisearch آماده شود..."
sleep 3

# بررسی سلامت
echo "بررسی سلامت Meilisearch..."
for i in {1..10}; do
    if curl -s http://localhost:7700/health > /dev/null 2>&1; then
        echo "✓ Meilisearch آماده است!"
        echo ""
        echo "اطلاعات:"
        echo "  - URL: http://localhost:7700"
        echo "  - Health: http://localhost:7700/health"
        echo ""
        echo "برای همگام‌سازی محصولات:"
        echo "  python init_search_index.py"
        exit 0
    fi
    echo "  تلاش $i/10..."
    sleep 2
done

echo "❌ Meilisearch آماده نشد!"
echo "لاگ‌ها:"
docker logs meilisearch --tail 20
exit 1

