from django.test import TestCase
from django.urls import reverse

from bookclubs.models import User, Post, Club, Vote, Role
from bookclubs.tests.helpers import reverse_with_next


class PostUpvoteViewTestCase(TestCase):
    """Tests for the up-voting of a post"""

    VIEW = 'post_upvote'

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.role = Role.objects.create(
            user=self.user,
            club=self.club,
            club_role='MEM'
        )
        self.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            club=self.club,
            body="The quick brown fox jumps over the lazy dog."
        )
        self.url = reverse(self.VIEW, kwargs={'post_id': self.post.id})

    def test_post_upvote_url(self):
        self.assertEqual(self.url, f'/upvote/{self.post.id}/')

    def test_post_upvote_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_post_upvote(self):
        self.client.login(username=self.user.username, password="Password123")
        vote_count_before = Vote.objects.count()
        response = self.client.post(self.url, follow=True)
        vote_count_after = Vote.objects.count()
        self.assertEqual(vote_count_after, vote_count_before + 1)
        new_vote = Vote.objects.latest('id')
        self.assertEqual(self.user, new_vote.user)
        self.assertEqual(self.post, new_vote.post)
        response_url = f'/club/{self.club.club_name}/feed/#{self.post.id}'
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, 'club_feed.html')
