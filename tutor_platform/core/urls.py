from django.urls import path
from .views import *

urlpatterns = [
    path('register/student/', StudentRegisterView.as_view()),
    path('register/tutor/', TutorRegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('admin/review-user/<int:pk>/', ReviewUserView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),

]
