from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Book, Club, Meeting, MeetingAttendance, Role
from bookclubs.tests.helpers import reverse_with_next


class ShowMeetingViewTestCase(TestCase):
    """Tests for the showing details of a meeting"""

    VIEW = 'show_meeting'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
        'bookclubs/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.host = User.objects.get(username='@johndoe')
        self.user = User.objects.get(username='@janedoe')
        self.book = Book.objects.get(ISBN='0195153448')
        self.club = Club.objects.get(club_name='private_online')
        Role.objects.create(
            user=self.host,
            club=self.club,
            club_role='MEM'
        )
        self.user_role = Role.objects.create(
            user=self.user,
            club=self.club,
            club_role='MEM'
        )
        self.meeting = Meeting.objects.create(
            club=self.club,
            book=self.book,
            topic='alpha bravo charlie',
            description='delta foxtrot golf hotel india',
            meeting_status='OFF',
            location='Bush House',
            date='2022-04-01',
            time_start='10:00',
            duration=60
        )
        MeetingAttendance.objects.create(
            user=self.host,
            meeting=self.meeting,
            meeting_role='H'
        )
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'meeting_id': self.meeting.id})

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_show_meeting_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/meeting/{self.meeting.id}/')

    def test_show_meeting_with_invalid_club(self):
        self.log_in(self.user)
        url = reverse(self.VIEW, kwargs={'club_name': 'invalid', 'meeting_id': self.meeting.id})
        redirect_url = reverse('feed')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_meeting_with_invalid_meeting(self):
        self.log_in(self.user)
        url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'meeting_id': 999})
        redirect_url = reverse('feed')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_meeting_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_meeting_redirects_when_not_a_member(self):
        self.log_in(self.user)
        self.user_role.delete()
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_meeting_successful_when_not_attendee_or_host(self):
        self.log_in(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_meeting.html')
        self.assertContains(response, f'Meeting #{self.meeting.id}')
        self.assertContains(response, f'{self.book.title}')

    def test_show_meeting_successful_when_attendee(self):
        self.log_in(self.user)
        MeetingAttendance.objects.create(user=self.user, meeting=self.meeting, meeting_role='A')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_meeting.html')
        self.assertContains(response, f'Meeting #{self.meeting.id}')
        self.assertContains(response, f'{self.book.title}')

    def test_show_meeting_successful_when_host(self):
        self.log_in(self.host)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_meeting.html')
        self.assertContains(response, f'Meeting #{self.meeting.id}')
        self.assertContains(response, f'{self.book.title}')
