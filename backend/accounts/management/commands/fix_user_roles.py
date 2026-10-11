"""
Management command to check and fix user roles in the database
"""
from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Faculty, Student


class Command(BaseCommand):
    help = 'Check and fix user roles in the database'

    def handle(self, *args, **options):
        self.stdout.write('Checking user roles...\n')
        
        # Check all users
        users = CustomUser.objects.all()
        fixed_count = 0
        
        for user in users:
            self.stdout.write(f'User: {user.username} - Current Role: "{user.role}"')
            
            # Check if role is empty or None
            if not user.role or user.role == '':
                # Try to determine role from profile
                if hasattr(user, 'faculty_profile'):
                    self.stdout.write(f'  -> Has Faculty profile, setting role to FACULTY')
                    user.role = 'FACULTY'
                    user.save()
                    fixed_count += 1
                elif hasattr(user, 'student_profile'):
                    self.stdout.write(f'  -> Has Student profile, setting role to STUDENT')
                    user.role = 'STUDENT'
                    user.save()
                    fixed_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'  -> No profile found, skipping'))
            else:
                self.stdout.write(self.style.SUCCESS(f'  -> Role is set correctly'))
        
        self.stdout.write(self.style.SUCCESS(f'\nFixed {fixed_count} user(s)'))
        
        # Summary
        faculty_count = CustomUser.objects.filter(role='FACULTY').count()
        student_count = CustomUser.objects.filter(role='STUDENT').count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  Faculty users: {faculty_count}')
        self.stdout.write(f'  Student users: {student_count}')
