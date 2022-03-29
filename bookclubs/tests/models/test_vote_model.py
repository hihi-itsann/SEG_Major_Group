from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Post, Vote, Club


class VoteModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(Username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            club=self.club,
            body="The quick brown fox jumps over the lazy dog."
        )
        self.vote = Vote.objects.create(
            user=self.user,
            post=self.post,
            vote_type=True
        )

    # def test_valid_vote(self):
