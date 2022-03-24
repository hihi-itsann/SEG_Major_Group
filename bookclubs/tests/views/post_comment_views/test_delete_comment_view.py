from django.test import TestCase
from django.urls import reverse
from bookclubs.models import Post, User, Comment, Club
from bookclubs.tests.helpers import reverse_with_next


class DeleteCommentTest(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json'
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
        self.comment = Comment.objects.create(
            author=self.user,
            related_post=self.post,
            body="this is a comment."
        )
        self.url = reverse('delete_comment', kwargs={'pk': self.comment.id})

    def test_delete_comment_url(self):
        self.assertEqual(self.url, f'/delete_comment/{self.comment.id}/')

    def test_create_user_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_delete_comment(self):
        self.client.login(username=self.user.username, password="Password123")
        comment_count_before = Comment.objects.count()
        response = self.client.delete(self.url)
        comment_count_after = Comment.objects.count()
        self.assertEqual(comment_count_after, comment_count_before-1)
        response_url = reverse('club_feed',kwargs={'club_name': self.club.club_name})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
