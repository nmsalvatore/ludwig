from django.contrib.auth import get_user, get_user_model
from django.test import Client, TestCase
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
        # make GET request to login url
        response = self.client.get(self.login_url)

        # check that response status is 200
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_successful_login(self):
        # log in user via POST request
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "complexpassword123"
        })

        # check that user is logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_wrong_password(self):
        # try to log in user with wrong password
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "complexpassword345"
        })

        # check that user is not logged in
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("accounts:login")
        self.logout_url = reverse("accounts:logout")
        self.test_login_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="complexpassword123"
        )

    def test_successful_logout(self):
        # login in user via POST request
        response = self.client.post(self.login_url, {
            "username": "testuser",
            "password": "complexpassword123"
        })

        # check that user is logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # log out user via POST request
        self.client.post(self.logout_url)

        # get fresh snapshot of user
        user_after_logout = get_user(self.client)
        self.assertFalse(user_after_logout.is_authenticated)

    def test_logout_redirect(self):
        # login in user via POST request
        self.client.post(self.login_url, {
            "username": "testuser",
            "password": "complexpassword123"
        })

        # verify successful login
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # log out user via POST request
        response = self.client.post(self.logout_url)

        # check that response redirects to login page
        self.assertRedirects(response, reverse('accounts:login'))
