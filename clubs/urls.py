"""clubs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from bookclubs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('club/<str:club_name>/feed/', views.club_feed, name='club_feed'),
    path('club/<str:club_name>/', views.club_welcome, name='club_welcome'),
    path('create_club/', views.create_club, name='create_club'),
    path('club/<str:club_name>/delete/', views.delete_club, name = 'delete_club'),
    path('new_application/<str:club_name>/', views.new_application, name='new_application'),
    path('edit_application/<str:club_name>/', views.edit_application, name='edit_application'),
    path('withdraw_application/<str:club_name>/', views.withdraw_application, name='withdraw_application'),
    path('club_list/', views.club_list, name = 'club_list'),
    path('myClubs/', views.myClubs, name='myClubs'),

]
