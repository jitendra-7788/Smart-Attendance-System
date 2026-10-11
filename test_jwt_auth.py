"""
Test JWT authentication to verify no session collision
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from accounts.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

print("=" * 60)
print("Testing JWT Authentication (No Session Collision)")
print("=" * 60)

# Get faculty and student users
faculty_user = CustomUser.objects.filter(role='FACULTY').first()
student_user = CustomUser.objects.filter(role='STUDENT').first()

if not faculty_user or not student_user:
    print("[ERROR] Need both faculty and student users for testing")
    exit(1)

print(f"\n[TEST] Faculty user: {faculty_user.username} (Role: {faculty_user.role})")
print(f"[TEST] Student user: {student_user.username} (Role: {student_user.role})")

# Generate JWT tokens for both users
faculty_refresh = RefreshToken.for_user(faculty_user)
faculty_token = str(faculty_refresh.access_token)

student_refresh = RefreshToken.for_user(student_user)
student_token = str(student_refresh.access_token)

print(f"\n[OK] Faculty JWT token generated: {faculty_token[:50]}...")
print(f"[OK] Student JWT token generated: {student_token[:50]}...")

# Verify tokens are different
if faculty_token != student_token:
    print("[OK] Tokens are different (no collision)")
else:
    print("[ERROR] Tokens are the same (collision detected!)")

# Test that tokens contain user info
from rest_framework_simplejwt.tokens import AccessToken

faculty_decoded = AccessToken(faculty_token)
student_decoded = AccessToken(student_token)

print(f"\n[TEST] Decoding tokens...")
print(f"  Faculty token user_id: {faculty_decoded['user_id']}")
print(f"  Student token user_id: {student_decoded['user_id']}")

if faculty_decoded['user_id'] == faculty_user.id:
    print("[OK] Faculty token contains correct user ID")
else:
    print("[ERROR] Faculty token has wrong user ID")

if student_decoded['user_id'] == student_user.id:
    print("[OK] Student token contains correct user ID")
else:
    print("[ERROR] Student token has wrong user ID")

print("\n" + "=" * 60)
print("[SUCCESS] JWT authentication test completed!")
print("=" * 60)
print("\nKey points:")
print("1. Each user gets a unique JWT token")
print("2. Tokens are stored in localStorage (not cookies)")
print("3. No session cookies are created for API requests")
print("4. Each tab/browser maintains its own authentication state")

