"""
Test session creation via API to verify the fix works
"""
import os
import sys
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

API_BASE_URL = 'http://127.0.0.1:8000/api'

print("=" * 60)
print("Testing Session Creation via API")
print("=" * 60)

# Test with atul7788 user
username = "atul7788"
password = input(f"Enter password for {username} (or press Enter to skip): ").strip()

if not password:
    print("[SKIP] Skipping API test. Please test manually in browser.")
    sys.exit(0)

try:
    # Step 1: Login
    print(f"\n1. Logging in as {username}...")
    response = requests.post(
        f'{API_BASE_URL}/auth/login/',
        json={'username': username, 'password': password},
        timeout=5
    )
    
    if response.status_code != 200:
        print(f"[ERROR] Login failed: {response.json()}")
        sys.exit(1)
    
    data = response.json()
    token = data['tokens']['access']
    user_data = data['user']
    
    print(f"[OK] Login successful!")
    print(f"     Username: {user_data['username']}")
    print(f"     Role: {user_data['role']}")
    
    if user_data['role'] != 'FACULTY':
        print(f"[ERROR] User role is '{user_data['role']}', expected 'FACULTY'")
        sys.exit(1)
    
    # Step 2: Create Session
    print("\n2. Creating session...")
    headers = {'Authorization': f'Bearer {token}'}
    
    session_data = {
        'course_name': 'Test API Course',
        'session_date': '2025-11-29',
        'session_time': '16:00:00',
        'otp_enabled': True
    }
    
    response = requests.post(
        f'{API_BASE_URL}/sessions/',
        headers=headers,
        json=session_data,
        timeout=5
    )
    
    print(f"     Status Code: {response.status_code}")
    
    if response.status_code == 201:
        session = response.json()
        print(f"[OK] Session created successfully!")
        print(f"     Session ID: {session.get('id')}")
        print(f"     Course: {session.get('course_name')}")
    elif response.status_code == 403:
        error_data = response.json()
        print(f"[ERROR] Permission denied: {error_data}")
        print(f"     This indicates the role check is working but user role might be wrong")
    else:
        error_data = response.json()
        print(f"[ERROR] Failed to create session: {error_data}")
    
except requests.exceptions.ConnectionError:
    print("[ERROR] Cannot connect to server. Please start Django server:")
    print("        python backend\\manage.py runserver")
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
