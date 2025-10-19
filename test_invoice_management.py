"""
تست سیستم مدیریت فاکتورهای مشتریان
"""

import unittest
from datetime import datetime
from app import app, db
from models import User, Invoice, InvoiceItem, Product, UserNotification
from invoice_notification_service import InvoiceNotificationService

class TestInvoiceManagement(unittest.TestCase):
    """تست‌های سیستم مدیریت فاکتورها"""
    
    def setUp(self):
        """تنظیمات اولیه برای هر تست"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.create_test_data()
    
    def tearDown(self):
        """پاکسازی پس از هر تست"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def create_test_data(self):
        """ایجاد داده‌های تست"""
        # ایجاد کاربر تست
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash='test_hash',
            full_name='کاربر تست',
            phone='09123456789',
            is_admin=False
        )
        db.session.add(self.test_user)
        
        # ایجاد ادمین تست
        self.test_admin = User(
            username='admin',
            email='admin@example.com',
            password_hash='admin_hash',
            full_name='ادمین تست',
            phone='09123456788',
            is_admin=True
        )
        db.session.add(self.test_admin)
        
        # ایجاد محصول تست
        self.test_product = Product(
            sku='TEST001',
            name='محصول تست',
            name_fa='محصول تست',
            bulk_price_cash=1000,
            retail_price_cash=1200,
            bulk_price_check=1100,
            retail_price_check=1300
        )
        db.session.add(self.test_product)
        
        db.session.commit()
        
        # ایجاد فاکتور تست
        self.test_invoice = Invoice(
            invoice_number='INV001',
            user_id=self.test_user.id,
            total_amount=1000,
            payment_type='cash',
            approval_status='pending'
        )
        db.session.add(self.test_invoice)
        
        # ایجاد آیتم فاکتور
        self.test_invoice_item = InvoiceItem(
            invoice_id=self.test_invoice.id,
            product_id=self.test_product.id,
            quantity=1,
            unit_price=1000,
            total_price=1000,
            price_type='cash'
        )
        db.session.add(self.test_invoice_item)
        
        db.session.commit()
    
    def test_invoice_creation(self):
        """تست ایجاد فاکتور"""
        with self.app.app_context():
            invoice = Invoice.query.filter_by(invoice_number='INV001').first()
            self.assertIsNotNone(invoice)
            self.assertEqual(invoice.approval_status, 'pending')
            self.assertEqual(invoice.total_amount, 1000)
    
    def test_approval_notification(self):
        """تست ارسال اطلاع‌رسانی تایید"""
        with self.app.app_context():
            # ارسال اطلاع‌رسانی تایید
            result = InvoiceNotificationService.send_approval_notification(
                self.test_invoice.id, 
                'تایید شد'
            )
            
            self.assertTrue(result)
            
            # بررسی ایجاد اطلاع‌رسانی
            notification = UserNotification.query.filter_by(
                user_id=self.test_user.id,
                notification_type='invoice_approved'
            ).first()
            
            self.assertIsNotNone(notification)
            self.assertEqual(notification.related_invoice_id, self.test_invoice.id)
            self.assertEqual(notification.notification_action, 'approve')
            
            # بررسی آپدیت فاکتور
            invoice = Invoice.query.get(self.test_invoice.id)
            self.assertTrue(invoice.notification_sent)
            self.assertIsNotNone(invoice.notification_sent_at)
    
    def test_rejection_notification(self):
        """تست ارسال اطلاع‌رسانی رد"""
        with self.app.app_context():
            # ارسال اطلاع‌رسانی رد
            result = InvoiceNotificationService.send_rejection_notification(
                self.test_invoice.id,
                'مشکل در مستندات',
                'لطفاً مجدداً اقدام کنید'
            )
            
            self.assertTrue(result)
            
            # بررسی ایجاد اطلاع‌رسانی
            notification = UserNotification.query.filter_by(
                user_id=self.test_user.id,
                notification_type='invoice_rejected'
            ).first()
            
            self.assertIsNotNone(notification)
            self.assertEqual(notification.related_invoice_id, self.test_invoice.id)
            self.assertEqual(notification.notification_action, 'reject')
            self.assertIn('مشکل در مستندات', notification.message)
    
    def test_review_notification(self):
        """تست ارسال اطلاع‌رسانی بررسی"""
        with self.app.app_context():
            # ارسال اطلاع‌رسانی بررسی
            result = InvoiceNotificationService.send_review_notification(
                self.test_invoice.id,
                'در حال بررسی'
            )
            
            self.assertTrue(result)
            
            # بررسی ایجاد اطلاع‌رسانی
            notification = UserNotification.query.filter_by(
                user_id=self.test_user.id,
                notification_type='invoice_under_review'
            ).first()
            
            self.assertIsNotNone(notification)
            self.assertEqual(notification.related_invoice_id, self.test_invoice.id)
            self.assertEqual(notification.notification_action, 'review')
    
    def test_get_invoice_notifications(self):
        """تست دریافت اطلاع‌رسانی‌های فاکتور"""
        with self.app.app_context():
            # ایجاد چندین اطلاع‌رسانی
            InvoiceNotificationService.send_approval_notification(
                self.test_invoice.id, 'تایید 1'
            )
            InvoiceNotificationService.send_rejection_notification(
                self.test_invoice.id, 'رد', 'یادداشت'
            )
            
            # دریافت اطلاع‌رسانی‌ها
            notifications = InvoiceNotificationService.get_invoice_notifications(
                self.test_invoice.id
            )
            
            self.assertEqual(len(notifications), 2)
            self.assertEqual(notifications[0].notification_type, 'invoice_rejected')
            self.assertEqual(notifications[1].notification_type, 'invoice_approved')
    
    def test_get_user_invoice_notifications(self):
        """تست دریافت اطلاع‌رسانی‌های فاکتور کاربر"""
        with self.app.app_context():
            # ایجاد اطلاع‌رسانی‌ها
            InvoiceNotificationService.send_approval_notification(
                self.test_invoice.id, 'تایید'
            )
            
            # دریافت اطلاع‌رسانی‌های کاربر
            notifications = InvoiceNotificationService.get_user_invoice_notifications(
                self.test_user.id
            )
            
            self.assertEqual(len(notifications), 1)
            self.assertEqual(notifications[0].notification_type, 'invoice_approved')
    
    def test_mark_notification_as_read(self):
        """تست علامت‌گذاری اطلاع‌رسانی به عنوان خوانده شده"""
        with self.app.app_context():
            # ایجاد اطلاع‌رسانی
            InvoiceNotificationService.send_approval_notification(
                self.test_invoice.id, 'تایید'
            )
            
            notification = UserNotification.query.filter_by(
                user_id=self.test_user.id,
                notification_type='invoice_approved'
            ).first()
            
            # علامت‌گذاری به عنوان خوانده شده
            result = InvoiceNotificationService.mark_notification_as_read(
                notification.id
            )
            
            self.assertTrue(result)
            
            # بررسی آپدیت
            updated_notification = UserNotification.query.get(notification.id)
            self.assertTrue(updated_notification.is_read)
            self.assertIsNotNone(updated_notification.read_at)
    
    def test_invoice_approval_route(self):
        """تست روت تایید فاکتور"""
        with self.app.app_context():
            # لاگین ادمین
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.test_admin.id
            
            # ارسال درخواست تایید
            response = self.client.post(
                f'/admin/invoices/{self.test_invoice.id}/approve',
                data={
                    'admin_notes': 'تایید تست',
                    'send_notification': 'on'
                }
            )
            
            # بررسی پاسخ
            self.assertEqual(response.status_code, 302)  # Redirect
            
            # بررسی آپدیت فاکتور
            invoice = Invoice.query.get(self.test_invoice.id)
            self.assertEqual(invoice.approval_status, 'approved')
            self.assertEqual(invoice.admin_notes, 'تایید تست')
            self.assertEqual(invoice.approved_by, self.test_admin.id)
    
    def test_invoice_rejection_route(self):
        """تست روت رد فاکتور"""
        with self.app.app_context():
            # لاگین ادمین
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.test_admin.id
            
            # ارسال درخواست رد
            response = self.client.post(
                f'/admin/invoices/{self.test_invoice.id}/reject',
                data={
                    'rejection_reason': 'مشکل در مستندات',
                    'admin_notes': 'رد تست',
                    'send_notification': 'on'
                }
            )
            
            # بررسی پاسخ
            self.assertEqual(response.status_code, 302)  # Redirect
            
            # بررسی آپدیت فاکتور
            invoice = Invoice.query.get(self.test_invoice.id)
            self.assertEqual(invoice.approval_status, 'rejected')
            self.assertEqual(invoice.rejection_reason, 'مشکل در مستندات')
            self.assertEqual(invoice.admin_notes, 'رد تست')
    
    def test_invoice_review_route(self):
        """تست روت بررسی فاکتور"""
        with self.app.app_context():
            # لاگین ادمین
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.test_admin.id
            
            # ارسال درخواست بررسی
            response = self.client.post(
                f'/admin/invoices/{self.test_invoice.id}/set-review',
                data={
                    'admin_notes': 'بررسی تست'
                }
            )
            
            # بررسی پاسخ
            self.assertEqual(response.status_code, 302)  # Redirect
            
            # بررسی آپدیت فاکتور
            invoice = Invoice.query.get(self.test_invoice.id)
            self.assertEqual(invoice.approval_status, 'under_review')
            self.assertEqual(invoice.admin_review_notes, 'بررسی تست')
    
    def test_invoice_statistics_api(self):
        """تست API آمار فاکتورها"""
        with self.app.app_context():
            # لاگین ادمین
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.test_admin.id
            
            # درخواست آمار
            response = self.client.get('/api/admin/invoices/statistics')
            
            # بررسی پاسخ
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            
            self.assertIn('total_invoices', data)
            self.assertIn('pending_approval', data)
            self.assertIn('approved', data)
            self.assertIn('rejected', data)
            self.assertIn('under_review', data)
            self.assertIn('total_amount', data)
            
            self.assertEqual(data['total_invoices'], 1)
            self.assertEqual(data['pending_approval'], 1)
    
    def test_invoice_search_api(self):
        """تست API جستجوی فاکتورها"""
        with self.app.app_context():
            # لاگین ادمین
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.test_admin.id
            
            # جستجو
            response = self.client.get('/api/admin/invoices/search?approval_status=pending')
            
            # بررسی پاسخ
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            
            self.assertIn('invoices', data)
            self.assertIn('total', data)
            self.assertEqual(data['total'], 1)
            self.assertEqual(len(data['invoices']), 1)
            self.assertEqual(data['invoices'][0]['approval_status'], 'pending')

if __name__ == '__main__':
    unittest.main()
