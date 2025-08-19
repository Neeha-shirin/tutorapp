from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('role', 'admin')  
        extra_fields.setdefault('mobile_number', None)  

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False) 
    rejection_reason = models.TextField(blank=True, null=True) 
    reset_password_token = models.CharField(max_length=255, blank=True, null=True)
    reset_password_token_created_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def generate_reset_token(self):
        token = str(uuid.uuid4())
        self.reset_password_token = token
        self.reset_password_token_created_at = timezone.now()
        self.save()
        return token

    def clear_reset_token(self):
        self.reset_password_token = None
        self.reset_password_token_created_at = None
        self.save()


class TutorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')
    full_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='tutors/', blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=200)
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField()
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    subjects = models.TextField(help_text="Comma-separated subjects")
    description = models.TextField()
    available_days = models.CharField(max_length=200)

    def __str__(self):
        return self.full_name


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    full_name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='students/', blank=True, null=True)
    class_name = models.CharField(max_length=50)
    required_subjects = models.TextField(help_text="Comma-separated subjects")
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.full_name
