# راهنمای نصب و راه‌اندازی Meilisearch

این راهنما نحوه نصب و راه‌اندازی Meilisearch را برای سیستم جستجوی فروشگاه توضیح می‌دهد.

## پیش‌نیازها

- Docker (پیشنهادی) یا
- Meilisearch binary

## نصب با Docker (پیشنهادی)

### 1. اجرای Meilisearch با Docker

```bash
docker run -d \
  --name meilisearch \
  -p 7700:7700 \
  -v $(pwd)/meilisearch_data:/meili_data \
  getmeili/meilisearch:latest \
  meilisearch --env="development"
```

برای production:

```bash
docker run -d \
  --name meilisearch \
  -p 7700:7700 \
  -v $(pwd)/meilisearch_data:/meili_data \
  -e MEILI_MASTER_KEY=your_master_key_here \
  getmeili/meilisearch:latest
```

### 2. نصب Python Package

```bash
pip install meilisearch
```

یا:

```bash
pip install -r requirements.txt
```

## تنظیمات

### Environment Variables (اختیاری)

می‌توانید این متغیرهای محیطی را تنظیم کنید:

```bash
export MEILISEARCH_HOST=http://localhost:7700
export MEILISEARCH_MASTER_KEY=your_master_key_here  # فقط برای production
```

یا در فایل `.env`:

```
MEILISEARCH_HOST=http://localhost:7700
MEILISEARCH_MASTER_KEY=your_master_key_here
```

### تنظیمات پیش‌فرض

در `search_config.py` تنظیمات پیش‌فرض تعریف شده است:
- Host: `http://localhost:7700`
- Index Name: `products`
- Timeout: 5 seconds

## همگام‌سازی اولیه

### 1. همگام‌سازی از طریق Admin Panel

1. وارد پنل مدیریت شوید
2. به صفحه مدیریت محصولات بروید
3. دکمه "همگام‌سازی با موتور جستجو" را بزنید

### 2. همگام‌سازی از طریق API

```bash
curl -X POST http://localhost:8081/admin/search/sync \
  -H "Cookie: session=your_session_cookie"
```

### 3. همگام‌سازی از طریق Python Script

```python
from app import app
from search_sync import get_sync_service

with app.app_context():
    sync_service = get_sync_service()
    result = sync_service.sync_all_products()
    print(result)
```

## تست

### 1. بررسی دسترسی به Meilisearch

```bash
curl http://localhost:7700/health
```

باید پاسخ زیر را ببینید:

```json
{"status":"available"}
```

### 2. تست جستجو

بعد از همگام‌سازی، به صفحه فروشگاه بروید و یک جستجو انجام دهید. اگر Meilisearch در دسترس باشد، از آن استفاده می‌شود، در غیر این صورت از SQL search استفاده می‌شود (fallback).

### 3. بررسی Index

```bash
curl http://localhost:7700/indexes/products
```

## ویژگی‌ها

### جستجوی پیشرفته

- **Typo Tolerance**: به صورت خودکار typo های کوچک را handle می‌کند
- **Multi-language**: پشتیبانی از فارسی و انگلیسی
- **Synonyms**: کلمات مترادف (مثلاً خودرو = ماشین)
- **Highlighting**: برجسته‌سازی کلمات جستجو در نتایج

### فیلترها

- برند (brand_id)
- دسته‌بندی (category_id)
- نوع خودرو (vehicle_type_id)
- موجودی (stock_quantity)
- وضعیت (is_active, is_featured)

### مرتب‌سازی

- مرتبط‌ترین (default)
- جدیدترین
- ارزان‌ترین / گران‌ترین
- بیشترین موجودی

## همگام‌سازی Real-time (پیشنهادی برای آینده)

برای همگام‌سازی خودکار هنگام ایجاد/ویرایش/حذف محصول، می‌توانید از SQLAlchemy events استفاده کنید:

```python
from sqlalchemy import event
from models import Product
from search_sync import get_sync_service

@event.listens_for(Product, 'after_insert')
@event.listens_for(Product, 'after_update')
def sync_product_after_change(mapper, connection, target):
    """Sync product to Meilisearch after insert/update"""
    sync_service = get_sync_service()
    sync_service.sync_product(target.id)

@event.listens_for(Product, 'after_delete')
def delete_product_from_index(mapper, connection, target):
    """Delete product from Meilisearch after deletion"""
    sync_service = get_sync_service()
    sync_service.delete_product(target.id)
```

## Troubleshooting

### مشکل: Meilisearch در دسترس نیست

- بررسی کنید که Docker container اجرا شده باشد: `docker ps`
- بررسی کنید که port 7700 باز باشد
- بررسی لاگ‌ها: `docker logs meilisearch`

### مشکل: Index ایجاد نمی‌شود

- بررسی کنید که Meilisearch به درستی اجرا شده باشد
- بررسی لاگ‌های application برای خطاها
- بررسی کنید که master key (در production) صحیح باشد

### مشکل: نتایج جستجو خالی است

- مطمئن شوید که همگام‌سازی انجام شده باشد
- بررسی کنید که محصولات در index موجود باشند: `curl http://localhost:7700/indexes/products/stats`
- بررسی فیلترها - ممکن است فیلترها همه محصولات را حذف کرده باشند

## Performance Tips

1. **Batch Size**: برای همگام‌سازی اولیه، batch size مناسب انتخاب کنید (100-500)
2. **Periodic Sync**: برای همگام‌سازی دوره‌ای از background task استفاده کنید
3. **Index Settings**: تنظیمات index را بر اساس نیاز خود بهینه کنید

## Production Considerations

1. **Master Key**: حتماً master key تنظیم کنید
2. **HTTPS**: از HTTPS برای ارتباط با Meilisearch استفاده کنید
3. **Backup**: به صورت منظم از index backup بگیرید
4. **Monitoring**: لاگ‌ها و performance را monitor کنید
5. **Resource Limits**: memory و CPU limits مناسب تنظیم کنید

## منابع بیشتر

- [Meilisearch Documentation](https://www.meilisearch.com/docs)
- [Meilisearch Python SDK](https://github.com/meilisearch/meilisearch-python)

