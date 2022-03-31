from django.test import TestCase
from django.urls import reverse

from bookclubs.models import Post, User, Club, Role
from bookclubs.tests.helpers import reverse_with_next


class CreatePostTest(TestCase):
    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.role = Role.objects.create(
            user=self.user,
            club=self.club,
            club_role='MEM'
        )
        self.url = reverse('create_post', kwargs={'pk': self.club.id})
        self.data = {'title': 'a title',
                     'body': 'The quick brown fox jumps over the lazy dog.'}

    def test_create_post_url(self):
        self.assertEqual(self.url, f'/create_post/{self.club.id}/')

    def test_create_post_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_create_post(self):
        self.client.login(username='@johndoe', password="Password123")
        post_count_before = Post.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        post_count_after = Post.objects.count()
        self.assertEqual(post_count_after, post_count_before + 1)
        new_post = Post.objects.latest('post_datetime')
        self.assertEqual(self.user, new_post.author)
        self.assertEqual(self.club, new_post.club)
        response_url = reverse('club_feed', kwargs={'club_name': self.club.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'club_feed.html')

    def test_unsuccessful_create_post_with_blank_body(self):
        self.client.login(username='@johndoe', password='Password123')
        post_count_before = Post.objects.count()
        self.data['body'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        post_count_after = Post.objects.count()
        self.assertEqual(post_count_after, post_count_before)
        self.assertTemplateUsed(response, 'create_post.html')
