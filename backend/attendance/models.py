from django.db import models
from django.utils import timezone
from accounts.models import Faculty, Student
import secrets
from datetime import timedelta


class Session(models.Model):
    """Session model for attendance tracking"""
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='sessions')
    course_name = models.CharField(max_length=200)
    session_date = models.DateField()
    session_time = models.TimeField()
    otp_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['-session_date', '-session_time']
    
    def __str__(self):
        return f"{self.course_name} - {self.session_date} {self.session_time}"


class OTP(models.Model):
    """OTP model for attendance verification"""
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Always generate OTP code if not set
        if not self.otp_code:
            # Generate 6-digit OTP (ensuring it's always 6 digits, padding with zeros if needed)
            self.otp_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Always set expiration if not set
        if not self.expires_at:
            # Set expiration to 30 seconds from now
            self.expires_at = timezone.now() + timedelta(seconds=30)
        
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and timezone.now() <= self.expires_at
    
    def __str__(self):
        return f"OTP {self.otp_code} for {self.session.course_name}"


class Attendance(models.Model):
    """Attendance record model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendances')
    marked_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    otp_used = models.ForeignKey(OTP, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendances')
    
    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        ordering = ['-marked_at']
        unique_together = ['student', 'session']  # Prevent duplicate attendance
    
    def __str__(self):
        return f"{self.student.full_name} - {self.session.course_name} - {self.marked_at.strftime('%Y-%m-%d %H:%M')}"
