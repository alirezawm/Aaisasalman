"""
سرویس اتصال به API تدبیر
Tadbir Accounting System API Service
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TadbirAPIService:
    """سرویس اتصال به API تدبیر"""
    
    def __init__(self):
        """Initialize Tadbir API service"""
        self.base_url = os.getenv('TADBIR_API_URL', 'http://5.202.90.240:8085')
        self.username = os.getenv('TADBIR_USERNAME', 'Asia@tadbir.biz')
        self.password = os.getenv('TADBIR_PASSWORD', 'Asia@tadbir.biz')
        self.timeout = int(os.getenv('TADBIR_TIMEOUT', '300'))
        self.retry_attempts = int(os.getenv('TADBIR_RETRY_ATTEMPTS', '3'))
        
        # Price categories configuration
        # Note: خریدار تکی فقط قیمت چکی دارد، خریدار عمده هر دو نقدی و چکی دارد
        self.price_categories = {
            'retail_check': {'price_list_key': 13, 'markup_percentage': 10},  # لیست قیمت چکی خرده (تکی)
            'bulk_cash': {'price_list_key': 14, 'markup_percentage': 10},   # لیست قیمت نقدی عمده
            'bulk_check': {'price_list_key': 13, 'markup_percentage': 10}    # لیست قیمت چکی عمده
        }
        
        # Stock code for inventory
        self.stock_code = '10'
        
        # Token management
        self._access_token = None
        self._token_expires_at = None
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self._access_token:
            headers['Authorization'] = f'Bearer {self._access_token}'
            
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        for attempt in range(self.retry_attempts):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check for authentication errors
                if response.status_code == 401:
                    logger.warning("Authentication failed, attempting to refresh token")
                    self._access_token = None
                    self._token_expires_at = None
                    if attempt < self.retry_attempts - 1:
                        self.authenticate()
                        continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{self.retry_attempts}): {str(e)}")
                if attempt == self.retry_attempts - 1:
                    raise
                # Wait before retry (exponential backoff)
                import time
                time.sleep(2 ** attempt)
        
        raise Exception("All retry attempts failed")
    
    def authenticate(self) -> str:
        """احراز هویت و دریافت توکن"""
        try:
            # Use the working authentication format (form data with grant_type=password)
            auth_data = {
                'grant_type': 'password',
                'username': self.username,
                'password': self.password
            }
            
            url = f"{self.base_url}/token"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            logger.info(f"Authenticating with Tadbir API: {url}")
            response = requests.post(url, data=auth_data, headers=headers, timeout=self.timeout)
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    token_data = response.json()
                    self._access_token = token_data.get('access_token')
                    expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                    self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    logger.info("Successfully authenticated with Tadbir API")
                    return self._access_token
                except json.JSONDecodeError:
                    # Maybe it's plain text token
                    self._access_token = response.text.strip()
                    self._token_expires_at = datetime.utcnow() + timedelta(hours=1)
                    logger.info("Successfully authenticated with plain text token")
                    return self._access_token
            else:
                error_msg = f"Authentication failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise Exception(f"TADBIR_AUTH_ERROR: خطا در احراز هویت - {str(e)}")
    
    def _ensure_authenticated(self):
        """Ensure we have a valid token"""
        if not self._access_token or (self._token_expires_at and datetime.utcnow() >= self._token_expires_at):
            self.authenticate()
    
    def get_products(self, last_update: Optional[datetime] = None, 
                    skip: Optional[int] = None, top: Optional[int] = None) -> List[Dict]:
        """دریافت لیست کالاها"""
        try:
            self._ensure_authenticated()
            
            params = {}
            if last_update:
                params['$filter'] = f"LastUpdate ge {last_update.isoformat()}"
            if skip:
                params['$skip'] = skip
            if top:
                params['$top'] = top
            
            response = self._make_request('GET', '/odata/GeneralDescs', params=params)
            data = response.json()
            
            products = data.get('value', [])
            logger.info(f"Retrieved {len(products)} products from Tadbir API")
            
            return products
            
        except Exception as e:
            logger.error(f"Failed to get products: {str(e)}")
            raise Exception(f"TADBIR_API_ERROR: خطا در دریافت کالاها - {str(e)}")
    
    def get_inventory(self, stock_code: str = None, item_code: Optional[str] = None,
                     skip: Optional[int] = None, top: Optional[int] = None) -> List[Dict]:
        """دریافت موجودی کالاها"""
        try:
            self._ensure_authenticated()
            
            stock_code = stock_code or self.stock_code
            
            # Use the correct endpoint: /odata/GeneralDescs/Tadbir.GetRem(stock='10')
            endpoint = f"/odata/GeneralDescs/Tadbir.GetRem(stock='{stock_code}')"
            
            params = {}
            if skip:
                params['$skip'] = skip
            if top:
                params['$top'] = top
            
            response = self._make_request('GET', endpoint, params=params)
            data = response.json()
            
            inventory = data.get('value', [])
            
            # Filter by item_code if specified
            if item_code:
                inventory = [item for item in inventory if item.get('Itemcode') == item_code]
            
            logger.info(f"Retrieved {len(inventory)} inventory records from Tadbir API")
            
            return inventory
            
        except Exception as e:
            logger.error(f"Failed to get inventory: {str(e)}")
            raise Exception(f"TADBIR_API_ERROR: خطا در دریافت موجودی - {str(e)}")
    
    def get_prices(self, price_list_key: Optional[int] = None, 
                  last_update: Optional[datetime] = None,
                  skip: Optional[int] = None, top: Optional[int] = None) -> List[Dict]:
        """دریافت قیمت‌های کالاها"""
        try:
            self._ensure_authenticated()
            
            params = {}
            if price_list_key:
                params['$filter'] = f"PriceListKey eq {price_list_key}"
            if last_update:
                if params.get('$filter'):
                    params['$filter'] += f" and LastUpdate ge {last_update.isoformat()}"
                else:
                    params['$filter'] = f"LastUpdate ge {last_update.isoformat()}"
            if skip:
                params['$skip'] = skip
            if top:
                params['$top'] = top
            
            response = self._make_request('GET', '/odata/PriceListDetails', params=params)
            data = response.json()
            
            prices = data.get('value', [])
            logger.info(f"Retrieved {len(prices)} price records from Tadbir API")
            
            return prices
            
        except Exception as e:
            logger.error(f"Failed to get prices: {str(e)}")
            raise Exception(f"TADBIR_API_ERROR: خطا در دریافت قیمت‌ها - {str(e)}")
    
    def calculate_final_price(self, base_price: float, price_type: str) -> float:
        """محاسبه قیمت نهایی با اعمال درصد اضافی"""
        if price_type not in self.price_categories:
            raise ValueError(f"Invalid price type: {price_type}")
        
        markup_percentage = self.price_categories[price_type]['markup_percentage']
        final_price = base_price * (1 + markup_percentage / 100)
        
        # Round to 2 decimal places
        return round(final_price, 2)
    
    def test_connection(self) -> Dict[str, Any]:
        """تست اتصال به API تدبیر"""
        try:
            # Try to authenticate
            token = self.authenticate()
            
            # Try to get a small sample of products
            products = self.get_products(top=1)
            
            return {
                'success': True,
                'message': 'اتصال به API تدبیر برقرار است',
                'token_received': bool(token),
                'products_accessible': len(products) > 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'خطا در اتصال به API تدبیر: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def debug_api_endpoints(self) -> Dict[str, Any]:
        """Debug API endpoints to understand the structure"""
        debug_info = {
            'base_url': self.base_url,
            'username': self.username,
            'endpoints_tested': [],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Test different possible endpoints
        endpoints_to_test = [
            '/token',
            '/api/token',
            '/auth/token',
            '/login',
            '/api/login',
            '/auth/login',
            '/',
            '/api',
            '/odata',
            '/api/odata'
        ]
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{self.base_url}{endpoint}"
                logger.info(f"Testing endpoint: {url}")
                
                # Test GET request
                response = requests.get(url, timeout=10)
                debug_info['endpoints_tested'].append({
                    'endpoint': endpoint,
                    'method': 'GET',
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'response_preview': response.text[:200] if response.text else ''
                })
                
                # Test POST request with basic auth
                response = requests.post(url, auth=(self.username, self.password), timeout=10)
                debug_info['endpoints_tested'].append({
                    'endpoint': endpoint,
                    'method': 'POST',
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'response_preview': response.text[:200] if response.text else ''
                })
                
            except Exception as e:
                debug_info['endpoints_tested'].append({
                    'endpoint': endpoint,
                    'error': str(e)
                })
        
        return debug_info
    
    def get_api_status(self) -> Dict[str, Any]:
        """دریافت وضعیت API"""
        return {
            'base_url': self.base_url,
            'username': self.username,
            'has_token': bool(self._access_token),
            'token_expires_at': self._token_expires_at.isoformat() if self._token_expires_at else None,
            'timeout': self.timeout,
            'retry_attempts': self.retry_attempts,
            'price_categories': self.price_categories,
            'stock_code': self.stock_code
        }
    
    def get_total_counts(self) -> Dict[str, int]:
        """دریافت تعداد کل کالاها و قیمت‌ها"""
        try:
            self._ensure_authenticated()
            
            counts = {}
            
            # Get total products count
            try:
                response = self._make_request('GET', '/odata/GeneralDescs', params={'$count': 'true', '$top': '0'})
                data = response.json()
                counts['total_products'] = data.get('@odata.count', 0)
            except Exception as e:
                logger.warning(f"Failed to get products count: {e}")
                counts['total_products'] = 0
            
            # Get total prices count
            try:
                response = self._make_request('GET', '/odata/PriceListDetails', params={'$count': 'true', '$top': '0'})
                data = response.json()
                counts['total_prices'] = data.get('@odata.count', 0)
            except Exception as e:
                logger.warning(f"Failed to get prices count: {e}")
                counts['total_prices'] = 0
            
            # Get total inventory count (for stock code 10)
            try:
                endpoint = f"/odata/GeneralDescs/Tadbir.GetRem(stock='{self.stock_code}')"
                response = self._make_request('GET', endpoint, params={'$count': 'true', '$top': '0'})
                data = response.json()
                counts['total_inventory'] = data.get('@odata.count', 0)
            except Exception as e:
                logger.warning(f"Failed to get inventory count: {e}")
                counts['total_inventory'] = 0
            
            return counts
            
        except Exception as e:
            logger.error(f"Failed to get total counts: {str(e)}")
            return {'total_products': 0, 'total_prices': 0}
