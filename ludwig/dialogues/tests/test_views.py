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
        1. Query value greater than 2 characters should be in context data
        2. Query values less than 2 characters should return None
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
        Query values greater than 2 characters should be in context
        data.
        """
        query = "Test"
        response = self.client.get(
            reverse("dialogues:search_users"),
            {"query": query}
        )
        self.assertEqual(response.context_data.get("query"), query)

    def test_short_query(self):
        """
        Query with less than 2 characters should be in context data
        with a value of None.
        """
        query = "x"
        response = self.client.get(
            reverse("dialogues:search_users"),
            {"query": query}
        )
        self.assertEqual(response.context_data.get("query"), None)


class DialogueDetailViewTests(TestCase):
    """
    Testing suite for DialogueDetailView.

    Tests included:
        1. Successful page load of private dialogue
        2. Successful page load of public dialogue
        3. New post rendered in dialogue
        4. HTMX post returns partial template
        5. Non-participant can view public dialogue
        6. Non-participant cannot view private dialogue
    """
    def setUp(self):
        """
        Initial setup of testing suite.
        """
        self.client1 = Client()
        self.client2 = Client()

        self.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@example.com",
            password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="testpassword"
        )

        self.client1.post(reverse("accounts:login"), {
            "username": "testuser1",
            "password": "testpassword"
        })
        self.client2.post(reverse("accounts:login"), {
            "username": "testuser2",
            "password": "testpassword"
        })

        self.private_dialogue = Dialogue.objects.create(
            title="Private test dialogue",
            summary="Testy business",
            author=self.user1
        )
        self.private_dialogue_url = reverse(
            "dialogues:dialogue_detail",
            args=[self.private_dialogue.id]
        )

        self.public_dialogue = Dialogue.objects.create(
            title="Public test dialogue",
            summary="Testosteroni",
            author=self.user1,
            is_visible=True
        )
        self.public_dialogue_url = reverse(
            "dialogues:dialogue_detail",
            args=[self.public_dialogue.id]
        )

    def test_successful_page_load_private_dialogue(self):
        """
        Detail page should successfully load private dialogue with
        dialogue detail template.
        """
        response = self.client1.get(self.private_dialogue_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(TemplateName.DIALOGUE_DETAIL)
        self.assertFalse(self.private_dialogue.is_visible)

    def test_successful_page_load_public_dialogue(self):
        """
        Detail page should successfully load public dialogue with
        dialogue detail template.
        """
        response = self.client1.get(self.public_dialogue_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(TemplateName.DIALOGUE_DETAIL)
        self.assertTrue(self.public_dialogue.is_visible)

    def test_new_post(self):
        """
        New post should be rendered in dialogue.
        """
        post_body = "Hello world"
        response = self.client.get(self.private_dialogue_url)
        self.assertNotIn(post_body, response.text)
        self.client1.post(self.private_dialogue_url, {
            "body": post_body
        })
        response = self.client1.get(self.private_dialogue_url)
        self.assertIn(post_body, response.text)

    def test_htmx_post_response(self):
        """
        New posts with HTMX should return partial template containing
        post body and `last_id` of post.
        """
        post_body = "Hello world"
        response = self.client1.post(
            self.private_dialogue_url,
            {"body": post_body},
            headers={
                "HX-Request": True
            })
        self.assertIn(post_body, response.text)
        self.assertTrue(response.context.get("last_id"))

    def test_nonparticipant_can_view_public_dialogue(self):
        """
        Non-participants should be able to view public dialogues.
        """
        self.assertIn(self.user1, self.public_dialogue.participants.all())
        self.assertNotIn(self.user2, self.public_dialogue.participants.all())
        self.assertTrue(self.public_dialogue.is_visible)
        response = self.client2.get(self.public_dialogue_url)
        self.assertEqual(response.status_code, 200)

    def test_nonparticipant_cannot_view_private_dialogue(self):
        """
        Non-participants should not be able to view private dialogues.
        """
        self.assertIn(self.user1, self.private_dialogue.participants.all())
        self.assertNotIn(self.user2, self.private_dialogue.participants.all())
        self.assertFalse(self.private_dialogue.is_visible)
        response = self.client2.get(self.private_dialogue_url)
        self.assertEqual(response.status_code, 403)


class DeleteDialogueViewTests(TestCase):
    """
    Testing suite for DeleteDialogueView.

    Tests included:
        1. Successfully delete dialogue
        2. Must be author to delete dialogue
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

        self.dialogue = Dialogue.objects.create(
            author=self.user,
            title="To be deleted dialogue"
        )

    def test_delete_dialogue(self):
        """
        POST request to `delete_dialogue` URL should remove dialogue
        from the database.
        """
        self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "password": "testpassword"
        })

        self.assertTrue(
            Dialogue.objects.filter(id=self.dialogue.id).exists()
        )

        self.client.post(reverse(
            "dialogues:delete_dialogue",
            args=[self.dialogue.id]
        ))

        self.assertFalse(
            Dialogue.objects.filter(id=self.dialogue.id).exists()
        )

    def test_login_required_for_delete(self):
        """
        User should not be able to delete dialogue if not dialogue author.
        """
        User.objects.create_user(
            username="randomuser",
            email="randomuser@example.com",
            password="randompassword"
        )

        self.client.post(reverse("accounts:login"), {
            "username": "randomuser",
            "password": "randompassword"
        })

        random_user = get_user(self.client)

        self.assertEqual(self.dialogue.author, self.user)
        self.assertNotEqual(self.dialogue.author, random_user)
        self.assertTrue(random_user.is_authenticated)

        response = self.client.post(reverse(
            "dialogues:delete_dialogue",
            args=[self.dialogue.id]
        ))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Dialogue.objects.filter(id=self.dialogue.id).exists()
        )
