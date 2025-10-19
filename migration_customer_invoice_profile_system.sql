-- Migration: سیستم مدیریت فاکتورهای مشتریان در پروفایل
-- تاریخ: 2025-01-27
-- توضیحات: اضافه کردن جداول و فیلدهای مورد نیاز برای سیستم فاکتورهای مشتریان

-- اضافه کردن فیلدهای جدید به جدول user
ALTER TABLE user ADD COLUMN customer_type VARCHAR(20) DEFAULT 'individual';
ALTER TABLE user ADD COLUMN sales_manager_id INTEGER REFERENCES user(id);
ALTER TABLE user ADD COLUMN bulk_customer_level VARCHAR(20) DEFAULT 'bronze';
ALTER TABLE user ADD COLUMN total_purchase_amount DECIMAL(15,2) DEFAULT 0;

-- اضافه کردن فیلدهای جدید به جدول invoice
ALTER TABLE invoice ADD COLUMN customer_type VARCHAR(20) DEFAULT 'individual';
ALTER TABLE invoice ADD COLUMN approval_workflow_status VARCHAR(30) DEFAULT 'pending';
ALTER TABLE invoice ADD COLUMN document_required BOOLEAN DEFAULT FALSE;
ALTER TABLE invoice ADD COLUMN auto_approval_threshold DECIMAL(15,2) DEFAULT 1000000;
ALTER TABLE invoice ADD COLUMN bulk_discount_applied DECIMAL(5,2) DEFAULT 0;
ALTER TABLE invoice ADD COLUMN credit_used DECIMAL(15,2) DEFAULT 0;
ALTER TABLE invoice ADD COLUMN sales_manager_id INTEGER REFERENCES user(id);
ALTER TABLE invoice ADD COLUMN customer_notes TEXT;

-- ایجاد جدول پروفایل فاکتور مشتری
CREATE TABLE customer_invoice_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES user(id),
    customer_type VARCHAR(20) DEFAULT 'individual',
    auto_approval_limit DECIMAL(15,2) DEFAULT 1000000,
    bulk_discount_percentage DECIMAL(5,2) DEFAULT 0,
    credit_limit DECIMAL(15,2) DEFAULT 0,
    current_credit_used DECIMAL(15,2) DEFAULT 0,
    assigned_sales_manager INTEGER REFERENCES user(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ایجاد جدول فرآیند تایید فاکتور
CREATE TABLE invoice_approval_workflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL REFERENCES invoice(id),
    workflow_status VARCHAR(30) DEFAULT 'pending',
    auto_approval_eligible BOOLEAN DEFAULT FALSE,
    manual_approval_required BOOLEAN DEFAULT TRUE,
    assigned_to INTEGER REFERENCES user(id),
    priority_level INTEGER DEFAULT 1,
    deadline DATETIME,
    approval_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ایجاد جدول مزایای مشتریان عمده
CREATE TABLE bulk_customer_benefits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES user(id),
    benefit_type VARCHAR(50) NOT NULL,
    benefit_value DECIMAL(10,2) NOT NULL,
    benefit_description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    valid_from DATETIME,
    valid_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ایجاد جدول تایید مدارک فاکتور
CREATE TABLE invoice_document_approval (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES invoice_document(id),
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES user(id),
    approval_date DATETIME,
    rejection_reason TEXT,
    admin_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ایجاد ایندکس‌ها برای بهبود عملکرد
CREATE INDEX idx_customer_invoice_profile_user_id ON customer_invoice_profile(user_id);
CREATE INDEX idx_customer_invoice_profile_customer_type ON customer_invoice_profile(customer_type);
CREATE INDEX idx_invoice_approval_workflow_invoice_id ON invoice_approval_workflow(invoice_id);
CREATE INDEX idx_invoice_approval_workflow_status ON invoice_approval_workflow(workflow_status);
CREATE INDEX idx_invoice_approval_workflow_assigned_to ON invoice_approval_workflow(assigned_to);
CREATE INDEX idx_bulk_customer_benefits_user_id ON bulk_customer_benefits(user_id);
CREATE INDEX idx_bulk_customer_benefits_active ON bulk_customer_benefits(is_active);
CREATE INDEX idx_invoice_document_approval_document_id ON invoice_document_approval(document_id);
CREATE INDEX idx_invoice_document_approval_status ON invoice_document_approval(approval_status);

-- ایجاد ایندکس‌های جدید برای فیلدهای اضافه شده
CREATE INDEX idx_user_customer_type ON user(customer_type);
CREATE INDEX idx_user_sales_manager_id ON user(sales_manager_id);
CREATE INDEX idx_invoice_customer_type ON invoice(customer_type);
CREATE INDEX idx_invoice_approval_workflow_status ON invoice(approval_workflow_status);
CREATE INDEX idx_invoice_sales_manager_id ON invoice(sales_manager_id);

-- به‌روزرسانی داده‌های موجود
-- تنظیم نوع مشتری بر اساس وضعیت bulk_buyer
UPDATE user SET customer_type = 'bulk' WHERE is_bulk_buyer = TRUE AND bulk_buyer_approval_status = 'approved';
UPDATE user SET customer_type = 'individual' WHERE is_bulk_buyer = FALSE OR bulk_buyer_approval_status != 'approved';

-- تنظیم سطح مشتریان عمده بر اساس مبلغ خرید
UPDATE user SET bulk_customer_level = 'bronze' WHERE customer_type = 'bulk' AND total_purchase_amount < 10000000;
UPDATE user SET bulk_customer_level = 'silver' WHERE customer_type = 'bulk' AND total_purchase_amount >= 10000000 AND total_purchase_amount < 50000000;
UPDATE user SET bulk_customer_level = 'gold' WHERE customer_type = 'bulk' AND total_purchase_amount >= 50000000 AND total_purchase_amount < 100000000;
UPDATE user SET bulk_customer_level = 'platinum' WHERE customer_type = 'bulk' AND total_purchase_amount >= 100000000;

-- ایجاد پروفایل فاکتور برای کاربران موجود
INSERT INTO customer_invoice_profile (user_id, customer_type, auto_approval_limit, bulk_discount_percentage, credit_limit)
SELECT 
    id,
    customer_type,
    CASE 
        WHEN customer_type = 'bulk' THEN 5000000  -- 5 میلیون برای مشتریان عمده
        ELSE 1000000  -- 1 میلیون برای مشتریان تکی
    END,
    CASE 
        WHEN bulk_customer_level = 'platinum' THEN 15.0
        WHEN bulk_customer_level = 'gold' THEN 12.0
        WHEN bulk_customer_level = 'silver' THEN 8.0
        WHEN bulk_customer_level = 'bronze' THEN 5.0
        ELSE 0.0
    END,
    CASE 
        WHEN customer_type = 'bulk' THEN total_purchase_amount * 0.1  -- 10% از خرید کل
        ELSE 0
    END
FROM user 
WHERE id NOT IN (SELECT user_id FROM customer_invoice_profile);

-- به‌روزرسانی فاکتورهای موجود
UPDATE invoice SET customer_type = (
    SELECT customer_type FROM user WHERE user.id = invoice.user_id
);

-- تنظیم آستانه تایید خودکار برای فاکتورها
UPDATE invoice SET auto_approval_threshold = (
    SELECT auto_approval_limit FROM customer_invoice_profile 
    WHERE customer_invoice_profile.user_id = invoice.user_id
);

-- تنظیم تخفیف عمده برای فاکتورهای مشتریان عمده
UPDATE invoice SET bulk_discount_applied = (
    SELECT bulk_discount_percentage FROM customer_invoice_profile 
    WHERE customer_invoice_profile.user_id = invoice.user_id
);

-- ایجاد فرآیند تایید برای فاکتورهای موجود
INSERT INTO invoice_approval_workflow (invoice_id, workflow_status, auto_approval_eligible, manual_approval_required)
SELECT 
    id,
    CASE 
        WHEN approval_status = 'approved' THEN 'manual_approved'
        WHEN approval_status = 'rejected' THEN 'rejected'
        ELSE 'pending'
    END,
    CASE 
        WHEN total_amount <= (
            SELECT auto_approval_limit FROM customer_invoice_profile 
            WHERE customer_invoice_profile.user_id = invoice.user_id
        ) THEN TRUE
        ELSE FALSE
    END,
    CASE 
        WHEN total_amount > (
            SELECT auto_approval_limit FROM customer_invoice_profile 
            WHERE customer_invoice_profile.user_id = invoice.user_id
        ) THEN TRUE
        ELSE FALSE
    END
FROM invoice 
WHERE id NOT IN (SELECT invoice_id FROM invoice_approval_workflow);

-- ایجاد مزایای پیش‌فرض برای مشتریان عمده
INSERT INTO bulk_customer_benefits (user_id, benefit_type, benefit_value, benefit_description, is_active)
SELECT 
    id,
    'discount',
    CASE 
        WHEN bulk_customer_level = 'platinum' THEN 15.0
        WHEN bulk_customer_level = 'gold' THEN 12.0
        WHEN bulk_customer_level = 'silver' THEN 8.0
        WHEN bulk_customer_level = 'bronze' THEN 5.0
        ELSE 0.0
    END,
    'تخفیف عمده - سطح ' || bulk_customer_level,
    TRUE
FROM user 
WHERE customer_type = 'bulk' AND id NOT IN (
    SELECT user_id FROM bulk_customer_benefits WHERE benefit_type = 'discount'
);

-- ایجاد مزایای اعتبار برای مشتریان عمده
INSERT INTO bulk_customer_benefits (user_id, benefit_type, benefit_value, benefit_description, is_active)
SELECT 
    id,
    'credit_increase',
    total_purchase_amount * 0.1,  -- 10% از خرید کل
    'افزایش اعتبار بر اساس حجم خرید',
    TRUE
FROM user 
WHERE customer_type = 'bulk' AND total_purchase_amount > 0 AND id NOT IN (
    SELECT user_id FROM bulk_customer_benefits WHERE benefit_type = 'credit_increase'
);

-- ایجاد مزایای پشتیبانی اولویت‌دار
INSERT INTO bulk_customer_benefits (user_id, benefit_type, benefit_value, benefit_description, is_active)
SELECT 
    id,
    'priority_support',
    1.0,
    'پشتیبانی اولویت‌دار',
    TRUE
FROM user 
WHERE customer_type = 'bulk' AND bulk_customer_level IN ('gold', 'platinum') AND id NOT IN (
    SELECT user_id FROM bulk_customer_benefits WHERE benefit_type = 'priority_support'
);

-- به‌روزرسانی وضعیت فرآیند تایید فاکتورها
UPDATE invoice SET approval_workflow_status = (
    SELECT workflow_status FROM invoice_approval_workflow 
    WHERE invoice_approval_workflow.invoice_id = invoice.id
);

-- تنظیم نیاز به مدرک برای فاکتورهای بزرگ
UPDATE invoice SET document_required = TRUE 
WHERE total_amount > 5000000 AND approval_workflow_status = 'pending';

-- تنظیم مدیر فروش برای مشتریان عمده (اختیاری - می‌تواند بعداً تنظیم شود)
-- UPDATE user SET sales_manager_id = 1 WHERE customer_type = 'bulk' AND sales_manager_id IS NULL;

-- نمایش آمار نهایی
SELECT 
    'Migration completed successfully' as status,
    (SELECT COUNT(*) FROM customer_invoice_profile) as customer_profiles_created,
    (SELECT COUNT(*) FROM invoice_approval_workflow) as approval_workflows_created,
    (SELECT COUNT(*) FROM bulk_customer_benefits) as bulk_benefits_created,
    (SELECT COUNT(*) FROM user WHERE customer_type = 'individual') as individual_customers,
    (SELECT COUNT(*) FROM user WHERE customer_type = 'bulk') as bulk_customers;
