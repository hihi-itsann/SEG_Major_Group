from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Post, Club

class PostModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json'
    ]

    def setUp(self):
        super(TestCase,self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            club=self.club,
            body="The quick brown fox jumps over the lazy dog."
        )

    def test_valid_comment(self):
        try:
            self.post.full_clean()
        except ValidationError:
            self.fail("Test post should be valid")

    def test_author_must_not_be_blank(self):
        self.post.author = None
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_club_must_not_be_blank(self):
        self.post.club = None
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_body_must_not_be_blank(self):
        self.post.body = ''
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_body_must_not_be_overlong(self):
        self.post.body = 'x' * 521
        with self.assertRaises(ValidationError):
            self.post.full_clean()
