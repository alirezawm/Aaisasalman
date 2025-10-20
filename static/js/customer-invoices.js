/**
 * Customer Invoices Management JavaScript
 * مدیریت فاکتورهای مشتریان
 */

$(document).ready(function() {
    // Initialize the page
    initializeCustomerInvoices();
    
    // Bind events
    bindEvents();
});

function initializeCustomerInvoices() {
    console.log('Customer Invoices page initialized');
    
    // Set up form validation
    setupFormValidation();
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
}

function bindEvents() {
    // Filter form submission
    $('#invoice-filters-form').on('submit', function(e) {
        e.preventDefault();
        applyFilters();
    });
    
    // Real-time search
    $('#user_search').on('input', debounce(function() {
        applyFilters();
    }, 500));
    
    // Status and payment type change
    $('#approval_status, #payment_type').on('change', function() {
        applyFilters();
    });
    
    // Date range changes
    $('#date_from, #date_to').on('change', function() {
        applyFilters();
    });
}

function setupFormValidation() {
    // Approve form validation
    $('#approve-invoice-form').on('submit', function(e) {
        e.preventDefault();
        submitApproveInvoice();
    });
    
    // Reject form validation
    $('#reject-invoice-form').on('submit', function(e) {
        e.preventDefault();
        submitRejectInvoice();
    });
}

function applyFilters() {
    const form = $('#invoice-filters-form');
    const formData = form.serialize();
    
    // Show loading indicator
    showLoadingIndicator();
    
    // Redirect with filters
    const url = new URL(window.location);
    const params = new URLSearchParams(formData);
    
    // Update URL parameters
    for (const [key, value] of params) {
        if (value) {
            url.searchParams.set(key, value);
        } else {
            url.searchParams.delete(key);
        }
    }
    
    // Remove page parameter to start from page 1
    url.searchParams.delete('page');
    
    // Redirect to filtered results
    window.location.href = url.toString();
}

function refreshInvoices() {
    // Reload the current page
    window.location.reload();
}

function viewInvoiceDetails(invoiceId) {
    console.log('Viewing invoice details for ID:', invoiceId);
    
    // Redirect to invoice detail page
    window.location.href = `/invoice/${invoiceId}`;
}

function displayInvoiceDetails(invoice) {
    const content = `
        <div class="row">
            <!-- Invoice Header -->
            <div class="col-12 mb-4">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white">
                        <div class="row align-items-center">
                            <div class="col-md-6">
                                <h5 class="mb-0">
                                    <i class="fas fa-file-invoice me-2"></i>فاکتور شماره ${invoice.invoice_number}
                                </h5>
                            </div>
                            <div class="col-md-6 text-end">
                                <span class="badge ${getStatusBadgeClass(invoice.approval_status)} fs-6">
                                    ${invoice.approval_status_display}
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>تاریخ ایجاد:</strong> ${invoice.created_at_persian}</p>
                                <p><strong>نوع پرداخت:</strong> ${invoice.payment_type_display}</p>
                                <p><strong>مبلغ کل:</strong> <span class="text-success fw-bold">${formatPrice(invoice.total_amount)} هزار ریال</span></p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>تعداد آیتم‌ها:</strong> ${invoice.items_count}</p>
                                <p><strong>تعداد اسناد:</strong> ${invoice.documents_count}</p>
                                ${invoice.due_date ? `<p><strong>تاریخ سررسید:</strong> ${formatDate(invoice.due_date)}</p>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Customer Information -->
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-user me-2"></i>اطلاعات مشتری
                        </h6>
                    </div>
                    <div class="card-body">
                        <p><strong>نام:</strong> ${invoice.customer.full_name}</p>
                        <p><strong>نام کاربری:</strong> ${invoice.customer.username}</p>
                        ${invoice.customer.company_name ? `<p><strong>شرکت:</strong> ${invoice.customer.company_name}</p>` : ''}
                        <p><strong>تلفن:</strong> ${invoice.customer.phone}</p>
                        ${invoice.customer.email ? `<p><strong>ایمیل:</strong> ${invoice.customer.email}</p>` : ''}
                        ${invoice.customer.address ? `<p><strong>آدرس:</strong> ${invoice.customer.address}</p>` : ''}
                        <p><strong>خریدار عمده:</strong> 
                            <span class="badge ${invoice.customer.is_bulk_buyer ? 'bg-success' : 'bg-secondary'}">
                                ${invoice.customer.is_bulk_buyer ? 'بله' : 'خیر'}
                            </span>
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Invoice Status -->
            <div class="col-md-6 mb-4">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h6 class="mb-0">
                            <i class="fas fa-info-circle me-2"></i>وضعیت فاکتور
                        </h6>
                    </div>
                    <div class="card-body">
                        <p><strong>وضعیت:</strong> 
                            <span class="badge ${getStatusBadgeClass(invoice.approval_status)}">
                                ${invoice.approval_status_display}
                            </span>
                        </p>
                        ${invoice.approval_date ? `<p><strong>تاریخ تایید/رد:</strong> ${formatDate(invoice.approval_date)}</p>` : ''}
                        ${invoice.approved_by ? `<p><strong>تایید/رد شده توسط:</strong> ${invoice.approved_by}</p>` : ''}
                        ${invoice.rejection_reason ? `<p><strong>دلیل رد:</strong> ${invoice.rejection_reason}</p>` : ''}
                        ${invoice.admin_notes ? `<p><strong>یادداشت مدیر:</strong> ${invoice.admin_notes}</p>` : ''}
                    </div>
                </div>
            </div>
            
            <!-- Invoice Items -->
            <div class="col-12 mb-4">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-shopping-cart me-2"></i>آیتم‌های فاکتور
                        </h6>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th>نام محصول</th>
                                        <th>کد محصول</th>
                                        <th>تعداد</th>
                                        <th>قیمت واحد</th>
                                        <th>قیمت کل</th>
                                        <th>نوع قیمت</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${invoice.items.map(item => `
                                        <tr>
                                            <td>${item.product_name}</td>
                                            <td><code>${item.product_sku}</code></td>
                                            <td>${item.quantity}</td>
                                            <td>${formatPrice(item.unit_price)} هزار ریال</td>
                                            <td class="fw-bold text-success">${formatPrice(item.total_price)} هزار ریال</td>
                                            <td>
                                                <span class="badge ${item.price_type === 'cash' ? 'bg-success' : 'bg-primary'}">
                                                    ${item.price_type === 'cash' ? 'نقدی' : 'چکی'}
                                                </span>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Documents -->
            ${invoice.documents.length > 0 ? `
            <div class="col-12 mb-4">
                <div class="card">
                    <div class="card-header bg-secondary text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-file-alt me-2"></i>اسناد فاکتور
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            ${invoice.documents.map(doc => `
                                <div class="col-md-6 mb-3">
                                    <div class="card border">
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-start">
                                                <div>
                                                    <h6 class="card-title">
                                                        <i class="fas fa-file-${doc.document_type === 'check' ? 'check' : 'receipt'} me-2"></i>
                                                        ${doc.document_type_display}
                                                    </h6>
                                                    <p class="card-text text-muted">
                                                        <small>بارگذاری شده: ${formatDate(doc.uploaded_at)}</small>
                                                    </p>
                                                    <span class="badge ${doc.is_approved ? 'bg-success' : 'bg-warning'}">
                                                        ${doc.is_approved ? 'تایید شده' : 'در انتظار تایید'}
                                                    </span>
                                                </div>
                                                <div>
                                                    <a href="/static/${doc.file_path}" target="_blank" class="btn btn-sm btn-outline-primary">
                                                        <i class="fas fa-download me-1"></i>دانلود
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
            ` : ''}
        </div>
    `;
    
    $('#invoice-details-content').html(content);
}

function approveInvoice(invoiceId) {
    console.log('Approving invoice ID:', invoiceId);
    
    // Set invoice ID in form
    $('#approve-invoice-id').val(invoiceId);
    
    // Clear previous notes
    $('#approve-admin-notes').val('');
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('approveInvoiceModal'));
    modal.show();
}

function submitApproveInvoice() {
    const invoiceId = $('#approve-invoice-id').val();
    const adminNotes = $('#approve-admin-notes').val();
    
    if (!invoiceId) {
        showError('شناسه فاکتور یافت نشد');
        return;
    }
    
    // Show loading
    const submitBtn = $('#approveInvoiceModal .btn-success');
    const originalText = submitBtn.html();
    submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>در حال تایید...');
    submitBtn.prop('disabled', true);
    
    // Submit request
    $.ajax({
        url: `/api/profile/customer-invoices/${invoiceId}/approve`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({
            admin_notes: adminNotes
        }),
        success: function(response) {
            if (response.success) {
                showSuccess(response.message);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('approveInvoiceModal'));
                modal.hide();
                
                // Refresh the page
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showError('خطا در تایید فاکتور: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error approving invoice:', error);
            let errorMessage = 'خطا در تایید فاکتور';
            
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            
            showError(errorMessage);
        },
        complete: function() {
            // Restore button
            submitBtn.html(originalText);
            submitBtn.prop('disabled', false);
        }
    });
}

function rejectInvoice(invoiceId) {
    console.log('Rejecting invoice ID:', invoiceId);
    
    // Set invoice ID in form
    $('#reject-invoice-id').val(invoiceId);
    
    // Clear previous data
    $('#reject-reason').val('');
    $('#reject-admin-notes').val('');
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('rejectInvoiceModal'));
    modal.show();
}

function submitRejectInvoice() {
    const invoiceId = $('#reject-invoice-id').val();
    const rejectionReason = $('#reject-reason').val();
    const adminNotes = $('#reject-admin-notes').val();
    
    if (!invoiceId) {
        showError('شناسه فاکتور یافت نشد');
        return;
    }
    
    if (!rejectionReason.trim()) {
        showError('دلیل رد فاکتور الزامی است');
        $('#reject-reason').focus();
        return;
    }
    
    // Show loading
    const submitBtn = $('#rejectInvoiceModal .btn-danger');
    const originalText = submitBtn.html();
    submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>در حال رد...');
    submitBtn.prop('disabled', true);
    
    // Submit request
    $.ajax({
        url: `/api/profile/customer-invoices/${invoiceId}/reject`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({
            rejection_reason: rejectionReason,
            admin_notes: adminNotes
        }),
        success: function(response) {
            if (response.success) {
                showSuccess(response.message);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('rejectInvoiceModal'));
                modal.hide();
                
                // Refresh the page
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showError('خطا در رد فاکتور: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error rejecting invoice:', error);
            let errorMessage = 'خطا در رد فاکتور';
            
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            
            showError(errorMessage);
        },
        complete: function() {
            // Restore button
            submitBtn.html(originalText);
            submitBtn.prop('disabled', false);
        }
    });
}

// Utility Functions

function getStatusBadgeClass(status) {
    switch (status) {
        case 'pending':
            return 'bg-warning';
        case 'approved':
            return 'bg-success';
        case 'rejected':
            return 'bg-danger';
        case 'under_review':
            return 'bg-info';
        default:
            return 'bg-secondary';
    }
}

function formatPrice(price) {
    return new Intl.NumberFormat('fa-IR').format(price);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
}

function showLoadingIndicator() {
    // You can implement a global loading indicator here
    console.log('Loading...');
}

function showSuccess(message) {
    // Create and show success alert
    const alert = $(`
        <div class="alert alert-success alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            <i class="fas fa-check-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.alert('close');
    }, 5000);
}

function showError(message) {
    // Create and show error alert
    const alert = $(`
        <div class="alert alert-danger alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            <i class="fas fa-exclamation-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(alert);
    
    // Auto remove after 7 seconds
    setTimeout(() => {
        alert.alert('close');
    }, 7000);
}

// Debounce function for search input
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
