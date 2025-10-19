/**
 * Customer Invoice Management JavaScript
 * Handles all client-side functionality for invoice management in customer profile
 */

// Global variables
let currentPage = 1;
let totalPages = 1;
let currentFilters = {};

// Initialize dashboard
function loadDashboard() {
    loadInvoices();
    updateStatistics();
}

// Load invoices with pagination and filters
function loadInvoices(page = 1) {
    currentPage = page;
    
    // Show loading state
    showLoading();
    
    // Build query parameters
    const params = new URLSearchParams({
        page: page,
        per_page: 10,
        ...currentFilters
    });
    
    // Make API request
    fetch(`/api/profile/invoices?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert('خطا در بارگذاری فاکتورها: ' + data.error, 'danger');
                return;
            }
            
            // Update statistics
            updateStatisticsCards(data.statistics);
            
            // Render invoices table
            renderInvoicesTable(data.invoices);
            
            // Update pagination
            updatePagination(data.pagination);
            
            // Update count
            document.getElementById('invoices-count').textContent = 
                `${data.pagination.total} فاکتور`;
            
            hideLoading();
        })
        .catch(error => {
            console.error('Error loading invoices:', error);
            showAlert('خطا در بارگذاری فاکتورها', 'danger');
            hideLoading();
        });
}

// Update statistics cards
function updateStatisticsCards(stats) {
    document.getElementById('total-invoices').textContent = stats.total_invoices || 0;
    document.getElementById('pending-invoices').textContent = stats.pending_approval || 0;
    document.getElementById('approved-invoices').textContent = 
        (stats.auto_approved || 0) + (stats.manual_approved || 0);
    document.getElementById('total-amount').textContent = 
        formatCurrency(stats.total_amount || 0);
}

// Render invoices table
function renderInvoicesTable(invoices) {
    const tbody = document.getElementById('invoices-tbody');
    
    if (invoices.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <div class="text-muted">
                        <i class="fas fa-inbox fa-3x mb-3"></i>
                        <p>هیچ فاکتوری یافت نشد</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = invoices.map(invoice => `
        <tr class="fade-in">
            <td>
                <strong>${invoice.invoice_number}</strong>
                ${invoice.customer_type === 'bulk' ? 
                    '<span class="badge bg-primary ms-2">عمده</span>' : 
                    '<span class="badge bg-secondary ms-2">تکی</span>'
                }
            </td>
            <td>
                <div class="fw-bold">${formatCurrency(invoice.total_amount)}</div>
                ${invoice.bulk_discount_applied > 0 ? 
                    `<small class="text-success">تخفیف: ${invoice.bulk_discount_applied}%</small>` : ''
                }
            </td>
            <td>
                <span class="badge ${invoice.payment_type === 'cash' ? 'bg-success' : 'bg-info'}">
                    ${invoice.payment_type === 'cash' ? 'نقدی' : 'چکی'}
                </span>
            </td>
            <td>
                <span class="status-badge status-${invoice.approval_workflow_status}">
                    ${getStatusText(invoice.approval_workflow_status)}
                </span>
            </td>
            <td>
                <div>${formatDate(invoice.created_at)}</div>
                ${invoice.due_date ? `<small class="text-muted">سررسید: ${formatDate(invoice.due_date)}</small>` : ''}
            </td>
            <td>
                <div class="d-flex align-items-center justify-content-center">
                    <span class="badge bg-info me-1">${invoice.documents_count}</span>
                    <span class="badge bg-success">${invoice.approved_documents_count}</span>
                </div>
                ${invoice.document_required ? 
                    '<small class="text-warning d-block">نیاز به مدرک</small>' : ''
                }
            </td>
            <td>
                <div class="btn-group" role="group">
                    <button class="action-btn btn-view" onclick="viewInvoice(${invoice.id})" title="مشاهده">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${invoice.document_required && invoice.approval_workflow_status === 'pending' ? 
                        `<button class="action-btn btn-upload" onclick="openUploadModal(${invoice.id})" title="بارگذاری مدرک">
                            <i class="fas fa-upload"></i>
                        </button>` : ''
                    }
                    ${invoice.approval_workflow_status === 'pending' ? 
                        `<button class="action-btn btn-approve" onclick="openApprovalModal(${invoice.id}, 'approve')" title="تایید">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="action-btn btn-reject" onclick="openApprovalModal(${invoice.id}, 'reject')" title="رد">
                            <i class="fas fa-times"></i>
                        </button>` : ''
                    }
                </div>
            </td>
        </tr>
    `).join('');
}

// Update pagination
function updatePagination(pagination) {
    const nav = document.getElementById('pagination-nav');
    const ul = document.getElementById('pagination-ul');
    
    if (pagination.pages <= 1) {
        nav.style.display = 'none';
        return;
    }
    
    nav.style.display = 'block';
    
    let paginationHTML = '';
    
    // Previous button
    if (pagination.has_prev) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadInvoices(${pagination.page - 1})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    }
    
    // Page numbers
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.pages, pagination.page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === pagination.page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadInvoices(${i})">${i}</a>
            </li>
        `;
    }
    
    // Next button
    if (pagination.has_next) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="loadInvoices(${pagination.page + 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
    }
    
    ul.innerHTML = paginationHTML;
}

// Apply filters
function applyFilters() {
    currentFilters = {
        status: document.getElementById('status-filter').value,
        customer_type: document.getElementById('customer-type-filter').value,
        date_from: document.getElementById('date-from-filter').value,
        date_to: document.getElementById('date-to-filter').value
    };
    
    // Remove empty filters
    Object.keys(currentFilters).forEach(key => {
        if (!currentFilters[key]) {
            delete currentFilters[key];
        }
    });
    
    loadInvoices(1);
}

// Clear filters
function clearFilters() {
    document.getElementById('status-filter').value = '';
    document.getElementById('customer-type-filter').value = '';
    document.getElementById('date-from-filter').value = '';
    document.getElementById('date-to-filter').value = '';
    
    currentFilters = {};
    loadInvoices(1);
}

// View invoice details
function viewInvoice(invoiceId) {
    fetch(`/api/profile/invoices/${invoiceId}/status`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert('خطا در بارگذاری جزئیات فاکتور: ' + data.error, 'danger');
                return;
            }
            
            renderInvoiceDetail(data);
            new bootstrap.Modal(document.getElementById('invoiceDetailModal')).show();
        })
        .catch(error => {
            console.error('Error loading invoice details:', error);
            showAlert('خطا در بارگذاری جزئیات فاکتور', 'danger');
        });
}

// Render invoice detail
function renderInvoiceDetail(invoice) {
    const content = document.getElementById('invoice-detail-content');
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>اطلاعات فاکتور</h6>
                <table class="table table-sm">
                    <tr><td>شماره فاکتور:</td><td><strong>${invoice.invoice_number}</strong></td></tr>
                    <tr><td>وضعیت:</td><td><span class="status-badge status-${invoice.approval_workflow_status}">${getStatusText(invoice.approval_workflow_status)}</span></td></tr>
                    <tr><td>نوع مشتری:</td><td>${invoice.customer_type === 'bulk' ? 'عمده' : 'تکی'}</td></tr>
                    <tr><td>تاریخ ایجاد:</td><td>${formatDate(invoice.created_at)}</td></tr>
                    <tr><td>نیاز به مدرک:</td><td>${invoice.document_required ? 'بله' : 'خیر'}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6>وضعیت فرآیند</h6>
                ${invoice.workflow ? `
                    <table class="table table-sm">
                        <tr><td>وضعیت فرآیند:</td><td>${getStatusText(invoice.workflow.status)}</td></tr>
                        <tr><td>تایید خودکار:</td><td>${invoice.workflow.auto_approval_eligible ? 'بله' : 'خیر'}</td></tr>
                        <tr><td>تایید دستی:</td><td>${invoice.workflow.manual_approval_required ? 'بله' : 'خیر'}</td></tr>
                        <tr><td>اولویت:</td><td>${invoice.workflow.priority_level}</td></tr>
                        ${invoice.workflow.deadline ? `<tr><td>مهلت:</td><td>${formatDate(invoice.workflow.deadline)}</td></tr>` : ''}
                        ${invoice.workflow.approval_notes ? `<tr><td>یادداشت:</td><td>${invoice.workflow.approval_notes}</td></tr>` : ''}
                    </table>
                ` : '<p class="text-muted">اطلاعات فرآیند در دسترس نیست</p>'}
            </div>
        </div>
        
        ${invoice.documents && invoice.documents.length > 0 ? `
            <div class="mt-4">
                <h6>مدارک بارگذاری شده</h6>
                <div class="row">
                    ${invoice.documents.map(doc => `
                        <div class="col-md-4 mb-3">
                            <div class="card">
                                <div class="card-body">
                                    <h6 class="card-title">${getDocumentTypeText(doc.type)}</h6>
                                    <p class="card-text">
                                        <small class="text-muted">بارگذاری: ${formatDate(doc.uploaded_at)}</small><br>
                                        <span class="badge ${doc.approval_status === 'approved' ? 'bg-success' : doc.approval_status === 'rejected' ? 'bg-danger' : 'bg-warning'}">
                                            ${getApprovalStatusText(doc.approval_status)}
                                        </span>
                                    </p>
                                    ${doc.approval_status === 'rejected' && doc.rejection_reason ? 
                                        `<small class="text-danger">دلیل رد: ${doc.rejection_reason}</small>` : ''
                                    }
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
}

// Open upload modal
function openUploadModal(invoiceId) {
    document.getElementById('upload-invoice-id').value = invoiceId;
    document.getElementById('document-upload-form').reset();
    new bootstrap.Modal(document.getElementById('documentUploadModal')).show();
}

// Upload document
function uploadDocument() {
    const invoiceId = document.getElementById('upload-invoice-id').value;
    const documentType = document.getElementById('document-type').value;
    const file = document.getElementById('document-file').files[0];
    const description = document.getElementById('document-description').value;
    
    if (!documentType || !file) {
        showAlert('لطفاً نوع مدرک و فایل را انتخاب کنید', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('file', file);
    formData.append('description', description);
    
    showLoading();
    
    fetch(`/api/profile/invoices/${invoiceId}/upload-document`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('مدرک با موفقیت بارگذاری شد', 'success');
            bootstrap.Modal.getInstance(document.getElementById('documentUploadModal')).hide();
            loadInvoices(currentPage);
        } else {
            showAlert('خطا در بارگذاری مدرک: ' + data.error, 'danger');
        }
        hideLoading();
    })
    .catch(error => {
        console.error('Error uploading document:', error);
        showAlert('خطا در بارگذاری مدرک', 'danger');
        hideLoading();
    });
}

// Open approval modal
function openApprovalModal(invoiceId, action) {
    document.getElementById('approval-invoice-id').value = invoiceId;
    
    const modal = document.getElementById('approvalModal');
    const title = document.getElementById('approval-modal-title');
    const label = document.getElementById('approval-label');
    const notesField = document.getElementById('approval-notes');
    const reasonDiv = document.getElementById('rejection-reason-div');
    const reasonField = document.getElementById('rejection-reason');
    const approveBtn = document.getElementById('approve-btn');
    const rejectBtn = document.getElementById('reject-btn');
    
    if (action === 'approve') {
        title.textContent = 'تایید فاکتور';
        label.textContent = 'یادداشت تایید (اختیاری)';
        notesField.placeholder = 'یادداشت خود را وارد کنید...';
        reasonDiv.style.display = 'none';
        approveBtn.style.display = 'inline-block';
        rejectBtn.style.display = 'none';
        reasonField.required = false;
    } else {
        title.textContent = 'رد فاکتور';
        label.textContent = 'یادداشت رد (اختیاری)';
        notesField.placeholder = 'یادداشت خود را وارد کنید...';
        reasonDiv.style.display = 'block';
        approveBtn.style.display = 'none';
        rejectBtn.style.display = 'inline-block';
        reasonField.required = true;
    }
    
    new bootstrap.Modal(modal).show();
}

// Approve invoice
function approveInvoice() {
    const invoiceId = document.getElementById('approval-invoice-id').value;
    const notes = document.getElementById('approval-notes').value;
    
    const data = {
        approval_notes: notes
    };
    
    showLoading();
    
    fetch(`/api/profile/invoices/${invoiceId}/approve`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('فاکتور با موفقیت تایید شد', 'success');
            bootstrap.Modal.getInstance(document.getElementById('approvalModal')).hide();
            loadInvoices(currentPage);
        } else {
            showAlert('خطا در تایید فاکتور: ' + data.error, 'danger');
        }
        hideLoading();
    })
    .catch(error => {
        console.error('Error approving invoice:', error);
        showAlert('خطا در تایید فاکتور', 'danger');
        hideLoading();
    });
}

// Reject invoice
function rejectInvoice() {
    const invoiceId = document.getElementById('approval-invoice-id').value;
    const notes = document.getElementById('approval-notes').value;
    const reason = document.getElementById('rejection-reason').value;
    
    if (!reason.trim()) {
        showAlert('لطفاً دلیل رد را وارد کنید', 'warning');
        return;
    }
    
    const data = {
        customer_notes: notes,
        rejection_reason: reason
    };
    
    showLoading();
    
    fetch(`/api/profile/invoices/${invoiceId}/reject`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('فاکتور رد شد', 'success');
            bootstrap.Modal.getInstance(document.getElementById('approvalModal')).hide();
            loadInvoices(currentPage);
        } else {
            showAlert('خطا در رد فاکتور: ' + data.error, 'danger');
        }
        hideLoading();
    })
    .catch(error => {
        console.error('Error rejecting invoice:', error);
        showAlert('خطا در رد فاکتور', 'danger');
        hideLoading();
    });
}

// Load bulk benefits (for bulk customers)
function loadBulkBenefits() {
    fetch('/api/profile/bulk-benefits')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading bulk benefits:', data.error);
                return;
            }
            
            renderBulkBenefits(data);
        })
        .catch(error => {
            console.error('Error loading bulk benefits:', error);
        });
}

// Render bulk benefits
function renderBulkBenefits(data) {
    const section = document.getElementById('bulk-benefits-section');
    const content = document.getElementById('bulk-benefits-content');
    
    if (!section || !content) return;
    
    content.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="benefit-item">
                    <div class="d-flex align-items-center">
                        <div class="benefit-icon">
                            <i class="fas fa-percentage"></i>
                        </div>
                        <div>
                            <div class="benefit-value">${data.profile.bulk_discount_percentage}%</div>
                            <div class="benefit-description">تخفیف عمده</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="benefit-item">
                    <div class="d-flex align-items-center">
                        <div class="benefit-icon">
                            <i class="fas fa-credit-card"></i>
                        </div>
                        <div>
                            <div class="benefit-value">${formatCurrency(data.profile.available_credit)}</div>
                            <div class="benefit-description">اعتبار موجود</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="row mt-3">
            <div class="col-12">
                <div class="alert alert-info">
                    <strong>سطح فعلی:</strong> ${data.level_info.current_level} | 
                    <strong>مجموع خرید:</strong> ${formatCurrency(data.level_info.total_purchase_amount)}
                </div>
            </div>
        </div>
    `;
    
    section.style.display = 'block';
}

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' ریال';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fa-IR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'در انتظار تایید',
        'auto_approved': 'تایید خودکار',
        'manual_approved': 'تایید دستی',
        'rejected': 'رد شده'
    };
    return statusMap[status] || status;
}

function getDocumentTypeText(type) {
    const typeMap = {
        'check': 'چک',
        'receipt': 'رسید',
        'bank_transfer': 'فیش بانکی'
    };
    return typeMap[type] || type;
}

function getApprovalStatusText(status) {
    const statusMap = {
        'pending': 'در انتظار تایید',
        'approved': 'تایید شده',
        'rejected': 'رد شده'
    };
    return statusMap[status] || status;
}

function showLoading() {
    document.body.classList.add('loading');
}

function hideLoading() {
    document.body.classList.remove('loading');
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of content
    const content = document.querySelector('.container-fluid');
    content.insertBefore(alertDiv, content.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function refreshDashboard() {
    loadDashboard();
    if (typeof loadBulkBenefits === 'function') {
        loadBulkBenefits();
    }
}
