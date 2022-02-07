from django.contrib import admin
from .models import User, Application, Club


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username',
                    'email']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'club_name']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'club',
                    'statement']