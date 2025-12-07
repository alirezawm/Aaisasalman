-- Migration to reduce points by three digits (divide by 1000)
-- This script updates existing data to reflect the new points system

-- Update existing PointsRule records
UPDATE points_rule 
SET 
    points_per_100k_rials = points_per_100k_rials / 1000,
    bonus_points_per_product = bonus_points_per_product / 1000,
    max_bonus_points = max_bonus_points / 1000
WHERE points_per_100k_rials > 0;

-- Update existing UserLevel records
UPDATE user_level 
SET 
    min_points = min_points / 1000,
    max_points = CASE 
        WHEN max_points IS NOT NULL THEN max_points / 1000 
        ELSE NULL 
    END
WHERE min_points > 0;

-- Update existing Reward records
UPDATE reward 
SET points_required = points_required / 1000
WHERE points_required > 0;

-- Update existing UserPoints records
UPDATE user_points 
SET 
    current_points = current_points / 1000,
    total_earned_points = total_earned_points / 1000,
    total_spent_points = total_spent_points / 1000
WHERE current_points > 0 OR total_earned_points > 0 OR total_spent_points > 0;

-- Update existing PointsTransaction records
UPDATE points_transaction 
SET points_amount = points_amount / 1000
WHERE points_amount != 0;

-- Update existing RewardRedemption records
UPDATE reward_redemption 
SET points_spent = points_spent / 1000
WHERE points_spent > 0;
