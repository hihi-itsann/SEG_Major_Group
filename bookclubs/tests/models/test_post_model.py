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
        
    def test_to_string(self):
        self.assertEqual(self.post.__str__(), f'{self.post.title} | {self.post.author}')

    def test_valid_post(self):
        try:
            self.post.full_clean()
        except ValidationError:
            self.fail("Test post should be valid")

    def test_post_title_must_not_be_blank(self):
        self.post.title = ''
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_post_author_must_not_be_blank(self):
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

    def test_post_rejects_overlong_input_text(self):
        self.post.title = 'x'*255
        self.post.body ='x'*521
        with self.assertRaises(ValidationError):
            self.post.full_clean()
