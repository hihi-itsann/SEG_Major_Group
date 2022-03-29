from django.test import TestCase
from bookclubs.models import User, Post
from bookclubs.forms import PostForm

class PostFormTestCase(TestCase):

    fixtures = ['bookclubs/tests/fixtures/default_user.json']

    def setUp(self):

        self.user = User.objects.get(username='@johndoe')
        self.form_input = {
            'title' : 'this is a title.',
            'author' : self.user,
            body="The quick brown fox jumps over the lazy dog."
        }

    def test_valid_post_form(self):
        form = CommentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_post_must_not_be_blank(self):
        self.form_input['title'] = ''
        self.form_input['body'] = ''
        form = CommentForm(data=self.form_input)
        self.assertFalse(form_is_valid())

    def test_post_rejects_overlong_input_text(self):
        self.form_input['title'] = 'x'*255
        self.form_input['body'] = 'x'*521
        form = CommentForm(data=self.form_input)
        self.assertFalse(form_is_valid())
