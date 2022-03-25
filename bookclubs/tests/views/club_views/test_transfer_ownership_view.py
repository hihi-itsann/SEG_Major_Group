from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclubs.tests.helpers import reverse_with_next

from bookclubs.models import User, Club, Meeting, Role, Book, MeetingAttendance


class TransferOwnershipViewTestCase(TestCase):
    """Tests for the leaving of a meeting"""

    VIEW = 'transfer_ownership'

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
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'user_id': self.member.id})

    def test_transfer_ownership_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/transfer_ownership/{self.member.id}/')

    def test_get_transfer_ownership_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_owner_successfully_transfer_ownership_to_mod(self):
        Role.objects.create(user=self.owner, club=self.club, club_role='OWN')
        Role.objects.create(user=self.member, club=self.club, club_role='MOD')
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        response_url = reverse('member_list', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertEqual(self.club.get_club_role(self.member), 'OWN')
        self.assertEqual(self.club.get_club_role(self.owner), 'MOD')

    def test_owner_unsuccessfully_transfer_ownership_to_member(self):
        Role.objects.create(user=self.owner, club=self.club, club_role='OWN')
        Role.objects.create(user=self.member, club=self.club, club_role='MEM')
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        response_url = reverse('member_list', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertEqual(self.club.get_club_role(self.member), 'MEM')
        self.assertEqual(self.club.get_club_role(self.owner), 'OWN')

    def test_member_unsuccessfully_transfer_ownership(self):
        Role.objects.create(user=self.owner, club=self.club, club_role='OWN')
        Role.objects.create(user=self.member, club=self.club, club_role='MEM')
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        self.assertEqual(self.club.get_club_role(self.member), 'MEM')
        self.assertEqual(self.club.get_club_role(self.owner), 'OWN')
        response_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

    def test_membership_required_when_user_is_banned(self):
        Role.objects.create(user=self.member, club=self.club, club_role='BAN')
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_membership_required_when_does_not_have_a_role(self):
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_get_redirect_when_club_does_not_exist(self):
        Role.objects.create(user=self.member, club=self.club, club_role='OWN')
        url = reverse(self.VIEW, kwargs={'club_name': 'WrongClubName', 'user_id': self.member.id})
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(url, follow=True)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_get_redirect_when_user_id_does_not_exist(self):
        Role.objects.create(user=self.member, club=self.club, club_role='OWN')
        url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'user_id': 999})
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.post(url, follow=True)
        redirect_url = reverse('member_list', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)
