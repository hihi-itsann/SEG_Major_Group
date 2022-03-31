from django.test import TestCase

from bookclubs.forms import PostForm
from bookclubs.models import User, Club


class PostFormTestCase(TestCase):
    """Unit tests for the PostForm"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.club = Club.objects.get(club_name='private_online')
        self.form_input = {
            'club': self.club,
            'title': 'this is a title.',
            'author': self.user,
            'body': "The quick brown fox jumps over the lazy dog."
        }

    def test_post_must_not_be_blank(self):
        self.form_input['title'] = ''
        self.form_input['body'] = ''
        form = PostForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_contains_required_fields(self):
        form = PostForm()
        self.assertIn('title', form.fields)
        self.assertIn('body', form.fields)

    def test_valid_post_form(self):
        form_input = {'title': 'x' * 255,
                      'body': 'x' * 520}
        form = PostForm(data=form_input)
        self.assertTrue(form.is_valid())

    def test_invalid_post_form_with_invalid_title(self):
        form_input = {'title': 'x' * 256,
                      'body': 'x' * 520}
        form = PostForm(data=form_input)
        self.assertFalse(form.is_valid())

    def test_invalid_post_form_with_invalid_body(self):
        form_input = {'title': 'x' * 255,
                      'body': 'x' * 521}
        form = PostForm(data=form_input)
        self.assertFalse(form.is_valid())
