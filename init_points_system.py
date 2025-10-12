#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی اولیه سیستم امتیازدهی
ایجاد جداول و داده‌های اولیه
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, UserPoints, PointsTransaction, Reward, RewardRedemption, UserLevel, PointsRule
from points_service import init_points_system
from datetime import datetime

def main():
    """راه‌اندازی اولیه سیستم امتیازدهی"""
    with app.app_context():
        try:
            print("Starting points system setup...")
            
            # ایجاد جداول
            print("Creating database tables...")
            db.create_all()
            print("Tables created successfully")
            
            # ایجاد داده‌های اولیه
            print("Creating initial data...")
            if init_points_system():
                print("Initial data created successfully")
            else:
                print("Error creating initial data")
                return False
            
            # بررسی داده‌های ایجاد شده
            print("Checking created data...")
            
            # بررسی قوانین
            rules_count = PointsRule.query.count()
            print(f"Rules count: {rules_count}")
            
            # بررسی سطح‌بندی
            levels_count = UserLevel.query.count()
            print(f"Levels count: {levels_count}")
            
            # بررسی جوایز
            rewards_count = Reward.query.count()
            print(f"Rewards count: {rewards_count}")
            
            # نمایش قوانین فعال
            active_rule = PointsRule.query.filter_by(is_active=True).first()
            if active_rule:
                print(f"Active rule: {active_rule.rule_name_fa}")
                print(f"   - Points per 100k rials: {active_rule.points_per_100k_rials}")
                print(f"   - Bonus points per product: {active_rule.bonus_points_per_product}")
                print(f"   - Max bonus points: {active_rule.max_bonus_points}")
            
            # نمایش سطح‌بندی
            print("User levels:")
            levels = UserLevel.query.filter_by(is_active=True).order_by(UserLevel.min_points).all()
            for level in levels:
                print(f"   - {level.level_name_fa}: {level.min_points}+ points ({level.discount_percentage}% discount)")
            
            # نمایش جوایز
            print("Available rewards:")
            rewards = Reward.query.filter_by(is_active=True).all()
            for reward in rewards:
                print(f"   - {reward.name_fa}: {reward.points_required} points ({reward.reward_type})")
            
            print("\nPoints system setup completed successfully!")
            print("\nImportant notes:")
            print("   - Every 100,000 rials purchase = 500 points (default)")
            print("   - Every additional product = 50 bonus points (default)")
            print("   - Max bonus points per purchase = 1000 (default)")
            print("   - Points expire after 12 months")
            print("   - Users are leveled based on points")
            
            return True
            
        except Exception as e:
            print(f"Error in points system setup: {str(e)}")
            return False

def create_sample_data():
    """ایجاد داده‌های نمونه برای تست"""
    with app.app_context():
        try:
            print("Creating sample data...")
            
            # ایجاد جوایز نمونه اضافی
            sample_rewards = [
                {
                    'name': '10% Discount',
                    'name_fa': 'تخفیف 10 درصدی',
                    'description': '10% discount on your next purchase',
                    'description_fa': 'تخفیف 10 درصدی در خرید بعدی',
                    'points_required': 2000,
                    'discount_percentage': 10,
                    'reward_type': 'discount_percentage',
                    'is_active': True
                },
                {
                    'name': '50,000 Rials Discount',
                    'name_fa': 'تخفیف 50 هزار ریالی',
                    'description': '50,000 Rials discount on your next purchase',
                    'description_fa': 'تخفیف 50 هزار ریالی در خرید بعدی',
                    'points_required': 1500,
                    'discount_amount': 50000,
                    'reward_type': 'discount_amount',
                    'is_active': True
                },
                {
                    'name': 'Premium Product',
                    'name_fa': 'محصول ویژه',
                    'description': 'Get a premium product for free',
                    'description_fa': 'دریافت یک محصول ویژه به صورت رایگان',
                    'points_required': 5000,
                    'reward_type': 'product',
                    'is_active': True
                }
            ]
            
            for reward_data in sample_rewards:
                existing_reward = Reward.query.filter_by(name=reward_data['name']).first()
                if not existing_reward:
                    reward = Reward(**reward_data)
                    db.session.add(reward)
            
            db.session.commit()
            print("Sample data created successfully")
            
        except Exception as e:
            print(f"Error creating sample data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("=" * 60)
    print("Points System - Initial Setup")
    print("=" * 60)
    
    if main():
        print("\n" + "=" * 60)
        print("Do you want to create sample data? (y/n)")
        choice = input().lower().strip()
        if choice in ['y', 'yes']:
            create_sample_data()
        
        print("\n" + "=" * 60)
        print("Setup completed successfully!")
        print("You can now use the points system:")
        print("   - Users: /points")
        print("   - Admin: /admin/points")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Setup failed!")
        print("=" * 60)
        sys.exit(1)
