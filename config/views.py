from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView


class IndexView(LoginRequiredMixin, RedirectView):
    """
    Direct logged in users to dashboard, otherwise to direct to login.
    """

    url = reverse_lazy("dashboard:home")
