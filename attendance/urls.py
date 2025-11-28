from django.urls import path
from .views import (
    SessionListCreateView,
    GenerateOTPView,
    GetOTPView,
    MarkAttendanceView,
    AttendanceHistoryView,
    SessionAttendanceView
)

urlpatterns = [
    # Session management
    path('sessions/', SessionListCreateView.as_view(), name='session-list-create'),
    
    # OTP management
    path('otp/generate/', GenerateOTPView.as_view(), name='generate-otp'),
    path('otp/<int:session_id>/', GetOTPView.as_view(), name='get-otp'),
    
    # Attendance
    path('attendance/mark/', MarkAttendanceView.as_view(), name='mark-attendance'),
    path('attendance/history/', AttendanceHistoryView.as_view(), name='attendance-history'),
    path('attendance/session/<int:session_id>/', SessionAttendanceView.as_view(), name='session-attendance'),
]
