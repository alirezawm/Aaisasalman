-- Migration for Invoice Management System
-- اضافه کردن فیلدهای جدید به جداول موجود

-- اضافه کردن فیلدهای جدید به جدول invoice
ALTER TABLE invoice ADD COLUMN admin_review_notes TEXT;
ALTER TABLE invoice ADD COLUMN notification_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE invoice ADD COLUMN notification_sent_at DATETIME;

-- اضافه کردن فیلدهای جدید به جدول user_notification
ALTER TABLE user_notification ADD COLUMN related_invoice_id INTEGER;
ALTER TABLE user_notification ADD COLUMN notification_action VARCHAR(50);

-- اضافه کردن foreign key constraint برای related_invoice_id
-- (این خط ممکن است در SQLite کار نکند، اما در PostgreSQL/MySQL کار می‌کند)
-- ALTER TABLE user_notification ADD CONSTRAINT fk_user_notification_invoice 
--     FOREIGN KEY (related_invoice_id) REFERENCES invoice(id);

-- ایجاد ایندکس برای بهبود عملکرد
CREATE INDEX IF NOT EXISTS idx_invoice_approval_status ON invoice(approval_status);
CREATE INDEX IF NOT EXISTS idx_invoice_notification_sent ON invoice(notification_sent);
CREATE INDEX IF NOT EXISTS idx_user_notification_related_invoice ON user_notification(related_invoice_id);
CREATE INDEX IF NOT EXISTS idx_user_notification_action ON user_notification(notification_action);

-- بروزرسانی رکوردهای موجود
UPDATE invoice SET notification_sent = FALSE WHERE notification_sent IS NULL;
