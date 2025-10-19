-- Database Migration for Enhanced Cart System
-- Run this script to update the existing database with new cart features

-- Add new columns to existing cart table
ALTER TABLE cart ADD COLUMN discount_amount FLOAT DEFAULT 0;
ALTER TABLE cart ADD COLUMN discount_type VARCHAR(20) DEFAULT 'fixed';
ALTER TABLE cart ADD COLUMN session_id VARCHAR(100);
ALTER TABLE cart ADD COLUMN is_saved_for_later BOOLEAN DEFAULT FALSE;
ALTER TABLE cart ADD COLUMN notes TEXT;
ALTER TABLE cart ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE cart ADD COLUMN expires_at DATETIME DEFAULT (datetime('now', '+30 days'));

-- Create cart_session table
CREATE TABLE IF NOT EXISTS cart_session (
    id VARCHAR(100) PRIMARY KEY,
    user_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Create wishlist table
CREATE TABLE IF NOT EXISTS wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (product_id) REFERENCES product(id),
    UNIQUE(user_id, product_id)
);

-- Create cart_notification table
CREATE TABLE IF NOT EXISTS cart_notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_cart_user_product_price ON cart(user_id, product_id, price_type);
CREATE INDEX IF NOT EXISTS idx_cart_session ON cart(session_id);
CREATE INDEX IF NOT EXISTS idx_cart_expires ON cart(expires_at);
CREATE INDEX IF NOT EXISTS idx_cart_saved ON cart(is_saved_for_later);
CREATE INDEX IF NOT EXISTS idx_cart_session_user ON cart_session(user_id);
CREATE INDEX IF NOT EXISTS idx_cart_session_active ON cart_session(is_active);
CREATE INDEX IF NOT EXISTS idx_wishlist_user ON wishlist(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_product ON wishlist(product_id);
CREATE INDEX IF NOT EXISTS idx_notification_user ON cart_notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_read ON cart_notification(is_read);
CREATE INDEX IF NOT EXISTS idx_notification_type ON cart_notification(type);

-- Update existing cart items to have expiration dates
UPDATE cart SET expires_at = datetime('now', '+30 days') WHERE expires_at IS NULL;

-- Update existing cart items to have updated_at timestamps
UPDATE cart SET updated_at = created_at WHERE updated_at IS NULL;

-- Create trigger to automatically update updated_at column
CREATE TRIGGER IF NOT EXISTS update_cart_updated_at 
    AFTER UPDATE ON cart
    FOR EACH ROW
    BEGIN
        UPDATE cart SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Create trigger to automatically update cart_session last_activity
CREATE TRIGGER IF NOT EXISTS update_cart_session_activity 
    AFTER UPDATE ON cart_session
    FOR EACH ROW
    BEGIN
        UPDATE cart_session SET last_activity = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Insert sample notifications for testing
INSERT INTO cart_notification (user_id, type, title, message, data) 
SELECT 
    u.id,
    'welcome',
    'خوش آمدید',
    'به سیستم سبد خرید پیشرفته خوش آمدید!',
    '{"welcome": true}'
FROM user u 
WHERE u.id NOT IN (SELECT DISTINCT user_id FROM cart_notification WHERE type = 'welcome');

-- Create view for cart summary
CREATE VIEW IF NOT EXISTS cart_summary AS
SELECT 
    c.id,
    c.user_id,
    c.product_id,
    p.name as product_name,
    c.quantity,
    c.price_type,
    c.unit_price,
    c.discount_amount,
    c.discount_type,
    c.is_saved_for_later,
    c.notes,
    c.created_at,
    c.updated_at,
    c.expires_at,
    (c.quantity * c.unit_price) as base_total,
    CASE 
        WHEN c.discount_type = 'percentage' THEN 
            (c.quantity * c.unit_price) - ((c.quantity * c.unit_price) * (c.discount_amount / 100))
        ELSE 
            (c.quantity * c.unit_price) - c.discount_amount
    END as final_total
FROM cart c
JOIN product p ON c.product_id = p.id;

-- Create view for wishlist summary
CREATE VIEW IF NOT EXISTS wishlist_summary AS
SELECT 
    w.id,
    w.user_id,
    w.product_id,
    p.name as product_name,
    p.retail_price_cash,
    p.retail_price_check,
    p.bulk_price_cash,
    p.bulk_price_check,
    w.notes,
    w.created_at
FROM wishlist w
JOIN product p ON w.product_id = p.id;

-- Create view for notification summary
CREATE VIEW IF NOT EXISTS notification_summary AS
SELECT 
    n.id,
    n.user_id,
    u.full_name as user_name,
    n.type,
    n.title,
    n.message,
    n.is_read,
    n.created_at
FROM cart_notification n
JOIN user u ON n.user_id = u.id;

-- Create function to clean up expired cart items
CREATE TRIGGER IF NOT EXISTS cleanup_expired_carts
    AFTER INSERT ON cart
    FOR EACH ROW
    BEGIN
        DELETE FROM cart WHERE expires_at < CURRENT_TIMESTAMP;
    END;

-- Create function to clean up expired cart sessions
CREATE TRIGGER IF NOT EXISTS cleanup_expired_sessions
    AFTER INSERT ON cart_session
    FOR EACH ROW
    BEGIN
        DELETE FROM cart_session WHERE last_activity < datetime('now', '-7 days');
    END;

-- Add constraints
ALTER TABLE cart ADD CONSTRAINT chk_discount_amount CHECK (discount_amount >= 0);
ALTER TABLE cart ADD CONSTRAINT chk_discount_type CHECK (discount_type IN ('fixed', 'percentage'));
ALTER TABLE cart ADD CONSTRAINT chk_quantity CHECK (quantity > 0);
ALTER TABLE cart ADD CONSTRAINT chk_unit_price CHECK (unit_price >= 0);

-- Add foreign key constraints if they don't exist
PRAGMA foreign_keys = ON;

-- Update product table to add image_url if it doesn't exist
ALTER TABLE product ADD COLUMN image_url VARCHAR(255);

-- Create analytics table for tracking
CREATE TABLE IF NOT EXISTS analytics_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id VARCHAR(100),
    event_name VARCHAR(100) NOT NULL,
    event_data TEXT,
    page_url VARCHAR(500),
    user_agent TEXT,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Create indexes for analytics
CREATE INDEX IF NOT EXISTS idx_analytics_user ON analytics_event(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_session ON analytics_event(session_id);
CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics_event(event_name);
CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics_event(created_at);

-- Create view for analytics summary
CREATE VIEW IF NOT EXISTS analytics_summary AS
SELECT 
    event_name,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions,
    DATE(created_at) as event_date
FROM analytics_event
GROUP BY event_name, DATE(created_at);

-- Insert default data
INSERT OR IGNORE INTO cart_notification (user_id, type, title, message, data)
VALUES (1, 'system', 'سیستم به‌روزرسانی شد', 'سیستم سبد خرید با قابلیت‌های جدید به‌روزرسانی شد', '{"update": true}');

-- Create backup of existing cart data
CREATE TABLE IF NOT EXISTS cart_backup AS SELECT * FROM cart;

-- Update cart table structure
-- Note: SQLite doesn't support ALTER COLUMN, so we need to recreate the table
-- This is a simplified version - in production, you might want to use a more sophisticated migration

-- Create new cart table with all features
CREATE TABLE IF NOT EXISTS cart_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    price_type VARCHAR(10) NOT NULL,
    unit_price FLOAT NOT NULL,
    discount_amount FLOAT DEFAULT 0,
    discount_type VARCHAR(20) DEFAULT 'fixed',
    session_id VARCHAR(100),
    is_saved_for_later BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME DEFAULT (datetime('now', '+30 days')),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- Copy data from old cart table
INSERT INTO cart_new (id, user_id, product_id, quantity, price_type, unit_price, created_at)
SELECT id, user_id, product_id, quantity, price_type, unit_price, created_at
FROM cart;

-- Drop old cart table
DROP TABLE cart;

-- Rename new cart table
ALTER TABLE cart_new RENAME TO cart;

-- Recreate indexes
CREATE INDEX IF NOT EXISTS idx_cart_user_product_price ON cart(user_id, product_id, price_type);
CREATE INDEX IF NOT EXISTS idx_cart_session ON cart(session_id);
CREATE INDEX IF NOT EXISTS idx_cart_expires ON cart(expires_at);
CREATE INDEX IF NOT EXISTS idx_cart_saved ON cart(is_saved_for_later);

-- Recreate triggers
CREATE TRIGGER IF NOT EXISTS update_cart_updated_at 
    AFTER UPDATE ON cart
    FOR EACH ROW
    BEGIN
        UPDATE cart SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Final cleanup
VACUUM;

-- Display migration completion message
SELECT 'Cart system migration completed successfully!' as message;
