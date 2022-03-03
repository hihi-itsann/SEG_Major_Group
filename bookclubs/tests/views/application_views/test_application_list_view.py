from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Club, Application, Role
from bookclubs.tests.helpers import reverse_with_next


class ApplicationListViewTestCase(TestCase):
    """Tests for the application list owner/ moderator view"""

    VIEW = 'application_list'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.owner = User.objects.get(username='@johndoe')
        self.applicant = User.objects.get(username='@janedoe')
        self.club = Club.objects.get(club_name='private_online')
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name})
        Role.objects.create(user=self.owner, club=self.club, club_role='OWN')
        Application.objects.create(user=self.applicant, club=self.club, statement='[Statement]', status='P')

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_edit_application_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/applications/')

    def test_application_list_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_application_list_redirects_when_not_a_member(self):
        self.log_in(self.applicant)
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_application_list_redirects_when_a_member(self):
        self.log_in(self.applicant)
        Role.objects.create(user=self.applicant, club=self.club, club_role='MEM')
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_application_list_is_successful_when_moderator(self):
    #     self.log_in(self.owner)
    #     Role.objects.get(user=self.owner, club=self.club).club_role = 'MOD'
    #     before_count = Application.objects.count()
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     after_count = Application.objects.count()
    #     self.assertEqual(after_count, before_count)
    #     self.assertTemplateUsed(response, f'{self.VIEW}.html')
    #     self.assertContains(response, self.applicant)

    def test_application_list_is_successful_when_owner(self):
        self.log_in(self.owner)
        before_count = Application.objects.count()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        self.assertContains(response, self.applicant)
