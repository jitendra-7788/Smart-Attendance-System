"""
Test script to verify session creation works correctly
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from accounts.models import CustomUser, Faculty
from attendance.models import Session
from django.utils import timezone
from datetime import date, time as time_obj

print("=" * 60)
print("Testing Session Creation")
print("=" * 60)

# Check user roles
print("\n1. Checking user roles...")
faculty_users = CustomUser.objects.filter(role='FACULTY')
print(f"   Found {faculty_users.count()} faculty user(s)")

if faculty_users.count() == 0:
    print("[ERROR] No faculty users found!")
    print("   Please create a faculty user first.")
    sys.exit(1)

for user in faculty_users:
    print(f"   - {user.username} (role: {user.role})")
    try:
        faculty_profile = user.faculty_profile
        print(f"     Faculty profile: EXISTS")
    except Faculty.DoesNotExist:
        print(f"     Faculty profile: MISSING (will be auto-created)")

# Test session creation
print("\n2. Testing session creation...")
test_user = faculty_users.first()
print(f"   Using user: {test_user.username}")

# Ensure faculty profile exists
try:
    faculty = test_user.faculty_profile
except Faculty.DoesNotExist:
    faculty = Faculty.objects.create(user=test_user)
    print(f"   Created faculty profile for {test_user.username}")

# Try to create a session
try:
    session = Session.objects.create(
        faculty=faculty,
        course_name="Test Course - Session Creation",
        session_date=date.today(),
        session_time=time_obj(15, 0),
        otp_enabled=True
    )
    print(f"[OK] Session created successfully!")
    print(f"     Session ID: {session.id}")
    print(f"     Course: {session.course_name}")
    print(f"     Date: {session.session_date}")
    print(f"     Time: {session.session_time}")
    print(f"     Faculty: {session.faculty.user.username}")
except Exception as e:
    print(f"[ERROR] Failed to create session: {e}")
    sys.exit(1)

# Verify the session
print("\n3. Verifying session...")
sessions = Session.objects.filter(faculty=faculty)
print(f"   Total sessions for {test_user.username}: {sessions.count()}")

if sessions.filter(id=session.id).exists():
    print("[OK] Session verified in database")
else:
    print("[ERROR] Session not found in database!")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All tests passed!")
print("=" * 60)

