from django.test import TestCase
from bookclubs.models import User, Post
from bookclubs.forms import PostForm

class PostFormTestCase(TestCase):

    fixtures = ['bookclubs/tests/fixtures/default_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')

    def test_form_contains_required_fields(self):
        form = PostForm()
        self.assertIn('title', form.fields)
        self.assertIn('body', form.fields)

    def test_valid_post_form(self):
        input = {'title': 'x'*255,
                 'body': 'x'*520 }
        form = PostForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form_with_invalid_title(self):
        input = {'title': 'x'*256,
                 'body': 'x'*520 }
        form = PostForm(data=input)
        self.assertFalse(form.is_valid())

    def test_invalid_post_form_with_invalid_body(self):
        input = {'title': 'x'*255,
                 'body': 'x'*521 }
        form = PostForm(data=input)
        self.assertFalse(form.is_valid())
