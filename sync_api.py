"""
API همگام‌سازی تدبیر
Tadbir Sync API
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
import logging

from enhanced_tadbir_scheduler import get_enhanced_scheduler
from optimized_tadbir_sync_service import get_optimized_sync_service

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
sync_api_bp = Blueprint('sync_api', __name__, url_prefix='/api/sync')


@sync_api_bp.route('/status')
@login_required
def get_sync_status():
    """دریافت وضعیت همگام‌سازی"""
    try:
        enhanced_scheduler = get_enhanced_scheduler()
        optimized_sync = get_optimized_sync_service()
        
        status = enhanced_scheduler.get_enhanced_status()
        performance = optimized_sync.get_performance_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'scheduler': status,
                'performance': performance
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sync_api_bp.route('/run', methods=['POST'])
@login_required
def run_sync():
    """اجرای همگام‌سازی"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    try:
        data = request.get_json() or {}
        sync_type = data.get('type', 'all')
        use_optimized = data.get('optimized', True)
        
        enhanced_scheduler = get_enhanced_scheduler()
        
        if use_optimized:
            # استفاده از سرویس بهینه
            results = enhanced_scheduler.run_optimized_sync_now(sync_type)
        else:
            # استفاده از سرویس قدیمی
            if sync_type == 'prices':
                results = enhanced_scheduler.run_optimized_sync_now('prices')
            elif sync_type == 'inventory':
                results = enhanced_scheduler.run_optimized_sync_now('inventory')
            else:
                results = enhanced_scheduler.run_optimized_sync_now('all')
        
        return jsonify({
            'success': True,
            'message': 'Sync completed successfully',
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Error running sync: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sync_api_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def manage_settings():
    """مدیریت تنظیمات همگام‌سازی"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    try:
        enhanced_scheduler = get_enhanced_scheduler()
        
        if request.method == 'GET':
            # دریافت تنظیمات
            status = enhanced_scheduler.get_enhanced_status()
            return jsonify({
                'success': True,
                'data': {
                    'settings': status.get('settings', {}),
                    'performance': status.get('performance', {})
                }
            })
        
        elif request.method == 'POST':
            # بروزرسانی تنظیمات
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            enhanced_scheduler.update_enhanced_settings(data)
            
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully'
            })
        
    except Exception as e:
        logger.error(f"Error managing settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sync_api_bp.route('/clear-cache', methods=['POST'])
@login_required
def clear_cache():
    """پاک کردن کش"""
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Access denied'
        }), 403
    
    try:
        enhanced_scheduler = get_enhanced_scheduler()
        enhanced_scheduler.clear_optimized_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sync_api_bp.route('/performance')
@login_required
def get_performance():
    """دریافت آمار عملکرد"""
    try:
        optimized_sync = get_optimized_sync_service()
        performance = optimized_sync.get_performance_stats()
        
        return jsonify({
            'success': True,
            'data': performance
        })
        
    except Exception as e:
        logger.error(f"Error getting performance: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
