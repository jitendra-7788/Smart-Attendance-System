from django.contrib import admin
from .models import Session, OTP, Attendance


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['course_name', 'faculty', 'session_date', 'session_time', 'otp_enabled', 'created_at']
    list_filter = ['otp_enabled', 'session_date', 'faculty']
    search_fields = ['course_name', 'faculty__user__username']
    date_hierarchy = 'session_date'


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['otp_code', 'session', 'created_at', 'expires_at', 'is_used', 'is_valid']
    list_filter = ['is_used', 'created_at']
    search_fields = ['otp_code', 'session__course_name']
    readonly_fields = ['created_at', 'expires_at']
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'marked_at', 'verified']
    list_filter = ['verified', 'marked_at', 'session']
    search_fields = ['student__full_name', 'student__roll_number', 'session__course_name']
    date_hierarchy = 'marked_at'
    readonly_fields = ['marked_at']
