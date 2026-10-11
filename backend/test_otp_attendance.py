"""
Test script for OTP generation and mark attendance functionality
Run this after starting the Django server
"""
import requests
import json
import time

API_BASE_URL = 'http://127.0.0.1:8000/api'

def test_otp_generation_and_attendance():
    """Test OTP generation and mark attendance flow"""
    
    print("=" * 60)
    print("Testing OTP Generation and Mark Attendance")
    print("=" * 60)
    
    # Step 1: Faculty Login
    print("\n1. Faculty Login...")
    faculty_login_data = {
        'username': input("Enter faculty username: "),
        'password': input("Enter faculty password: ")
    }
    
    response = requests.post(
        f'{API_BASE_URL}/auth/login/',
        json=faculty_login_data
    )
    
    if response.status_code != 200:
        print(f"❌ Faculty login failed: {response.json()}")
        return
    
    faculty_data = response.json()
    faculty_token = faculty_data['access']
    print("✅ Faculty logged in successfully")
    
    # Step 2: Get Faculty Sessions
    print("\n2. Getting faculty sessions...")
    headers = {'Authorization': f'Bearer {faculty_token}'}
    response = requests.get(f'{API_BASE_URL}/sessions/', headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get sessions: {response.json()}")
        return
    
    sessions = response.json()
    if not sessions:
        print("❌ No sessions found. Please create a session first.")
        return
    
    print(f"✅ Found {len(sessions)} session(s)")
    for i, session in enumerate(sessions, 1):
        print(f"   {i}. {session['course_name']} - {session['session_date']} {session['session_time']}")
    
    # Step 3: Generate OTP
    print("\n3. Generating OTP...")
    session_id = sessions[0]['id']
    print(f"   Using session ID: {session_id}")
    
    response = requests.post(
        f'{API_BASE_URL}/otp/generate/',
        headers=headers,
        json={'session_id': session_id}
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to generate OTP: {response.json()}")
        return
    
    otp_data = response.json()
    otp_code = otp_data['otp']['otp_code']
    expires_at = otp_data['otp']['expires_at']
    
    print(f"✅ OTP generated successfully!")
    print(f"   OTP Code: {otp_code}")
    print(f"   Expires at: {expires_at}")
    
    # Step 4: Student Login
    print("\n4. Student Login...")
    student_login_data = {
        'username': input("Enter student username: "),
        'password': input("Enter student password: ")
    }
    
    response = requests.post(
        f'{API_BASE_URL}/auth/student/login/',
        json=student_login_data
    )
    
    if response.status_code != 200:
        print(f"❌ Student login failed: {response.json()}")
        return
    
    student_data = response.json()
    student_token = student_data['access']
    print("✅ Student logged in successfully")
    
    # Step 5: Mark Attendance
    print("\n5. Marking attendance...")
    student_headers = {'Authorization': f'Bearer {student_token}'}
    
    # Wait a moment to ensure OTP is still valid
    time.sleep(1)
    
    response = requests.post(
        f'{API_BASE_URL}/attendance/mark/',
        headers=student_headers,
        json={
            'session_id': session_id,
            'otp_code': otp_code
        }
    )
    
    if response.status_code == 201:
        attendance_data = response.json()
        print("✅ Attendance marked successfully!")
        print(f"   {json.dumps(attendance_data, indent=2)}")
    else:
        print(f"❌ Failed to mark attendance: {response.json()}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_otp_generation_and_attendance()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

