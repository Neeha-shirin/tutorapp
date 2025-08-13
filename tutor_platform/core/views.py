from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.authtoken.models import Token
from .serializers import *
from core.models import User


class StudentRegisterView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer
    permission_classes = [AllowAny]  # ✅ Public endpoint

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Student registered successfully. Awaiting admin approval.",
            "token": token.key,
            "role": user.role,
            "is_approved": user.is_approved
        }, status=status.HTTP_201_CREATED)


class TutorRegisterView(generics.CreateAPIView):
    serializer_class = TutorRegistrationSerializer
    permission_classes = [AllowAny]  # ✅ Public endpoint

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Tutor registered successfully. Awaiting admin approval.",
            "token": token.key,
            "role": user.role,
            "is_approved": user.is_approved
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]  # ✅ Public endpoint

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # ❌ Block unapproved users from logging in
        if not user.is_approved:
            return Response(
                {"detail": "Your account is awaiting admin approval."},
                status=status.HTTP_403_FORBIDDEN
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'role': user.role,
            'is_approved': user.is_approved
        })


class ReviewUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        action = request.data.get('action', '').lower()

        if action == 'approve':
            user.is_approved = True
            user.is_rejected = False
            user.rejection_reason = ''
            msg = f"{user.email} approved successfully"

        elif action == 'reject':
            user.is_approved = False
            user.is_rejected = True
            user.rejection_reason = request.data.get('reason', 'No reason provided')
            msg = f"{user.email} rejected successfully"

        else:
            return Response({"error": "Invalid action. Use 'approve' or 'reject'."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.save()
        return Response({
            "message": msg,
            "is_approved": user.is_approved,
            "is_rejected": user.is_rejected,
            "rejection_reason": user.rejection_reason
        })

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.context['user']
        token = user.generate_reset_token()

        # For now, return token in response (testing only)
        return Response({"message": "Password reset token generated", "reset_token": token})


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully"})
