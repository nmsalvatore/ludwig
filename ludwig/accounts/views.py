from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserLoginForm, UserRegistrationForm


class UserRegistrationView(SuccessMessageMixin, CreateView):
    """
    Defines user registration view that displays user registation form
    and creates a new user with CreateView.
    """

    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("accounts:login")
    success_message = "Registration successful! Please login with your new credentials."


class UserLoginView(LoginView):
    """
    Defines user login view that displays login form and logs in user.
    """

    template_name = "accounts/login.html"
    authentication_form = UserLoginForm


class UserLogoutView(LogoutView):
    """
    Defines user logout view that logs out user.
    """

    next_page = reverse_lazy("accounts:login")
