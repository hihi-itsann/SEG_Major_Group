from django.test import SimpleTestCase
from django.urls import reverse, resolve
import random
from bookclubs.views import home, feed, SignUpView, LogInView, log_out, ProfileUpdateView,\
                            show_user, PasswordView ,BookListView, ShowBookView, CreateBookRateReviewView,\
                            create_book_status, delete_book_status, change_book_status, reading_book_list,\
                            club_feed, club_welcome, create_club, delete_club, create_application,\
                            withdraw_application, my_applications, application_list, accept_applicant, \
                            reject_applicant, club_list, my_clubs, member_list, PostCommentView, \
                            CreatePostView, DeletePostView, CreateCommentView, DeleteCommentView,\
                            remove_member, moderator_list, transfer_ownership, show_book_recommendations,\
                            create_meeting


class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse('home')
        self.assertEquals(resolve(url).func, home)

    def test_feed_url_is_resolved(self):
        url = reverse('feed')
        self.assertEquals(resolve(url).func, feed)

    def test_sign_up_url_is_resolved(self):
        url = reverse('sign_up')
        self.assertEquals(resolve(url).func.view_class, SignUpView)

    def test_login_in_url_is_resolved(self):
        url = reverse('log_in')
        self.assertEquals(resolve(url).func.view_class, LogInView)

    def test_log_out_is_resolved(self):
        url = reverse('log_out')
        self.assertEquals(resolve(url).func, log_out)

    def test_ProfileUpdateView_url_is_resolved(self):
        url = reverse('profile')
        self.assertEquals(resolve(url).func.view_class, ProfileUpdateView)

    def test_show_user_url_is_resolved(self):
        url = reverse('show_user',args=['some-str'])
        self.assertEquals(resolve(url).func,show_user)

    def test_password_url_is_resolved(self):
        url = reverse('password')
        self.assertEquals(resolve(url).func.view_class, PasswordView)

    def test_book_list_url_is_resolved(self):
        url = reverse('book_list',args=['some-str'])
        self.assertEquals(resolve(url).func.view_class, BookListView)

    def test_show_book_url_is_resolved(self):
        url = reverse('show_book',args=['some-str'])
        self.assertEquals(resolve(url).func.view_class, ShowBookView)

    def test_create_book_rating_review_url_is_resolved(self):
        url = reverse('create_book_rating_review',args=['some-str'])
        self.assertEquals(resolve(url).func.view_class, CreateBookRateReviewView)

    def test_create_book_status_url_is_resolved(self):
        url = reverse('create_book_status',args=['some-str'])
        self.assertEquals(resolve(url).func, create_book_status)

    def test_delete_book_status_url_is_resolved(self):
        url = reverse('delete_book_status',args=['some-str'])
        self.assertEquals(resolve(url).func, delete_book_status)

    def test_change_book_status_url_is_resolved(self):
        url = reverse('change_book_status',args=['some-str','some-str'])
        self.assertEquals(resolve(url).func, change_book_status)

    def test_reading_book_list_url_is_resolved(self):
        url = reverse('reading_book_list',args=['some-str'])
        self.assertEquals(resolve(url).func, reading_book_list)

    def test_club_feed_url_is_resolved(self):
        url = reverse('club_feed',args=['some-str'])
        self.assertEquals(resolve(url).func, club_feed)

    def test_club_welcome_url_is_resolved(self):
        url = reverse('club_welcome',args=['some-str'])
        self.assertEquals(resolve(url).func, club_welcome)

    def test_create_club_url_is_resolved(self):
        url = reverse('create_club')
        self.assertEquals(resolve(url).func, create_club)

    def test_delete_club_url_is_resolved(self):
        url = reverse('delete_club',args=['some-str'])
        self.assertEquals(resolve(url).func, delete_club)

    def test_create_application_url_is_resolved(self):
        url = reverse('create_application',args=['some-str'])
        self.assertEquals(resolve(url).func, create_application)

    def test_withdraw_application_url_is_resolved(self):
        url = reverse('withdraw_application',args=['some-str'])
        self.assertEquals(resolve(url).func, withdraw_application)

    def test_my_applications_url_is_resolved(self):
        url = reverse('my_applications')
        self.assertEquals(resolve(url).func, my_applications)

    def test_application_list_url_is_resolved(self):
        url = reverse('application_list',args=['some-str'])
        self.assertEquals(resolve(url).func, application_list)

    def test_accept_applicant_url_is_resolved(self):
        url = reverse('accept_applicant',args=['some-str',random.randint(0,100)])
        self.assertEquals(resolve(url).func, accept_applicant)

    def test_reject_applicant_url_is_resolved(self):
        url = reverse('reject_applicant',args=['some-str',random.randint(0,100)])
        self.assertEquals(resolve(url).func, reject_applicant)

    def test_club_list_url_is_resolved(self):
        url = reverse('club_list',args=['some-str'])
        self.assertEquals(resolve(url).func, club_list)

    def test_my_clubs_url_is_resolved(self):
        url = reverse('my_clubs')
        self.assertEquals(resolve(url).func, my_clubs)

    def test_member_list_url_is_resolved(self):
        url = reverse('member_list',args=['some-str'])
        self.assertEquals(resolve(url).func, member_list)

    def test_post_comment_url_is_resolved(self):
        url = reverse('post_comment')
        self.assertEquals(resolve(url).func.view_class, PostCommentView)

    def test_create_post_url_is_resolved(self):
        url = reverse('create_post')
        self.assertEquals(resolve(url).func.view_class, CreatePostView)

    def test_delete_post_url_is_resolved(self):
        url = reverse('delete_post',args=[random.randint(0,100)])
        self.assertEquals(resolve(url).func.view_class, DeletePostView)

    def test_create_comment_url_is_resolved(self):
        url = reverse('create_comment',args=[random.randint(0,100)])
        self.assertEquals(resolve(url).func.view_class, CreateCommentView)

    def test_delete_comment_url_is_resolved(self):
        url = reverse('delete_comment',args=[random.randint(0,100)])
        self.assertEquals(resolve(url).func.view_class, DeleteCommentView)

    def test_remove_member_url_is_resolved(self):
        url = reverse('remove_applicant',args=['some-str',random.randint(0,100)])
        self.assertEquals(resolve(url).func, remove_member)

    def test_moderator_list_url_is_resolved(self):
        url = reverse('moderator_list',args=['some-str'])
        self.assertEquals(resolve(url).func, moderator_list)

    def test_transfer_ownership_url_is_resolved(self):
        url = reverse('transfer_ownership',args=['some-str',random.randint(0,100)])
        self.assertEquals(resolve(url).func, transfer_ownership)

    def test_show_book_recommendations_url_is_resolved(self):
        url = reverse('show_book_recommendations',args=['some-str'])
        self.assertEquals(resolve(url).func, show_book_recommendations)

    def test_create_meeting_url_is_resolved(self):
        url = reverse('create_meeting',args=['some-str','some-str'])
        self.assertEquals(resolve(url).func, create_meeting)
