from django.test import TestCase
from django.urls import reverse

from bookclubs.forms import NewMeetingForm
from bookclubs.models import User, Club, Meeting, MeetingAttendance, Role
from bookclubs.tests.helpers import reverse_with_next


class CreateMeetingApplicationViewTestCase(TestCase):
    """Tests for the creation of a meeting"""

    VIEW = 'create_meeting'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(username='@johndoe')
        self.member = User.objects.get(username='@janedoe')
        self.club = Club.objects.get(club_name='private_online')
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name})
        Role.objects.create(user=self.owner, club=self.club, club_role='OWN')

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_create_meeting_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/host_meeting/')

    def test_create_meeting_redirects_when_not_logged_in(self):
        before_count = Meeting.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_redirects_when_a_banned_user(self):
        self.log_in(self.member)
        Role.objects.create(user=self.member, club=self.club, club_role='BAN')
        before_count = Meeting.objects.count()
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_redirects_when_a_member(self):
        self.log_in(self.member)
        Role.objects.create(user=self.member, club=self.club, club_role='MEM')
        before_count = Meeting.objects.count()
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_meeting_shows_form(self):
        self.log_in(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewMeetingForm))
        self.assertFalse(form.is_bound)
