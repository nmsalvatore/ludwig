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
        4. Delete dialogue
        5. Change dialogue title
        6. Author should be a participant
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass"
        )

    def test_create_dialogue(self):
        """
        Dialogue successfully created with required values.
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
        Creating a dialogue without a title should fail.
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
        Creating a dialogue without an author should fail.
        """
        with self.assertRaises(ValidationError):
            Dialogue.objects.create(
                summary="Testing",
                title="Testing",
            )
        dialogue = Dialogue.objects.filter(summary="Testing")
        self.assertFalse(dialogue.exists())

    def test_delete_dialogue(self):
        """
        Deleting dialogue should remove dialogue from database.
        """
        Dialogue.objects.create(
            summary="Testing",
            title="Testing",
            author=self.user
        )
        dialogue = Dialogue.objects.filter(summary="Testing")
        self.assertTrue(dialogue.exists())
        dialogue.delete()
        self.assertFalse(dialogue.exists())

    def test_change_dialogue_title(self):
        """
        Changing dialogue title should update the title in the database.
        """
        dialogue = Dialogue.objects.create(
            summary="Testing",
            title="Testing",
            author=self.user
        )
        self.assertEqual(dialogue.title, "Testing")
        dialogue.title = "Updated Title"
        dialogue.save()
        self.assertEqual(dialogue.title, "Updated Title")

    def test_author_is_participant(self):
        """
        Author should be a participant.
        """
        dialogue = Dialogue.objects.create(
            summary="Testing",
            title="Testing",
            author=self.user
        )
        participants = dialogue.participants.all()
        self.assertIn(self.user, participants)


class PostModelTests(TestCase):
    """
    Testing suite for Post model.

    Tests included:
        1. Successfully create a post in a dialogue
        2. Post shows up in dialogue.posts
        2. Post without body not created
        3. Post without author not created
        4. Delete post
        5. Edit post
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
        Post successfully created with required values.
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
        Post should be found in `posts` attribute of dialogue instance.
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
        Creating a post without a body should fail.
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
        Creating post without an author should fail.
        """
        with self.assertRaises(ValidationError):
            Post.objects.create(
                dialogue=self.dialogue,
                body="Test post",
            )
        post = Post.objects.filter(dialogue=self.dialogue)
        self.assertFalse(post.exists())

    def test_delete_post(self):
        """
        Deleting post should remove post from dialogue.
        """
        post = Post.objects.create(
            dialogue=self.dialogue,
            author=self.user1,
            body="Test post",
        )
        self.assertIn(post, self.dialogue.posts.all())
        self.assertEqual(self.dialogue.posts.count(), 1)
        post.delete()
        self.assertNotIn(post, self.dialogue.posts.all())
        self.assertEqual(self.dialogue.posts.count(), 0)

    def test_edit_post(self):
        """
        Editing post should update post body.
        """
        post = Post.objects.create(
            dialogue=self.dialogue,
            author=self.user1,
            body="Test post",
        )
        self.assertIn(post, self.dialogue.posts.all())
        self.assertEqual(self.dialogue.posts.count(), 1)
        post.body = "Updated post"
        post.save()
        self.assertIn(post, self.dialogue.posts.all())
        self.assertEqual(self.dialogue.posts.count(), 1)
        self.assertEqual(post.body, "Updated post")
