from django.contrib import admin
from .models import Grievance, Grievant, Handler, Update
from import_export import resources
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path

class GrievantAdmin(admin.ModelAdmin):
    list_display = ('user', 'uType', 'program',)
    search_fields = ('user__username',)

admin.site.register(Grievant, GrievantAdmin)

class HandlerAdmin(admin.ModelAdmin):
    list_display = ('user', 'grievantType', 'category', 'level')
    search_fields = ('user__username', 'user__first_name', 'grievantType', 'category', 'level')

admin.site.register(Handler, HandlerAdmin)

admin.site.register(Grievance)
#admin.site.register(Update)