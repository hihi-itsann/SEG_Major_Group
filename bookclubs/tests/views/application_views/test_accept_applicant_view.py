from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Club, Application, Role
from bookclubs.tests.helpers import reverse_with_next


class AcceptApplicantViewTestCase(TestCase):
    """Tests for the acceptance of an application"""

    VIEW = 'accept_applicant'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(username='@johndoe')
        self.applicant = User.objects.get(username='@janedoe')
        self.club = Club.objects.get(club_name='private_online')
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name, 'user_id': self.applicant.id})
        Role.objects.create(user=self.owner, club=self.club, club_role='OWN')
        Application.objects.create(user=self.applicant, club=self.club, statement='[Statement]', status='P')

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_accept_applicant_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/accept/{self.applicant.id}/')

    def test_accept_applicant_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_accept_applicant_redirects_when_not_a_member(self):
        self.log_in(self.applicant)
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_accept_applicant_redirects_when_a_member(self):
        self.log_in(self.applicant)
        Role.objects.create(user=self.applicant, club=self.club, club_role='MEM')
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_accept_applicant_is_successful_when_owner(self):
        self.log_in(self.owner)
        before_count_applications = Application.objects.count()
        before_count_members = Role.objects.filter(club=self.club).count()
        response = self.client.get(self.url)
        after_count_applications = Application.objects.count()
        after_count_members = Role.objects.filter(club=self.club).count()
        response_url = reverse('application_list', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(after_count_applications, before_count_applications)
        self.assertEqual(after_count_members, before_count_members + 1)
        application = Application.objects.get(user=self.applicant, club=self.club)
        self.assertEqual(application.status, 'A')
