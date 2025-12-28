# مگاپرامپت: افزودن موتور جستجوی حرفه‌ای به فروشگاه آسیا سلمان

## 📋 خلاصه اجرایی

این مگاپرامپت راهنمای جامع برای پیاده‌سازی یک موتور جستجوی حرفه‌ای و پیشرفته در فروشگاه آنلاین قطعات خودرو آسیا سلمان است. این سیستم شامل جستجوی چندلایه، پیشنهادات هوشمند، فیلترهای پیشرفته، آنالیتیکس و بهینه‌سازی عملکرد می‌باشد.

---

## 🎯 اهداف اصلی

1. **تجربه کاربری برتر**: جستجوی سریع، دقیق و کاربرپسند
2. **دقت بالا**: نتایج مرتبط و مرتب‌شده بر اساس اولویت
3. **پشتیبانی کامل از فارسی**: نرمال‌سازی و جستجوی هوشمند متن فارسی
4. **عملکرد بهینه**: جستجوی سریع حتی با حجم بالای داده
5. **قابلیت‌های پیشرفته**: فیلترها، مرتب‌سازی، پیشنهادات و آنالیتیکس

---

## 🏗️ معماری سیستم

### 1. لایه‌های جستجو (Search Layers)

سیستم جستجو باید در 5 لایه پیاده‌سازی شود:

#### لایه 1: جستجوی دقیق (Exact Match) - بالاترین اولویت
- جستجوی دقیق در SKU و OEM Code
- جستجوی کد عددی
- امتیاز: 100

#### لایه 2: جستجوی برند-مدل (Brand-Model Context)
- استخراج خودکار برند و مدل از کوئری
- جستجو در زمینه برند و مدل خاص
- امتیاز: 80-90

#### لایه 3: جستجوی دسته‌بندی (Category Search)
- جستجو در نام دسته‌بندی و زیردسته
- جستجو در محصولات مرتبط با دسته
- امتیاز: 60-70

#### لایه 4: جستجوی فازی (Fuzzy Search)
- تحمل خطاهای تایپی
- جستجوی بدون حروف صدادار (برای فارسی)
- امتیاز: 40-50

#### لایه 5: جستجوی معنایی (Semantic Search)
- جستجو در تگ‌ها و مشخصات فنی
- استفاده از مترادف‌ها
- امتیاز: 20-30

### 2. سیستم امتیازدهی (Scoring System)

هر نتیجه باید بر اساس معیارهای زیر امتیازدهی شود:

```python
# فرمول امتیازدهی
base_score = search_layer_score  # امتیاز لایه جستجو
stock_bonus = 10 if stock_quantity > 0 else 0
featured_bonus = 5 if is_featured else 0
user_preference_bonus = 15 if brand in user_preferred_brands else 0
relevance_bonus = calculate_relevance(query, product)

total_score = base_score + stock_bonus + featured_bonus + user_preference_bonus + relevance_bonus
```

---

## 🔍 ویژگی‌های جستجو

### 1. جستجوی چندزبانه (Multi-language Search)

#### پشتیبانی از فارسی
- نرمال‌سازی کاراکترهای فارسی/عربی (ی/ي، ک/ك، ا/أ/إ/آ)
- حذف اعراب و ZWNJ
- تبدیل اعداد عربی به فارسی
- جستجوی بدون حساسیت به حروف صدادار

#### پشتیبانی از انگلیسی
- جستجوی case-insensitive
- پشتیبانی از مترادف‌های رایج

### 2. پیشنهادات هوشمند (Smart Suggestions)

#### انواع پیشنهادات:
1. **پیشنهادات برند**: بر اساس کوئری کاربر
2. **پیشنهادات مدل**: در صورت وجود برند در کوئری
3. **پیشنهادات دسته‌بندی**: دسته‌های مرتبط
4. **پیشنهادات محصول**: محصولات محبوب و مرتبط

#### ویژگی‌های پیشنهادات:
- نمایش در زمان تایپ (Real-time)
- مرتب‌سازی بر اساس مرتبط‌بودن
- نمایش آیکون و متادیتا
- پشتیبانی از کیبورد (Arrow keys, Enter, Escape)

### 3. فیلترهای پیشرفته (Advanced Filters)

#### فیلترهای موجود:
- **برند**: فیلتر بر اساس برند
- **نوع خودرو**: فیلتر بر اساس نوع خودرو
- **دسته‌بندی**: فیلتر بر اساس دسته و زیردسته
- **قیمت**: محدوده قیمت (نقدی/چکی)
- **موجودی**: فقط موجود، فقط ناموجود، همه
- **ویژگی‌های خاص**: Featured, ISACO Warehouse 15

#### ویژگی‌های فیلتر:
- فیلترهای ترکیبی (AND/OR)
- حفظ فیلترها در URL
- نمایش تعداد نتایج برای هر فیلتر
- امکان پاک کردن همه فیلترها

### 4. مرتب‌سازی نتایج (Sorting)

#### گزینه‌های مرتب‌سازی:
1. **مرتبط‌ترین** (پیش‌فرض): بر اساس امتیاز relevance
2. **جدیدترین**: بر اساس تاریخ ایجاد
3. **ارزان‌ترین**: بر اساس قیمت صعودی
4. **گران‌ترین**: بر اساس قیمت نزولی
5. **بیشترین موجودی**: بر اساس stock_quantity
6. **محبوب‌ترین**: بر اساس تعداد فروش/بازدید

---

## 🎨 رابط کاربری (UI/UX)

### 1. نوار جستجو (Search Bar)

#### ویژگی‌ها:
- **Auto-focus**: فوکوس خودکار در صفحه فروشگاه
- **Placeholder هوشمند**: نمایش مثال‌های جستجو
- **آیکون جستجو**: آیکون واضح و قابل کلیک
- **دکمه پاک کردن**: برای پاک کردن سریع کوئری
- **جستجوی صوتی** (اختیاری): برای کاربران موبایل

#### استایل:
```css
.search-bar {
    position: relative;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
}

.search-input {
    padding: 12px 45px 12px 15px;
    border: 2px solid #dc3545;
    border-radius: 25px;
    font-size: 16px;
    transition: all 0.3s ease;
}

.search-input:focus {
    border-color: #c82333;
    box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
}
```

### 2. پیشنهادات جستجو (Search Suggestions Dropdown)

#### ویژگی‌ها:
- نمایش در زیر نوار جستجو
- حداکثر 10 پیشنهاد
- گروه‌بندی بر اساس نوع (برند، مدل، محصول، دسته)
- هایلایت کلمات جستجو در پیشنهادات
- انیمیشن نرم برای نمایش/پنهان‌سازی

#### استایل:
```css
.search-suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 0 0 8px 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    max-height: 400px;
    overflow-y: auto;
    z-index: 1000;
}

.suggestion-item {
    padding: 12px 16px;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
    transition: background-color 0.2s;
}

.suggestion-item:hover,
.suggestion-item.active {
    background-color: #f8f9fa;
}

.suggestion-icon {
    width: 24px;
    height: 24px;
    margin-left: 12px;
    color: #6c757d;
}

.suggestion-highlight {
    background-color: #fff3cd;
    font-weight: 600;
}
```

### 3. فیلترهای جانبی (Sidebar Filters)

#### ویژگی‌ها:
- فیلترهای قابل جمع‌شدن (Collapsible)
- نمایش تعداد نتایج برای هر فیلتر
- چک‌باکس‌ها و رنج‌اسلایدرها
- دکمه "اعمال فیلتر" و "پاک کردن"
- نمایش فیلترهای فعال

### 4. نمایش نتایج (Results Display)

#### ویژگی‌ها:
- **Grid View**: نمایش به صورت کارت
- **List View**: نمایش به صورت لیست (جدول)
- **Pagination**: صفحه‌بندی با نمایش تعداد کل
- **Loading State**: نمایش حالت بارگذاری
- **Empty State**: پیام مناسب در صورت نبود نتیجه
- **Highlight**: برجسته‌سازی کلمات جستجو در نتایج

---

## ⚡ بهینه‌سازی عملکرد

### 1. Caching

#### استراتژی Cache:
- **Query Cache**: کش کردن نتایج جستجو برای 5 دقیقه
- **Suggestions Cache**: کش کردن پیشنهادات برای 10 دقیقه
- **Filter Cache**: کش کردن فیلترها برای 30 دقیقه

#### پیاده‌سازی:
```python
from functools import lru_cache
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=300)  # 5 minutes
def cached_search(query, filters, page):
    # Search logic
    pass
```

### 2. Debouncing

#### برای پیشنهادات:
- تاخیر 300ms قبل از ارسال درخواست
- لغو درخواست‌های قبلی در صورت تایپ جدید

#### پیاده‌سازی JavaScript:
```javascript
let searchTimeout;
$('#searchInput').on('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function() {
        fetchSuggestions($(this).val());
    }, 300);
});
```

### 3. Lazy Loading

#### برای نتایج:
- بارگذاری تدریجی نتایج (Infinite Scroll)
- یا صفحه‌بندی با بارگذاری پیش‌بار (Prefetch)

### 4. Index Optimization

#### برای Meilisearch:
- تنظیمات بهینه searchable attributes
- تنظیمات typo tolerance
- استفاده از synonyms
- تنظیم ranking rules

---

## 📊 آنالیتیکس و ردیابی (Analytics & Tracking)

### 1. ردیابی جستجوها

#### داده‌های جمع‌آوری شده:
- کوئری جستجو
- فیلترهای اعمال شده
- تعداد نتایج
- زمان جستجو
- نوع کاربر (عمده/تکی)

#### مدل داده:
```python
class UserSearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_query = db.Column(db.String(500))
    search_filters = db.Column(db.Text)  # JSON
    results_count = db.Column(db.Integer)
    clicked_product_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 2. ردیابی کلیک‌ها

#### داده‌های جمع‌آوری شده:
- محصول کلیک شده
- موقعیت در نتایج (rank)
- کوئری مرتبط
- زمان کلیک

### 3. گزارش‌های آنالیتیکس

#### گزارش‌های موجود:
1. **محبوب‌ترین جستجوها**: 10 جستجوی برتر
2. **جستجوهای بدون نتیجه**: برای بهبود
3. **نرخ تبدیل**: درصد کلیک به خرید
4. **جستجوهای رایج**: برای پیشنهادات بهتر

---

## 🔧 پیاده‌سازی فنی

### 1. Backend API Endpoints

#### `/api/search`
```python
@app.route('/api/search')
def api_search():
    """
    جستجوی محصولات با پشتیبانی از Meilisearch و SQL fallback
    
    Query Parameters:
    - q: Query string
    - brand_id: Filter by brand
    - category_id: Filter by category
    - vehicle_type_id: Filter by vehicle type
    - min_price: Minimum price
    - max_price: Maximum price
    - in_stock: Filter by stock (true/false)
    - sort: Sort criteria (relevance, price_asc, price_desc, newest, stock)
    - page: Page number
    - per_page: Results per page
    
    Returns:
    {
        "results": [...],
        "total": 100,
        "page": 1,
        "per_page": 12,
        "filters_applied": {...},
        "suggestions": [...]
    }
    """
    pass
```

#### `/api/search/suggestions`
```python
@app.route('/api/search/suggestions')
def api_search_suggestions():
    """
    دریافت پیشنهادات جستجو
    
    Query Parameters:
    - q: Query string (min 2 characters)
    - limit: Maximum suggestions (default: 10)
    - context: Search context (brand_id, category_id, etc.)
    
    Returns:
    {
        "suggestions": [
            {
                "type": "brand|model|product|category",
                "text": "Toyota",
                "text_fa": "تویوتا",
                "id": 1,
                "icon": "fas fa-car",
                "relevance": 0.95
            },
            ...
        ]
    }
    """
    pass
```

#### `/api/search/analytics`
```python
@app.route('/api/search/analytics')
@login_required
@admin_required
def api_search_analytics():
    """
    دریافت آمار و گزارش‌های جستجو (فقط برای ادمین)
    
    Returns:
    {
        "popular_searches": [...],
        "no_result_searches": [...],
        "conversion_rate": 0.15,
        "total_searches": 1000,
        "avg_results_per_search": 25
    }
    """
    pass
```

### 2. Frontend JavaScript

#### کلاس SearchEngine:
```javascript
class ProfessionalSearchEngine {
    constructor(options) {
        this.apiUrl = options.apiUrl || '/api/search';
        this.suggestionsUrl = options.suggestionsUrl || '/api/search/suggestions';
        this.debounceDelay = options.debounceDelay || 300;
        this.minQueryLength = options.minQueryLength || 2;
        this.cache = new Map();
        this.init();
    }
    
    init() {
        this.setupSearchInput();
        this.setupFilters();
        this.setupSorting();
        this.setupPagination();
    }
    
    async search(query, filters = {}, page = 1) {
        // Search logic with caching
    }
    
    async getSuggestions(query, context = {}) {
        // Suggestions logic with debouncing
    }
    
    highlightText(text, query) {
        // Highlight search terms in results
    }
    
    trackSearch(query, filters, resultsCount) {
        // Track search for analytics
    }
    
    trackClick(productId, rank) {
        // Track product clicks
    }
}
```

### 3. Integration with Meilisearch

#### استفاده از SearchService:
```python
from search_service import get_search_service

search_service = get_search_service()

# Check if Meilisearch is available
if search_service.is_available():
    # Use Meilisearch
    results = search_service.search(
        query=query,
        filters=filters,
        sort=sort,
        page=page,
        per_page=per_page
    )
else:
    # Fallback to SQL search
    results = sql_search(query, filters, page, per_page)
```

---

## 📱 پشتیبانی موبایل

### 1. Responsive Design

#### Breakpoints:
- **Mobile**: < 576px
- **Tablet**: 576px - 992px
- **Desktop**: > 992px

#### ویژگی‌های موبایل:
- نوار جستجو تمام عرض
- فیلترهای قابل جمع‌شدن
- نمایش نتایج به صورت کارت
- دکمه‌های بزرگ برای لمس راحت

### 2. Touch Gestures

- Swipe برای تغییر صفحه
- Pull to refresh
- Long press برای منوی سریع

---

## 🧪 تست و کیفیت

### 1. Unit Tests

```python
def test_exact_match_search():
    """Test exact match search"""
    results = search_engine.search("SKU123")
    assert len(results) > 0
    assert results[0]['sku'] == "SKU123"

def test_fuzzy_search():
    """Test fuzzy search with typos"""
    results = search_engine.search("toyta")  # typo for "toyota"
    assert len(results) > 0

def test_persian_normalization():
    """Test Persian text normalization"""
    results = search_engine.search("تویوتا")
    # Should also find "تويوتا" (with Arabic yeh)
    assert len(results) > 0
```

### 2. Performance Tests

- تست سرعت جستجو (< 200ms)
- تست با حجم بالای داده (100K+ محصول)
- تست همزمان (Concurrent requests)

### 3. User Acceptance Tests

- تست با کاربران واقعی
- جمع‌آوری بازخورد
- بهبود بر اساس بازخورد

---

## 🚀 مراحل پیاده‌سازی

### فاز 1: زیرساخت (هفته 1)
- [ ] نصب و راه‌اندازی Meilisearch
- [ ] پیاده‌سازی SearchService
- [ ] همگام‌سازی اولیه محصولات
- [ ] تست اتصال و عملکرد

### فاز 2: Backend API (هفته 2)
- [ ] پیاده‌سازی `/api/search`
- [ ] پیاده‌سازی `/api/search/suggestions`
- [ ] پیاده‌سازی سیستم امتیازدهی
- [ ] پیاده‌سازی فیلترها

### فاز 3: Frontend UI (هفته 3)
- [ ] طراحی و پیاده‌سازی نوار جستجو
- [ ] پیاده‌سازی پیشنهادات
- [ ] پیاده‌سازی فیلترهای جانبی
- [ ] پیاده‌سازی نمایش نتایج

### فاز 4: بهینه‌سازی (هفته 4)
- [ ] پیاده‌سازی Caching
- [ ] بهینه‌سازی Query
- [ ] بهبود UX
- [ ] تست عملکرد

### فاز 5: آنالیتیکس (هفته 5)
- [ ] پیاده‌سازی ردیابی جستجوها
- [ ] پیاده‌سازی ردیابی کلیک‌ها
- [ ] ایجاد داشبورد آنالیتیکس
- [ ] گزارش‌های آماری

### فاز 6: تست و انتشار (هفته 6)
- [ ] تست کامل سیستم
- [ ] رفع باگ‌ها
- [ ] مستندسازی
- [ ] انتشار نسخه نهایی

---

## 📝 چک‌لیست نهایی

### عملکرد
- [ ] جستجو در کمتر از 200ms
- [ ] پیشنهادات در کمتر از 100ms
- [ ] پشتیبانی از 100K+ محصول
- [ ] Cache برای بهبود عملکرد

### تجربه کاربری
- [ ] رابط کاربری زیبا و کاربرپسند
- [ ] پیشنهادات هوشمند و دقیق
- [ ] فیلترهای قدرتمند
- [ ] نمایش نتایج واضح

### پشتیبانی فارسی
- [ ] نرمال‌سازی کامل متن فارسی
- [ ] جستجوی بدون حساسیت به حروف صدادار
- [ ] پشتیبانی از اعداد فارسی/عربی
- [ ] مترادف‌های رایج

### آنالیتیکس
- [ ] ردیابی جستجوها
- [ ] ردیابی کلیک‌ها
- [ ] گزارش‌های آماری
- [ ] داشبورد مدیریت

### امنیت
- [ ] اعتبارسنجی ورودی‌ها
- [ ] محافظت در برابر SQL Injection
- [ ] Rate Limiting
- [ ] CSRF Protection

---

## 🔗 منابع و مراجع

### مستندات
- [Meilisearch Documentation](https://www.meilisearch.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### کتابخانه‌های پیشنهادی
- `meilisearch`: برای اتصال به Meilisearch
- `flask-caching`: برای Caching
- `fuzzywuzzy`: برای جستجوی فازی (اختیاری)

---

## 📞 پشتیبانی

در صورت بروز مشکل یا نیاز به راهنمایی:
1. بررسی لاگ‌های سیستم
2. بررسی مستندات Meilisearch
3. تماس با تیم توسعه

---

**نسخه**: 1.0  
**تاریخ**: 2024  
**نویسنده**: تیم توسعه آسیا سلمان

