from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
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
                return Session.objects.filter(faculty=faculty)
            except Faculty.DoesNotExist:
                return Session.objects.none()
        else:
            # Students can see all sessions
            return Session.objects.all()
    
    def perform_create(self, serializer):
        # Only faculty can create sessions
        if self.request.user.role != 'FACULTY':
            raise permissions.PermissionDenied('Only faculty members can create sessions')
        
        try:
            faculty = self.request.user.faculty_profile
            serializer.save(faculty=faculty)
        except Faculty.DoesNotExist:
            raise permissions.PermissionDenied('Faculty profile not found')


class GenerateOTPView(APIView):
    """API endpoint to generate OTP for a session"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
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
        
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if session belongs to this faculty
        try:
            faculty = request.user.faculty_profile
            if session.faculty != faculty:
                return Response(
                    {'error': 'You do not have permission to generate OTP for this session'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Faculty.DoesNotExist:
            return Response(
                {'error': 'Faculty profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new OTP
        otp = OTP.objects.create(session=session)
        
        return Response({
            'message': 'OTP generated successfully',
            'otp': OTPSerializer(otp).data
        }, status=status.HTTP_201_CREATED)


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
        try:
            faculty = request.user.faculty_profile
            if session.faculty != faculty:
                return Response(
                    {'error': 'You do not have permission to view OTP for this session'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Faculty.DoesNotExist:
            return Response(
                {'error': 'Faculty profile not found'},
                status=status.HTTP_400_BAD_REQUEST
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
