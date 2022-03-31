from django.core.exceptions import ValidationError
from django.test import TestCase

from bookclubs.models import User, Post, Club, Vote


class PostModelTestCase(TestCase):
    """Unit tests for the Post model"""

    fixtures = [
        'bookclubs/tests/fixtures/default_user.json',
        'bookclubs/tests/fixtures/other_users.json',
        'bookclubs/tests/fixtures/default_clubs.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.club = Club.objects.get(club_name='private_online')
        self.post = Post.objects.create(
            title="this is a title.",
            author=self.user,
            club=self.club,
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

    def test_club_must_not_be_blank(self):
        self.post.club = None
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_body_must_not_be_blank(self):
        self.post.body = ''
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    def test_post_rejects_overlong_input_text(self):
        self.post.title = 'x' * 255
        self.post.body = 'x' * 521
        with self.assertRaises(ValidationError):
            self.post.full_clean()

    # Method tests

    def test_to_string(self):
        """Test to_string method"""
        self.assertEqual(self.post.__str__(), f'{self.post.title} | {self.post.author}')

    def test_toggle_upvote_with_no_previous_vote(self):
        """Test toggle_upvote method when the user hasn't previously upvoted or downvoted the post"""
        vote_count_before = Vote.objects.all().count()
        self.post.toggle_upvote(self.user)
        vote_count_after = Vote.objects.all().count()
        self.assertEqual(vote_count_after, vote_count_before + 1)

    def test_toggle_upvote_with_previous_upvote(self):
        """Test toggle_upvote method when the user has previously upvoted the post"""
        Vote.objects.create(user=self.user, post=self.post, vote_type=True)
        vote_count_before = Vote.objects.all().count()
        self.post.toggle_upvote(self.user)
        vote_count_after = Vote.objects.all().count()
        self.assertEqual(vote_count_after, vote_count_before - 1)

    def test_toggle_upvote_with_previous_downvote(self):
        """Test toggle_upvote method when the user has previously downvoted the post"""
        Vote.objects.create(user=self.user, post=self.post, vote_type=False)
        vote_count_before = Vote.objects.all().count()
        self.post.toggle_upvote(self.user)
        vote_count_after = Vote.objects.all().count()
        self.assertEqual(vote_count_after, vote_count_before)

    def test_toggle_downvote_with_no_previous_vote(self):
        """Test toggle_downvote method when the user hasn't previously upvoted or downvoted the post"""
        vote_count_before = Vote.objects.all().count()
        self.post.toggle_downvote(self.user)
        vote_count_after = Vote.objects.all().count()
        self.assertEqual(vote_count_after, vote_count_before + 1)

    def test_toggle_downvote_with_previous_downvote(self):
        """Test toggle_downvote method when the user has previously downvoted the post"""
        Vote.objects.create(user=self.user, post=self.post, vote_type=False)
        vote_count_before = Vote.objects.all().count()
        self.post.toggle_downvote(self.user)
        vote_count_after = Vote.objects.all().count()
        self.assertEqual(vote_count_after, vote_count_before - 1)

    def test_toggle_downvote_with_previous_upvote(self):
        """Test toggle_downvote method when the user has previously upvoted the post"""
        Vote.objects.create(user=self.user, post=self.post, vote_type=True)
        vote_count_before = Vote.objects.all().count()
        self.post.toggle_downvote(self.user)
        vote_count_after = Vote.objects.all().count()
        self.assertEqual(vote_count_after, vote_count_before)

    def test_get_upvotes(self):
        """Test get_upvotes method"""
        self.assertEqual(self.post.get_upvotes(), 0)
        Vote.objects.create(user=self.user, post=self.post, vote_type=True)
        self.assertEqual(self.post.get_upvotes(), 1)
        Vote.objects.create(user=self.other_user, post=self.post, vote_type=True)
        self.assertEqual(self.post.get_upvotes(), 2)

    def test_get_downvotes(self):
        """Test get_downvotes method"""
        self.assertEqual(self.post.get_downvotes(), 0)
        Vote.objects.create(user=self.user, post=self.post, vote_type=False)
        self.assertEqual(self.post.get_downvotes(), 1)
        Vote.objects.create(user=self.other_user, post=self.post, vote_type=False)
        self.assertEqual(self.post.get_downvotes(), 2)
