from rest_framework import serializers
from .models import Session, OTP, Attendance
from accounts.models import Student


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for session"""
    faculty_name = serializers.CharField(source='faculty.user.get_full_name', read_only=True)
    
    class Meta:
        model = Session
        fields = ['id', 'course_name', 'session_date', 'session_time', 'otp_enabled', 
                  'faculty_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'faculty_name']


class OTPSerializer(serializers.ModelSerializer):
    """Serializer for OTP"""
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = OTP
        fields = ['id', 'otp_code', 'created_at', 'expires_at', 'is_used', 'is_valid']
        read_only_fields = ['id', 'otp_code', 'created_at', 'expires_at']
    
    def get_is_valid(self, obj):
        return obj.is_valid()


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for attendance"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    course_name = serializers.CharField(source='session.course_name', read_only=True)
    session_date = serializers.DateField(source='session.session_date', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'student_name', 'roll_number', 'course_name', 'session_date', 
                  'marked_at', 'verified']
        read_only_fields = ['id', 'marked_at']


class MarkAttendanceSerializer(serializers.Serializer):
    """Serializer for marking attendance with OTP"""
    session_id = serializers.IntegerField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6, min_length=6)
    
    def validate(self, attrs):
        session_id = attrs.get('session_id')
        otp_code = attrs.get('otp_code')
        
        # Check if session exists
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            raise serializers.ValidationError({"session_id": "Session not found."})
        
        # Check if OTP is valid
        try:
            otp = OTP.objects.filter(session=session, otp_code=otp_code).latest('created_at')
            if not otp.is_valid():
                raise serializers.ValidationError({"otp_code": "OTP has expired or already been used."})
        except OTP.DoesNotExist:
            raise serializers.ValidationError({"otp_code": "Invalid OTP code."})
        
        attrs['session'] = session
        attrs['otp'] = otp
        return attrs
