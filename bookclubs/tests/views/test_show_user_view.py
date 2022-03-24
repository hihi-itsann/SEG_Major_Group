# from django.test import TestCase
# from django.urls import reverse
# from bookclubs.models import User
# from bookclubs.tests.helpers import reverse_with_next
#
#
# class ShowUserViewTestCase(TestCase):
#
#     VIEW = 'show_user'
#
#     fixtures = [
#         'bookclubs/tests/fixtures/default_user.json',
#         'bookclubs/tests/fixtures/other_users.json'
#     ]
#
#     def setUp(self):
#         self.user = User.objects.get(username='@johndoe')
#         self.target_user = User.objects.get(username='@janedoe')
#         self.url = reverse(self.VIEW, kwargs={'username': self.target_user.username})
#
#     def test_show_user_url(self):
#         self.assertEqual(self.url, f'/user/{self.target_user.username}/')
#
#     def test_get_show_user_with_valid_id(self):
#         self.client.login(username=self.user.username, password='Password123')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, f'{self.VIEW}.html')
#         self.assertContains(response, "Jane Doe")
#         self.assertContains(response, "@janedoe")
#
#     def test_get_show_user_with_own_id(self):
#         self.client.login(username=self.user.username, password='Password123')
#         url = reverse(self.VIEW, kwargs={'username': self.user.username})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, f'{self.VIEW}.html')
#         self.assertContains(response, "John Doe")
#         self.assertContains(response, "@johndoe")
#
#     def test_get_show_user_with_invalid_id(self):
#         self.client.login(username=self.user.username, password='Password123')
#         url = reverse('show_user', kwargs={'username': '@invalid_user'})
#         response = self.client.get(url, follow=True)
#         response_url = reverse('feed')
#         self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
#         self.assertTemplateUsed(response, 'feed.html')
#
#     def test_get_show_user_redirects_when_not_logged_in(self):
#         redirect_url = reverse_with_next('log_in', self.url)
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
