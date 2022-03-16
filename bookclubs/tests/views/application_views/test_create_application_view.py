from django.test import TestCase
from django.urls import reverse

from bookclubs.forms import NewApplicationForm
from bookclubs.models import User, Club, Application, Role
from bookclubs.tests.helpers import reverse_with_next


class CreateApplicationViewTestCase(TestCase):
    """Tests for the creation of an application"""

    VIEW = 'create_application'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club_private = Club.objects.get(club_name='private_online')
        self.url_private = reverse(self.VIEW, kwargs={'club_name': self.club_private.club_name})
        self.club_public = Club.objects.get(club_name='public_in-person')
        self.url_public = reverse(self.VIEW, kwargs={'club_name': self.club_public.club_name})
        self.form_input = {
            'statement': 'Hello I would like to join this club.'
        }

    def log_in(self, user):
        self.client.login(username=user.username, password="Password123")

    def test_create_application_url(self):
        self.assertEqual(self.url_private, f'/club/{self.club_private.club_name}/apply/')
        self.assertEqual(self.url_public, f'/club/{self.club_public.club_name}/apply/')

    def test_create_application_redirects_when_not_logged_in(self):
        before_count = Application.objects.count()
        redirect_url = reverse_with_next('log_in', self.url_private)
        response = self.client.get(self.url_private)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_redirects_when_an_owner(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club_private, club_role='OWN')
        before_count = Application.objects.count()
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club_private.club_name})
        response = self.client.get(self.url_private)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_redirects_when_a_banned_user(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club_private, club_role='BAN')
        before_count = Application.objects.count()
        redirect_url = reverse('feed')
        response = self.client.get(self.url_private)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_redirects_when_a_member(self):
        self.log_in(self.user)
        Role.objects.create(user=self.user, club=self.club_private, club_role='MEM')
        before_count = Application.objects.count()
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club_private.club_name})
        response = self.client.get(self.url_private)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_redirects_when_rejected_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club_private, statement='not empty', status='R')
        before_count = Application.objects.count()
        redirect_url = reverse('my_applications')
        response = self.client.get(self.url_private)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_redirects_when_accepted_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club_private, statement='not empty', status='A')
        before_count = Application.objects.count()
        redirect_url = reverse('club_feed', kwargs={'club_name': self.club_private.club_name})
        response = self.client.get(self.url_private)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_redirects_when_pending_applicant(self):
        self.log_in(self.user)
        Application.objects.create(user=self.user, club=self.club_private, statement='not empty', status='P')
        before_count = Application.objects.count()
        redirect_url = reverse('my_applications')
        response = self.client.get(self.url_private)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count)

    def test_create_application_is_successful_private_club(self):
        self.log_in(self.user)
        before_count = Application.objects.count()
        response = self.client.post(self.url_private, self.form_input, follow=True)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('my_applications')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'my_applications.html')
        application = Application.objects.get(user=self.user, club=self.club_private)
        self.assertEqual(application.statement, 'Hello I would like to join this club.')
        self.assertEqual(application.status, 'P')

    def test_create_application_is_successful_public_club(self):
        self.log_in(self.user)
        before_count = Application.objects.count()
        response = self.client.get(self.url_public)
        after_count = Application.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('my_applications')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        application = Application.objects.get(user=self.user, club=self.club_public)
        self.assertEqual(application.statement, '')
        self.assertEqual(application.status, 'A')

    def test_create_application_shows_form(self):
        self.log_in(self.user)
        response = self.client.get(self.url_private)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, f'{self.VIEW}.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewApplicationForm))
        self.assertFalse(form.is_bound)
