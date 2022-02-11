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
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('user/<str:username>/', views.show_user, name='show_user'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('book_list/', views.BookListView.as_view(), name='book_list'),
    path('show_book/<str:ISBN>/', views.ShowBookView.as_view(), name='show_book'),
    path('create_book_rating/<str:ISBN>/', views.CreateBookRateView.as_view(), name='create_book_rating'),
    path('club/<str:club_name>/feed/', views.club_feed, name='club_feed'),
    path('club/<str:club_name>/', views.club_welcome, name='club_welcome'),
    path('create_club/', views.create_club, name='create_club'),
    path('club/<str:club_name>/delete/', views.delete_club, name='delete_club'),
    path('club/<str:club_name>/apply/', views.new_application, name='new_application'),
    path('club/<str:club_name>/edit_application/', views.edit_application, name='edit_application'),
    path('club/<str:club_name>/withdraw_application/', views.withdraw_application, name='withdraw_application'),
    path('my_applications/', views.my_applications, name='my_applications'),
    path('club/<str:club_name>/applications/', views.application_list, name='application_list'),
    path('club/<str:club_name>/accept/<int:user_id>/', views.accept_applicant, name='accept_applicant'),
    path('club/<str:club_name>/reject/<int:user_id>/', views.reject_applicant, name='reject_applicant'),
    path('club_list/', views.club_list, name='club_list'),
    path('my_clubs/', views.my_clubs, name='my_clubs'),
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('create_post/', views.CreatePostView.as_view(), name='create_post'),
    path('article/delete/<int:pk>', views.DeletePostView.as_view(), name='delete_post'),
    path('create_comment/<int:pk>', views.CreateCommentView.as_view(), name='create_comment'),
    path('delete_comment/<int:pk>', views.DeleteCommentView.as_view(), name='delete_comment'),
]
