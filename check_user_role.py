"""
Check user role and test session creation via API
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from accounts.models import CustomUser

print("=" * 60)
print("Checking User Roles")
print("=" * 60)

# Find user with 'atul' in username
users = CustomUser.objects.filter(username__icontains='atul')
print(f"\nFound {users.count()} user(s) with 'atul' in username:")

for user in users:
    print(f"\n  Username: {user.username}")
    print(f"  Role: {user.role}")
    print(f"  Email: {user.email}")
    print(f"  Is Faculty: {user.role == 'FACULTY'}")
    print(f"  Is Student: {user.role == 'STUDENT'}")

# Check all faculty users
print("\n" + "=" * 60)
print("All Faculty Users:")
print("=" * 60)
faculty_users = CustomUser.objects.filter(role='FACULTY')
for user in faculty_users:
    print(f"  - {user.username}")

