from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Club, Application, Role
from bookclubs.tests.helpers import reverse_with_next


class EditApplicationViewTestCase(TestCase):
    """Tests for the creation of an application"""

    VIEW = 'withdraw_application'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name})

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_create_application_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/withdraw_application/')

    def test_edit_application_redirects_when_not_logged_in(self):
        before_count = Application.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_an_owner(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='OWN')
        before_count = Application.objects.count()
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_a_banned_user(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='BAN')
        before_count = Application.objects.count()
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_a_member(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='MEM')
        before_count = Application.objects.count()
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_rejected_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club, statement='not empty', status='R')
        before_count = Application.objects.count()
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_withdraw_application_redirects_when_accepted_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club, statement='not empty', status='A')
        before_count = Application.objects.count()
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_withdraw_application_redirects_when_not_applicant(self):
        self.log_in(self.user)
        before_count = Application.objects.count()
        redirect_url = reverse('create_application', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_withdraw_application_is_successful_when_pending_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club, statement='not empty', status='P')
        before_count = Application.objects.count()
        redirect_url = reverse('my_applications')
        response = self.client.get(self.url)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count - 1)
        self.assertEqual(0, Application.objects.filter(user=self.user, club=self.club).count())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
