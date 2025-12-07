#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Notification Service for Customer Invoice Management
Handles all types of notifications for the invoice management system
"""

from datetime import datetime, timedelta
from models import db, UserNotification, User, Invoice, CustomerInvoiceProfile
import logging
import json

logger = logging.getLogger(__name__)

class NotificationService:
    """سرویس اطلاع‌رسانی پیشرفته"""
    
    def __init__(self):
        self.notification_templates = {
            'invoice_created': {
                'title': 'فاکتور جدید ایجاد شد',
                'template': 'فاکتور شماره {invoice_number} با مبلغ {amount} ریال ایجاد شد',
                'priority': 'info',
                'auto_read': False
            },
            'invoice_auto_approved': {
                'title': 'فاکتور تایید شد',
                'template': 'فاکتور شماره {invoice_number} با مبلغ {amount} ریال به صورت خودکار تایید شد',
                'priority': 'success',
                'auto_read': False
            },
            'invoice_manual_approved': {
                'title': 'فاکتور تایید شد',
                'template': 'فاکتور شماره {invoice_number} با مبلغ {amount} ریال توسط تیم ما تایید شد',
                'priority': 'success',
                'auto_read': False
            },
            'invoice_rejected': {
                'title': 'فاکتور رد شد',
                'template': 'فاکتور شماره {invoice_number} رد شد. دلیل: {reason}',
                'priority': 'error',
                'auto_read': False
            },
            'document_required': {
                'title': 'نیاز به بارگذاری مدرک',
                'template': 'لطفاً مدرک پرداخت فاکتور شماره {invoice_number} را بارگذاری کنید',
                'priority': 'warning',
                'auto_read': False
            },
            'document_approved': {
                'title': 'مدرک تایید شد',
                'template': 'مدرک فاکتور شماره {invoice_number} تایید شد',
                'priority': 'success',
                'auto_read': True
            },
            'document_rejected': {
                'title': 'مدرک رد شد',
                'template': 'مدرک فاکتور شماره {invoice_number} رد شد. دلیل: {reason}',
                'priority': 'error',
                'auto_read': False
            },
            'level_upgrade': {
                'title': 'ارتقای سطح مشتری',
                'template': 'تبریک! سطح شما به {new_level} ارتقا یافت. مزایای جدید برای شما فعال شد.',
                'priority': 'success',
                'auto_read': False
            },
            'credit_limit_warning': {
                'title': 'هشدار حد اعتبار',
                'template': 'اعتبار شما در حال اتمام است. اعتبار باقی‌مانده: {remaining_credit} ریال',
                'priority': 'warning',
                'auto_read': False
            },
            'payment_reminder': {
                'title': 'یادآوری پرداخت',
                'template': 'فاکتور شماره {invoice_number} در حال انقضا است. لطفاً نسبت به پرداخت اقدام کنید.',
                'priority': 'warning',
                'auto_read': False
            },
            'bulk_benefit_activated': {
                'title': 'مزایای جدید فعال شد',
                'template': 'مزایای جدید مشتریان عمده برای شما فعال شد: {benefits}',
                'priority': 'info',
                'auto_read': False
            }
        }
    
    def send_notification(self, user_id, notification_type, data=None, related_invoice_id=None, action=None):
        """ارسال اطلاع‌رسانی"""
        try:
            # Get notification template
            template = self.notification_templates.get(notification_type)
            if not template:
                logger.error(f"Unknown notification type: {notification_type}")
                return False
            
            # Format message
            message = self.format_message(template['template'], data or {})
            
            # Create notification
            notification = UserNotification(
                user_id=user_id,
                notification_type=notification_type,
                title=template['title'],
                message=message,
                related_invoice_id=related_invoice_id,
                notification_action=action,
                is_read=template['auto_read']
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Send real-time notification if user is online
            self.send_realtime_notification(user_id, notification)
            
            logger.info(f"Notification sent to user {user_id}: {notification_type}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sending notification: {str(e)}")
            return False
    
    def format_message(self, template, data):
        """فرمت‌بندی پیام اطلاع‌رسانی"""
        try:
            # Format currency values
            if 'amount' in data:
                data['amount'] = f"{data['amount']:,.0f}"
            
            if 'remaining_credit' in data:
                data['remaining_credit'] = f"{data['remaining_credit']:,.0f}"
            
            # Format date values
            if 'date' in data and isinstance(data['date'], datetime):
                data['date'] = data['date'].strftime('%Y/%m/%d %H:%M')
            
            # Format level names
            if 'new_level' in data:
                level_names = {
                    'bronze': 'برنزی',
                    'silver': 'نقره‌ای',
                    'gold': 'طلایی',
                    'platinum': 'پلاتینی'
                }
                data['new_level'] = level_names.get(data['new_level'], data['new_level'])
            
            return template.format(**data)
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return template
    
    def send_realtime_notification(self, user_id, notification):
        """ارسال اطلاع‌رسانی لحظه‌ای"""
        try:
            # This would integrate with WebSocket or Server-Sent Events
            # For now, we'll just log it
            logger.info(f"Real-time notification for user {user_id}: {notification.title}")
            
            # In a real implementation, you would:
            # 1. Check if user is online
            # 2. Send WebSocket message
            # 3. Update notification count in real-time
            
        except Exception as e:
            logger.error(f"Error sending real-time notification: {str(e)}")
    
    def send_invoice_notifications(self, invoice_id, action, additional_data=None):
        """ارسال اطلاع‌رسانی‌های مربوط به فاکتور"""
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                return False
            
            data = {
                'invoice_number': invoice.invoice_number,
                'amount': float(invoice.total_amount),
                'date': invoice.created_at
            }
            
            if additional_data:
                data.update(additional_data)
            
            # Send to customer
            self.send_notification(
                user_id=invoice.user_id,
                notification_type=f'invoice_{action}',
                data=data,
                related_invoice_id=invoice_id,
                action=action
            )
            
            # Send to assigned admin if applicable
            if invoice.sales_manager_id:
                self.send_notification(
                    user_id=invoice.sales_manager_id,
                    notification_type=f'admin_invoice_{action}',
                    data=data,
                    related_invoice_id=invoice_id,
                    action=action
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending invoice notifications: {str(e)}")
            return False
    
    def send_document_notifications(self, document_id, action, additional_data=None):
        """ارسال اطلاع‌رسانی‌های مربوط به مدارک"""
        try:
            from models import InvoiceDocument
            document = InvoiceDocument.query.get(document_id)
            if not document:
                return False
            
            invoice = document.invoice
            data = {
                'invoice_number': invoice.invoice_number,
                'document_type': self.get_document_type_name(document.document_type)
            }
            
            if additional_data:
                data.update(additional_data)
            
            # Send to customer
            self.send_notification(
                user_id=invoice.user_id,
                notification_type=f'document_{action}',
                data=data,
                related_invoice_id=invoice.id,
                action=action
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending document notifications: {str(e)}")
            return False
    
    def get_document_type_name(self, document_type):
        """دریافت نام فارسی نوع مدرک"""
        type_names = {
            'check': 'چک',
            'receipt': 'رسید',
            'bank_transfer': 'فیش بانکی'
        }
        return type_names.get(document_type, document_type)
    
    def send_bulk_customer_notifications(self, user_id, notification_type, data=None):
        """ارسال اطلاع‌رسانی‌های مخصوص مشتریان عمده"""
        try:
            user = User.query.get(user_id)
            if not user or user.customer_type != 'bulk':
                return False
            
            # Add bulk-specific data
            if not data:
                data = {}
            
            profile = CustomerInvoiceProfile.query.filter_by(user_id=user_id).first()
            if profile:
                data['available_credit'] = float(profile.get_available_credit())
                data['discount_percentage'] = float(profile.bulk_discount_percentage)
            
            return self.send_notification(
                user_id=user_id,
                notification_type=notification_type,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending bulk customer notification: {str(e)}")
            return False
    
    def send_scheduled_notifications(self):
        """ارسال اطلاع‌رسانی‌های زمان‌بندی شده"""
        try:
            # Payment reminders
            self.send_payment_reminders()
            
            # Credit limit warnings
            self.send_credit_limit_warnings()
            
            # Document requirement reminders
            self.send_document_reminders()
            
            logger.info("Scheduled notifications sent")
            
        except Exception as e:
            logger.error(f"Error sending scheduled notifications: {str(e)}")
    
    def send_payment_reminders(self):
        """ارسال یادآوری‌های پرداخت"""
        try:
            # Get invoices due in next 3 days
            three_days_from_now = datetime.utcnow() + timedelta(days=3)
            
            due_invoices = Invoice.query.filter(
                Invoice.due_date <= three_days_from_now,
                Invoice.due_date >= datetime.utcnow(),
                Invoice.status == 'pending',
                Invoice.approval_workflow_status.in_(['auto_approved', 'manual_approved'])
            ).all()
            
            for invoice in due_invoices:
                days_until_due = (invoice.due_date - datetime.utcnow()).days
                
                data = {
                    'invoice_number': invoice.invoice_number,
                    'amount': float(invoice.total_amount),
                    'due_date': invoice.due_date.strftime('%Y/%m/%d'),
                    'days_remaining': days_until_due
                }
                
                self.send_notification(
                    user_id=invoice.user_id,
                    notification_type='payment_reminder',
                    data=data,
                    related_invoice_id=invoice.id,
                    action='payment_reminder'
                )
            
            logger.info(f"Payment reminders sent for {len(due_invoices)} invoices")
            
        except Exception as e:
            logger.error(f"Error sending payment reminders: {str(e)}")
    
    def send_credit_limit_warnings(self):
        """ارسال هشدارهای حد اعتبار"""
        try:
            # Get bulk customers with low credit
            profiles = CustomerInvoiceProfile.query.filter(
                CustomerInvoiceProfile.customer_type == 'bulk',
                CustomerInvoiceProfile.credit_limit > 0
            ).all()
            
            for profile in profiles:
                available_credit = profile.get_available_credit()
                credit_limit = float(profile.credit_limit)
                
                # Send warning if credit is below 20%
                if available_credit < (credit_limit * 0.2):
                    data = {
                        'remaining_credit': available_credit,
                        'credit_limit': credit_limit,
                        'percentage_used': ((credit_limit - available_credit) / credit_limit) * 100
                    }
                    
                    self.send_notification(
                        user_id=profile.user_id,
                        notification_type='credit_limit_warning',
                        data=data,
                        action='credit_warning'
                    )
            
            logger.info(f"Credit limit warnings sent for {len(profiles)} customers")
            
        except Exception as e:
            logger.error(f"Error sending credit limit warnings: {str(e)}")
    
    def send_document_reminders(self):
        """ارسال یادآوری‌های بارگذاری مدرک"""
        try:
            # Get invoices that require documents but don't have any
            invoices_without_docs = Invoice.query.filter(
                Invoice.document_required == True,
                Invoice.approval_workflow_status == 'pending'
            ).all()
            
            for invoice in invoices_without_docs:
                # Check if invoice has any documents
                if not invoice.documents:
                    # Check if reminder was sent in last 24 hours
                    last_reminder = UserNotification.query.filter(
                        UserNotification.user_id == invoice.user_id,
                        UserNotification.notification_type == 'document_required',
                        UserNotification.related_invoice_id == invoice.id,
                        UserNotification.created_at >= datetime.utcnow() - timedelta(hours=24)
                    ).first()
                    
                    if not last_reminder:
                        data = {
                            'invoice_number': invoice.invoice_number,
                            'amount': float(invoice.total_amount),
                            'days_pending': (datetime.utcnow() - invoice.created_at).days
                        }
                        
                        self.send_notification(
                            user_id=invoice.user_id,
                            notification_type='document_required',
                            data=data,
                            related_invoice_id=invoice.id,
                            action='document_reminder'
                        )
            
            logger.info(f"Document reminders sent for {len(invoices_without_docs)} invoices")
            
        except Exception as e:
            logger.error(f"Error sending document reminders: {str(e)}")
    
    def get_user_notifications(self, user_id, limit=20, unread_only=False):
        """دریافت اطلاع‌رسانی‌های کاربر"""
        try:
            query = UserNotification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(is_read=False)
            
            notifications = query.order_by(
                UserNotification.created_at.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': notif.id,
                    'type': notif.notification_type,
                    'title': notif.title,
                    'message': notif.message,
                    'is_read': notif.is_read,
                    'created_at': notif.created_at.isoformat(),
                    'related_invoice_id': notif.related_invoice_id,
                    'action': notif.notification_action
                }
                for notif in notifications
            ]
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    def mark_notification_read(self, notification_id, user_id):
        """علامت‌گذاری اطلاع‌رسانی به عنوان خوانده شده"""
        try:
            notification = UserNotification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    def mark_all_notifications_read(self, user_id):
        """علامت‌گذاری تمام اطلاع‌رسانی‌ها به عنوان خوانده شده"""
        try:
            UserNotification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).update({
                'is_read': True,
                'read_at': datetime.utcnow()
            })
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return False
    
    def get_notification_statistics(self, user_id):
        """دریافت آمار اطلاع‌رسانی‌ها"""
        try:
            total_notifications = UserNotification.query.filter_by(user_id=user_id).count()
            unread_notifications = UserNotification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).count()
            
            # Get notifications by type
            type_counts = {}
            notifications = UserNotification.query.filter_by(user_id=user_id).all()
            
            for notif in notifications:
                notif_type = notif.notification_type
                type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
            
            return {
                'total': total_notifications,
                'unread': unread_notifications,
                'read': total_notifications - unread_notifications,
                'by_type': type_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting notification statistics: {str(e)}")
            return {
                'total': 0,
                'unread': 0,
                'read': 0,
                'by_type': {}
            }

# Global instance
notification_service = NotificationService()
