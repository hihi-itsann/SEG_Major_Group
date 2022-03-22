from django.test import TestCase
from django.urls import reverse

from bookclubs.forms import MeetingForm
from bookclubs.models import User, Club, Meeting, Role, Book, MeetingAttendance
from bookclubs.tests.helpers import reverse_with_next


class CreateMeetingViewTestCase(TestCase):
    """Tests for the creation of a meeting"""

    VIEW = 'create_meeting'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(username='@johndoe')
        self.user = User.objects.get(username='@janedoe')
        self.club = Club.objects.get(club_name='private_online')
        self.book = Book.objects.get(ISBN="0195153448")
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'book_isbn': self.book.ISBN})
        Role.objects.create(user=self.owner, club=self.club, club_role='OWN')
        self.form_input = {
            'club': self.club,
            'book': self.book,
            'topic': 'alpha bravo charlie',
            'description': 'delta foxtrot golf hotel india',
            'meeting_status': 'OFF',
            'location': 'Bush House',
            'date': '2022-04-01',
            'time_start': '10:00',
            'duration': 60
        }

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_create_meeting_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/meeting/book/{self.book.ISBN}/create/')

    def test_create_meeting_with_invalid_club(self):
        self.log_in(self.user)
        url = reverse(self.VIEW, kwargs={'club_name': 'invalid', 'book_isbn': self.book.ISBN})
        redirect_url = reverse('feed')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_create_meeting_with_invalid_book(self):
        self.log_in(self.user)
        url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'book_isbn': 'XXXXX'})
        redirect_url = reverse('feed')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_create_meeting_redirects_when_not_logged_in(self):
        before_count = Meeting.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_meeting_redirects_when_a_banned_user(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='BAN')
        before_count = Meeting.objects.count()
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_meeting_successful_when_a_member(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='MEM')
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(MeetingAttendance.objects.all().count(), 1)
        response_url = reverse('meeting_list', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'meeting_list.html')

    def test_create_meeting_is_successful_when_owner(self):
        self.log_in(self.owner)
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(MeetingAttendance.objects.all().count(), 1)
        response_url = reverse('meeting_list', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'meeting_list.html')

    def test_create_meeting_shows_form(self):
        self.log_in(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertFalse(form.is_bound)
