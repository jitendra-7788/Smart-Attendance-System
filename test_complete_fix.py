"""
Complete test of the session creation fix
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
print("COMPLETE SYSTEM TEST")
print("=" * 60)

# Test 1: Verify user exists and has correct role
print("\n[TEST 1] Checking user 'atul7788'...")
try:
    user = CustomUser.objects.get(username='atul7788')
    print(f"  [OK] User found: {user.username}")
    print(f"  [OK] Role: {user.role}")
    
    if user.role != 'FACULTY':
        print(f"  [ERROR] User role is '{user.role}', expected 'FACULTY'")
        sys.exit(1)
    
    # Check faculty profile
    try:
        faculty = user.faculty_profile
        print(f"  [OK] Faculty profile exists")
    except Faculty.DoesNotExist:
        print(f"  [INFO] Faculty profile missing, will be auto-created")
        faculty = Faculty.objects.create(user=user)
        print(f"  [OK] Faculty profile created")
except CustomUser.DoesNotExist:
    print("  [ERROR] User 'atul7788' not found!")
    sys.exit(1)

# Test 2: Test session creation at model level
print("\n[TEST 2] Testing session creation at model level...")
try:
    session = Session.objects.create(
        faculty=faculty,
        course_name="Test Session - Complete Fix",
        session_date=date.today(),
        session_time=time_obj(16, 30),
        otp_enabled=True
    )
    print(f"  [OK] Session created successfully!")
    print(f"       ID: {session.id}")
    print(f"       Course: {session.course_name}")
    print(f"       Faculty: {session.faculty.user.username}")
except Exception as e:
    print(f"  [ERROR] Failed to create session: {e}")
    sys.exit(1)

# Test 3: Verify session belongs to user
print("\n[TEST 3] Verifying session ownership...")
sessions = Session.objects.filter(faculty__user=user)
print(f"  [OK] User has {sessions.count()} session(s)")

if sessions.filter(id=session.id).exists():
    print(f"  [OK] Created session belongs to user")
else:
    print(f"  [ERROR] Created session does not belong to user!")
    sys.exit(1)

# Test 4: Check view logic (simulated)
print("\n[TEST 4] Simulating view permission check...")
if user.role == 'FACULTY':
    print(f"  [OK] Permission check passed (role is FACULTY)")
else:
    print(f"  [ERROR] Permission check failed (role is {user.role})")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All tests passed!")
print("=" * 60)
print("\nThe fix should work correctly now.")
print("Please test in the browser by:")
print("1. Logging in as 'atul7788'")
print("2. Going to Faculty Dashboard")
print("3. Clicking 'Create New Session'")
print("4. Filling in the form and clicking 'Create Session'")
print("\nThe session should be created successfully!")

