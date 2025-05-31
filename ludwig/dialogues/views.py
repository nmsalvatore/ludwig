from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .constants import TemplateName
from .forms import DialogueCreationForm
from .models import Dialogue, Post


class CreateDialogueView(LoginRequiredMixin, CreateView):
    """
    Display a form to create a dialogue and redirect to dialogue detail
    page on successful dialogue creation.
    """

    form_class = DialogueCreationForm
    template_name = TemplateName.CREATE_DIALOGUE

    def _add_participants_to_dialogue(self, dialogue):
        """Add current user and selected participants to dialogue."""
        # get list of user ids from hidden form input field
        user_ids = self.request.POST.getlist("selected_participants")

        if user_ids:
            # get all users with selected ids and add as participants
            User = get_user_model()
            users = User.objects.filter(id__in=user_ids)
            dialogue.participants.add(*users)

    def form_valid(self, form):
        """Save form data and redirect to dialogue detail page."""

        dialogue = form.save(commit=False)
        dialogue.author = get_user(self.request)
        dialogue.save()

        # since the Dialogue model has many-to-many relation with the
        # User model and commit=False was used to save the form, we
        # have to wait until the new dialogue instance is in the
        # database before saving the many-to-many form data
        form.save_m2m()

        # add current user and selected participants to dialogue
        self._add_participants_to_dialogue(dialogue)

        return HttpResponseRedirect(
            reverse("dialogues:dialogue_detail", args=(dialogue.id,))
        )


class SearchForUsersView(LoginRequiredMixin, TemplateView):
    """
    Display a dropdown list of users matching the query in the
    participants input of the dialogue creation form. Results are
    only shown for queries 2 or more characters long.
    """

    template_name = TemplateName.USER_SEARCH_RESULTS

    def get_context_data(self, **kwargs):
        """Pass query value and matching users to context data."""

        context = super().get_context_data(**kwargs)

        # get value of the user search query from the `query` input
        query = self.request.GET.get("query", "")

        if len(query) >= 2:
            # filter users whose display name or username contain the
            # provided query value
            User = get_user_model()
            users = User.objects.filter(
                Q(username__icontains=query) | Q(display_name__icontains=query)
            ).exclude(id=self.request.user.id)[:10]

            context.update({"query": query, "users": users})

        return context


class DialogueDetailView(DetailView):
    """
    Display a specific dialogue and manage interactivity among
    participants. Limit access based on user auth status and dialogue
    settings.
    """

    model = Dialogue
    template_name = TemplateName.DIALOGUE_DETAIL
    context_object_name = "dialogue"
    pk_url_kwarg = "dialogue_id"

    def dispatch(self, request, *args, **kwargs):
        dialogue = self.get_object()
        user = get_user(request)

        if user not in dialogue.participants.all() and not dialogue.is_visible:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Pass all dialogue posts and last post ID to context data."""

        # get initial context data, includes dialogue
        context = super().get_context_data(**kwargs)

        # get dialogue object
        dialogue = self.get_object()

        # get all posts in the dialogue and cache related author data
        posts = (
            Post.objects.filter(dialogue=dialogue)
            .select_related("author")
            .order_by("id")
        )

        # get last post id
        last_post = posts.last() if posts.exists() else None
        last_id = last_post.id if last_post else 0

        context.update({"posts": posts, "last_id": last_id})

        return context

    def post(self, request, *args, **kwargs):
        """Handle POST requests within a dialogue."""

        # get current user instance
        user = get_user(request)

        # get dialogue object
        dialogue = self.get_object()

        if not user.is_authenticated and not user in dialogue.participants.all():
            raise PermissionDenied

        # get last post id
        last_id = request.POST.get("last_id", 0)

        if user in dialogue.participants.all():
            # get post body from post form and remove surrounding
            # whitespace the retrieved value
            post_body = request.POST.get("body", "").strip()

            if not post_body:
                return HttpResponse("")

            # add post to the database
            post = Post.objects.create(author=user, dialogue=dialogue, body=post_body)

            # if the request is from htmx, get all posts since the last
            # updated post id, including any posts from other users
            # that haven't been captured by the polling loop
            if request.headers.get("HX-Request"):
                posts = (
                    Post.objects.filter(dialogue=dialogue, id__gt=last_id)
                    .select_related("author")
                    .order_by("created_on")
                )

                context = {
                    "posts": posts,
                    "last_id": posts.last().id,
                    "dialogue": dialogue,
                }

                response = render(request, TemplateName.POLLING, context)
                response.headers["Vary"] = "HX-Request"
                return response

            return HttpResponseRedirect(
                f"{reverse('dialogues:dialogue_detail', args=(dialogue.id,))}#post_form"
            )


class PollingView(TemplateView):
    template_name = TemplateName.POLLING

    def dispatch(self, request, *args, **kwargs):
        """
        Check if user has permission to view the dialogue before
        processing the request. If a non-participant is viewing the
        dialogue in real-time and the visibility settings are set to
        private during the live viewing, the page will update in
        real-time to show the 403 page.
        """

        dialogue_id = kwargs.get("dialogue_id")
        dialogue = get_object_or_404(Dialogue, id=dialogue_id)
        user = get_user(request)

        if not dialogue.is_visible and not user in dialogue.participants.all():
            return render(request, TemplateName.PERMISSION_DENIED)

        return super().dispatch(request, *args, **kwargs)

    def _get_last_id(self):
        """Get and validate the last_id from request parameters"""

        try:
            last_id = self.request.GET.get("last_id", 0)
            return int(last_id)
        except (ValueError, TypeError):
            return 0

    def get_context_data(self, **kwargs):
        """Get new posts and pass them to the template"""

        context = super().get_context_data(**kwargs)

        dialogue_id = self.kwargs.get("dialogue_id")
        dialogue = get_object_or_404(Dialogue, id=dialogue_id)

        # to determine whether a post is new, get the ID of the most
        # recent post in the dialogue
        last_id = self._get_last_id()

        # get all posts with IDs greater than `last_id` and cache the
        # related author data
        posts = (
            Post.objects.filter(dialogue=dialogue, id__gt=last_id)
            .select_related("author")
            .order_by("created_on")
        )

        last_post = posts.last() if posts.exists() else None
        last_id = last_post.id if last_post else 0

        context.update(
            {
                "posts": posts,
                "last_id": last_id,
                "dialogue": dialogue,
            }
        )

        return context


class DeleteDialogueView(LoginRequiredMixin, DeleteView):
    model = Dialogue
    success_url = reverse_lazy("dashboard:home")
    pk_url_kwarg = "dialogue_id"


class ToggleVisibilityView(LoginRequiredMixin, View):
    def post(self, request, dialogue_id):
        dialogue = get_object_or_404(Dialogue, id=dialogue_id)
        dialogue.is_visible = not dialogue.is_visible
        dialogue.save()

        context = {"dialogue": dialogue}
        return render(request, TemplateName.TOGGLE_VISIBILITY, context)
