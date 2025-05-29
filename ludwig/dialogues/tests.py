from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.urls import reverse

from .models import Dialogue, Post

User = get_user_model()


class DialogueCreationTests(TestCase):
    """Test cases for dialogue creation functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.login_url = reverse("accounts:login")
        self.dialogue_create_url = reverse("dialogues:create_dialogue")

    def _dialogue_exists(self, title):
        """Check if dialogue with given title exists in database."""
        return Dialogue.objects.filter(title=title).exists()

    def test_successful_dialogue_creation(self):
        """Dialogue should exist in database after creation."""
        dialogue = Dialogue.objects.create(title="Test Dialogue", author=self.user)
        self.assertTrue(self._dialogue_exists("Test Dialogue"))
        self.assertEqual(dialogue.author, self.user)

    def test_creation_success_with_post(self):
        """Dialogue should be created via POST request from authenticated user."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            self.dialogue_create_url,
            {"title": "POST Created Dialogue", "summary": "Test summary"},
        )

        self.assertTrue(self._dialogue_exists("POST Created Dialogue"))
        dialogue = Dialogue.objects.get(title="POST Created Dialogue")
        self.assertEqual(dialogue.author, self.user)
        self.assertEqual(response.status_code, 302)

    def test_creation_failure_without_auth(self):
        """POST request should fail for unauthenticated users."""
        response = self.client.post(
            self.dialogue_create_url, {"title": "Unauthorized Dialogue"}
        )

        self.assertFalse(self._dialogue_exists("Unauthorized Dialogue"))
        self.assertRedirects(response, "/auth/login/?next=/dialogue/create/")


class DialoguePermissionsTests(TestCase):
    """Test cases for dialogue access permissions."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.author = User.objects.create_user(
            username="author", email="author@example.com", password="pass123"
        )
        self.participant = User.objects.create_user(
            username="participant", email="participant@example.com", password="pass123"
        )
        self.outsider = User.objects.create_user(
            username="outsider", email="outsider@example.com", password="pass123"
        )

        self.private_dialogue = Dialogue.objects.create(
            title="Private Dialogue", author=self.author, is_visible=False
        )
        self.private_dialogue.participants.add(self.author, self.participant)

        self.public_dialogue = Dialogue.objects.create(
            title="Public Dialogue", author=self.author, is_visible=True
        )

    def test_participant_can_access_private_dialogue(self):
        """Participants should be able to access private dialogues."""
        self.client.login(username="participant", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.private_dialogue.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Private Dialogue")

    def test_outsider_cannot_access_private_dialogue(self):
        """Non-participants should not be able to access private dialogues."""
        self.client.login(username="outsider", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.private_dialogue.id])
        response = self.client.get(url)

        self.assertRaises(PermissionDenied)

    def test_anyone_can_access_public_dialogue(self):
        """Anyone should be able to access public dialogues."""
        self.client.login(username="outsider", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.public_dialogue.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Public Dialogue")


class PostCreationTests(TestCase):
    """Test cases for post creation within dialogues."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="poster", email="poster@example.com", password="pass123"
        )
        self.dialogue = Dialogue.objects.create(title="Test Dialogue", author=self.user)
        self.dialogue.participants.add(self.user)

    def test_participant_can_create_post(self):
        """Participants should be able to create posts."""
        self.client.login(username="poster", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.dialogue.id])

        response = self.client.post(url, {"body": "This is a test post"})

        self.assertTrue(Post.objects.filter(body="This is a test post").exists())
        post = Post.objects.get(body="This is a test post")
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.dialogue, self.dialogue)

    def test_empty_post_not_created(self):
        """Empty posts should not be created."""
        self.client.login(username="poster", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.dialogue.id])

        response = self.client.post(
            url,
            {
                "body": "   ",
            },
        )

        self.assertEqual(Post.objects.count(), 0)


class HTMXFunctionalityTests(TestCase):
    """Test cases for HTMX real-time functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="htmxuser", email="htmx@example.com", password="pass123"
        )
        self.dialogue = Dialogue.objects.create(title="HTMX Dialogue", author=self.user)
        self.dialogue.participants.add(self.user)

    def test_htmx_post_creation_returns_partial(self):
        """HTMX post requests should return partial HTML."""
        self.client.login(username="htmxuser", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.dialogue.id])

        response = self.client.post(
            url, {"body": "HTMX test post"}, HTTP_HX_REQUEST="true"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HTMX test post")
        self.assertIn("HX-Request", response.get("Vary", ""))

    def test_polling_returns_new_posts(self):
        """Polling endpoint should return new posts."""
        self.client.login(username="htmxuser", password="pass123")
        self.assertContains
        existing_post = Post.objects.create(
            body="Existing post", author=self.user, dialogue=self.dialogue
        )

        new_post = Post.objects.create(
            body="New post", author=self.user, dialogue=self.dialogue
        )

        url = reverse("dialogues:polling", args=[self.dialogue.id])
        response = self.client.get(url, {"last_id": existing_post.id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New post")
        self.assertNotContains(response, "Existing post")


class SecurityAndDuplicationTests(TestCase):
    """Test cases for security and preventing duplications."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.participant = User.objects.create_user(
            username="participant", email="participant@example.com", password="pass123"
        )
        self.non_participant = User.objects.create_user(
            username="nonparticipant",
            email="nonparticipant@example.com",
            password="pass123",
        )
        self.dialogue = Dialogue.objects.create(
            title="Test Dialogue", author=self.participant, is_visible=True
        )
        self.dialogue.participants.add(self.participant)

    def test_no_duplicate_posts_from_polling(self):
        """Polling should not return duplicate posts."""
        post = Post.objects.create(
            body="Test post for polling",
            author=self.participant,
            dialogue=self.dialogue,
        )

        url = reverse("dialogues:polling", args=[self.dialogue.id])
        response1 = self.client.get(url)
        self.assertContains(response1, "Test post for polling")

        response2 = self.client.get(url)
        content = response2.content.decode()

        post_count = content.count("Test post for polling")
        self.assertEqual(post_count, 1)

        response3 = self.client.get(url, {"last_id": post.id})
        self.assertNotContains(response3, "Test post for polling")

    def test_no_duplicate_posts_from_creation(self):
        """Creating a post should not create duplicates."""
        self.client.login(username="participant", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.dialogue.id])

        response = self.client.post(url, {"body": "Unique test post"})

        posts = Post.objects.filter(body="Unique test post")
        self.assertEqual(posts.count(), 1)

        response2 = self.client.post(url, {"body": "Unique test post"})

        posts = Post.objects.filter(body="Unique test post")
        self.assertLessEqual(posts.count(), 2)

    def test_form_rendered_for_participants(self):
        """Post form should be rendered for participants."""
        self.client.login(username="participant", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.dialogue.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="post_form"')
        self.assertContains(response, 'name="body"')
        self.assertContains(response, "Submit post")

    def test_form_not_rendered_for_non_participants(self):
        """Post form should not be rendered for non-participants."""
        self.client.login(username="nonparticipant", password="pass123")
        url = reverse("dialogues:dialogue_detail", args=[self.dialogue.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="post_form"')
        self.assertNotContains(response, 'name="body"')
        self.assertNotContains(response, "Submit post")
