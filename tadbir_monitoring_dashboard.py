"""
داشبورد مانیتورینگ همگام‌سازی تدبیر
Tadbir Sync Monitoring Dashboard
"""

from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from models import db, TadbirSyncLog, Product, TadbirProductCache, TadbirPriceCache, TadbirInventoryCache
from enhanced_tadbir_scheduler import get_enhanced_scheduler
from optimized_tadbir_sync_service import get_optimized_sync_service

# Create blueprint
monitoring_bp = Blueprint('tadbir_monitoring', __name__, url_prefix='/admin/tadbir-monitoring')


@monitoring_bp.route('/')
@login_required
def dashboard():
    """صفحه اصلی داشبورد مانیتورینگ"""
    if not current_user.is_admin:
        return "Access denied", 403
    
    return render_template('admin/tadbir_monitoring_dashboard.html')


@monitoring_bp.route('/api/status')
@login_required
def api_status():
    """API وضعیت همگام‌سازی"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        enhanced_scheduler = get_enhanced_scheduler()
        optimized_sync = get_optimized_sync_service()
        
        # دریافت وضعیت کلی
        scheduler_status = enhanced_scheduler.get_enhanced_status()
        performance_stats = optimized_sync.get_performance_stats()
        
        # آمار محصولات
        total_products = Product.query.count()
        active_products = Product.query.filter_by(is_active=True).count()
        isaco_products = Product.query.filter_by(is_isaco_wh15=True).count()
        
        # آمار کش تدبیر
        tadbir_products_count = TadbirProductCache.query.count()
        tadbir_prices_count = TadbirPriceCache.query.count()
        tadbir_inventory_count = TadbirInventoryCache.query.count()
        
        # آخرین همگام‌سازی‌ها
        last_syncs = TadbirSyncLog.query.order_by(
            TadbirSyncLog.started_at.desc()
        ).limit(10).all()
        
        sync_history = []
        for sync in last_syncs:
            sync_history.append({
                'id': sync.id,
                'sync_type': sync.sync_type,
                'status': sync.status,
                'started_at': sync.started_at.isoformat() if sync.started_at else None,
                'completed_at': sync.completed_at.isoformat() if sync.completed_at else None,
                'duration_seconds': sync.duration_seconds,
                'records_processed': sync.records_processed,
                'records_successful': sync.records_successful,
                'records_failed': sync.records_failed,
                'error_message': sync.error_message
            })
        
        return jsonify({
            'scheduler': scheduler_status,
            'performance': performance_stats,
            'products': {
                'total': total_products,
                'active': active_products,
                'isaco': isaco_products
            },
            'tadbir_cache': {
                'products': tadbir_products_count,
                'prices': tadbir_prices_count,
                'inventory': tadbir_inventory_count
            },
            'sync_history': sync_history,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/performance')
@login_required
def api_performance():
    """API آمار عملکرد"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # آمار عملکرد 24 ساعت گذشته
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_syncs = TadbirSyncLog.query.filter(
            TadbirSyncLog.started_at >= yesterday
        ).order_by(TadbirSyncLog.started_at.desc()).all()
        
        # محاسبه آمار
        total_syncs = len(recent_syncs)
        successful_syncs = len([s for s in recent_syncs if s.status == 'completed'])
        failed_syncs = len([s for s in recent_syncs if s.status == 'failed'])
        
        # آمار زمان‌بندی
        avg_duration = 0
        total_records_processed = 0
        total_records_successful = 0
        
        if recent_syncs:
            durations = [s.duration_seconds for s in recent_syncs if s.duration_seconds]
            if durations:
                avg_duration = sum(durations) / len(durations)
            
            total_records_processed = sum(s.records_processed or 0 for s in recent_syncs)
            total_records_successful = sum(s.records_successful or 0 for s in recent_syncs)
        
        # آمار بر اساس نوع همگام‌سازی
        sync_type_stats = {}
        for sync in recent_syncs:
            sync_type = sync.sync_type
            if sync_type not in sync_type_stats:
                sync_type_stats[sync_type] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'avg_duration': 0,
                    'total_records': 0
                }
            
            sync_type_stats[sync_type]['total'] += 1
            if sync.status == 'completed':
                sync_type_stats[sync_type]['successful'] += 1
            elif sync.status == 'failed':
                sync_type_stats[sync_type]['failed'] += 1
            
            if sync.duration_seconds:
                sync_type_stats[sync_type]['avg_duration'] += sync.duration_seconds
                sync_type_stats[sync_type]['total_records'] += sync.records_processed or 0
        
        # محاسبه میانگین برای هر نوع
        for sync_type in sync_type_stats:
            if sync_type_stats[sync_type]['total'] > 0:
                sync_type_stats[sync_type]['avg_duration'] /= sync_type_stats[sync_type]['total']
                sync_type_stats[sync_type]['success_rate'] = (
                    sync_type_stats[sync_type]['successful'] / 
                    sync_type_stats[sync_type]['total'] * 100
                )
        
        return jsonify({
            'summary': {
                'total_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'failed_syncs': failed_syncs,
                'success_rate': (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0,
                'avg_duration_seconds': avg_duration,
                'total_records_processed': total_records_processed,
                'total_records_successful': total_records_successful
            },
            'by_type': sync_type_stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/sync-now', methods=['POST'])
@login_required
def api_sync_now():
    """API اجرای فوری همگام‌سازی"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json() or {}
        sync_type = data.get('sync_type', 'all')
        
        enhanced_scheduler = get_enhanced_scheduler()
        
        if sync_type == 'optimized':
            # اجرای همگام‌سازی بهینه
            results = enhanced_scheduler.run_optimized_sync_now('all')
        else:
            # اجرای همگام‌سازی عادی
            if sync_type == 'prices':
                results = enhanced_scheduler.run_optimized_sync_now('prices')
            elif sync_type == 'inventory':
                results = enhanced_scheduler.run_optimized_sync_now('inventory')
            else:
                results = enhanced_scheduler.run_optimized_sync_now('all')
        
        return jsonify({
            'success': True,
            'message': 'Sync started successfully',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def api_settings():
    """API مدیریت تنظیمات"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        enhanced_scheduler = get_enhanced_scheduler()
        
        if request.method == 'GET':
            # دریافت تنظیمات
            status = enhanced_scheduler.get_enhanced_status()
            return jsonify({
                'settings': status.get('settings', {}),
                'performance': status.get('performance', {})
            })
        
        elif request.method == 'POST':
            # بروزرسانی تنظیمات
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            enhanced_scheduler.update_enhanced_settings(data)
            
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/clear-cache', methods=['POST'])
@login_required
def api_clear_cache():
    """API پاک کردن کش"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        enhanced_scheduler = get_enhanced_scheduler()
        enhanced_scheduler.clear_optimized_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/sync-history')
@login_required
def api_sync_history():
    """API تاریخچه همگام‌سازی"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        sync_type = request.args.get('sync_type', '')
        status = request.args.get('status', '')
        
        # ساخت کوئری
        query = TadbirSyncLog.query
        
        if sync_type:
            query = query.filter(TadbirSyncLog.sync_type == sync_type)
        
        if status:
            query = query.filter(TadbirSyncLog.status == status)
        
        # مرتب‌سازی و صفحه‌بندی
        pagination = query.order_by(
            TadbirSyncLog.started_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        sync_logs = []
        for sync in pagination.items:
            sync_logs.append({
                'id': sync.id,
                'sync_type': sync.sync_type,
                'status': sync.status,
                'started_at': sync.started_at.isoformat() if sync.started_at else None,
                'completed_at': sync.completed_at.isoformat() if sync.completed_at else None,
                'duration_seconds': sync.duration_seconds,
                'records_processed': sync.records_processed,
                'records_successful': sync.records_successful,
                'records_failed': sync.records_failed,
                'error_message': sync.error_message
            })
        
        return jsonify({
            'sync_logs': sync_logs,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@monitoring_bp.route('/api/product-stats')
@login_required
def api_product_stats():
    """API آمار محصولات"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # آمار کلی محصولات
        total_products = Product.query.count()
        active_products = Product.query.filter_by(is_active=True).count()
        isaco_products = Product.query.filter_by(is_isaco_wh15=True).count()
        
        # آمار بر اساس برند
        brand_stats = db.session.query(
            Product.brand_id,
            db.func.count(Product.id).label('count')
        ).group_by(Product.brand_id).all()
        
        # آمار بر اساس دسته‌بندی
        category_stats = db.session.query(
            Product.category_id,
            db.func.count(Product.id).label('count')
        ).group_by(Product.category_id).all()
        
        # آمار قیمت‌ها
        price_stats = db.session.query(
            db.func.avg(Product.retail_price_cash).label('avg_retail_cash'),
            db.func.avg(Product.bulk_price_cash).label('avg_bulk_cash'),
            db.func.avg(Product.retail_price_check).label('avg_retail_check'),
            db.func.avg(Product.bulk_price_check).label('avg_bulk_check')
        ).first()
        
        # آمار موجودی
        inventory_stats = db.session.query(
            db.func.sum(Product.stock_quantity).label('total_stock'),
            db.func.avg(Product.stock_quantity).label('avg_stock'),
            db.func.count(Product.id).filter(Product.stock_quantity > 0).label('in_stock_count'),
            db.func.count(Product.id).filter(Product.stock_quantity == 0).label('out_of_stock_count')
        ).first()
        
        return jsonify({
            'overview': {
                'total_products': total_products,
                'active_products': active_products,
                'isaco_products': isaco_products,
                'inactive_products': total_products - active_products
            },
            'brands': [
                {'brand_id': brand_id, 'count': count} 
                for brand_id, count in brand_stats
            ],
            'categories': [
                {'category_id': category_id, 'count': count} 
                for category_id, count in category_stats
            ],
            'prices': {
                'avg_retail_cash': float(price_stats.avg_retail_cash) if price_stats.avg_retail_cash else 0,
                'avg_bulk_cash': float(price_stats.avg_bulk_cash) if price_stats.avg_bulk_cash else 0,
                'avg_retail_check': float(price_stats.avg_retail_check) if price_stats.avg_retail_check else 0,
                'avg_bulk_check': float(price_stats.avg_bulk_check) if price_stats.avg_bulk_check else 0
            },
            'inventory': {
                'total_stock': int(inventory_stats.total_stock) if inventory_stats.total_stock else 0,
                'avg_stock': float(inventory_stats.avg_stock) if inventory_stats.avg_stock else 0,
                'in_stock_count': inventory_stats.in_stock_count or 0,
                'out_of_stock_count': inventory_stats.out_of_stock_count or 0
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
