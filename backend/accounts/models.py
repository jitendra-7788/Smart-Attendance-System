from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model with role-based authentication"""
    ROLE_CHOICES = (
        ('FACULTY', 'Faculty'),
        ('STUDENT', 'Student'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Faculty(models.Model):
    """Faculty profile model"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='faculty_profile')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.department}"


class Student(models.Model):
    """Student profile model"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=200)
    roll_number = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    registered_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='registered_students')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['roll_number']
    
    def __str__(self):
        return f"{self.full_name} ({self.roll_number})"
