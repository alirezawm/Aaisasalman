/**
 * JavaScript برای سیستم امتیازدهی
 * مدیریت تعاملات کاربری مربوط به امتیازات و جوایز
 */

/**
 * Helper function برای بررسی JSON بودن response
 */
async function safeJsonResponse(response) {
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
        // احتمالاً redirect به صفحه login شده است
        return null;
    }
    try {
        return await response.json();
    } catch (error) {
        if (error instanceof SyntaxError && error.message.includes('JSON')) {
            // احتمالاً HTML دریافت شده (redirect به login)
            return null;
        }
        throw error;
    }
}

class PointsSystem {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadUserPoints();
    }

    bindEvents() {
        // رویدادهای مربوط به استفاده از جوایز
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="redeem-reward"]')) {
                this.redeemReward(e.target.dataset.rewardId);
            }
        });

        // رویدادهای مربوط به نمایش جزئیات تراکنش
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="show-transaction-details"]')) {
                this.showTransactionDetails(e.target.dataset.transactionId);
            }
        });
    }

    /**
     * بارگذاری امتیازات کاربر
     */
    async loadUserPoints() {
        try {
            const response = await fetch('/api/points/user');
            const data = await safeJsonResponse(response);
            
            if (data && data.success) {
                this.updatePointsDisplay(data.data);
            }
        } catch (error) {
            console.error('خطا در بارگذاری امتیازات:', error);
        }
    }

    /**
     * به‌روزرسانی نمایش امتیازات
     */
    updatePointsDisplay(pointsData) {
        // به‌روزرسانی امتیاز فعلی
        const currentPointsElement = document.getElementById('current-points');
        if (currentPointsElement) {
            currentPointsElement.textContent = pointsData.current_points.toLocaleString();
        }

        // به‌روزرسانی مجموع امتیازات کسب شده
        const totalEarnedElement = document.getElementById('total-earned');
        if (totalEarnedElement) {
            totalEarnedElement.textContent = pointsData.total_earned.toLocaleString();
        }

        // به‌روزرسانی مجموع امتیازات خرج شده
        const totalSpentElement = document.getElementById('total-spent');
        if (totalSpentElement) {
            totalSpentElement.textContent = pointsData.total_spent.toLocaleString();
        }

        // به‌روزرسانی سطح کاربر
        if (pointsData.user_level) {
            this.updateUserLevel(pointsData.user_level);
        }
    }

    /**
     * به‌روزرسانی نمایش سطح کاربر
     */
    updateUserLevel(levelData) {
        const levelElement = document.getElementById('user-level');
        if (levelElement) {
            levelElement.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="me-3">
                        ${this.getLevelIcon(levelData.name)}
                    </div>
                    <div>
                        <h4 class="mb-1">${levelData.name_fa}</h4>
                        ${levelData.discount_percentage > 0 ? 
                            `<p class="text-success mb-0">تخفیف ویژه: ${levelData.discount_percentage}%</p>` :
                            `<p class="text-muted mb-0">بدون تخفیف ویژه</p>`
                        }
                    </div>
                </div>
            `;
        }
    }

    /**
     * دریافت آیکون سطح کاربر
     */
    getLevelIcon(levelName) {
        const icons = {
            'Bronze': '<i class="fas fa-medal text-warning fa-2x"></i>',
            'Silver': '<i class="fas fa-medal text-secondary fa-2x"></i>',
            'Gold': '<i class="fas fa-medal text-warning fa-2x"></i>',
            'Platinum': '<i class="fas fa-crown text-primary fa-2x"></i>'
        };
        return icons[levelName] || '<i class="fas fa-star text-info fa-2x"></i>';
    }

    /**
     * استفاده از جایزه
     */
    async redeemReward(rewardId) {
        if (!confirm('آیا مطمئن هستید که می‌خواهید از این جایزه استفاده کنید؟')) {
            return;
        }

        try {
            const response = await fetch('/api/rewards/redeem', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    reward_id: rewardId
                })
            });

            const data = await safeJsonResponse(response);
            if (!data) {
                this.showErrorMessage('لطفاً ابتدا وارد حساب کاربری خود شوید');
                return;
            }

            if (data.success) {
                this.showSuccessMessage(data.message);
                this.loadUserPoints(); // بارگذاری مجدد امتیازات
                this.loadAvailableRewards(); // بارگذاری مجدد جوایز
            } else {
                this.showErrorMessage(data.message);
            }
        } catch (error) {
            console.error('خطا در استفاده از جایزه:', error);
            this.showErrorMessage('خطا در استفاده از جایزه');
        }
    }

    /**
     * بارگذاری جوایز قابل استفاده
     */
    async loadAvailableRewards() {
        try {
            const response = await fetch('/api/rewards');
            const data = await safeJsonResponse(response);
            
            if (data && data.success) {
                this.updateRewardsDisplay(data.data);
            }
        } catch (error) {
            console.error('خطا در بارگذاری جوایز:', error);
        }
    }

    /**
     * به‌روزرسانی نمایش جوایز
     */
    updateRewardsDisplay(rewards) {
        const rewardsContainer = document.getElementById('available-rewards');
        if (!rewardsContainer) return;

        if (rewards.length === 0) {
            rewardsContainer.innerHTML = '<p class="text-muted">هیچ جایزه‌ای در دسترس نیست.</p>';
            return;
        }

        const rewardsHTML = rewards.map(reward => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${reward.name_fa}</h5>
                        <p class="card-text">${reward.description_fa || ''}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-primary">${reward.points_required.toLocaleString()} امتیاز</span>
                            <button class="btn btn-success btn-sm" data-action="redeem-reward" data-reward-id="${reward.id}">
                                استفاده
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        rewardsContainer.innerHTML = `<div class="row">${rewardsHTML}</div>`;
    }

    /**
     * نمایش جزئیات تراکنش
     */
    async showTransactionDetails(transactionId) {
        try {
            const response = await fetch(`/api/points/transactions/${transactionId}`);
            const data = await safeJsonResponse(response);
            
            if (data && data.success) {
                this.showTransactionModal(data.data);
            }
        } catch (error) {
            console.error('خطا در بارگذاری جزئیات تراکنش:', error);
        }
    }

    /**
     * نمایش مودال جزئیات تراکنش
     */
    showTransactionModal(transaction) {
        const modalHTML = `
            <div class="modal fade" id="transactionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">جزئیات تراکنش</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-6"><strong>نوع تراکنش:</strong></div>
                                <div class="col-6">${this.getTransactionTypeText(transaction.transaction_type)}</div>
                            </div>
                            <div class="row">
                                <div class="col-6"><strong>مقدار امتیاز:</strong></div>
                                <div class="col-6">${transaction.points_amount > 0 ? '+' : ''}${transaction.points_amount.toLocaleString()}</div>
                            </div>
                            <div class="row">
                                <div class="col-6"><strong>توضیحات:</strong></div>
                                <div class="col-6">${transaction.description || '-'}</div>
                            </div>
                            <div class="row">
                                <div class="col-6"><strong>تاریخ:</strong></div>
                                <div class="col-6">${new Date(transaction.created_at).toLocaleDateString('fa-IR')}</div>
                            </div>
                            ${transaction.expires_at ? `
                                <div class="row">
                                    <div class="col-6"><strong>انقضا:</strong></div>
                                    <div class="col-6">${new Date(transaction.expires_at).toLocaleDateString('fa-IR')}</div>
                                </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">بستن</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // حذف مودال قبلی اگر وجود دارد
        const existingModal = document.getElementById('transactionModal');
        if (existingModal) {
            existingModal.remove();
        }

        // اضافه کردن مودال جدید
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // نمایش مودال
        const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
        modal.show();

        // حذف مودال پس از بسته شدن
        document.getElementById('transactionModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    /**
     * دریافت متن نوع تراکنش
     */
    getTransactionTypeText(type) {
        const types = {
            'earn': 'کسب امتیاز',
            'spend': 'خرج امتیاز',
            'expire': 'انقضا',
            'bonus': 'امتیاز اضافی',
            'admin_adjustment': 'تنظیم دستی'
        };
        return types[type] || type;
    }

    /**
     * نمایش پیام موفقیت
     */
    showSuccessMessage(message) {
        this.showAlert(message, 'success');
    }

    /**
     * نمایش پیام خطا
     */
    showErrorMessage(message) {
        this.showAlert(message, 'danger');
    }

    /**
     * نمایش پیام
     */
    showAlert(message, type) {
        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // پیدا کردن محل مناسب برای نمایش پیام
        const container = document.querySelector('.container') || document.body;
        container.insertAdjacentHTML('afterbegin', alertHTML);

        // حذف خودکار پیام پس از 5 ثانیه
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    /**
     * محاسبه امتیاز پیش‌نمایش
     */
    calculatePreviewPoints(invoiceTotal, productCount) {
        // این تابع می‌تواند برای نمایش پیش‌نمایش امتیازات استفاده شود
        const basePoints = Math.floor((invoiceTotal / 100) * 500); // فرض: 500 امتیاز به ازای هر 100 هزار ریال
        const bonusPoints = Math.min((productCount - 1) * 50, 1000); // فرض: 50 امتیاز اضافی به ازای هر محصول
        return basePoints + bonusPoints;
    }
}

// راه‌اندازی سیستم امتیازدهی
document.addEventListener('DOMContentLoaded', function() {
    window.pointsSystem = new PointsSystem();
});

// تابع سراسری برای استفاده از جایزه
function redeemReward(rewardId) {
    if (window.pointsSystem) {
        window.pointsSystem.redeemReward(rewardId);
    }
}


