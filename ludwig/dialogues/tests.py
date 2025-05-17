from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import get_user
from django.test import TestCase
from django.test.client import Client
from django.urls.base import reverse

from .models import Dialogue


class DialogueCreationTests(TestCase):
    def setUp(self):
        self.DIALOGUE_TEST_TITLE = "Some test dialogue"
        self.USERNAME = "sometestuser"
        self.EMAIL = "sometestuser@example.com"
        self.PASSWORD = "password234"

        self.client = Client()
        self.login_url = reverse("accounts:login")
        self.dialogue_create_url = reverse("dialogues:create_dialogue")
        self.good_login_credentials = {
            "username": self.USERNAME,
            "password": self.PASSWORD,
        }

        User = get_user_model()
        User.objects.create_user(
            username=self.USERNAME, email=self.EMAIL, password=self.PASSWORD
        )

    def _dialogue_exists(self, title):
        """Check if dialogue with given title exists in database"""
        return Dialogue.objects.filter(title=title).exists()

    def test_successful_dialogue_creation(self):
        """Dialogue should exist in database after creation."""
        Dialogue.objects.create(title=self.DIALOGUE_TEST_TITLE)
        dialogue_exists = self._dialogue_exists(self.DIALOGUE_TEST_TITLE)
        self.assertTrue(dialogue_exists)

    def test_creation_success_with_post(self):
        """
        Dialogue should exist in database after successful POST request
        from authenticated user.
        """
        self.client.post(self.login_url, self.good_login_credentials)
        self.client.post(self.dialogue_create_url, {"title": self.DIALOGUE_TEST_TITLE})
        dialogue_exists = self._dialogue_exists(self.DIALOGUE_TEST_TITLE)
        self.assertTrue(dialogue_exists)

    def test_creation_failure_without_auth(self):
        """
        POST request to dialogue creation url should fail for users
        that are not authenticated.
        """
        response = self.client.post(
            self.dialogue_create_url, {"title": self.DIALOGUE_TEST_TITLE}
        )
        dialogue_exists = self._dialogue_exists(self.DIALOGUE_TEST_TITLE)
        self.assertRedirects(response, "/auth/login/?next=/dialogue/create/")
        self.assertFalse(dialogue_exists)
