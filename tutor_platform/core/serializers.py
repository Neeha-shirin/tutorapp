from rest_framework import serializers
from django.contrib.auth import authenticate
from core.models import User, TutorProfile, StudentProfile

class StudentRegistrationSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    class_name = serializers.CharField(write_only=True)
    required_subjects = serializers.CharField(write_only=True)
    location = serializers.CharField(write_only=True)
    profile_photo = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'mobile_number', 'password', 'full_name', 'class_name', 'required_subjects', 'location', 'profile_photo']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        class_name = validated_data.pop('class_name')
        required_subjects = validated_data.pop('required_subjects')
        location = validated_data.pop('location')
        profile_photo = validated_data.pop('profile_photo', None)

        user = User.objects.create_user(role='student', **validated_data)
        StudentProfile.objects.create(
            user=user,
            full_name=full_name,
            class_name=class_name,
            required_subjects=required_subjects,
            location=location,
            profile_photo=profile_photo
        )
        return user


class TutorRegistrationSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    gender = serializers.CharField(write_only=True, required=False)
    location = serializers.CharField(write_only=True)
    qualification = serializers.CharField(write_only=True)
    experience_years = serializers.IntegerField(write_only=True)
    hourly_rate = serializers.DecimalField(max_digits=6, decimal_places=2, write_only=True)
    subjects = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    available_days = serializers.CharField(write_only=True)
    profile_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'mobile_number', 'password', 'full_name', 'gender', 'location', 'qualification', 'experience_years', 'hourly_rate', 'subjects', 'description', 'available_days', 'profile_image']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        gender = validated_data.pop('gender', '')
        location = validated_data.pop('location')
        qualification = validated_data.pop('qualification')
        experience_years = validated_data.pop('experience_years')
        hourly_rate = validated_data.pop('hourly_rate')
        subjects = validated_data.pop('subjects')
        description = validated_data.pop('description')
        available_days = validated_data.pop('available_days')
        profile_image = validated_data.pop('profile_image', None)

        user = User.objects.create_user(role='tutor', **validated_data)
        TutorProfile.objects.create(
            user=user,
            full_name=full_name,
            gender=gender,
            location=location,
            qualification=qualification,
            experience_years=experience_years,
            hourly_rate=hourly_rate,
            subjects=subjects,
            description=description,
            available_days=available_days,
            profile_image=profile_image
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if user.is_rejected:
            raise serializers.ValidationError(f"Account rejected: {user.rejection_reason or 'No reason provided'}")

        if not user.is_approved:
            raise serializers.ValidationError("Account not approved by admin yet")

        attrs['user'] = user
        return attrs

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email")
        self.context['user'] = user
        return value


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        token = attrs.get('token')
        try:
            user = User.objects.get(reset_password_token=token)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token")
        self.context['user'] = user
        return attrs

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.clear_reset_token()
        user.save()
        return user

class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    mobile_number = serializers.CharField(source='user.mobile_number')
    is_approved = serializers.BooleanField(source='user.is_approved')
    is_rejected = serializers.BooleanField(source='user.is_rejected')
    role = serializers.CharField(source='user.role')

    class Meta:
        model = StudentProfile
        fields = ['email', 'mobile_number', 'full_name', 'class_name', 'required_subjects', 'location', 'is_approved', 'is_rejected', 'role']


class TutorProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    mobile_number = serializers.CharField(source='user.mobile_number')
    is_approved = serializers.BooleanField(source='user.is_approved')
    is_rejected = serializers.BooleanField(source='user.is_rejected')
    role = serializers.CharField(source='user.role')

    class Meta:
        model = TutorProfile
        fields = ['email', 'mobile_number', 'full_name', 'gender', 'location', 'qualification', 'experience_years', 'hourly_rate', 'subjects', 'description', 'available_days', 'is_approved', 'is_rejected', 'role']
