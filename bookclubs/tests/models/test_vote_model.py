from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Post, Vote, Club


class VoteModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
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

    def test_valid_vote(self):
        try:
            self.vote.full_clean()
        except:
            self.fail("Test vote should be valid")

    def test_author_must_not_be_blank(self):
        self.vote.user = None
        with self.assertRaises(ValidationError):
            self.vote.full_clean()

    def test_post_must_not_be_blank(self):
        self.vote.post = None
        with self.assertRaises(ValidationError):
            self.vote.full_clean()
