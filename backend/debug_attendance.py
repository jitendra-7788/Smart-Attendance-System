import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from accounts.models import Faculty, Student
from attendance.models import Session, OTP
from datetime import date, time

User = get_user_model()

def run_debug():
    print("Setting up test data...")
    
    # Create Faculty
    faculty_user, _ = User.objects.get_or_create(
        username='debug_faculty',
        defaults={'email': 'faculty@debug.com', 'role': 'FACULTY'}
    )
    faculty_user.set_password('password123')
    faculty_user.save()
    
    faculty_profile, _ = Faculty.objects.get_or_create(user=faculty_user, defaults={'department': 'CS'})
    
    # Create Student
    student_user, _ = User.objects.get_or_create(
        username='debug_student',
        defaults={'email': 'student@debug.com', 'role': 'STUDENT'}
    )
    student_user.set_password('password123')
    student_user.save()
    
    student_profile, _ = Student.objects.get_or_create(
        user=student_user, 
        defaults={'full_name': 'Debug Student', 'roll_number': 'DEBUG001'}
    )
    
    # Create Session
    session, _ = Session.objects.get_or_create(
        faculty=faculty_profile,
        course_name='Debug Course',
        session_date=date.today(),
        session_time=time(10, 0),
        defaults={'otp_enabled': True}
    )
    
    # Generate OTP
    otp = OTP.objects.create(session=session, code='123456')
    
    print(f"Faculty: {faculty_user.username} (Role: {faculty_user.role})")
    print(f"Student: {student_user.username} (Role: {student_user.role})")
    print(f"Session ID: {session.id}")
    print(f"OTP: {otp.code}")
    
    # Test Marking Attendance
    client = APIClient()
    
    # Login as Student to get token
    response = client.post('/api/auth/login/student/', {
        'username': 'debug_student',
        'password': 'password123'
    })
    
    if response.status_code != 200:
        print(f"Login failed: {response.data}")
        return
        
    token = response.data['tokens']['access']
    print(f"Login successful. Token obtained.")
    
    # Set credentials
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    
    # Try to mark attendance
    print("\nAttempting to mark attendance...")
    response = client.post('/api/attendance/mark/', {
        'session_id': session.id,
        'otp_code': '123456'
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code == 403:
        print("\nFAILURE REPRODUCED: Permission Denied")
    elif response.status_code == 201:
        print("\nSUCCESS: Attendance marked")
    else:
        print(f"\nUnexpected result: {response.status_code}")

if __name__ == '__main__':
    try:
        run_debug()
    except Exception as e:
        print(f"Error: {e}")
