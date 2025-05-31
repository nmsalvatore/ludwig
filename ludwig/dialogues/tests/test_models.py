from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ludwig.dialogues.models import Dialogue, Post


User = get_user_model()


class DialogueModelTests(TestCase):
    """
    Testing suite for Dialogue model.

    Tests included:
        1. Successfully create a dialogue and verify model fields
        2. Dialogue without title not be created
        3. Dialogue without title not created
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass"
        )

    def test_create_dialogue(self):
        """
        Test that dialogue is successfully created in the database and
        that all model fields are as expected.
        """
        Dialogue.objects.create(
            title="Test",
            summary="Testing",
            author=self.user
        )

        dialogue = Dialogue.objects.get(title="Test")

        self.assertTrue(dialogue.title, "Test")
        self.assertTrue(dialogue.summary, "Testing")
        self.assertTrue(dialogue.author, self.user)
        self.assertIsNotNone(dialogue.id)
        self.assertIsNotNone(dialogue.created_on)
        self.assertFalse(dialogue.is_visible)
        self.assertFalse(dialogue.is_open)
        self.assertEqual(dialogue.participants.count(), 1)
        self.assertEqual(dialogue.participants.first(), dialogue.author)

    def test_dialogue_without_title_fails(self):
        """
        Test that creating a dialogue without a title will fail and
        raise a ValidationError.
        """
        with self.assertRaises(ValidationError):
            Dialogue.objects.create(
                summary="Testing",
                author=self.user
            )
        dialogue = Dialogue.objects.filter(summary="Testing")
        self.assertFalse(dialogue.exists())

    def test_dialogue_without_author(self):
        """
        Test that creating a dialogue without an author will fail and
        raise a ValidationError.
        """
        with self.assertRaises(ValidationError):
            Dialogue.objects.create(
                summary="Testing",
                title="Testing",
            )
        dialogue = Dialogue.objects.filter(summary="Testing")
        self.assertFalse(dialogue.exists())


class PostModelTests(TestCase):
    """
    Testing suite for Post model.

    Tests included:
        1. Successfully create a post in a dialogue
        2. Post shows up in dialogue.posts
        2. Post without body not created
        3. Post without author not created
    """

    def setUp(self):
        """
        Initial setup for the testing suite.
        """
        self.user1 = User.objects.create(
            username="testuser1",
            email="testuser1@example.com",
            password="testpassword"
        )
        self.user2 = User.objects.create(
            username="testuser2",
            email="testuser2@example.com",
            password="testpassword"
        )
        self.dialogue = Dialogue.objects.create(
            title="Test",
            summary="Testing",
            author=self.user1
        )

    def test_create_post(self):
        """
        Test that post is successfully added to a dialogue and that all
        model fields are as expected.
        """
        post = Post.objects.create(
            dialogue=self.dialogue,
            author=self.user1,
            body="Test post",
        )

        self.assertTrue(post.dialogue, self.dialogue)
        self.assertTrue(post.author, self.user1)
        self.assertTrue(post.body, "Test post")
        self.assertIsNotNone(post.id)
        self.assertIsNotNone(post.created_on)

    def test_post_in_dialogue_posts(self):
        """
        Test that post can be found in `Dialogue.posts`
        """
        post = Post.objects.create(
            dialogue=self.dialogue,
            author=self.user1,
            body="Test post",
        )
        self.assertIn(post, self.dialogue.posts.all())
        self.assertEqual(self.dialogue.posts.count(), 1)

    def test_post_without_body_not_created(self):
        """
        Test that a post without a body will not be created and will
        raise a ValidationError.
        """
        with self.assertRaises(ValidationError):
            Post.objects.create(
                dialogue=self.dialogue,
                author=self.user1,
            )
        post = Post.objects.filter(dialogue=self.dialogue)
        self.assertFalse(post.exists())

    def test_post_without_author_not_created(self):
        """
        Test that a post without an author will not be created and will
        raise a ValidationError.
        """
        with self.assertRaises(ValidationError):
            Post.objects.create(
                dialogue=self.dialogue,
                body="Test post",
            )
        post = Post.objects.filter(dialogue=self.dialogue)
        self.assertFalse(post.exists())
