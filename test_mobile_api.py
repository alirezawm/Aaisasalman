"""
فایل تست API موبایل
Mobile API Test File

برای اجرا:
python test_mobile_api.py
"""

import requests
import json
from datetime import datetime

# تنظیمات
BASE_URL = "http://localhost:5000/api/mobile/v1"
TEST_PHONE = "09123456789"

# برای ذخیره توکن
access_token = None
refresh_token = None


def print_section(title):
    """چاپ عنوان بخش"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_response(response):
    """چاپ پاسخ API"""
    print(f"\nStatus Code: {response.status_code}")
    try:
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print("Response Text:", response.text)


def test_send_otp():
    """تست ارسال OTP"""
    print_section("1. تست ارسال OTP")
    
    url = f"{BASE_URL}/auth/send-otp"
    data = {
        "phone": TEST_PHONE
    }
    
    response = requests.post(url, json=data)
    print_response(response)
    
    return response.status_code == 200


def test_verify_otp(otp_code):
    """تست تایید OTP"""
    print_section("2. تست تایید OTP")
    
    global access_token, refresh_token
    
    url = f"{BASE_URL}/auth/verify-otp"
    data = {
        "phone": TEST_PHONE,
        "otp_code": otp_code
    }
    
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            access_token = result.get('data', {}).get('access_token')
            refresh_token = result.get('data', {}).get('refresh_token')
            print(f"\n✅ توکن دریافت شد!")
            return True
    
    return False


def test_get_products():
    """تست دریافت لیست محصولات"""
    print_section("3. تست دریافت لیست محصولات")
    
    url = f"{BASE_URL}/products"
    params = {
        "page": 1,
        "per_page": 5
    }
    
    response = requests.get(url, params=params)
    print_response(response)
    
    return response.status_code == 200


def test_get_categories():
    """تست دریافت دسته‌بندی‌ها"""
    print_section("4. تست دریافت دسته‌بندی‌ها")
    
    url = f"{BASE_URL}/categories"
    
    response = requests.get(url)
    print_response(response)
    
    return response.status_code == 200


def test_get_user_profile():
    """تست دریافت پروفایل کاربر"""
    print_section("5. تست دریافت پروفایل کاربر")
    
    global access_token
    
    if not access_token:
        print("❌ نیاز به توکن است!")
        return False
    
    url = f"{BASE_URL}/user/profile"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response)
    
    return response.status_code == 200


def test_get_cart():
    """تست دریافت سبد خرید"""
    print_section("6. تست دریافت سبد خرید")
    
    global access_token
    
    if not access_token:
        print("❌ نیاز به توکن است!")
        return False
    
    url = f"{BASE_URL}/cart"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response)
    
    return response.status_code == 200


def test_get_orders():
    """تست دریافت سفارشات"""
    print_section("7. تست دریافت سفارشات")
    
    global access_token
    
    if not access_token:
        print("❌ نیاز به توکن است!")
        return False
    
    url = f"{BASE_URL}/orders"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    print_response(response)
    
    return response.status_code == 200


def test_get_config():
    """تست دریافت تنظیمات"""
    print_section("8. تست دریافت تنظیمات")
    
    url = f"{BASE_URL}/config"
    
    response = requests.get(url)
    print_response(response)
    
    return response.status_code == 200


def test_refresh_token():
    """تست تازه‌سازی توکن"""
    print_section("9. تست تازه‌سازی توکن")
    
    global access_token, refresh_token
    
    if not refresh_token:
        print("❌ نیاز به refresh token است!")
        return False
    
    url = f"{BASE_URL}/auth/refresh-token"
    headers = {
        "Authorization": f"Bearer {refresh_token}"
    }
    
    response = requests.post(url, headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            access_token = result.get('data', {}).get('access_token')
            print(f"\n✅ توکن جدید دریافت شد!")
            return True
    
    return False


def main():
    """تابع اصلی"""
    print("\n" + "="*60)
    print("  🚀 شروع تست API موبایل")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Phone: {TEST_PHONE}")
    
    results = []
    
    # تست ارسال OTP
    if test_send_otp():
        results.append(("ارسال OTP", "✅"))
        print("\n⚠️  لطفاً کد OTP را وارد کنید:")
        otp_code = input("OTP Code: ").strip()
        
        # تست تایید OTP
        if test_verify_otp(otp_code):
            results.append(("تایید OTP", "✅"))
        else:
            results.append(("تایید OTP", "❌"))
            print("\n⚠️  بدون توکن نمی‌توان تست‌های بعدی را انجام داد")
            print("="*60)
            return
    else:
        results.append(("ارسال OTP", "❌"))
        return
    
    # تست‌های عمومی (بدون نیاز به توکن)
    if test_get_products():
        results.append(("لیست محصولات", "✅"))
    else:
        results.append(("لیست محصولات", "❌"))
    
    if test_get_categories():
        results.append(("دسته‌بندی‌ها", "✅"))
    else:
        results.append(("دسته‌بندی‌ها", "❌"))
    
    if test_get_config():
        results.append(("تنظیمات", "✅"))
    else:
        results.append(("تنظیمات", "❌"))
    
    # تست‌های نیازمند توکن
    if test_get_user_profile():
        results.append(("پروفایل کاربر", "✅"))
    else:
        results.append(("پروفایل کاربر", "❌"))
    
    if test_get_cart():
        results.append(("سبد خرید", "✅"))
    else:
        results.append(("سبد خرید", "❌"))
    
    if test_get_orders():
        results.append(("سفارشات", "✅"))
    else:
        results.append(("سفارشات", "❌"))
    
    if test_refresh_token():
        results.append(("تازه‌سازی توکن", "✅"))
    else:
        results.append(("تازه‌سازی توکن", "❌"))
    
    # خلاصه نتایج
    print_section("📊 خلاصه نتایج")
    for test_name, status in results:
        print(f"{status} {test_name}")
    
    success_count = sum(1 for _, status in results if status == "✅")
    total_count = len(results)
    
    print(f"\n✅ موفق: {success_count}/{total_count}")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ تست متوقف شد!")
    except Exception as e:
        print(f"\n\n❌ خطا: {str(e)}")

