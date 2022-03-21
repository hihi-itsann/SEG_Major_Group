from django.test import TestCase
from bookclubs.models import User, Post, Comment
from bookclubs.forms import CommentForm

class CommentFormTestCase(TestCase):

    fixtures = ['bookclubs/tests/fixtures/default_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')

    def test_valid_comment_form(self):
        input = {'body': 'x'*520 }
        form = CommentForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form(self):
        input = {'body': 'x'*521 }
        form = CommentForm(data=input)
        self.assertFalse(form.is_valid())
