-- Migration script to convert prices from thousands of Rials to full Rials
-- Run this script before deploying the code changes
-- Date: 2025-01-16
-- Purpose: Fix Tadbir price display to show actual prices received from Tadbir API

-- Create backup of current prices
CREATE TABLE IF NOT EXISTS product_prices_backup_20250116 AS 
SELECT id, sku, bulk_price_cash, retail_price_cash, bulk_price_check, retail_price_check, 
       isaco_cash, isaco_1m, isaco_2m, isaco_3m, updated_at 
FROM product;

-- Create backup of Tadbir price cache
CREATE TABLE IF NOT EXISTS tadbir_price_cache_backup_20250116 AS 
SELECT * FROM tadbir_price_cache;

-- Convert product prices from thousands to full Rials
UPDATE product SET 
    bulk_price_cash = bulk_price_cash * 1000,
    retail_price_cash = retail_price_cash * 1000,
    bulk_price_check = bulk_price_check * 1000,
    retail_price_check = retail_price_check * 1000,
    isaco_cash = CASE WHEN isaco_cash IS NOT NULL THEN isaco_cash * 1000 ELSE isaco_cash END,
    isaco_1m = CASE WHEN isaco_1m IS NOT NULL THEN isaco_1m * 1000 ELSE isaco_1m END,
    isaco_2m = CASE WHEN isaco_2m IS NOT NULL THEN isaco_2m * 1000 ELSE isaco_2m END,
    isaco_3m = CASE WHEN isaco_3m IS NOT NULL THEN isaco_3m * 1000 ELSE isaco_3m END,
    updated_at = CURRENT_TIMESTAMP;

-- Convert Tadbir price cache from thousands to full Rials
UPDATE tadbir_price_cache SET 
    base_price = base_price * 1000,
    final_price = final_price * 1000,
    discount_amount = discount_amount * 1000,
    cached_at = CURRENT_TIMESTAMP;

-- Convert cart prices from thousands to full Rials
UPDATE cart SET 
    unit_price = unit_price * 1000,
    discount_amount = discount_amount * 1000,
    updated_at = CURRENT_TIMESTAMP;

-- Convert invoice item prices from thousands to full Rials
UPDATE invoice_item SET 
    unit_price = unit_price * 1000,
    total_price = total_price * 1000;

-- Convert invoice total amounts from thousands to full Rials
UPDATE invoice SET 
    total_amount = total_amount * 1000;

-- Verify the conversion
SELECT 'Product prices converted' as status, COUNT(*) as count FROM product WHERE bulk_price_cash > 1000;
SELECT 'Tadbir prices converted' as status, COUNT(*) as count FROM tadbir_price_cache WHERE base_price > 1000;
SELECT 'Cart prices converted' as status, COUNT(*) as count FROM cart WHERE unit_price > 1000;
SELECT 'Invoice prices converted' as status, COUNT(*) as count FROM invoice WHERE total_amount > 1000;

-- Show sample converted prices
SELECT 'Sample converted prices:' as info;
SELECT sku, bulk_price_cash, retail_price_cash, bulk_price_check, retail_price_check 
FROM product 
WHERE sku = '30613470' OR sku LIKE '%30613470%' 
LIMIT 5;
