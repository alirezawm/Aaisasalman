"""Test different authentication methods for Tadbir API"""

import requests
import json
from datetime import datetime

def test_auth_methods():
    """Test various authentication methods"""
    
    base_url = 'http://5.202.90.240:8085'
    username = 'Asia@tadbir.biz'
    password = 'Asia@tadbir.biz'
    
    print("="*70)
    print("TADBIR API AUTHENTICATION TESTS")
    print("="*70)
    print(f"\nBase URL: {base_url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}\n")
    
    # Test different authentication methods
    auth_tests = [
        {
            'name': 'Method 1: Form data with grant_type=password',
            'url': f'{base_url}/token',
            'method': 'POST',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'data': {
                'grant_type': 'password',
                'username': username,
                'password': password
            }
        },
        {
            'name': 'Method 2: Form data without grant_type',
            'url': f'{base_url}/token',
            'method': 'POST',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'data': {
                'username': username,
                'password': password
            }
        },
        {
            'name': 'Method 3: JSON body',
            'url': f'{base_url}/token',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'json': {
                'username': username,
                'password': password
            }
        },
        {
            'name': 'Method 4: Basic Authentication',
            'url': f'{base_url}/token',
            'method': 'POST',
            'headers': {},
            'auth': (username, password)
        },
        {
            'name': 'Method 5: Login endpoint with JSON',
            'url': f'{base_url}/login',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'json': {
                'username': username,
                'password': password
            }
        },
        {
            'name': 'Method 6: API Login endpoint',
            'url': f'{base_url}/api/login',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'json': {
                'username': username,
                'password': password
            }
        },
        {
            'name': 'Method 7: Direct OData access without auth',
            'url': f'{base_url}/odata/GeneralDescs?$top=1',
            'method': 'GET',
            'headers': {}
        },
        {
            'name': 'Method 8: OData with Basic Auth',
            'url': f'{base_url}/odata/GeneralDescs?$top=1',
            'method': 'GET',
            'headers': {},
            'auth': (username, password)
        },
    ]
    
    successful_methods = []
    
    for i, test in enumerate(auth_tests, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'='*70}")
        print(f"URL: {test['url']}")
        print(f"Method: {test['method']}")
        print(f"Headers: {test.get('headers', {})}")
        
        try:
            kwargs = {
                'headers': test.get('headers', {}),
                'timeout': 30
            }
            
            if 'data' in test:
                kwargs['data'] = test['data']
                print(f"Data: {test['data']}")
            
            if 'json' in test:
                kwargs['json'] = test['json']
                print(f"JSON: {test['json']}")
            
            if 'auth' in test:
                kwargs['auth'] = test['auth']
                print(f"Auth: Basic Authentication")
            
            print(f"\nSending request...")
            
            if test['method'] == 'GET':
                response = requests.get(test['url'], **kwargs)
            else:
                response = requests.post(test['url'], **kwargs)
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            # Show response
            response_text = response.text[:500]
            print(f"\nResponse:")
            print("-" * 70)
            
            try:
                # Try to format as JSON
                response_json = response.json()
                print(json.dumps(response_json, indent=2)[:500])
                
                # Check for token
                if 'access_token' in response_json:
                    token = response_json['access_token']
                    print(f"\n*** SUCCESS! Token received: {token[:50]}... ***")
                    successful_methods.append({
                        'method': test['name'],
                        'token': token
                    })
                elif response.status_code == 200:
                    print(f"\n*** SUCCESS! Request succeeded ***")
                    successful_methods.append({
                        'method': test['name'],
                        'response': 'Success'
                    })
                    
            except json.JSONDecodeError:
                print(response_text)
                if response.status_code == 200:
                    print(f"\n*** SUCCESS! (non-JSON response) ***")
                    successful_methods.append({
                        'method': test['name'],
                        'response': response_text[:100]
                    })
            
            print("-" * 70)
            
        except requests.exceptions.ConnectionError as e:
            print(f"CONNECTION ERROR: {str(e)}")
        except requests.exceptions.Timeout:
            print(f"TIMEOUT ERROR")
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total tests: {len(auth_tests)}")
    print(f"Successful: {len(successful_methods)}")
    print(f"Failed: {len(auth_tests) - len(successful_methods)}")
    
    if successful_methods:
        print("\nSUCCESSFUL METHODS:")
        for method in successful_methods:
            print(f"  - {method['method']}")
            if 'token' in method:
                print(f"    Token: {method['token'][:50]}...")
    else:
        print("\nNo successful authentication methods found!")
        print("\nPOSSIBLE ISSUES:")
        print("1. Username or password is incorrect")
        print("2. Account is locked or disabled")
        print("3. API requires different authentication method")
        print("4. Need to contact Tadbir administrator to verify credentials")
    
    print("="*70)
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'base_url': base_url,
        'username': username,
        'total_tests': len(auth_tests),
        'successful_tests': len(successful_methods),
        'successful_methods': successful_methods
    }
    
    filename = f"tadbir_auth_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved: {filename}")

if __name__ == '__main__':
    test_auth_methods()

