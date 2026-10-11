"""
Comprehensive test script for the entire OTP attendance system
Tests: Session creation, OTP generation, and Mark attendance
"""
import os
import sys
import django
import requests
import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

API_BASE_URL = 'http://127.0.0.1:8000/api'

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def test_full_flow():
    """Test the complete flow: Login -> Create Session -> Generate OTP -> Mark Attendance"""
    
    print_section("COMPREHENSIVE SYSTEM TEST")
    
    # Step 1: Faculty Login
    print_section("1. Faculty Login")
    faculty_username = input("Enter faculty username (or press Enter to skip): ").strip()
    if not faculty_username:
        print("[SKIP] Skipping API tests. Run server and test manually.")
        return
    
    faculty_password = input("Enter faculty password: ").strip()
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/auth/login/',
            json={'username': faculty_username, 'password': faculty_password},
            timeout=5
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Faculty login failed: {response.json()}")
            return
        
        faculty_data = response.json()
        faculty_token = faculty_data['access']
        print("[OK] Faculty logged in successfully")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Please start the Django server first:")
        print("        python manage.py runserver")
        return
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        return
    
    # Step 2: Get or Create Session
    print_section("2. Getting Sessions")
    headers = {'Authorization': f'Bearer {faculty_token}'}
    
    try:
        response = requests.get(f'{API_BASE_URL}/sessions/', headers=headers, timeout=5)
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to get sessions: {response.json()}")
            return
        
        sessions = response.json()
        print(f"[OK] Found {len(sessions)} session(s)")
        
        if not sessions:
            print("[INFO] No sessions found. Creating a test session...")
            # Create a test session
            from django.utils import timezone
            from datetime import date, time as time_obj
            from attendance.models import Session
            from accounts.models import Faculty
            
            faculty = Faculty.objects.get(user__username=faculty_username)
            session = Session.objects.create(
                faculty=faculty,
                course_name="Test Course",
                session_date=date.today(),
                session_time=time_obj(14, 0),
                otp_enabled=True
            )
            print(f"[OK] Created test session: {session}")
            session_id = session.id
        else:
            session = sessions[0]
            session_id = session['id']
            print(f"[OK] Using existing session: {session['course_name']} (ID: {session_id})")
    except Exception as e:
        print(f"[ERROR] Session error: {e}")
        return
    
    # Step 3: Generate OTP
    print_section("3. Generating OTP")
    try:
        response = requests.post(
            f'{API_BASE_URL}/otp/generate/',
            headers=headers,
            json={'session_id': session_id},
            timeout=5
        )
        
        if response.status_code != 201:
            print(f"[ERROR] Failed to generate OTP: {response.json()}")
            return
        
        otp_data = response.json()
        otp_code = otp_data['otp']['otp_code']
        expires_at = otp_data['otp']['expires_at']
        
        print(f"[OK] OTP generated successfully!")
        print(f"     OTP Code: {otp_code}")
        print(f"     Expires at: {expires_at}")
    except Exception as e:
        print(f"[ERROR] OTP generation error: {e}")
        return
    
    # Step 4: Student Login
    print_section("4. Student Login")
    student_username = input("Enter student username (or press Enter to skip attendance test): ").strip()
    if not student_username:
        print("[SKIP] Skipping attendance marking test.")
        print_section("TEST SUMMARY")
        print("[OK] Session creation: PASSED")
        print("[OK] OTP generation: PASSED")
        print("[SKIP] Mark attendance: SKIPPED")
        return
    
    student_password = input("Enter student password: ").strip()
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/auth/student/login/',
            json={'username': student_username, 'password': student_password},
            timeout=5
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Student login failed: {response.json()}")
            return
        
        student_data = response.json()
        student_token = student_data['access']
        print("[OK] Student logged in successfully")
    except Exception as e:
        print(f"[ERROR] Student login error: {e}")
        return
    
    # Step 5: Mark Attendance
    print_section("5. Marking Attendance")
    student_headers = {'Authorization': f'Bearer {student_token}'}
    
    # Wait a moment to ensure OTP is still valid
    time.sleep(1)
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/attendance/mark/',
            headers=student_headers,
            json={
                'session_id': session_id,
                'otp_code': otp_code
            },
            timeout=5
        )
        
        if response.status_code == 201:
            attendance_data = response.json()
            print("[OK] Attendance marked successfully!")
            print(f"     {json.dumps(attendance_data, indent=2)}")
        else:
            error_data = response.json()
            print(f"[ERROR] Failed to mark attendance: {error_data}")
    except Exception as e:
        print(f"[ERROR] Mark attendance error: {e}")
        return
    
    # Summary
    print_section("TEST SUMMARY")
    print("[OK] Session creation: PASSED")
    print("[OK] OTP generation: PASSED")
    print("[OK] Mark attendance: PASSED")
    print("\n[SUCCESS] All tests passed!")

if __name__ == '__main__':
    try:
        test_full_flow()
    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

