from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .constants import TemplateName
from .forms import UserLoginForm, UserRegistrationForm


class UserRegistrationView(SuccessMessageMixin, CreateView):
    """
    Defines user registration view that displays the user registation
    form, creates a new user, then redirects to the login page.
    """

    template_name = TemplateName.REGISTER
    form_class = UserRegistrationForm
    success_url = reverse_lazy("accounts:login")
    success_message = "Registration successful! Please login with your new credentials."


class UserLoginView(LoginView):
    """
    Defines user login view that displays login form and logs in user.
    """

    template_name = TemplateName.LOGIN
    authentication_form = UserLoginForm


class UserLogoutView(LoginRequiredMixin, LogoutView):
    """
    Defines user logout view that logs out user and redirects to the
    login page.
    """

    next_page = reverse_lazy("accounts:login")
