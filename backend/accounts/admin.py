from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Faculty, Student


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email', 'department']
    list_filter = ['department', 'created_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'roll_number', 'registered_by', 'created_at']
    search_fields = ['full_name', 'roll_number', 'user__username']
    list_filter = ['registered_by', 'created_at']
    readonly_fields = ['created_at']
