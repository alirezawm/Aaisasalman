"""
Points System Service
Classes and functions for calculating and managing user points
"""

from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models import db, UserPoints, PointsTransaction, Reward, RewardRedemption, UserLevel, PointsRule, User, Invoice, InvoiceItem
import json


class PointsService:
    """Main points system service"""
    
    def __init__(self):
        self.default_points_per_100k = 0.05  # Reduced from 500 to 0.05 (4 digits less)
        self.default_bonus_per_product = 0.005  # Reduced from 50 to 0.005 (4 digits less)
        self.default_max_bonus = 0.1  # Reduced from 1000 to 0.1 (4 digits less)
        self.points_expiration_months = 12
    
    def get_active_points_rule(self):
        """دریافت قانون فعال امتیازدهی"""
        rule = PointsRule.query.filter(
            PointsRule.is_active == True,
            or_(
                PointsRule.valid_from.is_(None),
                PointsRule.valid_from <= datetime.utcnow()
            ),
            or_(
                PointsRule.valid_until.is_(None),
                PointsRule.valid_until >= datetime.utcnow()
            )
        ).order_by(PointsRule.created_at.desc()).first()
        
        return rule
    
    def calculate_points_for_purchase(self, invoice_total, product_count):
        """
        محاسبه امتیازات برای خرید
        
        Args:
            invoice_total: مجموع فاکتور (در هزار ریال)
            product_count: تعداد محصولات در فاکتور
            
        Returns:
            dict: شامل امتیاز پایه، امتیاز اضافی و مجموع
        """
        rule = self.get_active_points_rule()
        
        if rule:
            points_per_100k = rule.points_per_100k_rials
            bonus_per_product = rule.bonus_points_per_product
            max_bonus = rule.max_bonus_points
        else:
            points_per_100k = self.default_points_per_100k
            bonus_per_product = self.default_bonus_per_product
            max_bonus = self.default_max_bonus
        
        # محاسبه امتیاز پایه بر اساس قیمت
        base_points = int((invoice_total / 100) * points_per_100k)
        
        # محاسبه امتیاز اضافی بر اساس تعداد محصولات
        if product_count > 1:
            bonus_points = min(
                (product_count - 1) * bonus_per_product,
                max_bonus
            )
        else:
            bonus_points = 0
        
        total_points = base_points + bonus_points
        
        return {
            'base_points': base_points,
            'bonus_points': bonus_points,
            'total_points': total_points,
            'rule_used': rule.rule_name_fa if rule else 'Default Rule'
        }
    
    def award_points_for_invoice(self, invoice_id):
        """
        اعطای امتیاز برای فاکتور
        
        Args:
            invoice_id: شناسه فاکتور
            
        Returns:
            dict: نتیجه عملیات
        """
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                return {'success': False, 'message': 'فاکتور یافت نشد'}
            
            # بررسی اینکه قبلاً امتیاز داده شده یا نه
            existing_transaction = PointsTransaction.query.filter_by(
                user_id=invoice.user_id,
                source_type='purchase',
                source_id=invoice_id
            ).first()
            
            if existing_transaction:
                return {'success': False, 'message': 'امتیاز قبلاً برای این فاکتور اعطا شده است'}
            
            # محاسبه امتیازات
            invoice_total = invoice.total_amount
            product_count = len(invoice.items)
            points_calculation = self.calculate_points_for_purchase(invoice_total, product_count)
            
            # ایجاد یا به‌روزرسانی امتیازات کاربر
            user_points = UserPoints.query.filter_by(user_id=invoice.user_id).first()
            if not user_points:
                user_points = UserPoints(user_id=invoice.user_id)
                db.session.add(user_points)
            
            # به‌روزرسانی امتیازات
            user_points.current_points += pointsC_calculation['total_points']
            user_points.total_earned_points += points_calculation['total_points']
            
            # ایجاد تراکنش امتیازی
            transaction = PointsTransaction(
                user_id=invoice.user_id,
                points_amount=points_calculation['total_points'],
                transaction_type='earn',
                source_type='purchase',
                source_id=invoice_id,
                description=f"امتیاز خرید - فاکتور {invoice.invoice_number}",
                expires_at=datetime.utcnow() + timedelta(days=365)  # 12 ماه
            )
            db.session.add(transaction)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f"{points_calculation['total_points']} امتیاز اعطا شد",
                'points': points_calculation
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'خطا در اعطای امتیاز: {str(e)}'}
    
    def get_user_points(self, user_id):
        """دریافت امتیازات کاربر"""
        user_points = UserPoints.query.filter_by(user_id=user_id).first()
        if not user_points:
            return {
                'current_points': 0,
                'total_earned': 0,
                'total_spent': 0,
                'user_level': self.get_user_level(user_id)
            }
        
        return {
            'current_points': user_points.current_points,
            'total_earned': user_points.total_earned_points,
            'total_spent': user_points.total_spent_points,
            'user_level': self.get_user_level(user_id)
        }
    
    def get_user_level(self, user_id):
        """دریافت سطح کاربر"""
        user_points = UserPoints.query.filter_by(user_id=user_id).first()
        if not user_points:
            points = 0
        else:
            points = user_points.current_points
        
        level = UserLevel.query.filter(
            UserLevel.is_active == True,
            UserLevel.min_points <= points,
            or_(
                UserLevel.max_points.is_(None),
                UserLevel.max_points >= points
            )
        ).order_by(UserLevel.min_points.desc()).first()
        
        if level:
            return {
                'id': level.id,
                'name': level.level_name,
                'name_fa': level.level_name_fa,
                'discount_percentage': level.discount_percentage,
                'min_points': level.min_points,
                'max_points': level.max_points
            }
        
        return None
    
    def get_user_transactions(self, user_id, page=1, per_page=20):
        """دریافت تاریخچه تراکنش‌های امتیازی کاربر"""
        transactions = PointsTransaction.query.filter_by(user_id=user_id)\
            .order_by(PointsTransaction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return transactions
    
    def get_available_rewards(self, user_id):
        """دریافت جوایز قابل استفاده برای کاربر"""
        user_points = UserPoints.query.filter_by(user_id=user_id).first()
        if not user_points:
            return []
        
        rewards = Reward.query.filter(
            Reward.is_active == True,
            Reward.points_required <= user_points.current_points,
            or_(
                Reward.valid_from.is_(None),
                Reward.valid_from <= datetime.utcnow()
            ),
            or_(
                Reward.valid_until.is_(None),
                Reward.valid_until >= datetime.utcnow()
            ),
            or_(
                Reward.max_redemptions.is_(None),
                Reward.current_redemptions < Reward.max_redemptions
            )
        ).all()
        
        return rewards
    
    def redeem_reward(self, user_id, reward_id, invoice_id=None):
        """
        استفاده از جایزه
        
        Args:
            user_id: شناسه کاربر
            reward_id: شناسه جایزه
            invoice_id: شناسه فاکتور (اختیاری)
            
        Returns:
            dict: نتیجه عملیات
        """
        try:
            user_points = UserPoints.query.filter_by(user_id=user_id).first()
            reward = Reward.query.get(reward_id)
            
            if not user_points or not reward:
                return {'success': False, 'message': 'کاربر یا جایزه یافت نشد'}
            
            if not reward.is_valid():
                return {'success': False, 'message': 'جایزه معتبر نیست'}
            
            if user_points.current_points < reward.points_required:
                return {'success': False, 'message': 'امتیاز کافی ندارید'}
            
            # ایجاد تراکنش خرج امتیاز
            transaction = PointsTransaction(
                user_id=user_id,
                points_amount=-reward.points_required,
                transaction_type='spend',
                source_type='reward_redemption',
                source_id=reward_id,
                description=f"استفاده از جایزه: {reward.name_fa}"
            )
            
            # به‌روزرسانی امتیاز کاربر
            user_points.current_points -= reward.points_required
            user_points.total_spent_points += reward.points_required
            
            # ثبت استفاده از جایزه
            redemption = RewardRedemption(
                user_id=user_id,
                reward_id=reward_id,
                points_spent=reward.points_required,
                invoice_id=invoice_id,
                status='used',
                used_at=datetime.utcnow()
            )
            
            # به‌روزرسانی تعداد استفاده جایزه
            reward.current_redemptions += 1
            
            db.session.add(transaction)
            db.session.add(redemption)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'جایزه "{reward.name_fa}" با موفقیت استفاده شد',
                'points_spent': reward.points_required,
                'remaining_points': user_points.current_points
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'خطا در استفاده از جایزه: {str(e)}'}
    
    def expire_old_points(self):
        """انقضای امتیازات قدیمی"""
        try:
            expired_date = datetime.utcnow() - timedelta(days=365)
            
            # پیدا کردن تراکنش‌های منقضی شده
            expired_transactions = PointsTransaction.query.filter(
                PointsTransaction.expires_at <= datetime.utcnow(),
                PointsTransaction.transaction_type == 'earn',
                PointsTransaction.points_amount > 0
            ).all()
            
            expired_points = 0
            affected_users = set()
            
            for transaction in expired_transactions:
                if transaction.points_amount > 0:
                    expired_points += transaction.points_amount
                    affected_users.add(transaction.user_id)
                    
                    # ایجاد تراکنش انقضا
                    expire_transaction = PointsTransaction(
                        user_id=transaction.user_id,
                        points_amount=-transaction.points_amount,
                        transaction_type='expire',
                        source_type='expiration',
                        source_id=transaction.id,
                        description=f"انقضای امتیاز از تراکنش {transaction.id}"
                    )
                    db.session.add(expire_transaction)
            
            # به‌روزرسانی امتیازات کاربران
            for user_id in affected_users:
                user_points = UserPoints.query.filter_by(user_id=user_id).first()
                if user_points:
                    user_points.current_points = max(0, user_points.current_points - expired_points)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'{len(expired_transactions)} تراکنش منقضی شد',
                'expired_points': expired_points,
                'affected_users': len(affected_users)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'خطا در انقضای امتیازات: {str(e)}'}
    
    def adjust_user_points(self, user_id, points_amount, description, admin_id):
        """
        تنظیم دستی امتیازات کاربر (فقط برای ادمین)
        
        Args:
            user_id: شناسه کاربر
            points_amount: مقدار امتیاز (مثبت یا منفی)
            description: توضیحات
            admin_id: شناسه ادمین
            
        Returns:
            dict: نتیجه عملیات
        """
        try:
            user_points = UserPoints.query.filter_by(user_id=user_id).first()
            if not user_points:
                user_points = UserPoints(user_id=user_id)
                db.session.add(user_points)
            
            # ایجاد تراکنش
            transaction = PointsTransaction(
                user_id=user_id,
                points_amount=points_amount,
                transaction_type='earn' if points_amount > 0 else 'spend',
                source_type='admin_adjustment',
                source_id=admin_id,
                description=description
            )
            
            # به‌روزرسانی امتیازات
            user_points.current_points += points_amount
            if points_amount > 0:
                user_points.total_earned_points += points_amount
            else:
                user_points.total_spent_points += abs(points_amount)
            
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'امتیاز کاربر با موفقیت تنظیم شد',
                'new_points': user_points.current_points
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'خطا در تنظیم امتیاز: {str(e)}'}


class PointsAnalytics:
    """کلاس تحلیل و آمار سیستم امتیازدهی"""
    
    @staticmethod
    def get_points_statistics():
        """دریافت آمار کلی سیستم امتیازدهی"""
        try:
            # آمار کاربران
            total_users_with_points = UserPoints.query.count()
            total_points_awarded = db.session.query(db.func.sum(UserPoints.total_earned_points)).scalar() or 0
            total_points_spent = db.session.query(db.func.sum(UserPoints.total_spent_points)).scalar() or 0
            total_current_points = db.session.query(db.func.sum(UserPoints.current_points)).scalar() or 0
            
            # آمار جوایز
            total_rewards = Reward.query.count()
            active_rewards = Reward.query.filter_by(is_active=True).count()
            total_redemptions = RewardRedemption.query.count()
            
            # آمار سطح‌بندی
            user_levels_stats = {}
            levels = UserLevel.query.filter_by(is_active=True).all()
            for level in levels:
                # ساخت کوئری بر اساس وجود یا عدم وجود حداکثر امتیاز
                if level.max_points is None:
                    # اگر حداکثر ندارد، فقط حداقل را بررسی می‌کنیم
                    count = UserPoints.query.filter(
                        UserPoints.current_points >= level.min_points
                    ).count()
                else:
                    # اگر حداکثر دارد، هر دو را بررسی می‌کنیم
                    count = UserPoints.query.filter(
                        UserPoints.current_points >= level.min_points,
                        UserPoints.current_points <= level.max_points
                    ).count()
                user_levels_stats[level.level_name_fa] = count
            
            return {
                'users': {
                    'total_with_points': total_users_with_points,
                    'total_points_awarded': total_points_awarded,
                    'total_points_spent': total_points_spent,
                    'total_current_points': total_current_points
                },
                'rewards': {
                    'total_rewards': total_rewards,
                    'active_rewards': active_rewards,
                    'total_redemptions': total_redemptions
                },
                'user_levels': user_levels_stats
            }
            
        except Exception as e:
            # بازگرداندن ساختار پیش‌فرض در صورت بروز خطا
            return {
                'users': {
                    'total_with_points': 0,
                    'total_points_awarded': 0,
                    'total_points_spent': 0,
                    'total_current_points': 0
                },
                'rewards': {
                    'total_rewards': 0,
                    'active_rewards': 0,
                    'total_redemptions': 0
                },
                'user_levels': {},
                'error': f'خطا در دریافت آمار: {str(e)}'
            }
    
    @staticmethod
    def get_top_users_by_points(limit=10):
        """دریافت کاربران برتر بر اساس امتیازات"""
        try:
            top_users = db.session.query(
                UserPoints, User
            ).join(User).order_by(
                UserPoints.current_points.desc()
            ).limit(limit).all()
            
            result = []
            for user_points, user in top_users:
                result.append({
                    'user_id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'current_points': user_points.current_points,
                    'total_earned': user_points.total_earned_points,
                    'level': PointsService().get_user_level(user.id)
                })
            
            return result
            
        except Exception as e:
            # بازگرداندن لیست خالی در صورت بروز خطا
            return []
    
    @staticmethod
    def get_points_trend(days=30):
        """دریافت روند امتیازات در روزهای اخیر"""
        try:
            from_date = datetime.utcnow() - timedelta(days=days)
            
            # تراکنش‌های کسب امتیاز
            earned_transactions = db.session.query(
                db.func.date(PointsTransaction.created_at).label('date'),
                db.func.sum(PointsTransaction.points_amount).label('points')
            ).filter(
                PointsTransaction.transaction_type == 'earn',
                PointsTransaction.created_at >= from_date
            ).group_by(
                db.func.date(PointsTransaction.created_at)
            ).all()
            
            # تراکنش‌های خرج امتیاز
            spent_transactions = db.session.query(
                db.func.date(PointsTransaction.created_at).label('date'),
                db.func.sum(db.func.abs(PointsTransaction.points_amount)).label('points')
            ).filter(
                PointsTransaction.transaction_type == 'spend',
                PointsTransaction.created_at >= from_date
            ).group_by(
                db.func.date(PointsTransaction.created_at)
            ).all()
            
            return {
                'earned': [{'date': str(t.date), 'points': t.points} for t in earned_transactions],
                'spent': [{'date': str(t.date), 'points': t.points} for t in spent_transactions]
            }
            
        except Exception as e:
            # بازگرداندن ساختار خالی در صورت بروز خطا
            return {
                'earned': [],
                'spent': []
            }


# تابع کمکی برای ایجاد داده‌های اولیه
def init_points_system():
    """ایجاد داده‌های اولیه سیستم امتیازدهی"""
    try:
        # ایجاد قانون پیش‌فرض امتیازدهی
        default_rule = PointsRule.query.filter_by(rule_name='Default Rule').first()
        if not default_rule:
            default_rule = PointsRule(
                rule_name='Default Rule',
                rule_name_fa='Default Rule',
                points_per_100k_rials=0.05,  # Reduced from 500 to 0.05 (4 digits less)
                bonus_points_per_product=0.005,  # Reduced from 50 to 0.005 (4 digits less)
                max_bonus_points=0.1,  # Reduced from 1000 to 0.1 (4 digits less)
                is_active=True
            )
            db.session.add(default_rule)
        
        # ایجاد سطح‌بندی پیش‌فرض
        default_levels = [
            {'level_name': 'Bronze', 'level_name_fa': 'Bronze', 'min_points': 0, 'max_points': 0.0999, 'discount_percentage': 0},  # Reduced from 999 to 0.0999
            {'level_name': 'Silver', 'level_name_fa': 'Silver', 'min_points': 0.1, 'max_points': 0.4999, 'discount_percentage': 5},  # Reduced from 1000-4999 to 0.1-0.4999
            {'level_name': 'Gold', 'level_name_fa': 'Gold', 'min_points': 0.5, 'max_points': 0.9999, 'discount_percentage': 10},  # Reduced from 5000-9999 to 0.5-0.9999
            {'level_name': 'Platinum', 'level_name_fa': 'Platinum', 'min_points': 1, 'max_points': None, 'discount_percentage': 15}  # Reduced from 10000+ to 1+
        ]
        
        for level_data in default_levels:
            existing_level = UserLevel.query.filter_by(level_name=level_data['level_name']).first()
            if not existing_level:
                level = UserLevel(**level_data)
                db.session.add(level)
        
        # ایجاد جوایز نمونه
        sample_rewards = [
            {
                'name': '5% Discount',
                'name_fa': '5% Discount',
                'description': '5% discount on your next purchase',
                'description_fa': '5% discount on your next purchase',
                'points_required': 0.1,  # Reduced from 1000 to 0.1 (4 digits less)
                'discount_percentage': 5,
                'reward_type': 'discount_percentage',
                'is_active': True
            },
            {
                'name': 'Free Shipping',
                'name_fa': 'Free Shipping',
                'description': 'Free shipping on your next order',
                'description_fa': 'Free shipping on your next order',
                'points_required': 0.05,  # Reduced from 500 to 0.05 (4 digits less)
                'reward_type': 'free_shipping',
                'is_active': True
            }
        ]
        
        for reward_data in sample_rewards:
            existing_reward = Reward.query.filter_by(name=reward_data['name']).first()
            if not existing_reward:
                reward = Reward(**reward_data)
                db.session.add(reward)
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating initial data: {str(e)}")
        return False
