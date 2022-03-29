from django.test import TestCase
from django.urls import reverse
from bookclubs.models import User, Post, Vote
from bookclubs.tests.helpers import reverse_with_next

class PostDownvoteViewTestCase(TestCase):

    VIEW = 'post_downvote'

    fixtures = ['bookclubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            body="The quick brown fox jumps over the lazy dog."
        )
