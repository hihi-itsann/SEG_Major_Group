from django.contrib import admin
from .models import User, Application, Club, Role, Book, Rating, BookStatus, Comment, Meeting


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username',
                    'email']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'club_name']


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
        'ISBN', 'title', 'author', 'year_of_publication', 'publisher', 'image_url_s', 'image_url_m', 'image_url_l'
    ]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = [
        'rate', 'book', 'user'
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


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['club',
                    'topic'
                    ]
