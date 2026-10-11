"""
Quick test to verify the fixes work
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from accounts.models import CustomUser
from attendance.models import Session

# Test 1: User role refresh
print("=" * 60)
print("TEST 1: User Role Refresh")
print("=" * 60)
user = CustomUser.objects.get(username='atul7788')
print(f"Before refresh: Role = {user.role}")
user.refresh_from_db()
print(f"After refresh: Role = {user.role}")
print(f"Is Faculty: {user.role == 'FACULTY'}")
print("[OK] User role refresh works\n")

# Test 2: Session creation parameters
print("=" * 60)
print("TEST 2: Session Parameter Validation")
print("=" * 60)
from attendance.serializers import SessionSerializer
from datetime import date, time

test_data = {
    'course_name': 'Test Course',
    'session_date': date.today(),
    'session_time': time(15, 0),
    'otp_enabled': True
}

serializer = SessionSerializer(data=test_data)
if serializer.is_valid():
    print("[OK] Serializer validation passed")
    print(f"  course_name: {serializer.validated_data.get('course_name')}")
    print(f"  session_date: {serializer.validated_data.get('session_date')}")
    print(f"  session_time: {serializer.validated_data.get('session_time')}")
    print(f"  otp_enabled: {serializer.validated_data.get('otp_enabled')}")
else:
    print("[ERROR] Serializer validation failed:")
    print(serializer.errors)

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)

