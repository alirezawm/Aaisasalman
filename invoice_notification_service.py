"""
سرویس اطلاع‌رسانی فاکتورها
ارسال اطلاع‌رسانی به مشتریان در مورد تغییر وضعیت فاکتورها
"""

from datetime import datetime
from models import db, UserNotification, Invoice, User
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class InvoiceNotificationService:
    """سرویس اطلاع‌رسانی فاکتورها"""
    
    @staticmethod
    def send_approval_notification(invoice_id, admin_notes=None):
        """
        ارسال اطلاع‌رسانی تایید فاکتور
        
        Args:
            invoice_id (int): شناسه فاکتور
            admin_notes (str): یادداشت ادمین
        """
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            # ایجاد پیام اطلاع‌رسانی
            title = "✅ فاکتور شما تایید شد"
            message = f"فاکتور شماره {invoice.invoice_number} شما با مبلغ {invoice.total_amount:,.0f} ریال تایید شد."
            
            if admin_notes:
                message += f"\n\nیادداشت ادمین: {admin_notes}"
            
            message += "\n\nبا تشکر از اعتماد شما"
            
            # ایجاد اطلاع‌رسانی
            notification = UserNotification(
                user_id=invoice.user_id,
                notification_type='invoice_approved',
                title=title,
                message=message,
                related_invoice_id=invoice_id,
                notification_action='approve'
            )
            
            db.session.add(notification)
            
            # آپدیت وضعیت اطلاع‌رسانی فاکتور
            invoice.notification_sent = True
            invoice.notification_sent_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Approval notification sent for invoice {invoice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending approval notification for invoice {invoice_id}: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def send_rejection_notification(invoice_id, rejection_reason, admin_notes=None):
        """
        ارسال اطلاع‌رسانی رد فاکتور
        
        Args:
            invoice_id (int): شناسه فاکتور
            rejection_reason (str): دلیل رد
            admin_notes (str): یادداشت ادمین
        """
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            # ایجاد پیام اطلاع‌رسانی
            title = "❌ فاکتور شما رد شد"
            message = f"متأسفانه فاکتور شماره {invoice.invoice_number} شما رد شد."
            message += f"\n\nدلیل رد: {rejection_reason}"
            
            if admin_notes:
                message += f"\n\nیادداشت ادمین: {admin_notes}"
            
            message += "\n\nلطفاً مجدداً اقدام به ثبت فاکتور کنید."
            
            # ایجاد اطلاع‌رسانی
            notification = UserNotification(
                user_id=invoice.user_id,
                notification_type='invoice_rejected',
                title=title,
                message=message,
                related_invoice_id=invoice_id,
                notification_action='reject'
            )
            
            db.session.add(notification)
            
            # آپدیت وضعیت اطلاع‌رسانی فاکتور
            invoice.notification_sent = True
            invoice.notification_sent_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Rejection notification sent for invoice {invoice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending rejection notification for invoice {invoice_id}: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def send_review_notification(invoice_id, admin_notes=None):
        """
        ارسال اطلاع‌رسانی بررسی فاکتور
        
        Args:
            invoice_id (int): شناسه فاکتور
            admin_notes (str): یادداشت ادمین
        """
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            # ایجاد پیام اطلاع‌رسانی
            title = "🔍 فاکتور شما در حال بررسی است"
            message = f"فاکتور شماره {invoice.invoice_number} شما در حال بررسی است."
            
            if admin_notes:
                message += f"\n\nیادداشت ادمین: {admin_notes}"
            
            message += "\n\nبه زودی نتیجه بررسی به شما اطلاع داده خواهد شد."
            
            # ایجاد اطلاع‌رسانی
            notification = UserNotification(
                user_id=invoice.user_id,
                notification_type='invoice_under_review',
                title=title,
                message=message,
                related_invoice_id=invoice_id,
                notification_action='review'
            )
            
            db.session.add(notification)
            
            # آپدیت وضعیت اطلاع‌رسانی فاکتور
            invoice.notification_sent = True
            invoice.notification_sent_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Review notification sent for invoice {invoice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending review notification for invoice {invoice_id}: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def send_document_required_notification(invoice_id):
        """
        ارسال اطلاع‌رسانی درخواست مستندات
        
        Args:
            invoice_id (int): شناسه فاکتور
        """
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice {invoice_id} not found")
                return False
            
            # ایجاد پیام اطلاع‌رسانی
            title = "📄 ارسال مستندات فاکتور"
            message = f"لطفاً مستندات مربوط به فاکتور شماره {invoice.invoice_number} را ارسال کنید."
            
            if invoice.payment_type == 'check':
                message += "\n\nلطفاً تصویر چک را بارگذاری کنید."
            else:
                message += "\n\nلطفاً رسید پرداخت را بارگذاری کنید."
            
            # ایجاد اطلاع‌رسانی
            notification = UserNotification(
                user_id=invoice.user_id,
                notification_type='document_required',
                title=title,
                message=message,
                related_invoice_id=invoice_id,
                notification_action='document_required'
            )
            
            db.session.add(notification)
            db.session.commit()
            
            logger.info(f"Document required notification sent for invoice {invoice_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending document required notification for invoice {invoice_id}: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_invoice_notifications(invoice_id):
        """
        دریافت تمام اطلاع‌رسانی‌های مربوط به یک فاکتور
        
        Args:
            invoice_id (int): شناسه فاکتور
            
        Returns:
            list: لیست اطلاع‌رسانی‌ها
        """
        try:
            notifications = UserNotification.query.filter_by(
                related_invoice_id=invoice_id
            ).order_by(UserNotification.created_at.desc()).all()
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting notifications for invoice {invoice_id}: {str(e)}")
            return []
    
    @staticmethod
    def get_user_invoice_notifications(user_id, limit=10):
        """
        دریافت اطلاع‌رسانی‌های فاکتورهای یک کاربر
        
        Args:
            user_id (int): شناسه کاربر
            limit (int): تعداد اطلاع‌رسانی‌ها
            
        Returns:
            list: لیست اطلاع‌رسانی‌ها
        """
        try:
            notifications = UserNotification.query.filter(
                UserNotification.user_id == user_id,
                UserNotification.notification_type.in_(['invoice_approved', 'invoice_rejected', 'invoice_under_review', 'document_required'])
            ).order_by(UserNotification.created_at.desc()).limit(limit).all()
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting invoice notifications for user {user_id}: {str(e)}")
            return []
    
    @staticmethod
    def mark_notification_as_read(notification_id):
        """
        علامت‌گذاری اطلاع‌رسانی به عنوان خوانده شده
        
        Args:
            notification_id (int): شناسه اطلاع‌رسانی
            
        Returns:
            bool: موفقیت عملیات
        """
        try:
            notification = UserNotification.query.get(notification_id)
            if notification:
                notification.mark_as_read()
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
            db.session.rollback()
            return False
