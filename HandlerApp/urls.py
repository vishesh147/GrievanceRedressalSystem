from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard/', views.Dashboard, name='handlerDashboard'),
    path('grievances/<slug:gID>', views.ViewGrievance, name='handleGrievance'),
    path('grievances/<slug:gID>/reject', views.Reject, name='reject'),
    path('grievances/<slug:gID>/solve', views.Solve, name='solve'),
    path('grievances/<slug:gID>/escalate', views.Escalate, name='escalate'),
]
