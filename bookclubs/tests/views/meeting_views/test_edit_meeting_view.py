from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from bookclubs.forms import MeetingForm
from bookclubs.models import User, Club, Meeting, Role, Book, MeetingAttendance
from bookclubs.tests.helpers import reverse_with_next


class EditMeetingViewTestCase(TestCase):
    """Tests for editing the details of a meeting"""

    VIEW = 'edit_meeting'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.host = User.objects.get(username='@johndoe')
        self.user = User.objects.get(username='@janedoe')
        self.club = Club.objects.get(club_name='private_in-person')
        self.book = Book.objects.get(ISBN="0195153448")
        Role.objects.create(user=self.host, club=self.club, club_role='OWN')
        self.membership = Role.objects.create(user=self.user, club=self.club, club_role='MEM')
        self.meeting = Meeting.objects.create(
            club=self.club,
            book=self.book,
            topic='alpha bravo charlie',
            description='delta foxtrot golf hotel india',
            meeting_status='OFF',
            location='Bush House',
            date=date.today() + timedelta(days=5),
            time_start='10:00',
            duration=60
        )
        MeetingAttendance.objects.create(
            user=self.host,
            meeting=self.meeting,
            meeting_role='H'
        )
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'meeting_id': self.meeting.id})
        self.form_input = {
            'topic': 'Edited',
            'description': 'delta foxtrot golf hotel india',
            'location': 'Bush House',
            'date': date.today() + timedelta(days=5),
            'time_start': '11:00',
            'duration': 45
        }

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_edit_meeting_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/meeting/{self.meeting.id}/edit/')

    def test_edit_meeting_with_invalid_club(self):
        self.log_in(self.user)
        url = reverse(self.VIEW, kwargs={'club_name': 'invalid', 'meeting_id': self.meeting.id})
        redirect_url = reverse('feed')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_meeting_with_invalid_meeting(self):
        self.log_in(self.user)
        url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'meeting_id': 999})
        redirect_url = reverse('feed')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_meeting_redirects_when_not_logged_in(self):
        before_count = Meeting.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_edit_meeting_redirects_when_a_banned_user(self):
        self.log_in(self.user)
        self.membership.delete()
        Role.objects.create(user=self.user, club=self.club, club_role='BAN')
        before_count = Meeting.objects.count()
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)

    def test_edit_meeting_successful_when_host(self):
        self.log_in(self.host)
        before_count = Meeting.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Meeting.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('show_meeting', kwargs={'club_name': self.club.club_name, 'meeting_id': self.meeting.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_meeting.html')
        self.meeting.refresh_from_db()
        self.assertEqual(self.meeting.topic, 'Edited')

    def test_edit_meeting_shows_form(self):
        self.log_in(self.host)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertFalse(form.is_bound)
