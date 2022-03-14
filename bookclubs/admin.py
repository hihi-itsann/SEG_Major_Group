from django.contrib import admin
from .models import User, Application, Club, Role, Book, BookRatingReview, BookStatus, Comment, Post, Meeting


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['userID','username',
                    'email','meeting_preference','location','country','city']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['club_name', 'id','meeting_status','location','country','city']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'club',
                    'club_role']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'user',
                    'club',
                    'statement']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'ISBN', 'title', 'genre','author', 'year_of_publication', 'publisher', 'image_url_s', 'image_url_m', 'image_url_l'
    ]


@admin.register(BookRatingReview)
class BookRatingReviewAdmin(admin.ModelAdmin):
    list_display = [
        'rate', 'book', 'user', 'review', 'created_at'
    ]

@admin.register(BookStatus)
class BookStatusAdmin(admin.ModelAdmin):
    list_display = [
        'status', 'book', 'user'
    ]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'author', 'body', 'created_at', 'related_post'
    ]

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'body', 'post_date', 'post_datetime'
    ]

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = [
        'club', 'book', 'topic', 'description', 'meeting_status', 'location', 'date', 'time_start', 'time_end'
    ]
