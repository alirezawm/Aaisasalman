#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Customer Type Service
Handles differentiation between individual and bulk customers
"""

from datetime import datetime, timedelta
from models import db, User, CustomerInvoiceProfile, BulkCustomerBenefits, Invoice
import logging

logger = logging.getLogger(__name__)

class CustomerTypeService:
    """سرویس تفکیک مشتریان تکی و عمده"""
    
    def __init__(self):
        self.customer_levels = {
            'bronze': {
                'min_amount': 0,
                'max_amount': 10000000,
                'discount_percentage': 5.0,
                'auto_approval_limit': 5000000,
                'credit_multiplier': 0.05,
                'priority_support': False
            },
            'silver': {
                'min_amount': 10000000,
                'max_amount': 50000000,
                'discount_percentage': 8.0,
                'auto_approval_limit': 10000000,
                'credit_multiplier': 0.08,
                'priority_support': False
            },
            'gold': {
                'min_amount': 50000000,
                'max_amount': 100000000,
                'discount_percentage': 12.0,
                'auto_approval_limit': 20000000,
                'credit_multiplier': 0.12,
                'priority_support': True
            },
            'platinum': {
                'min_amount': 100000000,
                'max_amount': float('inf'),
                'discount_percentage': 15.0,
                'auto_approval_limit': 50000000,
                'credit_multiplier': 0.15,
                'priority_support': True
            }
        }
    
    def create_customer_profile(self, user_id, customer_type='individual'):
        """ایجاد پروفایل مشتری"""
        try:
            # Check if profile already exists
            existing_profile = CustomerInvoiceProfile.query.filter_by(user_id=user_id).first()
            if existing_profile:
                logger.info(f"Profile already exists for user {user_id}")
                return existing_profile
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            # Determine customer type if not specified
            if customer_type == 'auto':
                customer_type = self.determine_customer_type(user)
            
            # Get level configuration
            level_config = self.get_level_config(customer_type, user.total_purchase_amount)
            
            # Create profile
            profile = CustomerInvoiceProfile(
                user_id=user_id,
                customer_type=customer_type,
                auto_approval_limit=level_config['auto_approval_limit'],
                bulk_discount_percentage=level_config['discount_percentage'],
                credit_limit=level_config['credit_limit'],
                current_credit_used=0
            )
            
            db.session.add(profile)
            
            # Update user
            user.customer_type = customer_type
            user.bulk_customer_level = level_config['level']
            
            db.session.commit()
            
            # Create benefits for bulk customers
            if customer_type == 'bulk':
                self.create_bulk_benefits(user_id, level_config)
            
            logger.info(f"Customer profile created for user {user_id} as {customer_type}")
            return profile
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating customer profile: {str(e)}")
            return None
    
    def determine_customer_type(self, user):
        """تعیین نوع مشتری بر اساس معیارها"""
        try:
            # Check if user is already marked as bulk buyer
            if user.is_bulk_buyer and user.bulk_buyer_approval_status == 'approved':
                return 'bulk'
            
            # Check purchase history
            total_purchases = float(user.total_purchase_amount)
            
            # If total purchases > 50 million, consider as bulk
            if total_purchases > 50000000:
                return 'bulk'
            
            # Check recent purchase frequency
            recent_invoices = Invoice.query.filter(
                Invoice.user_id == user.id,
                Invoice.created_at >= datetime.utcnow() - timedelta(days=90)
            ).count()
            
            # If more than 10 invoices in last 3 months, consider as bulk
            if recent_invoices > 10:
                return 'bulk'
            
            return 'individual'
            
        except Exception as e:
            logger.error(f"Error determining customer type: {str(e)}")
            return 'individual'
    
    def get_level_config(self, customer_type, total_amount):
        """دریافت تنظیمات سطح مشتری"""
        try:
            if customer_type == 'individual':
                return {
                    'level': 'individual',
                    'auto_approval_limit': 1000000,
                    'discount_percentage': 0.0,
                    'credit_limit': 0,
                    'priority_support': False
                }
            
            # Find appropriate level for bulk customers
            for level, config in self.customer_levels.items():
                if config['min_amount'] <= total_amount < config['max_amount']:
                    return {
                        'level': level,
                        'auto_approval_limit': config['auto_approval_limit'],
                        'discount_percentage': config['discount_percentage'],
                        'credit_limit': total_amount * config['credit_multiplier'],
                        'priority_support': config['priority_support']
                    }
            
            # If amount exceeds all levels, use platinum
            return {
                'level': 'platinum',
                'auto_approval_limit': self.customer_levels['platinum']['auto_approval_limit'],
                'discount_percentage': self.customer_levels['platinum']['discount_percentage'],
                'credit_limit': total_amount * self.customer_levels['platinum']['credit_multiplier'],
                'priority_support': self.customer_levels['platinum']['priority_support']
            }
            
        except Exception as e:
            logger.error(f"Error getting level config: {str(e)}")
            return self.customer_levels['bronze']
    
    def create_bulk_benefits(self, user_id, level_config):
        """ایجاد مزایای مشتریان عمده"""
        try:
            # Create discount benefit
            discount_benefit = BulkCustomerBenefits(
                user_id=user_id,
                benefit_type='discount',
                benefit_value=level_config['discount_percentage'],
                benefit_description=f'تخفیف عمده - سطح {level_config["level"]}',
                is_active=True
            )
            db.session.add(discount_benefit)
            
            # Create credit benefit
            if level_config['credit_limit'] > 0:
                credit_benefit = BulkCustomerBenefits(
                    user_id=user_id,
                    benefit_type='credit_increase',
                    benefit_value=level_config['credit_limit'],
                    benefit_description='افزایش اعتبار بر اساس سطح مشتری',
                    is_active=True
                )
                db.session.add(credit_benefit)
            
            # Create priority support benefit
            if level_config['priority_support']:
                priority_benefit = BulkCustomerBenefits(
                    user_id=user_id,
                    benefit_type='priority_support',
                    benefit_value=1.0,
                    benefit_description='پشتیبانی اولویت‌دار',
                    is_active=True
                )
                db.session.add(priority_benefit)
            
            db.session.commit()
            logger.info(f"Bulk benefits created for user {user_id}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating bulk benefits: {str(e)}")
    
    def update_customer_level(self, user_id):
        """به‌روزرسانی سطح مشتری"""
        try:
            user = User.query.get(user_id)
            if not user or user.customer_type != 'bulk':
                return False
            
            profile = CustomerInvoiceProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                return False
            
            # Get current level config
            current_config = self.get_level_config('bulk', user.total_purchase_amount)
            new_level = current_config['level']
            
            # Check if level changed
            if user.bulk_customer_level != new_level:
                old_level = user.bulk_customer_level
                
                # Update user level
                user.bulk_customer_level = new_level
                
                # Update profile
                profile.auto_approval_limit = current_config['auto_approval_limit']
                profile.bulk_discount_percentage = current_config['discount_percentage']
                profile.credit_limit = current_config['credit_limit']
                
                # Update benefits
                self.update_bulk_benefits(user_id, current_config)
                
                db.session.commit()
                
                # Send level upgrade notification
                self.send_level_upgrade_notification(user, old_level, new_level)
                
                logger.info(f"Customer {user.username} upgraded from {old_level} to {new_level}")
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating customer level: {str(e)}")
            return False
    
    def update_bulk_benefits(self, user_id, level_config):
        """به‌روزرسانی مزایای مشتریان عمده"""
        try:
            # Update discount benefit
            discount_benefit = BulkCustomerBenefits.query.filter_by(
                user_id=user_id,
                benefit_type='discount'
            ).first()
            
            if discount_benefit:
                discount_benefit.benefit_value = level_config['discount_percentage']
                discount_benefit.benefit_description = f'تخفیف عمده - سطح {level_config["level"]}'
            else:
                discount_benefit = BulkCustomerBenefits(
                    user_id=user_id,
                    benefit_type='discount',
                    benefit_value=level_config['discount_percentage'],
                    benefit_description=f'تخفیف عمده - سطح {level_config["level"]}',
                    is_active=True
                )
                db.session.add(discount_benefit)
            
            # Update credit benefit
            if level_config['credit_limit'] > 0:
                credit_benefit = BulkCustomerBenefits.query.filter_by(
                    user_id=user_id,
                    benefit_type='credit_increase'
                ).first()
                
                if credit_benefit:
                    credit_benefit.benefit_value = level_config['credit_limit']
                else:
                    credit_benefit = BulkCustomerBenefits(
                        user_id=user_id,
                        benefit_type='credit_increase',
                        benefit_value=level_config['credit_limit'],
                        benefit_description='افزایش اعتبار بر اساس سطح مشتری',
                        is_active=True
                    )
                    db.session.add(credit_benefit)
            
            # Update priority support benefit
            priority_benefit = BulkCustomerBenefits.query.filter_by(
                user_id=user_id,
                benefit_type='priority_support'
            ).first()
            
            if level_config['priority_support']:
                if not priority_benefit:
                    priority_benefit = BulkCustomerBenefits(
                        user_id=user_id,
                        benefit_type='priority_support',
                        benefit_value=1.0,
                        benefit_description='پشتیبانی اولویت‌دار',
                        is_active=True
                    )
                    db.session.add(priority_benefit)
            else:
                if priority_benefit:
                    priority_benefit.is_active = False
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating bulk benefits: {str(e)}")
    
    def send_level_upgrade_notification(self, user, old_level, new_level):
        """ارسال اطلاع‌رسانی ارتقای سطح"""
        try:
            from models import UserNotification
            
            level_names = {
                'bronze': 'برنزی',
                'silver': 'نقره‌ای',
                'gold': 'طلایی',
                'platinum': 'پلاتینی'
            }
            
            notification = UserNotification(
                user_id=user.id,
                notification_type='level_upgrade',
                title='ارتقای سطح مشتری',
                message=f'تبریک! سطح شما از {level_names.get(old_level, old_level)} به {level_names.get(new_level, new_level)} ارتقا یافت. مزایای جدید برای شما فعال شد.',
                notification_action='level_upgrade'
            )
            
            db.session.add(notification)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending level upgrade notification: {str(e)}")
    
    def get_customer_dashboard_data(self, user_id):
        """دریافت داده‌های داشبورد مشتری"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            profile = CustomerInvoiceProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                # Create profile if it doesn't exist
                profile = self.create_customer_profile(user_id)
                if not profile:
                    return None
            
            # Get recent invoices
            recent_invoices = Invoice.query.filter_by(user_id=user_id).order_by(
                Invoice.created_at.desc()
            ).limit(5).all()
            
            # Get statistics
            total_invoices = Invoice.query.filter_by(user_id=user_id).count()
            pending_invoices = Invoice.query.filter(
                Invoice.user_id == user_id,
                Invoice.approval_workflow_status == 'pending'
            ).count()
            approved_invoices = Invoice.query.filter(
                Invoice.user_id == user_id,
                Invoice.approval_workflow_status.in_(['auto_approved', 'manual_approved'])
            ).count()
            
            # Get bulk benefits if applicable
            benefits = []
            if user.customer_type == 'bulk':
                benefits = BulkCustomerBenefits.query.filter_by(
                    user_id=user_id,
                    is_active=True
                ).all()
            
            return {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'customer_type': user.customer_type,
                    'bulk_customer_level': user.bulk_customer_level,
                    'total_purchase_amount': float(user.total_purchase_amount)
                },
                'profile': {
                    'auto_approval_limit': float(profile.auto_approval_limit),
                    'bulk_discount_percentage': float(profile.bulk_discount_percentage),
                    'credit_limit': float(profile.credit_limit),
                    'current_credit_used': float(profile.current_credit_used),
                    'available_credit': float(profile.get_available_credit())
                },
                'statistics': {
                    'total_invoices': total_invoices,
                    'pending_invoices': pending_invoices,
                    'approved_invoices': approved_invoices,
                    'rejected_invoices': total_invoices - pending_invoices - approved_invoices
                },
                'recent_invoices': [
                    {
                        'id': inv.id,
                        'invoice_number': inv.invoice_number,
                        'total_amount': float(inv.total_amount),
                        'status': inv.approval_workflow_status,
                        'created_at': inv.created_at.isoformat()
                    }
                    for inv in recent_invoices
                ],
                'benefits': [
                    {
                        'type': benefit.benefit_type,
                        'value': float(benefit.benefit_value),
                        'description': benefit.benefit_description
                    }
                    for benefit in benefits
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting customer dashboard data: {str(e)}")
            return None
    
    def get_customer_type_statistics(self):
        """دریافت آمار انواع مشتریان"""
        try:
            individual_count = User.query.filter_by(customer_type='individual').count()
            bulk_count = User.query.filter_by(customer_type='bulk').count()
            
            # Get level distribution for bulk customers
            level_distribution = {}
            for level in ['bronze', 'silver', 'gold', 'platinum']:
                count = User.query.filter_by(
                    customer_type='bulk',
                    bulk_customer_level=level
                ).count()
                level_distribution[level] = count
            
            return {
                'individual_customers': individual_count,
                'bulk_customers': bulk_count,
                'total_customers': individual_count + bulk_count,
                'bulk_level_distribution': level_distribution
            }
            
        except Exception as e:
            logger.error(f"Error getting customer type statistics: {str(e)}")
            return {
                'individual_customers': 0,
                'bulk_customers': 0,
                'total_customers': 0,
                'bulk_level_distribution': {}
            }

# Global instance
customer_type_service = CustomerTypeService()
