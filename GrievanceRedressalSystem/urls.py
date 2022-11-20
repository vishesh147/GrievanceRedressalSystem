"""GrievanceRedressal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from re import template
from django.contrib import admin
from django.urls import path, include
import GrievanceRedressalSystemApp.views as views
import AnalyticsApp.views
from django.contrib.auth import views as authViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload', views.Upload),

    path('', views.Landing, name='landing'),
    path('login/<slug:slug>/', views.UserLogin, name="login"),
    path('login/verify/otp/', views.OTPlogin, name='OTPlogin'),
    path('logout/', views.Logout, name='logout'), 
    
    path('analytics/', AnalyticsApp.views.Analytics, name='analytics'),
    path('analytics/<int:year>/', AnalyticsApp.views.Analytics, name='analytics'),
    path('analytics/<int:year>/<str:gType>/', AnalyticsApp.views.Analytics, name='analytics'),
    path('analytics/<int:year>/<str:gType>/<str:category>/', AnalyticsApp.views.Analytics, name='analytics'),

    path('user/', include('UserApp.urls')),
    path('handler/', include('HandlerApp.urls')),
    
    path('change-password/', views.ChangePass, name='changepass'),

    path('reset-password/',
        authViews.PasswordResetView.as_view(template_name='password/reset.html'),
        name="reset_password"),

    path('reset-password-sent/',
        authViews.PasswordResetDoneView.as_view(template_name='password/reset_done.html'),
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
        authViews.PasswordResetConfirmView.as_view(template_name='password/reset_confirm.html'),
        name="password_reset_confirm"),

    path('reset-password-complete/',
        authViews.PasswordResetCompleteView.as_view(template_name='password/reset_complete.html'),
        name="password_reset_complete"),    
    
]
