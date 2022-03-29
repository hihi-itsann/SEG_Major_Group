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

    # General Views
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('user/<str:username>/', views.show_user, name='show_user'),

    # Book Views
    path('book_list/<str:book_genre>/', views.BookListView.as_view(), name='book_list'),
    path('book/<str:ISBN>/', views.ShowBookView.as_view(), name='show_book'),
    path('create_book_rating_review/<str:ISBN>/', views.CreateBookRateReviewView.as_view(), name='create_book_rating_review'),
    path('delete_book_rating_review/<str:ISBN>/<int:pk>/', views.delete_book_rating_review, name='delete_book_rating_review'),
    path('create_book_status/<str:ISBN>/', views.create_book_status, name='create_book_status'),
    path('delete_book_status/<str:ISBN>/', views.delete_book_status, name='delete_book_status'),
    path('change_book_status/<str:ISBN>/<str:choice>/', views.change_book_status, name='change_book_status'),
    path('reading_book_list/<str:book_genre>/', views.reading_book_list, name='reading_book_list'),

    # Club Views
    path('my_clubs/', views.my_clubs, name='my_clubs'),
    path('club_list/', views.club_list, name='club_list'),
    path('create_club/', views.create_club, name='create_club'),
    path('club/<str:club_name>/feed/', views.club_feed, name='club_feed'),
    path('club/<str:club_name>/leave_club/', views.leave_club, name='leave_club'),
    path('club/<str:club_name>/update_club_info/', views.update_club_info, name='update_club_info'),
    path('club/<str:club_name>/transfer_ownership/<int:user_id>/', views.transfer_ownership, name='transfer_ownership'),
    path('club/<str:club_name>/delete/', views.delete_club, name='delete_club'),
    path('club/<str:club_name>/promote/<int:user_id>/', views.promote_member, name='promote_member'),
    path('club/<str:club_name>/demote/<int:user_id>/', views.demote_moderator, name='demote_moderator'),
    path('club/<str:club_name>/remove/<int:user_id>/', views.remove_member, name='remove_from_club'),
    path('club/<str:club_name>/ban/<int:user_id>/', views.ban_member, name='ban_from_club'),
    path('club/<str:club_name>/unban/<int:user_id>/', views.unban_member, name='unban_from_club'),
    path('club/<str:club_name>/member_list/', views.member_list, name='member_list'),


    # Application Views
    path('my_applications/', views.my_applications, name='my_applications'),
    path('club/<str:club_name>/apply/', views.create_application, name='create_application'),
    path('club/<str:club_name>/edit_application/', views.edit_application, name='edit_application'),
    path('club/<str:club_name>/withdraw_application/', views.withdraw_application, name='withdraw_application'),
    path('club/<str:club_name>/applications/', views.application_list, name='application_list'),
    path('club/<str:club_name>/accept/<int:user_id>/', views.accept_applicant, name='accept_applicant'),
    path('club/<str:club_name>/reject/<int:user_id>/', views.reject_applicant, name='reject_applicant'),

    # Post Comment Views
    path('create_post/<int:pk>/', views.CreatePostView.as_view(), name='create_post'),
    path('delete_post/<int:pk>/', views.DeletePostView.as_view(), name='delete_post'),
    path('upvote/<post_id>/', views.post_upvote, name='post_upvote'),
    path('downvote/<post_id>/', views.post_downvote, name='post_downvote'),
    path('create_comment/<int:pk>/', views.CreateCommentView.as_view(), name='create_comment'),
    path('delete_comment/<int:pk>/', views.DeleteCommentView.as_view(), name='delete_comment'),

    # Meeting Views
    path('club/<str:club_name>/meeting/show_books/', views.show_book_recommendations, name='show_book_recommendations'),
    path('club/<str:club_name>/meeting/show_books/show', views.show_book_recommendations_show, name='show_book_recommendations_show'),
    path('club/<str:club_name>/meeting/book/<str:book_isbn>/create/', views.create_meeting, name='create_meeting'),
    path('club/<str:club_name>/meeting_list/', views.meeting_list, name='meeting_list'),
    path('club/<str:club_name>/meeting/<int:meeting_id>/', views.show_meeting, name='show_meeting'),
    path('club/<str:club_name>/meeting/<int:meeting_id>/join/', views.join_meeting, name='join_meeting'),
    path('club/<str:club_name>/meeting/<int:meeting_id>/leave/', views.leave_meeting, name='leave_meeting'),
    path('club/<str:club_name>/meeting/<int:meeting_id>/delete/', views.delete_meeting, name='delete_meeting'),
    path('club/<str:club_name>/meeting/<int:meeting_id>/edit/', views.edit_meeting, name='edit_meeting'),
    

    

]
