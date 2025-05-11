from django.contrib.auth import get_user, get_user_model, login
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.dashboard_url = reverse("dashboard:home")
        self.good_login_credentials = {
            "username": "testuser",
            "password": "somepassword123"
        }
        self.bad_login_credentials = {
            "username": "testuser",
            "password": "wrongpassword123"
        }
        self.test_login_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="somepassword123"
        )

    def test_login_page_loads(self):
        # make GET request to login URL
        response = self.client.get(self.login_url)

        # check that response status is 200
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_successful_login(self):
        # log in user via POST request
        response = self.client.post(
            self.login_url,
            self.good_login_credentials
        )

        # check that user is logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_successful_login_redirect(self):
        # log in user via POST request
        response = self.client.post(
            self.login_url,
            self.good_login_credentials
        )

        # check that response redirects to dashboard
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_wrong_password(self):
        # try to log in with wrong password
        response = self.client.post(
            self.login_url,
            self.bad_login_credentials
        )

        # check that user is not logged in
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_failed_login_redirect(self):
        # try to log in with wrong password
        response = self.client.post(
            self.login_url,
            self.bad_login_credentials,
            follow=True
        )

        # check that redirect chain is empty
        self.assertEqual(response.redirect_chain, [])

class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("accounts:login")
        self.logout_url = reverse("accounts:logout")
        self.login_credentials = {
            "username": "testuser",
            "password": "somepassword123"
        }
        self.test_login_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="somepassword123"
        )

    def test_successful_logout(self):
        # login in user via POST request
        response = self.client.post(self.login_url, self.login_credentials)

        # check that user is logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # log out user via POST request
        self.client.post(self.logout_url)

        # check that user is not logged in
        user_after_logout = get_user(self.client)
        self.assertFalse(user_after_logout.is_authenticated)

    def test_logout_redirect(self):
        # login in user via POST request
        self.client.post(self.login_url, self.login_credentials)

        # verify successful login
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # log out user via POST request
        response = self.client.post(self.logout_url)

        # check that response redirects to login page
        self.assertRedirects(response, reverse('accounts:login'))


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("accounts:login")
        self.register_url = reverse("accounts:register")
        self.good_registration_credentials = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "somepassword123",
            "password2": "somepassword123",
        }
        self.bad_registration_credentials = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "somepassword123",
            "password2": "mismatchedpassword"
        }

    def test_register_page_loads(self):
        # make GET request to register URL
        response = self.client.get(self.register_url)

        # check for successful response status
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("accounts/register.html")

    def test_successful_registration(self):
        # register user via POST request
        self.client.post(
            self.register_url,
            self.good_registration_credentials
        )

        # check that user is not logged in
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_successful_registration_redirect(self):
        # register user via POST request
        response = self.client.post(
            self.register_url,
            self.good_registration_credentials
        )

        # check that successful registration redirects to dashboard
        self.assertRedirects(response, reverse("accounts:login"))

    def test_failed_registration(self):
        # register user via POST request
        response = self.client.post(
            self.register_url,
            self.bad_registration_credentials
        )

        # check that user is not authenticated
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_failed_registration_redirect(self):
        # register user via POST request
        response = self.client.post(
            self.register_url,
            self.bad_registration_credentials,
            follow=True
        )

        # check that there is no redirect
        self.assertEqual(response.redirect_chain, [])
