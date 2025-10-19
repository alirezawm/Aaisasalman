"""
اسکریپت تست همگام‌سازی فروشگاه
Test Shop Sync Script
"""

import sys
from datetime import datetime
from app import app
from shop_sync_service import get_shop_sync_service
from tadbir_scheduler_service import get_scheduler


def print_separator(title: str = ""):
    """Print a separator line"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


def test_shop_prices_sync():
    """تست همگام‌سازی قیمت‌های فروشگاه"""
    print_separator("تست همگام‌سازی قیمت‌های فروشگاه")
    
    shop_sync = get_shop_sync_service()
    
    print("شروع همگام‌سازی قیمت‌ها...")
    sync_log = shop_sync.sync_shop_prices()
    
    print(f"\n✓ وضعیت: {sync_log.status}")
    print(f"✓ تعداد پردازش شده: {sync_log.records_processed}")
    print(f"✓ تعداد موفق: {sync_log.records_successful}")
    print(f"✓ تعداد ناموفق: {sync_log.records_failed}")
    
    if sync_log.duration_seconds:
        print(f"✓ مدت زمان: {sync_log.duration_seconds} ثانیه")
    
    if sync_log.error_message:
        print(f"✗ خطا: {sync_log.error_message}")
    
    return sync_log.status == 'completed'


def test_shop_inventory_sync():
    """تست همگام‌سازی موجودی فروشگاه"""
    print_separator("تست همگام‌سازی موجودی فروشگاه")
    
    shop_sync = get_shop_sync_service()
    
    print("شروع همگام‌سازی موجودی...")
    sync_log = shop_sync.sync_shop_inventory()
    
    print(f"\n✓ وضعیت: {sync_log.status}")
    print(f"✓ تعداد پردازش شده: {sync_log.records_processed}")
    print(f"✓ تعداد موفق: {sync_log.records_successful}")
    print(f"✓ تعداد ناموفق: {sync_log.records_failed}")
    
    if sync_log.duration_seconds:
        print(f"✓ مدت زمان: {sync_log.duration_seconds} ثانیه")
    
    if sync_log.error_message:
        print(f"✗ خطا: {sync_log.error_message}")
    
    return sync_log.status == 'completed'


def test_shop_products_sync():
    """تست همگام‌سازی اطلاعات محصولات فروشگاه"""
    print_separator("تست همگام‌سازی اطلاعات محصولات فروشگاه")
    
    shop_sync = get_shop_sync_service()
    
    print("شروع همگام‌سازی اطلاعات محصولات...")
    sync_log = shop_sync.sync_shop_products()
    
    print(f"\n✓ وضعیت: {sync_log.status}")
    print(f"✓ تعداد پردازش شده: {sync_log.records_processed}")
    print(f"✓ تعداد موفق: {sync_log.records_successful}")
    print(f"✓ تعداد ناموفق: {sync_log.records_failed}")
    
    if sync_log.duration_seconds:
        print(f"✓ مدت زمان: {sync_log.duration_seconds} ثانیه")
    
    if sync_log.error_message:
        print(f"✗ خطا: {sync_log.error_message}")
    
    return sync_log.status == 'completed'


def test_full_shop_sync():
    """تست همگام‌سازی کامل فروشگاه"""
    print_separator("تست همگام‌سازی کامل فروشگاه")
    
    shop_sync = get_shop_sync_service()
    
    print("شروع همگام‌سازی کامل فروشگاه...")
    sync_logs = shop_sync.full_shop_sync()
    
    all_success = True
    
    for sync_type, sync_log in sync_logs.items():
        print(f"\n--- {sync_type} ---")
        print(f"✓ وضعیت: {sync_log.status}")
        print(f"✓ تعداد موفق: {sync_log.records_successful}")
        
        if sync_log.status != 'completed':
            all_success = False
    
    return all_success


def test_scheduler_with_shop():
    """تست scheduler با همگام‌سازی فروشگاه"""
    print_separator("تست Scheduler با همگام‌سازی فروشگاه")
    
    scheduler = get_scheduler()
    
    # Get scheduler status
    status = scheduler.get_scheduler_status()
    
    print("✓ وضعیت Scheduler:")
    print(f"  - در حال اجرا: {status['is_running']}")
    print(f"  - اجرای بعدی: {status['next_run']}")
    print(f"  - تعداد job ها: {status['scheduled_jobs']}")
    
    print("\n✓ تنظیمات:")
    for key, value in status['settings'].items():
        print(f"  - {key}: {value}")
    
    # Test immediate shop sync
    print("\n\nاجرای فوری همگام‌سازی فروشگاه...")
    try:
        sync_logs = scheduler.run_shop_sync_now('full')
        print("✓ همگام‌سازی فروشگاه با موفقیت انجام شد")
        return True
    except Exception as e:
        print(f"✗ خطا در همگام‌سازی فروشگاه: {str(e)}")
        return False


def show_sync_status():
    """نمایش وضعیت همگام‌سازی"""
    print_separator("وضعیت همگام‌سازی فروشگاه")
    
    shop_sync = get_shop_sync_service()
    status = shop_sync.get_sync_status()
    
    if 'error' in status:
        print(f"✗ خطا: {status['error']}")
        return
    
    print("آخرین همگام‌سازی محصولات:")
    if status['last_products_sync']['status']:
        print(f"  - وضعیت: {status['last_products_sync']['status']}")
        print(f"  - تعداد موفق: {status['last_products_sync']['records_successful']}")
        print(f"  - زمان شروع: {status['last_products_sync']['started_at']}")
    else:
        print("  - هیچ همگام‌سازی انجام نشده است")
    
    print("\nآخرین همگام‌سازی موجودی:")
    if status['last_inventory_sync']['status']:
        print(f"  - وضعیت: {status['last_inventory_sync']['status']}")
        print(f"  - تعداد موفق: {status['last_inventory_sync']['records_successful']}")
        print(f"  - زمان شروع: {status['last_inventory_sync']['started_at']}")
    else:
        print("  - هیچ همگام‌سازی انجام نشده است")
    
    print("\nآخرین همگام‌سازی قیمت‌ها:")
    if status['last_prices_sync']['status']:
        print(f"  - وضعیت: {status['last_prices_sync']['status']}")
        print(f"  - تعداد موفق: {status['last_prices_sync']['records_successful']}")
        print(f"  - زمان شروع: {status['last_prices_sync']['started_at']}")
    else:
        print("  - هیچ همگام‌سازی انجام نشده است")
    
    print(f"\nآمار فروشگاه:")
    print(f"  - تعداد کل محصولات: {status['shop_stats']['total_products']}")
    print(f"  - تعداد محصولات فعال: {status['shop_stats']['active_products']}")


def main():
    """Main test function"""
    print_separator("تست سیستم همگام‌سازی فروشگاه")
    print(f"زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with app.app_context():
        try:
            # Show menu
            print("\nانتخاب کنید:")
            print("1. تست همگام‌سازی قیمت‌ها")
            print("2. تست همگام‌سازی موجودی")
            print("3. تست همگام‌سازی اطلاعات محصولات")
            print("4. تست همگام‌سازی کامل")
            print("5. تست Scheduler")
            print("6. نمایش وضعیت")
            print("7. اجرای همه تست‌ها")
            print("0. خروج")
            
            choice = input("\nانتخاب شما: ").strip()
            
            results = []
            
            if choice == '1':
                results.append(('قیمت‌ها', test_shop_prices_sync()))
            elif choice == '2':
                results.append(('موجودی', test_shop_inventory_sync()))
            elif choice == '3':
                results.append(('اطلاعات محصولات', test_shop_products_sync()))
            elif choice == '4':
                results.append(('همگام‌سازی کامل', test_full_shop_sync()))
            elif choice == '5':
                results.append(('Scheduler', test_scheduler_with_shop()))
            elif choice == '6':
                show_sync_status()
                return
            elif choice == '7':
                # Run all tests
                results.append(('اطلاعات محصولات', test_shop_products_sync()))
                results.append(('موجودی', test_shop_inventory_sync()))
                results.append(('قیمت‌ها', test_shop_prices_sync()))
                results.append(('Scheduler', test_scheduler_with_shop()))
            elif choice == '0':
                print("خروج...")
                return
            else:
                print("انتخاب نامعتبر!")
                return
            
            # Print summary
            if results:
                print_separator("خلاصه نتایج")
                for test_name, result in results:
                    status = "✓ موفق" if result else "✗ ناموفق"
                    print(f"{test_name}: {status}")
                
                # Overall result
                all_passed = all(result for _, result in results)
                if all_passed:
                    print("\n✓ همه تست‌ها با موفقیت انجام شدند!")
                else:
                    print("\n✗ برخی تست‌ها با خطا مواجه شدند.")
                
                # Show status at the end
                show_sync_status()
            
        except KeyboardInterrupt:
            print("\n\nعملیات توسط کاربر لغو شد.")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ خطای غیرمنتظره: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()

