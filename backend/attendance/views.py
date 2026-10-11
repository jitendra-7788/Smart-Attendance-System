from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.db import IntegrityError
from .models import Session, OTP, Attendance
from accounts.models import Faculty, Student
from .serializers import (
    SessionSerializer,
    OTPSerializer,
    AttendanceSerializer,
    MarkAttendanceSerializer
)


class SessionListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create sessions"""
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'FACULTY':
            # Faculty can see their own sessions
            try:
                faculty = user.faculty_profile
            except Faculty.DoesNotExist:
                # Auto-create faculty profile if it doesn't exist
                faculty = Faculty.objects.create(user=user)
            
            return Session.objects.filter(faculty=faculty)
        else:
            # Students can see all sessions
            return Session.objects.all()
    
    def perform_create(self, serializer):
        # Refresh user from database to ensure role is current
        self.request.user.refresh_from_db()
        
        # Only faculty can create sessions
        if self.request.user.role != 'FACULTY':
            raise PermissionDenied('Only faculty members can create sessions')
        
        try:
            faculty = self.request.user.faculty_profile
        except Faculty.DoesNotExist:
            # Auto-create faculty profile if it doesn't exist
            faculty = Faculty.objects.create(user=self.request.user)
        
        serializer.save(faculty=faculty)
    
    def create(self, request, *args, **kwargs):
        """Override create to provide better error handling"""
        # Ensure user is authenticated via JWT (not session)
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Refresh user from database to ensure role is current from JWT token
        request.user.refresh_from_db()
        
        # Check user role first before attempting creation
        if request.user.role != 'FACULTY':
            return Response(
                {'error': 'Only faculty members can create sessions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            return super().create(request, *args, **kwargs)
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            error_detail = str(e)
            # Extract validation errors if present
            if hasattr(e, 'detail'):
                if isinstance(e.detail, dict):
                    error_detail = '; '.join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in e.detail.items()])
                else:
                    error_detail = str(e.detail)
            return Response(
                {'error': error_detail, 'detail': 'Failed to create session. Please check your input.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class GenerateOTPView(APIView):
    """API endpoint to generate OTP for a session"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Ensure user is authenticated via JWT (not session)
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Refresh user from database to ensure role is current from JWT token
        request.user.refresh_from_db()
        
        # Only faculty can generate OTP
        if request.user.role != 'FACULTY':
            return Response(
                {'error': 'Only faculty members can generate OTP'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session_id = request.data.get('session_id')
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert to int if it's a string
        try:
            session_id = int(session_id)
        except (ValueError, TypeError):
            return Response(
                {'error': 'session_id must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if session belongs to this faculty
        # Check by user instead of faculty object to avoid issues with auto-created profiles
        if session.faculty.user != request.user:
            return Response(
                {'error': 'You do not have permission to generate OTP for this session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create new OTP (regardless of otp_enabled flag - OTP is generated on demand)
        try:
            otp = OTP.objects.create(session=session)
            return Response({
                'message': 'OTP generated successfully',
                'otp': OTPSerializer(otp).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Failed to generate OTP: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetOTPView(generics.RetrieveAPIView):
    """API endpoint to get current valid OTP for a session"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OTPSerializer
    
    def retrieve(self, request, session_id):
        # Only faculty can view OTP
        if request.user.role != 'FACULTY':
            return Response(
                {'error': 'Only faculty members can view OTP'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if session belongs to this faculty
        # Check by user instead of faculty object to avoid issues with auto-created profiles
        if session.faculty.user != request.user:
            return Response(
                {'error': 'You do not have permission to view OTP for this session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the latest valid OTP
        try:
            otp = OTP.objects.filter(session=session).latest('created_at')
            return Response({
                'otp': OTPSerializer(otp).data
            })
        except OTP.DoesNotExist:
            return Response(
                {'error': 'No OTP found for this session'},
                status=status.HTTP_404_NOT_FOUND
            )


class MarkAttendanceView(APIView):
    """API endpoint for students to mark attendance"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Only students can mark attendance
        if request.user.role != 'STUDENT':
            return Response(
                {'error': 'Only students can mark attendance'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MarkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        session = serializer.validated_data['session']
        otp = serializer.validated_data['otp']
        
        # Check if attendance already marked
        if Attendance.objects.filter(student=student, session=session).exists():
            return Response(
                {'error': 'Attendance already marked for this session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark attendance
        try:
            attendance = Attendance.objects.create(
                student=student,
                session=session,
                verified=True,
                otp_used=otp
            )
            
            # Mark OTP as used
            otp.is_used = True
            otp.save()
            
            return Response({
                'message': 'Attendance marked successfully',
                'attendance': AttendanceSerializer(attendance).data
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {'error': 'Attendance already marked for this session'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AttendanceHistoryView(generics.ListAPIView):
    """API endpoint for students to view their attendance history"""
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            try:
                student = user.student_profile
                return Attendance.objects.filter(student=student)
            except Student.DoesNotExist:
                return Attendance.objects.none()
        return Attendance.objects.none()


class SessionAttendanceView(generics.ListAPIView):
    """API endpoint for faculty to view attendance for a specific session"""
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.kwargs.get('session_id')
        user = self.request.user
        
        if user.role != 'FACULTY':
            return Attendance.objects.none()
        
        try:
            faculty = user.faculty_profile
            session = Session.objects.get(id=session_id, faculty=faculty)
            return Attendance.objects.filter(session=session)
        except (Session.DoesNotExist, Faculty.DoesNotExist):
            return Attendance.objects.none()
