#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Approval Service for Customer Invoices
Handles approval and rejection of uploaded documents
"""

from datetime import datetime
from models import db, InvoiceDocument, InvoiceDocumentApproval, Invoice, UserNotification
import logging
import os

logger = logging.getLogger(__name__)

class DocumentApprovalService:
    """سرویس تایید مدارک فاکتورها"""
    
    def __init__(self):
        self.allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.document_types = {
            'check': 'چک',
            'receipt': 'رسید',
            'bank_transfer': 'فیش بانکی'
        }
    
    def approve_document(self, document_id, admin_id, admin_notes=''):
        """تایید مدرک توسط ادمین"""
        try:
            document = InvoiceDocument.query.get(document_id)
            if not document:
                logger.error(f"Document {document_id} not found")
                return False
            
            # Check if document is already processed
            approval_record = InvoiceDocumentApproval.query.filter_by(document_id=document_id).first()
            if approval_record and approval_record.approval_status != 'pending':
                logger.warning(f"Document {document_id} already processed")
                return False
            
            # Update or create approval record
            if approval_record:
                approval_record.approval_status = 'approved'
                approval_record.approved_by = admin_id
                approval_record.approval_date = datetime.utcnow()
                approval_record.admin_notes = admin_notes
            else:
                approval_record = InvoiceDocumentApproval(
                    document_id=document_id,
                    approval_status='approved',
                    approved_by=admin_id,
                    approval_date=datetime.utcnow(),
                    admin_notes=admin_notes
                )
                db.session.add(approval_record)
            
            # Update document status
            document.is_approved = True
            document.approval_date = datetime.utcnow()
            document.approved_by = admin_id
            document.admin_notes = admin_notes
            
            db.session.commit()
            
            # Check if all required documents are approved
            self.check_invoice_document_completion(document.invoice_id)
            
            # Send notification to customer
            self.send_document_notification(document, 'approved')
            
            logger.info(f"Document {document_id} approved by admin {admin_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error approving document: {str(e)}")
            return False
    
    def reject_document(self, document_id, admin_id, rejection_reason, admin_notes=''):
        """رد مدرک توسط ادمین"""
        try:
            document = InvoiceDocument.query.get(document_id)
            if not document:
                logger.error(f"Document {document_id} not found")
                return False
            
            # Check if document is already processed
            approval_record = InvoiceDocumentApproval.query.filter_by(document_id=document_id).first()
            if approval_record and approval_record.approval_status != 'pending':
                logger.warning(f"Document {document_id} already processed")
                return False
            
            # Update or create approval record
            if approval_record:
                approval_record.approval_status = 'rejected'
                approval_record.approved_by = admin_id
                approval_record.approval_date = datetime.utcnow()
                approval_record.rejection_reason = rejection_reason
                approval_record.admin_notes = admin_notes
            else:
                approval_record = InvoiceDocumentApproval(
                    document_id=document_id,
                    approval_status='rejected',
                    approved_by=admin_id,
                    approval_date=datetime.utcnow(),
                    rejection_reason=rejection_reason,
                    admin_notes=admin_notes
                )
                db.session.add(approval_record)
            
            # Update document status
            document.is_approved = False
            document.approval_date = datetime.utcnow()
            document.approved_by = admin_id
            document.rejection_reason = rejection_reason
            document.admin_notes = admin_notes
            
            db.session.commit()
            
            # Send notification to customer
            self.send_document_notification(document, 'rejected', rejection_reason)
            
            logger.info(f"Document {document_id} rejected by admin {admin_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error rejecting document: {str(e)}")
            return False
    
    def check_invoice_document_completion(self, invoice_id):
        """بررسی تکمیل مدارک فاکتور"""
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                return False
            
            # Get all documents for this invoice
            documents = InvoiceDocument.query.filter_by(invoice_id=invoice_id).all()
            
            if not documents:
                return False
            
            # Check if all documents are approved
            all_approved = all(
                doc.approval_record and doc.approval_record.approval_status == 'approved'
                for doc in documents
            )
            
            if all_approved:
                # All documents approved, trigger invoice approval process
                self.trigger_invoice_approval(invoice_id)
            else:
                # Some documents not approved, check if any are rejected
                any_rejected = any(
                    doc.approval_record and doc.approval_record.approval_status == 'rejected'
                    for doc in documents
                )
                
                if any_rejected:
                    # Some documents rejected, may need customer action
                    self.notify_document_issues(invoice_id)
            
            return all_approved
            
        except Exception as e:
            logger.error(f"Error checking document completion: {str(e)}")
            return False
    
    def trigger_invoice_approval(self, invoice_id):
        """شروع فرآیند تایید فاکتور پس از تایید مدارک"""
        try:
            from services.auto_approval_service import auto_approval_service
            from services.manual_approval_service import manual_approval_service
            
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                return False
            
            # Try auto approval first
            if auto_approval_service.process_invoice_approval(invoice_id):
                logger.info(f"Invoice {invoice_id} auto-approved after document approval")
                return True
            
            # If auto approval failed, create manual approval workflow
            if manual_approval_service.create_approval_workflow(invoice_id):
                logger.info(f"Manual approval workflow created for invoice {invoice_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error triggering invoice approval: {str(e)}")
            return False
    
    def notify_document_issues(self, invoice_id):
        """اطلاع‌رسانی مشکلات مدارک"""
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                return False
            
            # Get rejected documents
            rejected_docs = []
            for doc in invoice.documents:
                if (doc.approval_record and 
                    doc.approval_record.approval_status == 'rejected'):
                    rejected_docs.append({
                        'type': self.document_types.get(doc.document_type, doc.document_type),
                        'reason': doc.approval_record.rejection_reason
                    })
            
            if rejected_docs:
                # Send notification to customer
                notification = UserNotification(
                    user_id=invoice.user_id,
                    notification_type='document_rejected',
                    title='مشکل در مدارک فاکتور',
                    message=f'برخی از مدارک فاکتور شماره {invoice.invoice_number} رد شده‌اند. لطفاً مدارک جدید بارگذاری کنید.',
                    related_invoice_id=invoice_id,
                    notification_action='document_issue'
                )
                
                db.session.add(notification)
                db.session.commit()
                
                logger.info(f"Document issues notification sent for invoice {invoice_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error notifying document issues: {str(e)}")
            return False
    
    def send_document_notification(self, document, action, reason=''):
        """ارسال اطلاع‌رسانی تایید/رد مدرک"""
        try:
            invoice = document.invoice
            document_type_text = self.document_types.get(document.document_type, document.document_type)
            
            if action == 'approved':
                title = 'مدرک تایید شد'
                message = f'مدرک {document_type_text} فاکتور شماره {invoice.invoice_number} تایید شد'
            elif action == 'rejected':
                title = 'مدرک رد شد'
                message = f'مدرک {document_type_text} فاکتور شماره {invoice.invoice_number} رد شد. دلیل: {reason}'
            else:
                return
            
            notification = UserNotification(
                user_id=invoice.user_id,
                notification_type=f'document_{action}',
                title=title,
                message=message,
                related_invoice_id=invoice.id,
                notification_action=f'document_{action}'
            )
            
            db.session.add(notification)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending document notification: {str(e)}")
    
    def get_pending_documents(self, admin_id=None):
        """دریافت مدارک در انتظار تایید"""
        try:
            query = InvoiceDocumentApproval.query.filter(
                InvoiceDocumentApproval.approval_status == 'pending'
            )
            
            if admin_id:
                # Get documents assigned to specific admin's invoices
                from models import Invoice
                admin_invoices = Invoice.query.filter_by(approved_by=admin_id).all()
                invoice_ids = [inv.id for inv in admin_invoices]
                
                if invoice_ids:
                    query = query.join(InvoiceDocument).filter(
                        InvoiceDocument.invoice_id.in_(invoice_ids)
                    )
                else:
                    return []
            
            return query.order_by(InvoiceDocumentApproval.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Error getting pending documents: {str(e)}")
            return []
    
    def validate_document(self, file):
        """اعتبارسنجی فایل مدرک"""
        try:
            # Check file extension
            if '.' not in file.filename:
                return False, 'فایل باید دارای پسوند باشد'
            
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            if file_ext not in self.allowed_extensions:
                return False, f'فرمت فایل مجاز نیست. فرمت‌های مجاز: {", ".join(self.allowed_extensions)}'
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > self.max_file_size:
                return False, f'حجم فایل نباید از {self.max_file_size // (1024*1024)} مگابایت بیشتر باشد'
            
            if file_size == 0:
                return False, 'فایل خالی است'
            
            return True, 'فایل معتبر است'
            
        except Exception as e:
            logger.error(f"Error validating document: {str(e)}")
            return False, 'خطا در اعتبارسنجی فایل'
    
    def get_document_statistics(self):
        """دریافت آمار مدارک"""
        try:
            total_documents = InvoiceDocument.query.count()
            pending_documents = InvoiceDocumentApproval.query.filter(
                InvoiceDocumentApproval.approval_status == 'pending'
            ).count()
            approved_documents = InvoiceDocumentApproval.query.filter(
                InvoiceDocumentApproval.approval_status == 'approved'
            ).count()
            rejected_documents = InvoiceDocumentApproval.query.filter(
                InvoiceDocumentApproval.approval_status == 'rejected'
            ).count()
            
            return {
                'total': total_documents,
                'pending': pending_documents,
                'approved': approved_documents,
                'rejected': rejected_documents,
                'approval_rate': (approved_documents / total_documents * 100) if total_documents > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting document statistics: {str(e)}")
            return {
                'total': 0,
                'pending': 0,
                'approved': 0,
                'rejected': 0,
                'approval_rate': 0
            }

# Global instance
document_approval_service = DocumentApprovalService()
