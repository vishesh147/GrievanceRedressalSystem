from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.Dashboard, name='userDashboard'),
    path('file-grievance/', views.FileGrievance, name='fileGrievance'),
    path('grievance/<slug:gID>', views.ViewGrievance, name='grievance')
]
