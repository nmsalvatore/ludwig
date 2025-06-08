from django.contrib.auth import get_user, get_user_model, login
from django.test import Client, TestCase
from django.urls import reverse

from ..constants import TemplateName


User = get_user_model()


class LoginViewTests(TestCase):
    """
    Testing suite for login view.

    Tests included:
        1. Successful page load
        2. Successful login with good credentials
        3. Successful login redirects users to dashboard
        4. Failed login with bad credentials
        5. Failed login doesn't redirect to dashboard
    """

    def setUp(self):
        """
        Initial setup for login view testing suite.
        """
        self.client = Client()

        # Create a test user
        self.test_login_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="somepassword123"
        )

        # URLs
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.dashboard_url = reverse("dashboard:home")

        # Login credentials
        self.good_login_credentials = {
            "username": "testuser",
            "password": "somepassword123",
        }
        self.bad_login_credentials = {
            "username": "testuser",
            "password": "wrongpassword123",
        }

    def test_login_page_loads(self):
        """
        Test for successful page load by checking for successful
        response to the login URL and that the login template is used.
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, TemplateName.LOGIN)

    def test_successful_login(self):
        """
        Test that the user is authenticated after a successful login
        with good credentials.
        """
        response = self.client.post(
            self.login_url,
            self.good_login_credentials
        )
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_successful_login_redirect(self):
        """
        Test for redirect to the user dashboard after a successful
        login.
        """
        response = self.client.post(self.login_url, self.good_login_credentials)
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_wrong_password(self):
        """
        Test that user is not authenticated after a failed login
        attempt with bad credentials.
        """
        response = self.client.post(self.login_url, self.bad_login_credentials)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_failed_login_redirect(self):
        """
        Test that no redirect takes place after a failed login attempt.
        """
        response = self.client.post(
            self.login_url, self.bad_login_credentials, follow=True
        )
        self.assertEqual(response.redirect_chain, [])


class LogoutViewTests(TestCase):
    """
    Testing suite for logout view.

    Tests included:
        1. Successful logout
        2. Redirect to login page after logout
        3. Logout message shown on login page after logout
    """

    def setUp(self):
        """
        Initial setup for logout view testing suite.
        """
        self.client = Client()

        # Create test user
        self.test_login_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="somepassword123"
        )

        # URLs
        self.login_url = reverse("accounts:login")
        self.logout_url = reverse("accounts:logout")

        # Login credentials
        self.login_credentials = {
            "username": "testuser",
            "password": "somepassword123"
        }

    def test_successful_logout(self):
        """
        Test that a logged in user is not authenticated after
        successfully logging out.
        """
        # Log in user
        response = self.client.post(
            self.login_url,
            self.login_credentials
        )

        # Make sure that user has successfully logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # Log out user
        self.client.post(self.logout_url)

        # Check that user is not authenticated
        user_after_logout = get_user(self.client)
        self.assertFalse(user_after_logout.is_authenticated)

    def test_logout_redirect(self):
        """
        Test that a logged in user is redirected to the login page
        after successfully logging out.
        """
        # Log in user
        self.client.post(self.login_url, self.login_credentials)

        # Make sure that user has successfully logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # Log out user
        response = self.client.post(self.logout_url)

        # Check that user is directed to login page after logging out
        self.assertRedirects(response, reverse("accounts:login"))

    def test_logged_out_message(self):
        """
        Test that login page shows the 'You have been successfully
        logged out` message after a successful logout.
        """
        # Log in user
        self.client.post(self.login_url, self.login_credentials)

        # Make sure that user has successfully logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # Log out user
        response = self.client.post(self.logout_url, follow=True)

        # Check the success message is shown on the login page
        success_message = "You have been successfully logged out."
        self.assertIn(success_message, response.text)


class RegisterViewTests(TestCase):
    """
    Testing suite for account registration view.

    Tests included:
        1. Successful page load
        2. Successful registration
        3. Redirect to login page after successful registration
        4. Login page has success message after registration
        5. Failed registration
        6. No redirect if registration fails
    """

    def setUp(self):
        """
        Initial setup for registration view testing suite.
        """
        self.client = Client()

        # URLs
        self.login_url = reverse("accounts:login")
        self.register_url = reverse("accounts:register")

        # Registration credentials
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
            "password2": "mismatchedpassword",
        }

    def test_register_page_loads(self):
        """
        Test for successful page load by checking for successful
        response from the register URL and that the correct template
        is used.
        """
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(TemplateName.REGISTER)

    def test_successful_registration(self):
        """
        Test for successful registration by checking that the user
        exists in the database after registration and that they can
        successfully login.
        """
        # Check that the user does not exist in the database prior to
        # registration
        unregistered_user = User.objects.filter(
            username=self.good_registration_credentials["username"],
            email=self.good_registration_credentials["email"]
        )
        assert not unregistered_user.exists()

        # Register user
        self.client.post(
            self.register_url,
            self.good_registration_credentials
        )

        # User should now be in the database
        registered_user = User.objects.filter(
            username=self.good_registration_credentials["username"],
            email=self.good_registration_credentials["email"]
        )
        assert registered_user.exists()

        # Log in user
        self.client.post(self.login_url, {
            "username": self.good_registration_credentials["username"],
            "password": self.good_registration_credentials["password1"]
        })

        # User should now be authenticated
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_successful_registration_redirect(self):
        """
        Test to see if user is redirected to the login page after a
        successful registration.
        """
        response = self.client.post(
            self.register_url,
            self.good_registration_credentials
        )
        self.assertRedirects(response, reverse("accounts:login"))

    def test_success_message(self):
        """
        Test for registration success message on the login page after a
        successful registration.
        """
        # Follow response to the login page
        response = self.client.post(
            self.register_url,
            self.good_registration_credentials,
            follow=True
        )

        # Check for success message on the login page
        success_message = "Registration successful! Please login with your new credentials."
        self.assertIn(success_message, response.text)

    def test_failed_registration(self):
        """
        Test for failed registration by making sure the user doesn't
        exist in the database after a failed attempt.
        """
        # Attempt registration with bad credentials (mismatched passwords)
        response = self.client.post(
            self.register_url,
            self.bad_registration_credentials
        )

        # User should not exist in the database
        user = User.objects.filter(
            username=self.bad_registration_credentials["username"],
            email=self.bad_registration_credentials["email"]
        )
        assert not user.exists()


    def test_failed_registration_redirect(self):
        """
        Test to make sure the user is not redirected after a failed
        registration attempt and that they remain on the registration
        page.
        """
        response = self.client.post(
            self.register_url,
            self.bad_registration_credentials,
            follow=True
        )
        self.assertEqual(response.redirect_chain, [])
        self.assertTemplateUsed(response, TemplateName.REGISTER)
