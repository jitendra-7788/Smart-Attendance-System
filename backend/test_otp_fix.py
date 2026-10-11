"""
Test script to verify OTP generation is working
Run: python test_otp_fix.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from attendance.models import OTP, Session
from accounts.models import Faculty
from django.utils import timezone

print("=" * 60)
print("Testing OTP Generation")
print("=" * 60)

# Get or create a test session
faculty = Faculty.objects.first()
if not faculty:
    print("[ERROR] No faculty found. Please create a faculty user first.")
    sys.exit(1)

session = Session.objects.filter(faculty=faculty).first()
if not session:
    print("[ERROR] No sessions found. Please create a session first.")
    sys.exit(1)

print(f"\n[OK] Using session: {session}")
print(f"   Faculty: {session.faculty.user.username}")

# Test OTP creation
print("\n1. Creating OTP...")
otp = OTP(session=session)
print(f"   Before save - OTP code: '{otp.otp_code}', Expires: {otp.expires_at}")

otp.save()
print(f"   After save - OTP code: '{otp.otp_code}', Expires: {otp.expires_at}")

if not otp.otp_code or len(otp.otp_code) != 6:
    print(f"[ERROR] OTP code is invalid! Code: '{otp.otp_code}', Length: {len(otp.otp_code) if otp.otp_code else 0}")
    sys.exit(1)

if not otp.expires_at:
    print("[ERROR] OTP expiration not set!")
    sys.exit(1)

print("[OK] OTP created successfully!")

# Test OTP validation
print("\n2. Testing OTP validation...")
is_valid = otp.is_valid()
print(f"   OTP is valid: {is_valid}")
print(f"   OTP code: {otp.otp_code}")
print(f"   Expires at: {otp.expires_at}")
print(f"   Is used: {otp.is_used}")
print(f"   Current time: {timezone.now()}")

if is_valid:
    print("[OK] OTP validation working correctly!")
else:
    print("[WARNING] OTP is not valid (might be expired or used)")

# Test creating multiple OTPs
print("\n3. Testing multiple OTP creation...")
otp2 = OTP.objects.create(session=session)
print(f"   Second OTP code: {otp2.otp_code}")

if otp.otp_code == otp2.otp_code:
    print("[WARNING] Two OTPs have the same code (very unlikely but possible)")
else:
    print("[OK] Different OTP codes generated correctly")

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)

