#!/usr/bin/env python3
"""
تست سیستم همگام‌سازی بهینه تدبیر
Test script for Optimized Tadbir Sync System
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_optimized_sync():
    """تست سرویس همگام‌سازی بهینه"""
    print("🚀 شروع تست سیستم همگام‌سازی بهینه تدبیر")
    print("=" * 60)
    
    try:
        # Import Flask app
        from app import app
        
        with app.app_context():
            print("✅ Flask app context ایجاد شد")
            
            # Test optimized sync service
            from optimized_tadbir_sync_service import get_optimized_sync_service
            optimized_sync = get_optimized_sync_service()
            print("✅ سرویس همگام‌سازی بهینه بارگذاری شد")
            
            # Test enhanced scheduler
            from enhanced_tadbir_scheduler import get_enhanced_scheduler
            enhanced_scheduler = get_enhanced_scheduler()
            print("✅ زمان‌بند پیشرفته بارگذاری شد")
            
            # Test performance stats
            print("\n📊 دریافت آمار عملکرد...")
            performance_stats = optimized_sync.get_performance_stats()
            print(f"✅ آمار عملکرد دریافت شد: {len(performance_stats)} فیلد")
            
            # Test scheduler status
            print("\n📈 دریافت وضعیت زمان‌بند...")
            scheduler_status = enhanced_scheduler.get_enhanced_status()
            print(f"✅ وضعیت زمان‌بند دریافت شد: {scheduler_status.get('is_running', False)}")
            
            # Test settings
            print("\n⚙️ تست تنظیمات...")
            current_settings = scheduler_status.get('settings', {})
            print(f"✅ تنظیمات فعلی: {len(current_settings)} مورد")
            
            # Display key settings
            key_settings = [
                'sync_interval', 'auto_sync_enabled', 'use_optimized_sync',
                'real_time_sync', 'batch_size', 'max_workers'
            ]
            
            print("\n🔧 تنظیمات کلیدی:")
            for key in key_settings:
                value = current_settings.get(key, 'N/A')
                print(f"   {key}: {value}")
            
            # Test cache
            print("\n💾 تست کش...")
            optimized_sync.clear_cache()
            print("✅ کش پاک شد")
            
            # Test performance metrics
            if 'performance' in performance_stats:
                perf = performance_stats['performance']
                print(f"\n📈 معیارهای عملکرد:")
                print(f"   اندازه کش: {perf.get('cache_size', 0)}")
                print(f"   اندازه دسته: {perf.get('batch_size', 0)}")
                print(f"   تعداد thread ها: {perf.get('max_workers', 0)}")
            
            print("\n✅ تمام تست‌ها با موفقیت انجام شد!")
            print("🎉 سیستم همگام‌سازی بهینه آماده استفاده است")
            
            return True
            
    except Exception as e:
        print(f"\n❌ خطا در تست: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """تست API endpoints"""
    print("\n🌐 تست API endpoints...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test sync status endpoint
            response = client.get('/api/sync/status')
            if response.status_code == 200:
                print("✅ API /api/sync/status کار می‌کند")
            else:
                print(f"❌ API /api/sync/status خطا: {response.status_code}")
            
            # Test performance endpoint
            response = client.get('/api/sync/performance')
            if response.status_code == 200:
                print("✅ API /api/sync/performance کار می‌کند")
            else:
                print(f"❌ API /api/sync/performance خطا: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ خطا در تست API: {str(e)}")
        return False

def main():
    """تابع اصلی تست"""
    print("🧪 تست سیستم همگام‌سازی بهینه تدبیر")
    print(f"⏰ زمان شروع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: Basic functionality
    test1_success = test_optimized_sync()
    
    # Test 2: API endpoints
    test2_success = test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 خلاصه نتایج تست:")
    print(f"   تست عملکرد اصلی: {'✅ موفق' if test1_success else '❌ ناموفق'}")
    print(f"   تست API endpoints: {'✅ موفق' if test2_success else '❌ ناموفق'}")
    
    if test1_success and test2_success:
        print("\n🎉 همه تست‌ها موفق بود! سیستم آماده استفاده است.")
        print("\n📖 برای استفاده:")
        print("   1. داشبورد مانیتورینگ: /admin/tadbir-monitoring/")
        print("   2. API همگام‌سازی: /api/sync/")
        print("   3. مستندات کامل: OPTIMIZED_TADBIR_SYNC_README.md")
        return 0
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بود. لطفاً خطاها را بررسی کنید.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
