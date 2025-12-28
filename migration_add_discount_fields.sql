-- Migration: Add discount_type and priority fields to product_discount table
-- Date: 2024-12-25

-- Add discount_type column (default: 'daily')
ALTER TABLE product_discount ADD COLUMN discount_type VARCHAR(20) DEFAULT 'daily';

-- Add priority column (default: 0)
ALTER TABLE product_discount ADD COLUMN priority INTEGER DEFAULT 0;

-- Update existing records to have discount_type = 'daily' if NULL
UPDATE product_discount SET discount_type = 'daily' WHERE discount_type IS NULL;

-- Create index on discount_type for better query performance
CREATE INDEX IF NOT EXISTS idx_product_discount_type ON product_discount(discount_type);

-- Create index on is_active and discount_type for filtering
CREATE INDEX IF NOT EXISTS idx_product_discount_active_type ON product_discount(is_active, discount_type);

-- Create index on priority for sorting
CREATE INDEX IF NOT EXISTS idx_product_discount_priority ON product_discount(priority DESC);

