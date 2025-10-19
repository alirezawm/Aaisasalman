-- Migration: اضافه کردن فیلدهای جدید پروفایل به جدول user
-- تاریخ: 2024-01-15
-- توضیحات: اضافه کردن فیلدهای کد ملی، تاریخ تولد، آدرس، شماره ثابت و شماره دوم

-- اضافه کردن فیلدهای جدید به جدول user
ALTER TABLE user ADD COLUMN national_id VARCHAR(20);
ALTER TABLE user ADD COLUMN birth_date DATE;
ALTER TABLE user ADD COLUMN address TEXT;
ALTER TABLE user ADD COLUMN landline_phone VARCHAR(20);
ALTER TABLE user ADD COLUMN secondary_phone VARCHAR(20);
ALTER TABLE user ADD COLUMN profile_completion_percentage INTEGER DEFAULT 0;
ALTER TABLE user ADD COLUMN profile_completed_at DATETIME;
ALTER TABLE user ADD COLUMN notification_preferences TEXT DEFAULT '{}';

-- ایجاد ایندکس برای جستجوی بهتر
CREATE INDEX idx_user_national_id ON user(national_id);
CREATE INDEX idx_user_profile_completion ON user(profile_completion_percentage);

-- به‌روزرسانی درصد تکمیل پروفایل برای کاربران موجود
UPDATE user SET profile_completion_percentage = 
    CASE 
        WHEN full_name IS NOT NULL AND email IS NOT NULL AND phone IS NOT NULL AND username IS NOT NULL 
             AND national_id IS NOT NULL AND birth_date IS NOT NULL AND address IS NOT NULL 
             AND (landline_phone IS NOT NULL OR secondary_phone IS NOT NULL) THEN 100
        WHEN full_name IS NOT NULL AND email IS NOT NULL AND phone IS NOT NULL AND username IS NOT NULL 
             AND (national_id IS NOT NULL OR birth_date IS NOT NULL OR address IS NOT NULL 
                  OR landline_phone IS NOT NULL OR secondary_phone IS NOT NULL) THEN 75
        WHEN full_name IS NOT NULL AND email IS NOT NULL AND phone IS NOT NULL AND username IS NOT NULL THEN 50
        ELSE 25
    END;

-- تنظیم تاریخ تکمیل پروفایل برای کاربرانی که پروفایل کامل دارند
UPDATE user SET profile_completed_at = datetime('now') 
WHERE profile_completion_percentage = 100 AND profile_completed_at IS NULL;

-- نمایش آمار
SELECT 
    COUNT(*) as total_users,
    AVG(profile_completion_percentage) as avg_completion,
    COUNT(CASE WHEN profile_completion_percentage = 100 THEN 1 END) as completed_profiles,
    COUNT(CASE WHEN profile_completion_percentage < 50 THEN 1 END) as incomplete_profiles
FROM user;
