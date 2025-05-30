import re
from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from ludwig.dialogues.models import Dialogue, Post

from ..constants import TemplateName


class DashboardViewTest(TestCase):
    """
    Test suite for user dashboard view.

    Tests included:
        1. Redirect unauthenticated users to login page
        2. Load page for authenticated users
        3. Of two empty dialogues, the most recently created should be
           shown first
        4. Posts should modify the order of the list of user dialogues
        5. Non-participant dialogues should not show up in list of user
           dialogues
    """

    def setUp(self):
        """
        Initial set up for the testing suite.
        """
        self.client = Client()

        # Create a test user
        User = get_user_model()
        self.test_user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@example.com",
            password="testpassword123",
        )

        # Create two test dialogues to see how they are reordered
        # after posts are submitted.
        self.dialogue1_title = "Dialogue #1"
        self.dialogue1 = Dialogue.objects.create(
            title=self.dialogue1_title
        )
        self.dialogue1.participants.set([self.test_user1])

        self.dialogue2_title = "Dialogue #2"
        self.dialogue2 = Dialogue.objects.create(
            title=self.dialogue2_title
        )
        self.dialogue2.participants.set([self.test_user1])

        # Store URLs for reuse
        self.dashboard_url = reverse("dashboard:home")
        self.login_url = reverse("accounts:login")

        # Store login credentials for reuse
        self.good_login_credentials = {
            "username": "testuser1",
            "password": "testpassword123",
        }

    def test_redirect_for_unauthenticated_user(self):
        """
        Unauthenticated users should be redirected to login page.
        """
        response = self.client.get(self.dashboard_url, follow=True)
        self.assertRedirects(response, "/auth/login/?next=/dashboard/")

    def test_page_load_for_authenticated_user(self):
        """
        Dashboard should successfully load for authenticated users by
        checking for successful response and dashboard template.
        """
        self.client.post(self.login_url, self.good_login_credentials)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TemplateName.DASHBOARD)

    def _get_dialogue_title_elements(self, text) -> list:
        """
        Get a list of all `p` elements with a class of `dialogue-title`
        in the list of user dialogues on the dashboard.
        """
        return re.findall(
            r'<p class="dialogue-title">.*?<\/p>', text
        )

    def test_empty_dialogue_order(self):
        """
        Test for most recently created dialogue at the top of the list
        of user dialogues. Since the dialogues are both empty, ordering
        should be determined by the `created_on` datetime.
        """
        self.client.post(self.login_url, self.good_login_credentials)

        # Get a list of all `p` elements in the dashboard with class
        # `dialogue-title`
        response = self.client.get(self.dashboard_url)
        dialogue_titles = self._get_dialogue_title_elements(response.text)

        # Dialogue 2 should be at the top of the list since it was
        # created most recently
        top_dialogue = dialogue_titles[0]
        self.assertIn(self.dialogue2_title, top_dialogue)

    def test_post_reorders_dialogue_list(self):
        """
        Test reordering of dialogues in the dashboard list of user
        dialogues.

        Order priority:
            1. Empty dialogues always at top, ordered by `created_on`
               if multiple empties exist
            2. Dialogues with posts ordered by most recently created
               posts
        """
        self.client.post(self.login_url, self.good_login_credentials)

        user = get_user(self.client)

        # Post in Dialogue 1
        Post.objects.create(
            dialogue=self.dialogue1,
            body="Test post",
            author=user
        )

        # Dialogue 2 should be at the top still because it is empty
        response = self.client.get(self.dashboard_url)
        dialogue_titles = self._get_dialogue_title_elements(response.text)
        top_dialogue = dialogue_titles[0]
        self.assertIn(self.dialogue2_title, top_dialogue)

        # Post in Dialogue 2
        Post.objects.create(
            dialogue=self.dialogue2,
            body="Test post",
            author=user
        )

        # Both dialogues have posts now and Dialogue 2 will remain at
        # the top since it has the most recent post
        response = self.client.get(self.dashboard_url)
        dialogue_titles = self._get_dialogue_title_elements(response.text)
        top_dialogue = dialogue_titles[0]
        self.assertIn(self.dialogue2_title, top_dialogue)

        # Post in Dialogue 1 again
        Post.objects.create(
            dialogue=self.dialogue1,
            body="Another test post",
            author=user
        )

        # Dialogue 1 should be at the top of the list now because both
        # dialogues have posts and Dialogue 1 has the most recent post
        response = self.client.get(self.dashboard_url)
        dialogue_titles = self._get_dialogue_title_elements(response.text)
        top_dialogue = dialogue_titles[0]
        self.assertIn(self.dialogue1_title, top_dialogue)

        # Post in Dialogue 2 again
        Post.objects.create(
            dialogue=self.dialogue2,
            body="Test post",
            author=user
        )

        # Dialogue 2 should be at the top of the list again because both
        # dialogues have posts and Dialogue 2 has the most recent post
        response = self.client.get(self.dashboard_url)
        dialogue_titles = self._get_dialogue_title_elements(response.text)
        top_dialogue = dialogue_titles[0]
        self.assertIn(self.dialogue2_title, top_dialogue)

    def test_nonparticipant_dialogues_not_shown(self):
        """
        Test that dialogues excluding the current user are not shown in
        the list of the user's dialogues. Additionally, check that the
        dialogue shows up in the user's dialogues after being added as
        a participant.
        """
        self.client.post(self.login_url, self.good_login_credentials)

        # Create second test user
        User = get_user_model()
        self.other_test_user = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="testpassword456",
        )

        # Create a dialogue authored by testuser2
        other_user_dialogue = Dialogue.objects.create(
            title="Secret dialogue",
            author=self.other_test_user
        )

        # Dialogue of testuser2 should not show up in list of
        # testuser1's dialogues since they are not a participant in the
        # dialogue
        response = self.client.get(self.dashboard_url)
        dialogue_titles = self._get_dialogue_title_elements(response.text)
        self.assertNotIn(
            '<p class="dialogue-title">Secret dialogue</p>',
            dialogue_titles
        )

        # Add testuser1 to testuser2's dialogue
        user = get_user(self.client)
        other_user_dialogue.participants.add(user)

        # Dialogue authored by testuser2 should now be in the list of
        # testuser1's dialogues
        response = self.client.get(self.dashboard_url)
        dialogue_titles = self._get_dialogue_title_elements(response.text)
        self.assertIn(
            '<p class="dialogue-title">Secret dialogue</p>',
            dialogue_titles
        )
