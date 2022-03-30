from django.test import TestCase

from bookclubs.forms import CommentForm
from bookclubs.models import User


class CommentFormTestCase(TestCase):
    """Unit tests for the CommentForm"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')

    def test_form_contains_required_fields(self):
        form = CommentForm()
        self.assertIn('body', form.fields)

    def test_valid_comment_form(self):
        form_input = {'body': 'x' * 520}
        form = CommentForm(data=form_input)
        self.assertTrue(form.is_valid())

    def test_invalid_comment_form(self):
        form_input = {'body': 'x' * 521}
        form = CommentForm(data=form_input)
        self.assertFalse(form.is_valid())
