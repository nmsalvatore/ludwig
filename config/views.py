from django import template
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView, View


class IndexView(LoginRequiredMixin, RedirectView):
    """
    Logged in users are automatically directed to the user dashboard,
    while the LoginRequiredMixin will ensure that users not logged in will be
    redirected to the LOGIN_URL defined in the Django settings.
    """

    url = reverse_lazy("dashboard:home")
