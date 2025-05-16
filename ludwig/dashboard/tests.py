from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse


class DashboardViewTest(TestCase):
    def setUp(self):
        User = get_user_model()

        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123"
        )

        self.client = Client()
        self.dashboard_url = reverse("dashboard:home")
        self.login_url = reverse("accounts:login")
        self.good_login_credentials = {
            "username": "testuser",
            "password": "testpassword123"
        }

    def test_redirect_for_unauthenticated_user(self):
        """Unauthenticated users should be redirected to login page"""
        response = self.client.get(self.dashboard_url, follow=True)
        self.assertRedirects(response, "/auth/login/?next=/dashboard/")

    def test_page_load_for_authenticated_user(self):
        """Dashboard should load for authenticated users"""
        self.client.post(self.login_url, self.good_login_credentials)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
