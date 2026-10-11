import sqlite3
import os

# Connect to the database
db_path = 'db.sqlite3'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("CHECKING USER ROLES IN DATABASE")
print("=" * 60)

# Get all users
cursor.execute("""
    SELECT id, username, email, role, is_superuser, is_staff
    FROM accounts_customuser
""")

users = cursor.fetchall()

print(f"\nFound {len(users)} users:\n")

for user_id, username, email, role, is_superuser, is_staff in users:
    print(f"ID: {user_id}")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Role: '{role}' (empty={role == '' or role is None})")
    print(f"  Superuser: {bool(is_superuser)}")
    print(f"  Staff: {bool(is_staff)}")
    
    # Check for faculty profile
    cursor.execute("SELECT id FROM accounts_faculty WHERE user_id = ?", (user_id,))
    faculty = cursor.fetchone()
    
    # Check for student profile
    cursor.execute("SELECT id FROM accounts_student WHERE user_id = ?", (user_id,))
    student = cursor.fetchone()
    
    if faculty:
        print(f"  Has Faculty Profile: YES")
        if not role or role == '':
            print(f"  -> FIXING: Setting role to 'FACULTY'")
            cursor.execute("UPDATE accounts_customuser SET role = 'FACULTY' WHERE id = ?", (user_id,))
    
    if student:
        print(f"  Has Student Profile: YES")
        if not role or role == '':
            print(f"  -> FIXING: Setting role to 'STUDENT'")
            cursor.execute("UPDATE accounts_customuser SET role = 'STUDENT' WHERE id = ?", (user_id,))
    
    print()

# Commit changes
conn.commit()

# Show summary
print("=" * 60)
print("SUMMARY AFTER FIX")
print("=" * 60)

cursor.execute("SELECT role, COUNT(*) FROM accounts_customuser GROUP BY role")
summary = cursor.fetchall()

for role, count in summary:
    print(f"Role '{role}': {count} user(s)")

conn.close()

print("\nDone! Please restart your Django server for changes to take effect.")
