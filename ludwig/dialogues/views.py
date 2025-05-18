import json
import time

from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, StreamingHttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from .forms import DialogueCreationForm
from .models import Dialogue, Post

User = get_user_model()


class CreateDialogueView(LoginRequiredMixin, CreateView):
    """
    Display a form to create a dialogue and redirect to dialogue detail
    page on successful dialogue creation.
    """

    form_class = DialogueCreationForm
    template_name = "dialogues/dialogue_create.html"

    def _add_participants_to_dialogue(self, dialogue):
        """Add current user and selected participants to dialogue."""

        # add current user as participant
        dialogue.participants.add(get_user(self.request))

        # get list of user ids from hidden form input field
        user_ids = self.request.POST.getlist("selected_participants")

        if user_ids:
            # get all users with selected ids and add as participants
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

        # store dialogue as object for get_success_url
        self.object = dialogue

        return HttpResponseRedirect(
            reverse("dialogues:dialogue_detail", args={dialogue.id})
        )


@login_required
def search_users(request):
    query = request.GET.get("query", "")

    if len(query) < 2:
        return HttpResponse("")

    users = User.objects.filter(
        Q(username__icontains=query) | Q(display_name__icontains=query)
    ).exclude(id=request.user.id)[:10]

    context = {"users": users, "query": query}
    return render(request, "dialogues/partials/user_search_results.html", context)


def dialogue_detail(request, dialogue_id):
    # get dialogue instance, otherwise throw a 404 error
    dialogue = get_object_or_404(Dialogue, id=dialogue_id)

    # get user instance from request
    user = get_user(request)
    if user in dialogue.participants.all() and request.method == "POST":
        # get post body and remove surrounding whitespace
        post_body = request.POST.get("body", "").strip()
        if post_body:
            # add the post to the database
            post = Post.objects.create(
                author=request.user,
                dialogue=dialogue,
                body=post_body
            )

        return redirect("dialogues:dialogue_detail", dialogue_id=dialogue_id)

    # get fresh queryset of posts, including the new one
    posts = Post.objects.filter(dialogue=dialogue).select_related("author").order_by("id")

    # Get the highest post ID for initial polling
    last_id = 0
    if posts.exists():
        last_id = posts.last().id

    context = {
        "dialogue": dialogue,
        "posts": posts,
        "last_id": last_id
    }

    return render(request, "dialogues/dialogue_detail.html", context)


@login_required
def new_posts(request, dialogue_id):
    dialogue = get_object_or_404(Dialogue, id=dialogue_id)

    last_id_str = request.GET.get("last_id", "0")
    try:
        last_id = int(last_id_str)
    except ValueError:
        last_id = 0

    new_posts = Post.objects.filter(
        dialogue=dialogue,
        id__gt=last_id
    ).select_related("author").order_by("created_on")

    highest_id = last_id

    if new_posts.exists():
        highest_id = new_posts.last().id

    context = {
        "posts": new_posts,
        "last_id": highest_id,
        "dialogue": dialogue
    }

    return render(request, "dialogues/partials/new_posts.html", context)


@login_required
def find_dialogue(request):
    pass
