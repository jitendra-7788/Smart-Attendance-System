"""
Test OTP generation functionality
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from accounts.models import CustomUser, Faculty
from attendance.models import Session, OTP
from attendance.views import GenerateOTPView
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
import json

print("=" * 60)
print("Testing OTP Generation")
print("=" * 60)

# Get a faculty user
faculty_user = CustomUser.objects.filter(role='FACULTY').first()
if not faculty_user:
    print("[ERROR] No faculty user found!")
    sys.exit(1)

print(f"\n[TEST] Using faculty user: {faculty_user.username}")

# Get or create a session
try:
    faculty = faculty_user.faculty_profile
except Faculty.DoesNotExist:
    faculty = Faculty.objects.create(user=faculty_user)

session = Session.objects.filter(faculty=faculty).first()
if not session:
    from datetime import date, time
    session = Session.objects.create(
        faculty=faculty,
        course_name="Test OTP Session",
        session_date=date.today(),
        session_time=time(16, 0),
        otp_enabled=True
    )
    print(f"[INFO] Created test session: {session.id}")

print(f"[TEST] Using session: {session.id} - {session.course_name}")

# Test OTP creation directly
print("\n[TEST 1] Testing OTP model creation...")
try:
    otp = OTP.objects.create(session=session)
    print(f"[OK] OTP created successfully!")
    print(f"     OTP Code: {otp.otp_code}")
    print(f"     Expires at: {otp.expires_at}")
    print(f"     Is valid: {otp.is_valid()}")
except Exception as e:
    print(f"[ERROR] Failed to create OTP: {e}")
    sys.exit(1)

# Test API endpoint
print("\n[TEST 2] Testing OTP generation API...")
factory = APIRequestFactory()

# Create JWT token
refresh = RefreshToken.for_user(faculty_user)
access_token = str(refresh.access_token)

# Create request
request = factory.post(
    '/api/otp/generate/',
    {'session_id': session.id},
    content_type='application/json',
    HTTP_AUTHORIZATION=f'Bearer {access_token}'
)

# Set user on request
request.user = faculty_user

# Call view
view = GenerateOTPView.as_view()
response = view(request)

print(f"     Status Code: {response.status_code}")
if hasattr(response, 'data'):
    response_data = response.data
    if response.status_code == 201:
        print(f"[OK] OTP generated via API!")
        print(f"     OTP Code: {response_data['otp']['otp_code']}")
        print(f"     Expires at: {response_data['otp']['expires_at']}")
    else:
        print(f"[ERROR] API failed: {response_data}")
else:
    print(f"[INFO] Response rendered, status: {response.status_code}")

print("\n" + "=" * 60)
print("[SUCCESS] OTP generation tests completed!")
print("=" * 60)

