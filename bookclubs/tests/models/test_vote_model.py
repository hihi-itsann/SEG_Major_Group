from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Post, Vote

class VoteModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(Username='@johndoe')
        slef.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            body="The quick brown fox jumps over the lazy dog."
        )
        self.vote = Vote.objects.create(
            user=self.user,
            postt=self.post,
            vote_type == True
        )

    def test_valid_vote(self):
