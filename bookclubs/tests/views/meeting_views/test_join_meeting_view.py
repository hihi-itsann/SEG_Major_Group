from django.test import TestCase
from django.urls import reverse

from bookclubs.forms import NewMeetingForm
from bookclubs.models import User, Club, Meeting, Role, Book, MeetingAttendance
from bookclubs.tests.helpers import reverse_with_next
from django.utils import timezone
from django.contrib import messages


class CreateMeetingViewTestCase(TestCase):
    """Tests for the creation of a meeting"""

    VIEW = 'join_meeting'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
        'bookclubs/tests/fixtures/default_book.json',

    ]

    def setUp(self):
        self.owner = User.objects.get(username='@johndoe')
        self.member = User.objects.get(username='@janedoe')
        self.club = Club.objects.get(club_name='private_online')
        self.book = Book.objects.get(ISBN='0195153448')
        self.ownerRole = Role.objects.create(user=self.owner, club=self.club, club_role='OWN')
        self.meeting = Meeting.objects.create(
            club = self.club,
            book = self.book,
            topic = 'alpha bravo charlie',
            description = 'delta foxtrot golf hotel india',
            meeting_status = False,
            location = 'Bush House',
            date = timezone.now(),
            time_start = '10:00',
            time_end = '11:00'
        )
        self.hostMeetingAttendance = MeetingAttendance.objects.create(
            user = self.owner,
            meeting = self.meeting,
            meeting_role = 'H'
        )
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'meeting_id': self.meeting.id})

    def test_join_meeting_url(self):
        self.assertEqual(self.url,f'/club/{self.club.club_name}/meeting/{self.meeting.id}/join/')

    def test_succssfully_join(self):
        Role.objects.create(user=self.member, club=self.club, club_role='MEM')
        self.client.login(username=self.member.username, password="Password123")
        meeting_attendance_count_before = MeetingAttendance.objects.count()
        response = self.client.post(self.url, follow=True)
        meeting_attendance_count_after = MeetingAttendance.objects.count()
        self.assertEqual(meeting_attendance_count_after, meeting_attendance_count_before+1)
        response_url = reverse('meeting_list', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

    def test_membership_required_when_role_is_ban(self):
        Role.objects.create(user=self.member, club=self.club, club_role='BAN')
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_membership_required_when_does_not_has_role(self):
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_get_redirect_when_club_do_not_exist(self):
        Role.objects.create(user=self.member, club=self.club, club_role='MEM')
        url = reverse(self.VIEW, kwargs={'club_name': 'WrongClubName', 'meeting_id': self.meeting.id})
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_get_redirect_when_meeting_do_not_exist(self):
        Role.objects.create(user=self.member, club=self.club, club_role='MEM')
        url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'meeting_id': 999})
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)
