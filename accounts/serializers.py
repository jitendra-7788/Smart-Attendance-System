from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Faculty, Student


class FacultyRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for faculty registration"""
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label='Confirm Password')
    department = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'department', 'phone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        # Remove password2 and extra fields
        validated_data.pop('password2')
        department = validated_data.pop('department', '')
        phone = validated_data.pop('phone', '')
        
        # Create user
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='FACULTY'
        )
        
        # Create faculty profile
        Faculty.objects.create(user=user, department=department, phone=phone)
        
        return user


class StudentRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for student registration by faculty"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    full_name = serializers.CharField(required=True)
    roll_number = serializers.CharField(required=True)
    photo = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Student
        fields = ['username', 'password', 'full_name', 'roll_number', 'photo']
    
    def validate_roll_number(self, value):
        if Student.objects.filter(roll_number=value).exists():
            raise serializers.ValidationError("A student with this roll number already exists.")
        return value
    
    def create(self, validated_data):
        # Get the faculty from context
        faculty = self.context['faculty']
        
        # Create user
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role='STUDENT'
        )
        
        # Create student profile
        student = Student.objects.create(
            user=user,
            full_name=validated_data['full_name'],
            roll_number=validated_data['roll_number'],
            photo=validated_data.get('photo'),
            registered_by=faculty
        )
        
        return student


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid username or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "username" and "password".')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'role']


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for student details"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'username', 'full_name', 'roll_number', 'photo', 'created_at']
        read_only_fields = ['id', 'created_at']


class FacultySerializer(serializers.ModelSerializer):
    """Serializer for faculty details"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Faculty
        fields = ['id', 'username', 'email', 'department', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']
