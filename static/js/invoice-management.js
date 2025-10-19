/**
 * اسکریپت‌های مدیریت فاکتورها
 * شامل جستجوی زنده، فیلترهای پویا، و مدیریت مدال‌ها
 */

// متغیرهای سراسری
let currentFilters = {};
let isLoading = false;

// مقداردهی اولیه
document.addEventListener('DOMContentLoaded', function() {
    initializeInvoiceManagement();
    setupEventListeners();
    loadStatistics();
});

/**
 * مقداردهی اولیه سیستم مدیریت فاکتورها
 */
function initializeInvoiceManagement() {
    // تنظیم فیلترهای فعلی
    currentFilters = {
        approval_status: document.getElementById('approval_status')?.value || '',
        payment_type: document.getElementById('payment_type')?.value || '',
        user_search: document.getElementById('user_search')?.value || '',
        date_from: document.getElementById('date_from')?.value || '',
        date_to: document.getElementById('date_to')?.value || '',
        amount_min: document.getElementById('amount_min')?.value || '',
        amount_max: document.getElementById('amount_max')?.value || ''
    };
    
    // تنظیم تاریخ‌های پیش‌فرض
    setupDefaultDates();
    
    // تنظیم جستجوی زنده
    setupLiveSearch();
    
    // تنظیم فیلترهای پویا
    setupDynamicFilters();
}

/**
 * تنظیم event listener ها
 */
function setupEventListeners() {
    // جستجوی زنده
    const userSearchInput = document.getElementById('user_search');
    if (userSearchInput) {
        userSearchInput.addEventListener('input', debounce(handleLiveSearch, 500));
    }
    
    // فیلترهای پویا
    const filterInputs = document.querySelectorAll('#approval_status, #payment_type, #date_from, #date_to, #amount_min, #amount_max');
    filterInputs.forEach(input => {
        input.addEventListener('change', handleFilterChange);
    });
    
    // مدیریت فرم‌های مدال
    setupModalForms();
    
    // مدیریت تصاویر
    setupImageHandlers();
}

/**
 * تنظیم تاریخ‌های پیش‌فرض
 */
function setupDefaultDates() {
    const dateFromInput = document.getElementById('date_from');
    const dateToInput = document.getElementById('date_to');
    
    if (dateFromInput && !dateFromInput.value) {
        // تاریخ 30 روز قبل
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        dateFromInput.value = thirtyDaysAgo.toISOString().split('T')[0];
    }
    
    if (dateToInput && !dateToInput.value) {
        // تاریخ امروز
        const today = new Date();
        dateToInput.value = today.toISOString().split('T')[0];
    }
}

/**
 * تنظیم جستجوی زنده
 */
function setupLiveSearch() {
    const searchInput = document.getElementById('user_search');
    if (!searchInput) return;
    
    // نمایش پیشنهادات
    searchInput.addEventListener('focus', function() {
        showSearchSuggestions();
    });
    
    searchInput.addEventListener('blur', function() {
        setTimeout(hideSearchSuggestions, 200);
    });
}

/**
 * مدیریت جستجوی زنده
 */
function handleLiveSearch(event) {
    const query = event.target.value.trim();
    currentFilters.user_search = query;
    
    if (query.length >= 2) {
        searchInvoices();
    } else if (query.length === 0) {
        // اگر جستجو خالی شد، نتایج را بازنشانی کن
        resetSearch();
    }
}

/**
 * مدیریت تغییر فیلترها
 */
function handleFilterChange(event) {
    const filterName = event.target.name;
    const filterValue = event.target.value;
    
    currentFilters[filterName] = filterValue;
    
    // اعمال فیلتر با تاخیر
    debounce(applyFilters, 300)();
}

/**
 * اعمال فیلترها
 */
function applyFilters() {
    if (isLoading) return;
    
    isLoading = true;
    showLoadingIndicator();
    
    // ساخت URL با فیلترها
    const url = buildFilterUrl();
    
    // درخواست AJAX
    fetch(url)
        .then(response => response.json())
        .then(data => {
            updateInvoiceTable(data);
            updateStatistics(data.statistics);
        })
        .catch(error => {
            console.error('خطا در اعمال فیلترها:', error);
            showError('خطا در اعمال فیلترها');
        })
        .finally(() => {
            isLoading = false;
            hideLoadingIndicator();
        });
}

/**
 * ساخت URL با فیلترها
 */
function buildFilterUrl() {
    const params = new URLSearchParams();
    
    Object.keys(currentFilters).forEach(key => {
        if (currentFilters[key]) {
            params.append(key, currentFilters[key]);
        }
    });
    
    return `/api/admin/invoices/search?${params.toString()}`;
}

/**
 * جستجوی فاکتورها
 */
function searchInvoices() {
    if (isLoading) return;
    
    isLoading = true;
    showLoadingIndicator();
    
    fetch(buildFilterUrl())
        .then(response => response.json())
        .then(data => {
            updateInvoiceTable(data);
        })
        .catch(error => {
            console.error('خطا در جستجو:', error);
            showError('خطا در جستجو');
        })
        .finally(() => {
            isLoading = false;
            hideLoadingIndicator();
        });
}

/**
 * بازنشانی جستجو
 */
function resetSearch() {
    currentFilters.user_search = '';
    applyFilters();
}

/**
 * بروزرسانی جدول فاکتورها
 */
function updateInvoiceTable(data) {
    const tbody = document.querySelector('.table tbody');
    if (!tbody) return;
    
    if (data.invoices && data.invoices.length > 0) {
        tbody.innerHTML = data.invoices.map(invoice => createInvoiceRow(invoice)).join('');
    } else {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5">
                    <i class="fas fa-file-invoice fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">هیچ فاکتوری یافت نشد</h5>
                    <p class="text-muted">با فیلترهای مختلف جستجو کنید</p>
                </td>
            </tr>
        `;
    }
    
    // بروزرسانی صفحه‌بندی
    updatePagination(data);
}

/**
 * ایجاد ردیف جدول فاکتور
 */
function createInvoiceRow(invoice) {
    const statusBadge = getStatusBadge(invoice.approval_status);
    const paymentBadge = getPaymentBadge(invoice.payment_type);
    const actions = getActionButtons(invoice);
    
    return `
        <tr>
            <td>
                <strong>${invoice.invoice_number}</strong>
                <div class="text-muted small">#${invoice.id}</div>
            </td>
            <td>
                <div>${invoice.customer_name}</div>
                ${invoice.customer_company ? `<div class="text-muted small">${invoice.customer_company}</div>` : ''}
            </td>
            <td>
                <strong class="text-primary">${formatPrice(invoice.total_amount)}</strong>
            </td>
            <td>${paymentBadge}</td>
            <td>${statusBadge}</td>
            <td>${formatPersianDate(invoice.created_at)}</td>
            <td>${actions}</td>
        </tr>
    `;
}

/**
 * دریافت badge وضعیت
 */
function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge bg-warning">در انتظار تایید</span>',
        'approved': '<span class="badge bg-success">تایید شده</span>',
        'rejected': '<span class="badge bg-danger">رد شده</span>',
        'under_review': '<span class="badge bg-info">در حال بررسی</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">نامشخص</span>';
}

/**
 * دریافت badge نوع پرداخت
 */
function getPaymentBadge(paymentType) {
    if (paymentType === 'cash') {
        return '<span class="badge bg-success">نقدی</span>';
    } else {
        return '<span class="badge bg-info">چکی</span>';
    }
}

/**
 * دریافت دکمه‌های عملیات
 */
function getActionButtons(invoice) {
    let buttons = `
        <a href="/admin/invoice/${invoice.id}" class="btn btn-success btn-sm">
            <i class="fas fa-eye"></i> مشاهده
        </a>
    `;
    
    if (invoice.approval_status === 'pending') {
        buttons += `
            <button type="button" class="btn btn-success btn-sm" onclick="showApproveModal(${invoice.id}, '${invoice.invoice_number}')">
                <i class="fas fa-check"></i> تایید
            </button>
            <button type="button" class="btn btn-danger btn-sm" onclick="showRejectModal(${invoice.id}, '${invoice.invoice_number}')">
                <i class="fas fa-times"></i> رد
            </button>
            <button type="button" class="btn btn-info btn-sm" onclick="showReviewModal(${invoice.id}, '${invoice.invoice_number}')">
                <i class="fas fa-search"></i> بررسی
            </button>
        `;
    }
    
    return `<div class="btn-group" role="group">${buttons}</div>`;
}

/**
 * بروزرسانی آمار
 */
function updateStatistics(stats) {
    if (!stats) return;
    
    const statElements = {
        'total_invoices': document.querySelector('.stat-card:nth-child(1) .stat-number'),
        'pending_approval': document.querySelector('.stat-card:nth-child(2) .stat-number'),
        'approved': document.querySelector('.stat-card:nth-child(3) .stat-number'),
        'rejected': document.querySelector('.stat-card:nth-child(4) .stat-number'),
        'under_review': document.querySelector('.stat-card:nth-child(5) .stat-number'),
        'total_amount': document.querySelector('.stat-card:nth-child(6) .stat-number')
    };
    
    Object.keys(statElements).forEach(key => {
        if (statElements[key] && stats[key] !== undefined) {
            animateNumber(statElements[key], stats[key]);
        }
    });
}

/**
 * انیمیشن اعداد
 */
function animateNumber(element, targetValue) {
    const startValue = parseInt(element.textContent) || 0;
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.round(startValue + (targetValue - startValue) * progress);
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

/**
 * بارگذاری آمار
 */
function loadStatistics() {
    fetch('/api/admin/invoices/statistics')
        .then(response => response.json())
        .then(data => {
            updateStatistics(data);
        })
        .catch(error => {
            console.error('خطا در بارگذاری آمار:', error);
        });
}

/**
 * تنظیم فرم‌های مدال
 */
function setupModalForms() {
    // اعتبارسنجی فرم‌ها
    const forms = document.querySelectorAll('#approveForm, #rejectForm, #reviewForm');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * اعتبارسنجی فرم
 */
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * تنظیم مدیریت تصاویر
 */
function setupImageHandlers() {
    // کلیک روی تصاویر برای نمایش در مدال
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'IMG' && e.target.closest('.document-preview')) {
            e.preventDefault();
            showImageModal(e.target.src);
        }
    });
}

/**
 * نمایش مدال تصویر
 */
function showImageModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    
    if (modal && modalImage) {
        modalImage.src = imageSrc;
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

/**
 * نمایش مدال تایید
 */
function showApproveModal(invoiceId, invoiceNumber) {
    const modal = document.getElementById('approveModal');
    const form = document.getElementById('approveForm');
    const message = document.getElementById('approveMessage');
    
    if (modal && form && message) {
        message.textContent = `آیا از تایید فاکتور ${invoiceNumber} اطمینان دارید؟`;
        form.action = `/admin/invoices/${invoiceId}/approve`;
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

/**
 * نمایش مدال رد
 */
function showRejectModal(invoiceId, invoiceNumber) {
    const modal = document.getElementById('rejectModal');
    const form = document.getElementById('rejectForm');
    const message = document.getElementById('rejectMessage');
    
    if (modal && form && message) {
        message.textContent = `آیا از رد فاکتور ${invoiceNumber} اطمینان دارید؟`;
        form.action = `/admin/invoices/${invoiceId}/reject`;
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

/**
 * نمایش مدال بررسی
 */
function showReviewModal(invoiceId, invoiceNumber) {
    const modal = document.getElementById('reviewModal');
    const form = document.getElementById('reviewForm');
    const message = document.getElementById('reviewMessage');
    
    if (modal && form && message) {
        message.textContent = `فاکتور ${invoiceNumber} به حالت "در حال بررسی" تنظیم خواهد شد.`;
        form.action = `/admin/invoices/${invoiceId}/set-review`;
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

/**
 * نمایش نشانگر لودینگ
 */
function showLoadingIndicator() {
    const loadingElement = document.getElementById('loadingIndicator');
    if (!loadingElement) {
        const loading = document.createElement('div');
        loading.id = 'loadingIndicator';
        loading.className = 'loading-overlay';
        loading.innerHTML = '<div class="loading"></div>';
        document.body.appendChild(loading);
    }
}

/**
 * مخفی کردن نشانگر لودینگ
 */
function hideLoadingIndicator() {
    const loadingElement = document.getElementById('loadingIndicator');
    if (loadingElement) {
        loadingElement.remove();
    }
}

/**
 * نمایش پیام خطا
 */
function showError(message) {
    // استفاده از toast یا alert
    if (typeof toastr !== 'undefined') {
        toastr.error(message);
    } else {
        alert(message);
    }
}

/**
 * نمایش پیام موفقیت
 */
function showSuccess(message) {
    if (typeof toastr !== 'undefined') {
        toastr.success(message);
    } else {
        alert(message);
    }
}

/**
 * فرمت قیمت
 */
function formatPrice(price) {
    return new Intl.NumberFormat('fa-IR').format(price) + ' هزار ریال';
}

/**
 * فرمت تاریخ فارسی
 */
function formatPersianDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
}

/**
 * تنظیم فیلترهای پویا
 */
function setupDynamicFilters() {
    // فیلتر مبلغ
    const amountMin = document.getElementById('amount_min');
    const amountMax = document.getElementById('amount_max');
    
    if (amountMin && amountMax) {
        amountMin.addEventListener('input', function() {
            if (this.value && amountMax.value && parseFloat(this.value) > parseFloat(amountMax.value)) {
                amountMax.value = this.value;
            }
        });
        
        amountMax.addEventListener('input', function() {
            if (this.value && amountMin.value && parseFloat(this.value) < parseFloat(amountMin.value)) {
                amountMin.value = this.value;
            }
        });
    }
    
    // فیلتر تاریخ
    const dateFrom = document.getElementById('date_from');
    const dateTo = document.getElementById('date_to');
    
    if (dateFrom && dateTo) {
        dateFrom.addEventListener('change', function() {
            if (this.value && dateTo.value && this.value > dateTo.value) {
                dateTo.value = this.value;
            }
        });
        
        dateTo.addEventListener('change', function() {
            if (this.value && dateFrom.value && this.value < dateFrom.value) {
                dateFrom.value = this.value;
            }
        });
    }
}

/**
 * نمایش پیشنهادات جستجو
 */
function showSearchSuggestions() {
    // پیاده‌سازی پیشنهادات جستجو
    console.log('نمایش پیشنهادات جستجو');
}

/**
 * مخفی کردن پیشنهادات جستجو
 */
function hideSearchSuggestions() {
    // پیاده‌سازی مخفی کردن پیشنهادات
    console.log('مخفی کردن پیشنهادات جستجو');
}

/**
 * بروزرسانی صفحه‌بندی
 */
function updatePagination(data) {
    // پیاده‌سازی بروزرسانی صفحه‌بندی
    console.log('بروزرسانی صفحه‌بندی', data);
}

/**
 * تابع debounce برای بهینه‌سازی عملکرد
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// اضافه کردن استایل‌های CSS برای لودینگ
const loadingStyles = `
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .loading {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .is-invalid {
        border-color: #dc3545 !important;
        box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
    }
`;

// اضافه کردن استایل‌ها به صفحه
const styleSheet = document.createElement('style');
styleSheet.textContent = loadingStyles;
document.head.appendChild(styleSheet);
