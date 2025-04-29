from django.contrib.auth import get_user, get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.dashboard_url = reverse("dashboard:home")
        self.test_login_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="complexpassword123"
        )

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "complexpassword123"
        })
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_wrong_password(self):
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "complexpassword345"
        })
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
