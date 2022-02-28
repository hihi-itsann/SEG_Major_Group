from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclubs.models import User, Post, Comment

class CommentModelTestCase(TestCase):

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        super(TestCase,self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            body="The quick brown fox jumps over the lazy dog."
        )
        self.comment = Comment.objects.create(
            author=self.user,
            related_post=self.post,
            body="this is a comment."
        )


    def test_valid_comment(self):
        try:
            self.comment.full_clean()
        except ValidationError:
            self.fail("Test comment should be valid")

    def test_author_must_not_be_blank(self):
        self.comment.author = None
        with self.assertRaises(ValidationError):
            self.comment.full_clean()

    def test_post_must_not_be_blank(self):
        self.comment.related_post = None
        with self.assertRaises(ValidationError):
            self.comment.full_clean()

    def test_body_must_not_be_blank(self):
        self.comment.body = ''
        with self.assertRaises(ValidationError):
            self.comment.full_clean()

    def test_body_must_not_be_overlong(self):
        self.comment.body = 'x' * 521
        with self.assertRaises(ValidationError):
            self.comment.full_clean()
