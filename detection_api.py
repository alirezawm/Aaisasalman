"""
API Endpoints for Detection System
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from detection_service import get_detection_service

detection_bp = Blueprint('detection_api', __name__, url_prefix='/api/detection')

@detection_bp.route('/detect', methods=['POST'])
@login_required
def detect():
    """تشخیص برند و نوع"""
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'status': 'error', 'message': 'متن الزامی است'}), 400
    
    service = get_detection_service()
    result = service.detect_single(text)
    
    return jsonify(result)

@detection_bp.route('/batch', methods=['POST'])
@login_required
def batch_detect():
    """تشخیص دسته‌ای"""
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'دسترسی غیرمجاز'}), 403
    
    data = request.get_json()
    texts = data.get('texts', [])
    
    service = get_detection_service()
    result = service.detect_batch(texts)
    
    return jsonify(result)

@detection_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """دریافت آمار"""
    from brand_vehicle_detector import get_detector
    detector = get_detector()
    stats = detector.get_detection_stats()
    
    return jsonify({'status': 'success', 'data': stats})
