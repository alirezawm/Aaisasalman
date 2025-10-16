"""
سرویس لایه میانی برای تشخیص
Detection Service Layer
"""

from brand_vehicle_detector import get_detector

class DetectionService:
    """سرویس مدیریت تشخیص"""
    
    def __init__(self):
        self.detector = get_detector()
    
    def detect_single(self, text, mode='auto', confidence_threshold=0.7):
        """تشخیص تکی"""
        result = self.detector.detect_brand_and_vehicle_types(text)
        
        if result['status'] == 'success':
            data = result['data']
            
            # Apply confidence threshold
            if data['detected_brand'] and confidence_threshold:
                if data['detected_brand'].get('confidence_score', 1.0) < confidence_threshold:
                    data['detected_brand'] = None
            
            if data['detected_vehicle_types'] and confidence_threshold:
                data['detected_vehicle_types'] = [
                    vt for vt in data['detected_vehicle_types']
                    if vt.get('confidence_score', 1.0) >= confidence_threshold
                ]
        
        return result
    
    def detect_batch(self, texts, update_database=False):
        """تشخیص دسته‌ای"""
        results = []
        for text in texts:
            result = self.detect_single(text)
            results.append(result)
        
        return {
            'status': 'success',
            'data': {
                'total': len(texts),
                'successful': sum(1 for r in results if r['status'] == 'success'),
                'results': results
            }
        }

def get_detection_service():
    """دریافت نمونه سرویس"""
    return DetectionService()
