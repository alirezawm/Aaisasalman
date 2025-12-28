import requests
import random
import string
from datetime import datetime, timedelta
from flask import current_app

class SMSService:
    """SMS service for sending OTP via Melipayamak API"""
    
    def __init__(self):
        self.api_url = "https://console.melipayamak.com/api/send/otp/6f1bfd209057496db99eaf7d1d3d92aa"
        self.timeout = 30  # seconds
    
    def generate_otp(self, length=6):
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_otp(self, phone_number):
        """
        Send OTP to phone number via Melipayamak API
        
        Args:
            phone_number (str): Phone number to send OTP to
            
        Returns:
            dict: Response containing success status and message
        """
        try:
            # Clean phone number (remove spaces, dashes, etc.)
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            
            # Ensure phone number starts with 09
            if not clean_phone.startswith('09'):
                if clean_phone.startswith('9'):
                    clean_phone = '0' + clean_phone
                else:
                    return {
                        'success': False,
                        'message': 'شماره تلفن باید با 09 شروع شود',
                        'code': None
                    }
            
            # Prepare request data
            data = {'to': clean_phone}
            
            # Send request to Melipayamak API
            response = requests.post(
                self.api_url, 
                json=data, 
                timeout=self.timeout
            )
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                
                # Log the full response for debugging
                current_app.logger.info(f"SMS API Response for {clean_phone}: {result}")
                
                # Check if we have a code (indicating success)
                if 'code' in result:
                    # Check if status exists and what it says
                    status = result.get('status', '')
                    status_lower = str(status).lower()
                    
                    # If status is None or indicates success, treat as success
                    # Common success indicators: None, empty, "success", "موفق", "ارسال موفق بود"
                    if not status or 'موفق' in status or 'success' in status_lower:
                        # Success - OTP sent
                        # Ensure code is returned as string
                        otp_code = str(result['code']).strip()
                        current_app.logger.info(f"OTP sent successfully to {clean_phone}: {otp_code} (type: {type(otp_code)})")
                        return {
                            'success': True,
                            'message': 'کد تأیید با موفقیت ارسال شد',
                            'code': otp_code,
                            'phone': clean_phone
                        }
                    else:
                        # Has code but status indicates error
                        error_message = status or result.get('message', 'خطای نامشخص در ارسال پیامک')
                        current_app.logger.error(f"SMS API Error for {clean_phone}: {error_message}, Full response: {result}")
                        return {
                            'success': False,
                            'message': f'خطا در ارسال پیامک: {error_message}',
                            'code': None
                        }
                else:
                    # No code in response - API returned error
                    error_message = result.get('status', result.get('message', 'خطای نامشخص در ارسال پیامک'))
                    current_app.logger.error(f"SMS API Error for {clean_phone}: {error_message}, Full response: {result}")
                    return {
                        'success': False,
                        'message': f'خطا در ارسال پیامک: {error_message}',
                        'code': None
                    }
            else:
                current_app.logger.error(f"SMS API HTTP Error for {clean_phone}: Status {response.status_code}, Response: {response.text}")
                return {
                    'success': False,
                    'message': f'خطا در ارتباط با سرویس پیامک (کد: {response.status_code})',
                    'code': None
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'زمان ارسال پیامک به پایان رسید. لطفاً دوباره تلاش کنید.',
                'code': None
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'message': 'خطا در اتصال به سرویس پیامک. لطفاً اتصال اینترنت خود را بررسی کنید.',
                'code': None
            }
        except Exception as e:
            current_app.logger.error(f"SMS Service Error: {str(e)}")
            return {
                'success': False,
                'message': 'خطای داخلی در ارسال پیامک. لطفاً با پشتیبانی تماس بگیرید.',
                'code': None
            }
    
    def verify_otp(self, user_code, stored_code, expires_at):
        """
        Verify OTP code
        
        Args:
            user_code (str): Code entered by user
            stored_code (str): Code stored in database
            expires_at (datetime): Expiration time of the code
            
        Returns:
            dict: Response containing verification result
        """
        try:
            # Check if code has expired
            if datetime.utcnow() > expires_at:
                return {
                    'success': False,
                    'message': 'کد تأیید منقضی شده است. لطفاً کد جدید درخواست کنید.',
                    'valid': False
                }
            
            # Normalize both codes: convert to string, strip whitespace, remove any non-digit characters
            user_code_normalized = ''.join(filter(str.isdigit, str(user_code).strip()))
            stored_code_normalized = ''.join(filter(str.isdigit, str(stored_code).strip()))
            
            # Log for debugging
            current_app.logger.info(f"OTP Verification - User code: '{user_code}' (type: {type(user_code)}, normalized: '{user_code_normalized}', len: {len(user_code_normalized)})")
            current_app.logger.info(f"OTP Verification - Stored code: '{stored_code}' (type: {type(stored_code)}, normalized: '{stored_code_normalized}', len: {len(stored_code_normalized)})")
            
            # Check if codes are empty after normalization
            if not user_code_normalized:
                current_app.logger.warning("OTP Verification - User code is empty after normalization")
                return {
                    'success': False,
                    'message': 'کد تأیید وارد شده معتبر نیست',
                    'valid': False
                }
            
            if not stored_code_normalized:
                current_app.logger.error("OTP Verification - Stored code is empty after normalization!")
                return {
                    'success': False,
                    'message': 'خطا در بررسی کد تأیید',
                    'valid': False
                }
            
            # Check if code lengths match (should be 6 digits)
            if len(user_code_normalized) != len(stored_code_normalized):
                current_app.logger.warning(f"OTP Verification - Code length mismatch. User: {len(user_code_normalized)}, Stored: {len(stored_code_normalized)}")
                return {
                    'success': False,
                    'message': 'کد تأیید اشتباه است',
                    'valid': False
                }
            
            # Check if codes match
            if user_code_normalized == stored_code_normalized:
                current_app.logger.info("OTP Verification - Codes match successfully")
                return {
                    'success': True,
                    'message': 'کد تأیید صحیح است',
                    'valid': True
                }
            else:
                current_app.logger.warning(f"OTP Verification - Codes don't match. User normalized: '{user_code_normalized}', Stored normalized: '{stored_code_normalized}'")
                return {
                    'success': False,
                    'message': 'کد تأیید اشتباه است',
                    'valid': False
                }
                
        except Exception as e:
            current_app.logger.error(f"OTP Verification Error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': 'خطا در بررسی کد تأیید',
                'valid': False
            }
    
    def get_expiration_time(self, minutes=5):
        """Get expiration time for OTP (default 5 minutes)"""
        return datetime.utcnow() + timedelta(minutes=minutes)
    
    def send_welcome_message(self, phone_number, user_name, user_type='regular'):
        """
        Send welcome message to user after successful login
        
        Args:
            phone_number (str): User's phone number
            user_name (str): User's full name
            user_type (str): Type of user (regular, bulk_buyer, admin)
            
        Returns:
            dict: Response containing success status and message
        """
        try:
            # Clean phone number
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            
            # Ensure phone number starts with 09
            if not clean_phone.startswith('09'):
                if clean_phone.startswith('9'):
                    clean_phone = '0' + clean_phone
                else:
                    return {
                        'success': False,
                        'message': 'شماره تلفن نامعتبر است'
                    }
            
            # Create personalized welcome message based on user type
            if user_type == 'bulk_buyer':
                welcome_message = f"سلام {user_name} عزیز! خوش آمدید به پنل خریداران عمده شرکت بازرگانی قطعات خودرو آسیا سلمان. ورود شما با موفقیت انجام شد. از مزایای ویژه و قیمت‌های خاص برخوردار شوید."
            elif user_type == 'admin':
                welcome_message = f"سلام {user_name} عزیز! خوش آمدید به پنل مدیریت شرکت بازرگانی قطعات خودرو آسیا سلمان. ورود شما با موفقیت انجام شد."
            else:
                welcome_message = f"سلام {user_name} عزیز! خوش آمدید به شرکت بازرگانی قطعات خودرو آسیا سلمان. ورود شما با موفقیت انجام شد. از خدمات ما لذت ببرید."
            
            # For now, we'll log the message since the current API is for OTP only
            # In production, you should use a proper SMS service that supports custom messages
            current_app.logger.info(f"Welcome message for {user_name} ({clean_phone}): {welcome_message}")
            
            # TODO: Implement actual SMS sending for welcome messages
            # This would require a different SMS service or API endpoint that supports custom messages
            
            return {
                'success': True,
                'message': 'پیام خوشامدگویی ارسال شد',
                'phone': clean_phone,
                'welcome_text': welcome_message
            }
            
        except Exception as e:
            current_app.logger.error(f"Welcome SMS Error: {str(e)}")
            return {
                'success': False,
                'message': 'خطا در ارسال پیام خوشامدگویی'
            }

# Create global instance
sms_service = SMSService()
