-- Migration script to add bulk buyer approval fields to User table
-- Run this script to update the database schema

-- Add new columns to User table
ALTER TABLE user ADD COLUMN bulk_buyer_approval_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE user ADD COLUMN bulk_buyer_approved_at DATETIME;
ALTER TABLE user ADD COLUMN bulk_buyer_approved_by INTEGER;

-- Add foreign key constraint for bulk_buyer_approved_by
-- Note: SQLite doesn't support adding foreign key constraints to existing tables
-- The constraint will be enforced at the application level

-- Update existing users to have approved status if they are not bulk buyers
UPDATE user SET bulk_buyer_approval_status = 'approved' WHERE is_bulk_buyer = 0;

-- Update existing bulk buyers to have pending status if not already set
UPDATE user SET bulk_buyer_approval_status = 'pending' WHERE is_bulk_buyer = 1 AND bulk_buyer_approval_status IS NULL;

-- Create index for better performance
CREATE INDEX idx_user_bulk_buyer_approval ON user(bulk_buyer_approval_status);
CREATE INDEX idx_user_bulk_buyer_status ON user(is_bulk_buyer, bulk_buyer_approval_status);
