from django.test import TestCase
from bookclubs.models import User, Post
from bookclubs.forms import PostForm

class PostFormTestCase(TestCase):

    fixtures = ['bookclubs/tests/fixtures/default_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            'title' : 'this is a title.',
            'author' : self.user,
            body="The quick brown fox jumps over the lazy dog."
        }

    def test_post_must_not_be_blank(self):
        self.form_input['title'] = ''
        self.form_input['body'] = ''
        form = PostForm(data=self.form_input)
        self.assertFalse(form_is_valid())

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
