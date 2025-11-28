from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    FacultyRegistrationView,
    StudentRegistrationView,
    LoginView,
    FacultyLoginView,
    StudentLoginView,
    UserProfileView
)

urlpatterns = [
    # Authentication
    path('register/faculty/', FacultyRegistrationView.as_view(), name='faculty-register'),
    path('register/student/', StudentRegistrationView.as_view(), name='student-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login/faculty/', FacultyLoginView.as_view(), name='faculty-login'),
    path('login/student/', StudentLoginView.as_view(), name='student-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
