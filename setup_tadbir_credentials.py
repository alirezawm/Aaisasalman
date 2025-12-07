"""
Setup Tadbir API Credentials
اسکریپت تنظیم اطلاعات احراز هویت تدبیر
"""

import sqlite3
import getpass
import os
import sys
import requests
from datetime import datetime

def test_credentials(base_url, username, password):
    """Test if credentials work"""
    try:
        auth_data = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(f"{base_url}/token", data=auth_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'access_token' in data:
                    return True, "Success! Valid credentials", data['access_token']
            except:
                pass
        
        return False, f"Authentication failed: {response.text}", None
        
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

def save_to_database(api_url, username, password):
    """Save credentials to database"""
    try:
        conn = sqlite3.connect('instance/asia_salman.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tadbir_sync_settings'
        """)
        
        if not cursor.fetchone():
            print("ERROR: Table 'tadbir_sync_settings' does not exist")
            print("Please run: python init_tadbir_config.py")
            conn.close()
            return False
        
        # Update or insert settings
        settings = [
            ('api_url', api_url),
            ('api_username', username),
            ('api_password', password)
        ]
        
        for key, value in settings:
            # Check if setting exists
            cursor.execute("""
                SELECT id FROM tadbir_sync_settings WHERE setting_key = ?
            """, (key,))
            
            if cursor.fetchone():
                # Update
                cursor.execute("""
                    UPDATE tadbir_sync_settings 
                    SET setting_value = ?
                    WHERE setting_key = ?
                """, (value, key))
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO tadbir_sync_settings (setting_key, setting_value)
                    VALUES (?, ?)
                """, (key, value))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database error: {e}")
        return False

def save_to_env_file(api_url, username, password):
    """Save credentials to .env file"""
    try:
        env_content = f"""# Tadbir API Configuration
TADBIR_API_URL={api_url}
TADBIR_USERNAME={username}
TADBIR_PASSWORD={password}
TADBIR_TIMEOUT=300
TADBIR_RETRY_ATTEMPTS=3

# Sync Configuration
SYNC_INTERVAL_HOURS=3
BATCH_SIZE=1000
ENABLE_INCREMENTAL_SYNC=True
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        return True
    except Exception as e:
        print(f"Error writing .env file: {e}")
        return False

def main():
    """Main setup function"""
    
    print("="*70)
    print("TADBIR API CREDENTIALS SETUP")
    print("="*70)
    print()
    print("This script will help you configure the correct credentials")
    print("for connecting to Tadbir API.")
    print()
    print("You need to provide:")
    print("  1. API URL (default: http://5.202.90.240:8085)")
    print("  2. Username")
    print("  3. Password")
    print()
    print("-"*70)
    
    # Get API URL
    default_url = "http://5.202.90.240:8085"
    api_url = input(f"\nAPI URL [{default_url}]: ").strip()
    if not api_url:
        api_url = default_url
    
    # Get Username
    default_username = "Asia@tadbir.biz"
    username = input(f"Username [{default_username}]: ").strip()
    if not username:
        username = default_username
    
    # Get Password
    password = getpass.getpass("Password: ").strip()
    if not password:
        print("ERROR: Password cannot be empty")
        sys.exit(1)
    
    print()
    print("-"*70)
    print("TESTING CREDENTIALS...")
    print("-"*70)
    print(f"API URL: {api_url}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    print()
    
    # Test credentials
    success, message, token = test_credentials(api_url, username, password)
    
    if success:
        print("SUCCESS! Credentials are valid")
        print(f"Token received: {token[:50]}...")
        print()
        
        # Ask to save
        save = input("Do you want to save these credentials? (yes/no) [yes]: ").strip().lower()
        if save in ['', 'y', 'yes']:
            print()
            print("Saving credentials...")
            
            # Save to database
            if save_to_database(api_url, username, password):
                print("  Saved to database")
            else:
                print("  Failed to save to database")
            
            # Save to .env file
            if save_to_env_file(api_url, username, password):
                print("  Saved to .env file")
            else:
                print("  Failed to save to .env file")
            
            print()
            print("="*70)
            print("SETUP COMPLETE!")
            print("="*70)
            print()
            print("You can now use the Tadbir API integration.")
            print("Run: python test_tadbir_simple.py to verify")
            print()
        else:
            print("Credentials not saved.")
    else:
        print("FAILED! Credentials are not valid")
        print(f"Error: {message}")
        print()
        print("Please check:")
        print("  1. Username is correct")
        print("  2. Password is correct")
        print("  3. API URL is correct")
        print("  4. Account is not locked")
        print()
        print("Contact your Tadbir administrator for help.")
        sys.exit(1)

if __name__ == '__main__':
    main()

