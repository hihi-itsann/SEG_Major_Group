from django.test import TestCase
from django.urls import reverse

from bookclubs.models import Post, User, Club, Role
from bookclubs.tests.helpers import reverse_with_next


class DeletePostTest(TestCase):
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            club=self.club,
            body="The quick brown fox jumps over the lazy dog."
        )
        self.role = Role.objects.create(
            user=self.user,
            club=self.club,
            club_role='MEM'
        )
        self.url = reverse('delete_post', kwargs={'pk': self.post.id})

    def test_delete_post_url(self):
        self.assertEqual(self.url, f'/delete_post/{self.post.id}/')

    def test_create_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_delete_post(self):
        self.client.login(username=self.user.username, password="Password123")
        post_count_before = Post.objects.count()
        response = self.client.delete(self.url)
        post_count_after = Post.objects.count()
        self.assertEqual(post_count_after, post_count_before - 1)
        response_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
