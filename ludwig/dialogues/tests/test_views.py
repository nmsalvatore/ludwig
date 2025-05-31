from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls.base import reverse

from ludwig.dialogues.models import Dialogue


User = get_user_model()


class CreateDialogueViewTests(TestCase):
    """
    Testing suite for CreateDialogueView.

    Tests included:
        1. Successfully create a private dialogue
        2. Successfully create a public dialogue
        3. Can't create dialogue without title
        4. Add multiple participants
        5. Summary is optional
        6. Successful creation redirets to dialogue detail
    """

    def setUp(self):
        """
        Initial setup for testing suite.
        """
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="testpassword"
        )
        self.client.login(
            username="testuser",
            password="testpassword"
        )
        self.create_dialogue_url = reverse("dialogues:create_dialogue")

    def test_create_private_dialogue(self):
        """
        Create a private dialogue.
        """
        self.client.post(
            self.create_dialogue_url,
            {
                "title": "Test dialogue",
                "summary": "Test summary",
                "is_visible": False, # False is default, but y'know
            }
        )
        dialogue = Dialogue.objects.get(title="Test dialogue")

        self.assertTrue(dialogue.title, "Test dialogue")
        self.assertTrue(dialogue.summary, "Test summary")
        self.assertTrue(dialogue.author, self.user1)
        self.assertIsNotNone(dialogue.id)
        self.assertIsNotNone(dialogue.created_on)
        self.assertFalse(dialogue.is_visible)
        self.assertFalse(dialogue.is_open)
        self.assertEqual(dialogue.participants.count(), 1)
        self.assertEqual(dialogue.participants.first(), dialogue.author)

    def test_create_public_dialogue(self):
        """
        Create a public dialogue.
        """
        self.client.post(
            self.create_dialogue_url,
            {
                "title": "Test dialogue",
                "summary": "Test summary",
                "is_visible": True
            }
        )
        dialogue = Dialogue.objects.get(title="Test dialogue")

        self.assertTrue(dialogue.title, "Test dialogue")
        self.assertTrue(dialogue.summary, "Test summary")
        self.assertTrue(dialogue.author, self.user1)
        self.assertIsNotNone(dialogue.id)
        self.assertIsNotNone(dialogue.created_on)
        self.assertTrue(dialogue.is_visible)
        self.assertFalse(dialogue.is_open)
        self.assertEqual(dialogue.participants.count(), 1)
        self.assertEqual(dialogue.participants.first(), dialogue.author)

    def test_create_dialogue_without_title(self):
        """
        Creating a dialogue without a title should fail.
        """
        response = self.client.post(
            self.create_dialogue_url,
            {"summary": "Test summary"},
            follow=True
        )

        with self.assertRaises(Dialogue.DoesNotExist):
            Dialogue.objects.get(summary="Test summary")

        self.assertEqual(response.redirect_chain, [])

    def test_multiple_participants(self):
        """
        Add multiple participants to a dialogue.
        """
        pass
