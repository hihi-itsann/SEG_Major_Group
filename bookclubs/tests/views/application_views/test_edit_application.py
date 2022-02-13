from django.test import TestCase
from django.urls import reverse

from bookclubs.forms import UpdateApplicationForm
from bookclubs.models import User, Club, Application, Role
from bookclubs.tests.helpers import reverse_with_next


class EditApplicationViewTestCase(TestCase):
    """Tests for the creation of an application"""

    VIEW = 'edit_application'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.url = reverse(self.VIEW, kwargs={'club_name': self.club.club_name})
        self.form_input = {
            'statement': 'Hello I am editing my application.'
        }

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_create_application_url(self):
        self.assertEqual(self.url, f'/club/{self.club.club_name}/edit_application/')

    def test_edit_application_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_an_owner(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='OWN')
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_a_banned_user(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='BAN')
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_a_member(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club, club_role='MEM')
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_rejected_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club, statement='not empty', status='R')
        redirect_url = reverse('feed')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_accepted_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club, statement='not empty', status='A')
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_redirects_when_not_applicant(self):
        self.log_in(self.user)
        redirect_url = reverse('create_application', kwargs={'club_name': self.club.club_name})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_application_is_successful_when_pending_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club, statement='not empty', status='P')
        before_count = Application.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('my_applications')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'my_applications.html')
        application = Application.objects.get(user=self.user, club=self.club)
        self.assertEqual(application.statement, 'Hello I am editing my application.')
        self.assertEqual(application.status, 'P')

    def test_edit_application_shows_form(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club, statement='not empty', status='P')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UpdateApplicationForm))
        self.assertTrue(form.is_bound)
