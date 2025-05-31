from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls.base import reverse

from ..constants import TemplateName
from ..models import Dialogue


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
        6. Successful dialogue creation redirects to dialogue detail
        7. Failed dialogue creation stays on dialogue creation page
        8. User must be logged in to create a dialogue
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
        self.user3 = User.objects.create_user(
            username="testuser3",
            email="testuser3@example.com",
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

    def test_participant_addition(self):
        """
        Add multiple participants to a dialogue.
        """
        response = self.client.post(
            self.create_dialogue_url,
            {
                "title": "Test dialogue",
                "summary": "Test summary",
                "participants": [self.user2.id, self.user3.id]
            }
        )

        dialogue = Dialogue.objects.get(title="Test dialogue")

        self.assertEqual(dialogue.participants.count(), 3)
        self.assertIn(self.user2, dialogue.participants.all())
        self.assertIn(self.user3, dialogue.participants.all())
        self.assertIn(self.user1, dialogue.participants.all())

    def test_summary_optional(self):
        """
        Creating a dialogue without a summary should succeed.
        """
        response = self.client.post(
            self.create_dialogue_url,
            {"title": "Test dialogue"}
        )

        dialogue = Dialogue.objects.get(title="Test dialogue")

        self.assertEqual(dialogue.title, "Test dialogue")
        self.assertEqual(dialogue.summary, "")

    def test_successful_dialogue_creation_redirects_to_detail(self):
        """
        Successful dialogue creation should redirect to the dialogue detail page.
        """
        response = self.client.post(
            self.create_dialogue_url,
            {"title": "Test dialogue"},
            follow=True
        )

        self.assertTemplateUsed(response, TemplateName.DIALOGUE_DETAIL)

    def test_failed_dialogue_creation_redirect(self):
        """
        Failed dialogue creation should keep user on dialogue creation page.
        """
        response = self.client.post(
            self.create_dialogue_url,
            {"title": ""}
        )

        self.assertNotEqual(response.status_code, 302)
        self.assertTemplateUsed(response, TemplateName.CREATE_DIALOGUE)

    def test_auth_required_for_dialogue_creation(self):
        """
        User must be logged in to successfully create a dialogue.
        """
        # Store title as variable to avoid typo-related errors
        dialogue_title = "Unauthorized dialogue"

        # Log out user to make sure that they can't create a dialogue
        # while not authenticated.
        self.client.post(reverse("accounts:logout"))
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.client.post(self.create_dialogue_url, {"title": dialogue_title})
        with self.assertRaises(Dialogue.DoesNotExist):
            Dialogue.objects.get(title=dialogue_title)

        # Log in user to successfully create a dialogue
        self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "testpassword"
        })
        self.client.post(self.create_dialogue_url, {"title": dialogue_title})
        dialogue = Dialogue.objects.get(title=dialogue_title)
        self.assertTrue(dialogue.id)
        self.assertEqual(dialogue.title, dialogue_title)


class SearchForUsersViewTests(TestCase):
    """
    Testing suite for SearchForUsersView.

    Tests included:
        1. Query should be in context data
    """
    def setUp(self):
        """
        Initial setup for testing suite.
        """
        self.client = Client()

        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )

        self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "testpassword"
        })

    def test_search_query(self):
        """
        Query value should be in context data.
        """
        query = "Test"
        response = self.client.get(
            reverse("dialogues:search_users"),
            {"query": query}
        )
        self.assertEqual(response.context_data.get("query"), query)

    def test_short_query(self):
        """
        Query with less than two characters should return None.
        """
        query = "x"
        response = self.client.get(
            reverse("dialogues:search_users"),
            {"query": query}
        )
        self.assertEqual(response.context_data.get("query"), None)
