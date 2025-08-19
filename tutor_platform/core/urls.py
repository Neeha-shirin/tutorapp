from django.urls import path
from .views import *

urlpatterns = [
    path('register/student/', StudentRegisterView.as_view()),
    path('register/tutor/', TutorRegisterView.as_view()),

    #api for login for both student and tutors
    path('login/', LoginView.as_view()),
    
    #api for admin approval
    path('admin/review-user/<int:pk>/', ReviewUserView.as_view()),

    #api for reset password
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),


    #listing all list approved and rejected
    path('admin/students/', AdminStudentListView.as_view()),
    path('admin/tutors/', AdminTutorListView.as_view()),

    #seperate list for approval and rejection 
    path('admin/students/approved/', ApprovedStudentsListView.as_view()),
    path('admin/students/rejected/', RejectedStudentsListView.as_view()),
    path('admin/tutors/approved/', ApprovedTutorsListView.as_view()),
    path('admin/tutors/rejected/', RejectedTutorsListView.as_view()),

    #tutor and student dashboard views 
     path('tutor/dashboard/students/', TutorDashboardStudentsView.as_view()),
     path('student/dashboard/tutors/', StudentDashboardTutorsView.as_view()),

]
