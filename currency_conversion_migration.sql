-- Database Migration: Convert Currency from Billions Toman to Thousands Rials
-- Created: 2025-01-27
-- Description: Converts all price fields from billions Toman to thousands Rials
-- Conversion factor: 1 billion Toman = 10,000 thousands Rials

-- Step 1: Create backup table
CREATE TABLE product_backup_currency_conversion AS 
SELECT * FROM product;

-- Step 2: Verify current data before conversion
SELECT 
    COUNT(*) as total_products,
    MIN(bulk_price_cash) as min_bulk_cash,
    MAX(bulk_price_cash) as max_bulk_cash,
    AVG(bulk_price_cash) as avg_bulk_cash
FROM product 
WHERE bulk_price_cash IS NOT NULL;

-- Step 3: Convert all price fields
-- Bulk prices
UPDATE products 
SET bulk_price_cash = bulk_price_cash * 10000 
WHERE bulk_price_cash IS NOT NULL;

UPDATE products 
SET bulk_price_check = bulk_price_check * 10000 
WHERE bulk_price_check IS NOT NULL;

-- Retail prices  
UPDATE products 
SET retail_price_cash = retail_price_cash * 10000 
WHERE retail_price_cash IS NOT NULL;

UPDATE products 
SET retail_price_check = retail_price_check * 10000 
WHERE retail_price_check IS NOT NULL;

-- Step 4: Verify conversion results
SELECT 
    COUNT(*) as total_products,
    MIN(bulk_price_cash) as min_bulk_cash,
    MAX(bulk_price_cash) as max_bulk_cash,
    AVG(bulk_price_cash) as avg_bulk_cash
FROM product 
WHERE bulk_price_cash IS NOT NULL;

-- Step 5: Check for any NULL or zero values that might indicate issues
SELECT COUNT(*) as null_prices FROM product 
WHERE bulk_price_cash IS NULL OR retail_price_cash IS NULL;

SELECT COUNT(*) as zero_prices FROM product 
WHERE bulk_price_cash = 0 OR retail_price_cash = 0;

-- Step 6: Sample verification - show first 10 products with converted prices
SELECT 
    id,
    name_fa,
    sku,
    bulk_price_cash,
    bulk_price_check,
    retail_price_cash,
    retail_price_check
FROM product 
LIMIT 10;

-- Rollback script (if needed):
-- UPDATE products SET bulk_price_cash = bulk_price_cash / 10000 WHERE bulk_price_cash IS NOT NULL;
-- UPDATE products SET bulk_price_check = bulk_price_check / 10000 WHERE bulk_price_check IS NOT NULL;
-- UPDATE products SET retail_price_cash = retail_price_cash / 10000 WHERE retail_price_cash IS NOT NULL;
-- UPDATE products SET retail_price_check = retail_price_check / 10000 WHERE retail_price_check IS NOT NULL;
