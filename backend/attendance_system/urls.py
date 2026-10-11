"""
URL configuration for attendance_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('attendance.urls')),
    
    # Frontend Pages
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('index.html', TemplateView.as_view(template_name='index.html')),
    path('login.html', TemplateView.as_view(template_name='login.html'), name='login'),
    path('login-faculty.html', TemplateView.as_view(template_name='login-faculty.html'), name='login-faculty'),
    path('login-student.html', TemplateView.as_view(template_name='login-student.html'), name='login-student'),
    path('register-faculty.html', TemplateView.as_view(template_name='register-faculty.html'), name='register-faculty'),
    path('register-student.html', TemplateView.as_view(template_name='register-student.html'), name='register-student'),
    path('faculty-dashboard.html', TemplateView.as_view(template_name='faculty-dashboard.html'), name='faculty-dashboard'),
    path('student-dashboard.html', TemplateView.as_view(template_name='student-dashboard.html'), name='student-dashboard'),
    path('generate-otp.html', TemplateView.as_view(template_name='generate-otp.html'), name='generate-otp'),
    path('mark-attendance.html', TemplateView.as_view(template_name='mark-attendance.html'), name='mark-attendance'),
    path('view-attendance.html', TemplateView.as_view(template_name='view-attendance.html'), name='view-attendance'),
    path('view-students.html', TemplateView.as_view(template_name='view-students.html'), name='view-students'),
    path('attendance-history.html', TemplateView.as_view(template_name='attendance-history.html'), name='attendance-history'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

