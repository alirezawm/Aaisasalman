#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual Approval Service for Customer Invoices
Handles manual approval workflow for invoices that require admin review
"""

from datetime import datetime, timedelta
from models import db, Invoice, CustomerInvoiceProfile, InvoiceApprovalWorkflow, UserNotification, User
import logging

logger = logging.getLogger(__name__)

class ManualApprovalService:
    """سرویس تایید دستی فاکتورها"""
    
    def __init__(self):
        self.priority_rules = {
            'high': {
                'amount_threshold': 20000000,  # 20 میلیون ریال
                'bulk_customer': True,
                'urgent_keywords': ['فوری', 'اضطراری', 'urgent']
            },
            'medium': {
                'amount_threshold': 10000000,  # 10 میلیون ریال
                'bulk_customer': True,
                'urgent_keywords': []
            },
            'low': {
                'amount_threshold': 0,
                'bulk_customer': False,
                'urgent_keywords': []
            }
        }
    
    def create_approval_workflow(self, invoice_id, assigned_to=None):
        """ایجاد فرآیند تایید دستی برای فاکتور"""
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            # Check if workflow already exists
            existing_workflow = InvoiceApprovalWorkflow.query.filter_by(invoice_id=invoice_id).first()
            if existing_workflow:
                logger.info(f"Workflow already exists for invoice {invoice_id}")
                return True
            
            # Get customer profile
            profile = CustomerInvoiceProfile.query.filter_by(user_id=invoice.user_id).first()
            if not profile:
                logger.error(f"Customer profile not found for user {invoice.user_id}")
                return False
            
            # Determine priority level
            priority = self.determine_priority(invoice, profile)
            
            # Assign to appropriate admin
            if not assigned_to:
                assigned_to = self.assign_to_admin(invoice, profile, priority)
            
            # Set deadline based on priority
            deadline = self.calculate_deadline(priority)
            
            # Create workflow
            workflow = InvoiceApprovalWorkflow(
                invoice_id=invoice_id,
                workflow_status='pending',
                auto_approval_eligible=False,
                manual_approval_required=True,
                assigned_to=assigned_to,
                priority_level=priority,
                deadline=deadline,
                approval_notes='در انتظار تایید دستی'
            )
            
            db.session.add(workflow)
            
            # Update invoice status
            invoice.approval_workflow_status = 'pending'
            invoice.document_required = self.requires_document(invoice, profile)
            
            db.session.commit()
            
            # Send notification to assigned admin
            self.send_assignment_notification(assigned_to, invoice, priority)
            
            # Send notification to customer
            self.send_customer_notification(invoice, 'pending_review')
            
            logger.info(f"Manual approval workflow created for invoice {invoice_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating approval workflow: {str(e)}")
            return False
    
    def determine_priority(self, invoice, profile):
        """تعیین اولویت فاکتور"""
        try:
            amount = float(invoice.total_amount)
            
            # Check for high priority conditions
            if (amount >= self.priority_rules['high']['amount_threshold'] or 
                profile.customer_type == 'bulk' and amount >= 10000000):
                return 3  # High priority
            
            # Check for medium priority conditions
            if (amount >= self.priority_rules['medium']['amount_threshold'] or 
                profile.customer_type == 'bulk'):
                return 2  # Medium priority
            
            return 1  # Low priority
            
        except Exception as e:
            logger.error(f"Error determining priority: {str(e)}")
            return 1
    
    def assign_to_admin(self, invoice, profile, priority):
        """تخصیص فاکتور به ادمین مناسب"""
        try:
            # Get available admins with order management role
            admins = User.query.filter(
                User.is_admin == True
            ).all()
            
            if not admins:
                logger.error("No admins available for assignment")
                return None
            
            # For bulk customers, try to assign to their sales manager
            if profile.customer_type == 'bulk' and profile.assigned_sales_manager:
                sales_manager = User.query.get(profile.assigned_sales_manager)
                if sales_manager and sales_manager.is_admin:
                    return sales_manager.id
            
            # For high priority invoices, assign to most experienced admin
            if priority == 3:
                # Find admin with least assigned invoices
                admin_workloads = []
                for admin in admins:
                    workload = InvoiceApprovalWorkflow.query.filter(
                        InvoiceApprovalWorkflow.assigned_to == admin.id,
                        InvoiceApprovalWorkflow.workflow_status == 'pending'
                    ).count()
                    admin_workloads.append((admin.id, workload))
                
                # Sort by workload and return least busy admin
                admin_workloads.sort(key=lambda x: x[1])
                return admin_workloads[0][0]
            
            # For medium and low priority, use round-robin or random assignment
            import random
            return random.choice(admins).id
            
        except Exception as e:
            logger.error(f"Error assigning to admin: {str(e)}")
            return None
    
    def calculate_deadline(self, priority):
        """محاسبه مهلت تایید بر اساس اولویت"""
        try:
            now = datetime.utcnow()
            
            if priority == 3:  # High priority
                return now + timedelta(hours=4)
            elif priority == 2:  # Medium priority
                return now + timedelta(hours=12)
            else:  # Low priority
                return now + timedelta(days=1)
                
        except Exception as e:
            logger.error(f"Error calculating deadline: {str(e)}")
            return datetime.utcnow() + timedelta(hours=24)
    
    def requires_document(self, invoice, profile):
        """بررسی نیاز به بارگذاری مدرک"""
        try:
            # Always require document for bulk customers with high amounts
            if profile.customer_type == 'bulk' and float(invoice.total_amount) > 5000000:
                return True
            
            # Require document for individual customers with high amounts
            if profile.customer_type == 'individual' and float(invoice.total_amount) > 2000000:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking document requirement: {str(e)}")
            return False
    
    def approve_invoice(self, invoice_id, admin_id, approval_notes=''):
        """تایید فاکتور توسط ادمین"""
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            workflow = InvoiceApprovalWorkflow.query.filter_by(invoice_id=invoice_id).first()
            if not workflow:
                logger.error(f"Workflow not found for invoice {invoice_id}")
                return False
            
            # Check if admin is authorized to approve this invoice
            if workflow.assigned_to != admin_id:
                logger.error(f"Admin {admin_id} not authorized to approve invoice {invoice_id}")
                return False
            
            # Update invoice status
            invoice.approval_workflow_status = 'manual_approved'
            invoice.approval_status = 'approved'
            invoice.approval_date = datetime.utcnow()
            invoice.approved_by = admin_id
            invoice.admin_notes = approval_notes
            
            # Update workflow
            workflow.workflow_status = 'manual_approved'
            workflow.approval_notes = approval_notes
            
            # Update customer profile if needed
            profile = CustomerInvoiceProfile.query.filter_by(user_id=invoice.user_id).first()
            if profile and profile.customer_type == 'bulk':
                profile.current_credit_used += float(invoice.total_amount)
            
            # Update customer total purchase amount
            invoice.user.total_purchase_amount += float(invoice.total_amount)
            
            db.session.commit()
            
            # Send notifications
            self.send_customer_notification(invoice, 'approved')
            self.send_admin_notification(admin_id, invoice, 'approved')
            
            logger.info(f"Invoice {invoice_id} approved by admin {admin_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error approving invoice: {str(e)}")
            return False
    
    def reject_invoice(self, invoice_id, admin_id, rejection_reason, admin_notes=''):
        """رد فاکتور توسط ادمین"""
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            workflow = InvoiceApprovalWorkflow.query.filter_by(invoice_id=invoice_id).first()
            if not workflow:
                logger.error(f"Workflow not found for invoice {invoice_id}")
                return False
            
            # Check if admin is authorized to reject this invoice
            if workflow.assigned_to != admin_id:
                logger.error(f"Admin {admin_id} not authorized to reject invoice {invoice_id}")
                return False
            
            # Update invoice status
            invoice.approval_workflow_status = 'rejected'
            invoice.approval_status = 'rejected'
            invoice.rejection_reason = rejection_reason
            invoice.admin_notes = admin_notes
            
            # Update workflow
            workflow.workflow_status = 'rejected'
            workflow.approval_notes = f"رد شده: {rejection_reason}"
            
            db.session.commit()
            
            # Send notifications
            self.send_customer_notification(invoice, 'rejected', rejection_reason)
            self.send_admin_notification(admin_id, invoice, 'rejected')
            
            logger.info(f"Invoice {invoice_id} rejected by admin {admin_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error rejecting invoice: {str(e)}")
            return False
    
    def send_assignment_notification(self, admin_id, invoice, priority):
        """ارسال اطلاع‌رسانی تخصیص به ادمین"""
        try:
            priority_text = {1: 'کم', 2: 'متوسط', 3: 'بالا'}.get(priority, 'نامشخص')
            
            notification = UserNotification(
                user_id=admin_id,
                notification_type='invoice_assigned',
                title='فاکتور جدید برای تایید',
                message=f'فاکتور شماره {invoice.invoice_number} با اولویت {priority_text} به شما تخصیص داده شد',
                related_invoice_id=invoice.id,
                notification_action='assign'
            )
            
            db.session.add(notification)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending assignment notification: {str(e)}")
    
    def send_customer_notification(self, invoice, action, reason=''):
        """ارسال اطلاع‌رسانی به مشتری"""
        try:
            if action == 'pending_review':
                title = 'فاکتور در حال بررسی'
                message = f'فاکتور شماره {invoice.invoice_number} در حال بررسی توسط تیم ما است'
            elif action == 'approved':
                title = 'فاکتور تایید شد'
                message = f'فاکتور شماره {invoice.invoice_number} با موفقیت تایید شد'
            elif action == 'rejected':
                title = 'فاکتور رد شد'
                message = f'فاکتور شماره {invoice.invoice_number} رد شد. دلیل: {reason}'
            else:
                return
            
            notification = UserNotification(
                user_id=invoice.user_id,
                notification_type=f'invoice_{action}',
                title=title,
                message=message,
                related_invoice_id=invoice.id,
                notification_action=action
            )
            
            db.session.add(notification)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending customer notification: {str(e)}")
    
    def send_admin_notification(self, admin_id, invoice, action):
        """ارسال اطلاع‌رسانی به ادمین"""
        try:
            if action == 'approved':
                title = 'فاکتور تایید شد'
                message = f'فاکتور شماره {invoice.invoice_number} با موفقیت تایید شد'
            elif action == 'rejected':
                title = 'فاکتور رد شد'
                message = f'فاکتور شماره {invoice.invoice_number} رد شد'
            else:
                return
            
            notification = UserNotification(
                user_id=admin_id,
                notification_type=f'admin_invoice_{action}',
                title=title,
                message=message,
                related_invoice_id=invoice.id,
                notification_action=action
            )
            
            db.session.add(notification)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending admin notification: {str(e)}")
    
    def get_pending_invoices(self, admin_id=None, priority=None):
        """دریافت فاکتورهای در انتظار تایید"""
        try:
            query = InvoiceApprovalWorkflow.query.filter(
                InvoiceApprovalWorkflow.workflow_status == 'pending'
            )
            
            if admin_id:
                query = query.filter(InvoiceApprovalWorkflow.assigned_to == admin_id)
            
            if priority:
                query = query.filter(InvoiceApprovalWorkflow.priority_level == priority)
            
            return query.order_by(
                InvoiceApprovalWorkflow.priority_level.desc(),
                InvoiceApprovalWorkflow.deadline.asc()
            ).all()
            
        except Exception as e:
            logger.error(f"Error getting pending invoices: {str(e)}")
            return []
    
    def get_overdue_invoices(self):
        """دریافت فاکتورهای منقضی شده"""
        try:
            now = datetime.utcnow()
            
            return InvoiceApprovalWorkflow.query.filter(
                InvoiceApprovalWorkflow.workflow_status == 'pending',
                InvoiceApprovalWorkflow.deadline < now
            ).order_by(InvoiceApprovalWorkflow.deadline.asc()).all()
            
        except Exception as e:
            logger.error(f"Error getting overdue invoices: {str(e)}")
            return []

# Global instance
manual_approval_service = ManualApprovalService()
