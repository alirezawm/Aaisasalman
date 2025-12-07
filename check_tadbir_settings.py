"""Check Tadbir settings from database"""

import sqlite3
import json

def check_settings():
    """Check Tadbir settings from database"""
    
    print("="*70)
    print("CHECKING TADBIR SETTINGS FROM DATABASE")
    print("="*70)
    
    try:
        conn = sqlite3.connect('instance/asia_salman.db')
        cursor = conn.cursor()
        
        # Check if TadbirSyncSettings table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tadbir_sync_settings'
        """)
        
        if cursor.fetchone():
            print("\nTable 'tadbir_sync_settings' found")
            print("-"*70)
            
            # Get all settings
            cursor.execute("""
                SELECT setting_key, setting_value
                FROM tadbir_sync_settings
            """)
            
            settings = cursor.fetchall()
            
            if settings:
                print(f"\nFound {len(settings)} settings:\n")
                for setting in settings:
                    key, value = setting
                    print(f"Key: {key}")
                    if 'password' in key.lower():
                        print(f"Value: {'*' * len(value)}")
                    else:
                        print(f"Value: {value}")
                    print("-"*70)
                    
                # Get specific auth settings
                print("\n" + "="*70)
                print("AUTHENTICATION CREDENTIALS")
                print("="*70)
                
                cursor.execute("""
                    SELECT setting_value FROM tadbir_sync_settings
                    WHERE setting_key = 'api_url'
                """)
                result = cursor.fetchone()
                api_url = result[0] if result else 'Not set'
                print(f"API URL: {api_url}")
                
                cursor.execute("""
                    SELECT setting_value FROM tadbir_sync_settings
                    WHERE setting_key = 'api_username'
                """)
                result = cursor.fetchone()
                username = result[0] if result else 'Not set'
                print(f"Username: {username}")
                
                cursor.execute("""
                    SELECT setting_value FROM tadbir_sync_settings
                    WHERE setting_key = 'api_password'
                """)
                result = cursor.fetchone()
                password = result[0] if result else 'Not set'
                print(f"Password: {'*' * len(password) if password != 'Not set' else 'Not set'}")
                print(f"Password (actual): {password}")
                
            else:
                print("\nNo settings found in database")
        else:
            print("\nTable 'tadbir_sync_settings' does not exist")
            print("Run 'python init_tadbir_config.py' to initialize")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    check_settings()

