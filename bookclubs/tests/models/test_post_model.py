from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Post

class PostModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            body="The quick brown fox jumps over the lazy dog."
        )

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

    def test_post_body_must_not_be_blank(self):
        self.post.body = ''
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_post_rejects_overlong_input_text(self):
        self.post.title = 'x'*255
        self.post.body ='x'*521
        with self.assertRaises(ValidationError):
            self.post.full_clean()
