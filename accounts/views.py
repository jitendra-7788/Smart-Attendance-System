from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser, Faculty, Student
from .serializers import (
    FacultyRegistrationSerializer,
    StudentRegistrationSerializer,
    LoginSerializer,
    UserSerializer,
    StudentSerializer,
    FacultySerializer
)


class FacultyRegistrationView(generics.CreateAPIView):
    """API endpoint for faculty registration"""
    serializer_class = FacultyRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Faculty registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class StudentRegistrationView(generics.CreateAPIView):
    """API endpoint for student registration (faculty only)"""
    serializer_class = StudentRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Check if user is faculty
        if request.user.role != 'FACULTY':
            return Response(
                {'error': 'Only faculty members can register students'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get faculty profile
        try:
            faculty = request.user.faculty_profile
        except Faculty.DoesNotExist:
            return Response(
                {'error': 'Faculty profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data, context={'faculty': faculty})
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        
        return Response({
            'message': 'Student registered successfully',
            'student': StudentSerializer(student).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """API endpoint for user login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Get user profile data
        profile_data = {}
        if user.role == 'FACULTY':
            try:
                profile_data = FacultySerializer(user.faculty_profile).data
            except Faculty.DoesNotExist:
                pass
        elif user.role == 'STUDENT':
            try:
                profile_data = StudentSerializer(user.student_profile).data
            except Student.DoesNotExist:
                pass
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'profile': profile_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class FacultyLoginView(APIView):
    """API endpoint for faculty login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Check if user is faculty
        if user.role != 'FACULTY':
            return Response(
                {'non_field_errors': ['Invalid credentials for faculty login.']},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Get faculty profile data
        profile_data = {}
        try:
            profile_data = FacultySerializer(user.faculty_profile).data
        except Faculty.DoesNotExist:
            pass
        
        return Response({
            'message': 'Faculty login successful',
            'user': UserSerializer(user).data,
            'profile': profile_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class StudentLoginView(APIView):
    """API endpoint for student login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Check if user is student
        if user.role != 'STUDENT':
            return Response(
                {'non_field_errors': ['Invalid credentials for student login.']},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Get student profile data
        profile_data = {}
        try:
            profile_data = StudentSerializer(user.student_profile).data
        except Student.DoesNotExist:
            pass
        
        return Response({
            'message': 'Student login successful',
            'user': UserSerializer(user).data,
            'profile': profile_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    """API endpoint to get current user profile"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        user_data = UserSerializer(user).data
        
        # Get profile data based on role
        profile_data = {}
        if user.role == 'FACULTY':
            try:
                profile_data = FacultySerializer(user.faculty_profile).data
            except Faculty.DoesNotExist:
                pass
        elif user.role == 'STUDENT':
            try:
                profile_data = StudentSerializer(user.student_profile).data
            except Student.DoesNotExist:
                pass
        
        return Response({
            'user': user_data,
            'profile': profile_data
        })
