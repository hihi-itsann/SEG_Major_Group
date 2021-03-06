from django.contrib import admin

from .models import User, Application, Club, Role, Book, BookRatingReview, BookStatus, Vote, Comment, Post, Meeting, \
    MeetingAttendance, ClubBookAverageRating


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['userID', 'username', 'email', 'meeting_preference',
                    'location', 'country', 'city', 'userID']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['club_name', 'id', 'public_status', 'meeting_status',
                    'location', 'country', 'city']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'club', 'club_role']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'club', 'statement']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'ISBN', 'title', 'genre', 'author', 'year_of_publication', 'publisher',
        'image_url_s', 'image_url_m', 'image_url_l'
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


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'post'
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'author', 'body', 'created_at', 'related_post'
    ]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'club', 'body', 'post_date', 'post_datetime'
    ]


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'club', 'book', 'topic', 'description', 'meeting_status',
        'location', 'date', 'time_start', 'duration', 'join_link'
    ]


@admin.register(MeetingAttendance)
class MeetingAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'meeting', 'meeting_role'
    ]


@admin.register(ClubBookAverageRating)
class ClubBookAverageRatingAdmin(admin.ModelAdmin):
    list_display = [
        'club', 'book', 'rate', 'number_of_ratings'
    ]
