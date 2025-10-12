"""Test Tadbir API Connection - Simple Version"""

import requests
import socket
import json
from datetime import datetime

def test_connection():
    """Test basic connection to Tadbir server"""
    print("="*60)
    print("TADBIR API CONNECTION TEST")
    print("="*60)
    
    # Configuration
    base_url = 'http://5.202.90.240:8085'
    username = 'Asia@tadbir.biz'
    password = 'Asia@tadbir.biz'
    
    print(f"\nBase URL: {base_url}")
    print(f"Username: {username}")
    
    # Test 1: Socket Connection
    print("\n" + "-"*60)
    print("TEST 1: Socket Connection")
    print("-"*60)
    
    try:
        host = '5.202.90.240'
        port = 8085
        print(f"Testing connection to {host}:{port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"SUCCESS: Port {port} is open and accessible")
        else:
            print(f"FAILED: Port {port} is closed or not accessible")
            print(f"Error code: {result}")
            print("\nPOSSIBLE CAUSES:")
            print("1. Tadbir server is not running")
            print("2. Firewall is blocking the connection")
            print("3. Wrong IP address or port")
            print("4. Network connectivity issues")
            return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False
    
    # Test 2: HTTP Endpoints
    print("\n" + "-"*60)
    print("TEST 2: HTTP Endpoints")
    print("-"*60)
    
    endpoints = [
        ('/', 'GET'),
        ('/token', 'GET'),
        ('/token', 'POST'),
        ('/odata', 'GET'),
    ]
    
    for endpoint, method in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n{method} {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, timeout=10)
            
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.text:
                preview = response.text[:150].replace('\n', ' ')
                print(f"  Response: {preview}...")
                
        except requests.exceptions.ConnectionError as e:
            print(f"  CONNECTION ERROR: {str(e)}")
        except requests.exceptions.Timeout:
            print(f"  TIMEOUT ERROR")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    # Test 3: Authentication
    print("\n" + "-"*60)
    print("TEST 3: Authentication")
    print("-"*60)
    
    auth_url = f"{base_url}/token"
    print(f"\nPOST {auth_url}")
    
    auth_data = {
        'grant_type': 'password',
        'username': username,
        'password': password
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        print("Sending authentication request...")
        response = requests.post(auth_url, data=auth_data, headers=headers, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'access_token' in data:
                    token = data['access_token']
                    print(f"\nSUCCESS: Token received")
                    print(f"Token (first 50 chars): {token[:50]}...")
                    return True
            except:
                pass
        else:
            print(f"\nFAILED: Authentication failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"CONNECTION ERROR: {str(e)}")
        print("\nSERVER IS NOT RESPONDING!")
        print("The Tadbir server appears to be down or unreachable.")
    except requests.exceptions.Timeout:
        print("TIMEOUT ERROR: Server is not responding in time")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    return False

def main():
    success = test_connection()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if success:
        print("RESULT: SUCCESS - Tadbir API is accessible")
    else:
        print("RESULT: FAILED - Tadbir API is not accessible")
        print("\nRECOMMENDED ACTIONS:")
        print("1. Check if Tadbir server is running on 5.202.90.240:8085")
        print("2. Test network connectivity: ping 5.202.90.240")
        print("3. Check firewall settings")
        print("4. Contact Tadbir server administrator")
        print("5. Verify the server URL and credentials")
    
    print("="*60)
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'success': success,
        'base_url': 'http://5.202.90.240:8085',
        'username': 'Asia@tadbir.biz'
    }
    
    filename = f"tadbir_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved: {filename}")

if __name__ == '__main__':
    main()

