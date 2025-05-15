from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.views.generic.base import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Display dashboard and show most recent dialogues.
    """

    template_name = "dashboard/dashboard.html"

    def _get_recent_user_dialogues(self):
        """Get recent user dialogues, sorted by most recent post"""
        user = get_user(self.request)
        user_dialogues = user.dialogues.annotate(
            latest_post_date=Max('posts__created_on')
        ).values(
            "id", "title", "latest_post_date"
        ).order_by('-latest_post_date')
        return user_dialogues

    def get_context_data(self, **kwargs):
        """Add user's recent dialogues to the view context"""
        context = super().get_context_data(**kwargs)
        context["user_dialogues"] = self._get_recent_user_dialogues()
        return context
