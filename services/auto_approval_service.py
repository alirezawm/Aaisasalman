#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Approval Service for Customer Invoices
Handles automatic approval of invoices based on customer type and amount
"""

from datetime import datetime, timedelta
from models import db, Invoice, CustomerInvoiceProfile, InvoiceApprovalWorkflow, UserNotification
import logging

logger = logging.getLogger(__name__)

class AutoApprovalService:
    """سرویس تایید خودکار فاکتورها"""
    
    def __init__(self):
        self.auto_approval_rules = {
            'individual': {
                'max_amount': 1000000,  # 1 میلیون ریال
                'require_document': False,
                'credit_check': False
            },
            'bulk': {
                'max_amount': 5000000,  # 5 میلیون ریال
                'require_document': True,
                'credit_check': True
            }
        }
    
    def process_invoice_approval(self, invoice_id):
        """پردازش تایید خودکار فاکتور"""
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            # Get customer profile
            profile = CustomerInvoiceProfile.query.filter_by(user_id=invoice.user_id).first()
            if not profile:
                logger.error(f"Customer profile not found for user {invoice.user_id}")
                return False
            
            # Check if invoice is eligible for auto approval
            if not self.is_eligible_for_auto_approval(invoice, profile):
                logger.info(f"Invoice {invoice_id} is not eligible for auto approval")
                return False
            
            # Apply auto approval
            success = self.apply_auto_approval(invoice, profile)
            
            if success:
                logger.info(f"Invoice {invoice_id} auto-approved successfully")
                self.send_approval_notification(invoice)
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing auto approval for invoice {invoice_id}: {str(e)}")
            return False
    
    def is_eligible_for_auto_approval(self, invoice, profile):
        """بررسی واجد شرایط بودن فاکتور برای تایید خودکار"""
        try:
            # Check if invoice is in pending status
            if invoice.approval_workflow_status != 'pending':
                return False
            
            # Get customer type rules
            customer_type = profile.customer_type
            rules = self.auto_approval_rules.get(customer_type, {})
            
            # Check amount threshold
            max_amount = rules.get('max_amount', 0)
            if float(invoice.total_amount) > max_amount:
                return False
            
            # Check if document is required
            if rules.get('require_document', False):
                if not invoice.documents or len(invoice.documents) == 0:
                    return False
                
                # Check if all required documents are approved
                for doc in invoice.documents:
                    if not doc.approval_record or doc.approval_record.approval_status != 'approved':
                        return False
            
            # Check credit limit for bulk customers
            if rules.get('credit_check', False):
                available_credit = profile.get_available_credit()
                if float(invoice.total_amount) > available_credit:
                    return False
            
            # Check if customer has good standing
            if not self.check_customer_standing(invoice.user_id):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking auto approval eligibility: {str(e)}")
            return False
    
    def apply_auto_approval(self, invoice, profile):
        """اعمال تایید خودکار فاکتور"""
        try:
            # Update invoice status
            invoice.approval_workflow_status = 'auto_approved'
            invoice.approval_status = 'approved'
            invoice.approval_date = datetime.utcnow()
            invoice.approved_by = None  # System approval
            
            # Apply bulk discount if applicable
            if profile.customer_type == 'bulk' and profile.bulk_discount_percentage > 0:
                discount_amount = float(invoice.total_amount) * (profile.bulk_discount_percentage / 100)
                invoice.bulk_discount_applied = profile.bulk_discount_percentage
                # Note: In a real system, you might want to create a separate discount record
            
            # Update or create workflow record
            workflow = InvoiceApprovalWorkflow.query.filter_by(invoice_id=invoice.id).first()
            if workflow:
                workflow.workflow_status = 'auto_approved'
                workflow.auto_approval_eligible = True
                workflow.manual_approval_required = False
                workflow.approval_notes = 'تایید خودکار توسط سیستم'
            else:
                workflow = InvoiceApprovalWorkflow(
                    invoice_id=invoice.id,
                    workflow_status='auto_approved',
                    auto_approval_eligible=True,
                    manual_approval_required=False,
                    approval_notes='تایید خودکار توسط سیستم'
                )
                db.session.add(workflow)
            
            # Update customer credit usage if applicable
            if profile.customer_type == 'bulk':
                profile.current_credit_used += float(invoice.total_amount)
            
            # Update customer total purchase amount
            invoice.user.total_purchase_amount += float(invoice.total_amount)
            
            # Update customer level if needed
            self.update_customer_level(invoice.user)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error applying auto approval: {str(e)}")
            return False
    
    def check_customer_standing(self, user_id):
        """بررسی وضعیت مشتری"""
        try:
            # Check if customer has any rejected invoices in the last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            rejected_count = Invoice.query.filter(
                Invoice.user_id == user_id,
                Invoice.approval_workflow_status == 'rejected',
                Invoice.created_at >= thirty_days_ago
            ).count()
            
            # If more than 3 rejections in 30 days, require manual approval
            if rejected_count > 3:
                return False
            
            # Check if customer has any overdue invoices
            overdue_count = Invoice.query.filter(
                Invoice.user_id == user_id,
                Invoice.approval_workflow_status == 'approved',
                Invoice.due_date < datetime.utcnow(),
                Invoice.status == 'pending'
            ).count()
            
            # If more than 2 overdue invoices, require manual approval
            if overdue_count > 2:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking customer standing: {str(e)}")
            return False
    
    def update_customer_level(self, user):
        """به‌روزرسانی سطح مشتری بر اساس حجم خرید"""
        try:
            if user.customer_type != 'bulk':
                return
            
            total_amount = float(user.total_purchase_amount)
            
            if total_amount >= 100000000:  # 100 میلیون
                new_level = 'platinum'
            elif total_amount >= 50000000:  # 50 میلیون
                new_level = 'gold'
            elif total_amount >= 10000000:  # 10 میلیون
                new_level = 'silver'
            else:
                new_level = 'bronze'
            
            if user.bulk_customer_level != new_level:
                old_level = user.bulk_customer_level
                user.bulk_customer_level = new_level
                
                # Update profile benefits
                profile = CustomerInvoiceProfile.query.filter_by(user_id=user.id).first()
                if profile:
                    # Update discount percentage based on new level
                    discount_map = {
                        'bronze': 5.0,
                        'silver': 8.0,
                        'gold': 12.0,
                        'platinum': 15.0
                    }
                    profile.bulk_discount_percentage = discount_map.get(new_level, 0.0)
                    
                    # Update auto approval limit
                    limit_map = {
                        'bronze': 5000000,
                        'silver': 10000000,
                        'gold': 20000000,
                        'platinum': 50000000
                    }
                    profile.auto_approval_limit = limit_map.get(new_level, 5000000)
                
                # Send level upgrade notification
                self.send_level_upgrade_notification(user, old_level, new_level)
                
                logger.info(f"Customer {user.username} upgraded from {old_level} to {new_level}")
            
        except Exception as e:
            logger.error(f"Error updating customer level: {str(e)}")
    
    def send_approval_notification(self, invoice):
        """ارسال اطلاع‌رسانی تایید فاکتور"""
        try:
            notification = UserNotification(
                user_id=invoice.user_id,
                notification_type='invoice_auto_approved',
                title='فاکتور تایید شد',
                message=f'فاکتور شماره {invoice.invoice_number} با مبلغ {invoice.total_amount:,.0f} ریال به صورت خودکار تایید شد',
                related_invoice_id=invoice.id,
                notification_action='auto_approve'
            )
            
            db.session.add(notification)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending approval notification: {str(e)}")
    
    def send_level_upgrade_notification(self, user, old_level, new_level):
        """ارسال اطلاع‌رسانی ارتقای سطح"""
        try:
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
                message=f'تبریک! سطح شما از {level_names.get(old_level, old_level)} به {level_names.get(new_level, new_level)} ارتقا یافت',
                notification_action='level_upgrade'
            )
            
            db.session.add(notification)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending level upgrade notification: {str(e)}")
    
    def process_pending_invoices(self):
        """پردازش فاکتورهای در انتظار تایید خودکار"""
        try:
            # Get invoices eligible for auto approval
            pending_invoices = Invoice.query.filter(
                Invoice.approval_workflow_status == 'pending',
                Invoice.created_at >= datetime.utcnow() - timedelta(hours=24)  # Only process recent invoices
            ).all()
            
            processed_count = 0
            approved_count = 0
            
            for invoice in pending_invoices:
                processed_count += 1
                if self.process_invoice_approval(invoice.id):
                    approved_count += 1
            
            logger.info(f"Processed {processed_count} pending invoices, {approved_count} auto-approved")
            return {
                'processed': processed_count,
                'approved': approved_count
            }
            
        except Exception as e:
            logger.error(f"Error processing pending invoices: {str(e)}")
            return {'processed': 0, 'approved': 0}

# Global instance
auto_approval_service = AutoApprovalService()
