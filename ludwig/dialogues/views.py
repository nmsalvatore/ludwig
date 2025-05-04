import json
import time

from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from .forms import DialogueCreationForm
from .models import Dialogue, Post


User = get_user_model()


@login_required
def create_dialogue(request):
    if request.method == "POST":
        form = DialogueCreationForm(request.POST)
        if form.is_valid():
            dialogue = form.save()

            dialogue.participants.add(request.user)

            participant_ids = request.POST.getlist("selected_participants")
            if participant_ids:
                for user_id in participant_ids:
                    try:
                        user = User.objects.get(id=user_id)
                        dialogue.participants.add(user)
                    except User.DoesNotExist:
                        pass

            return redirect("dialogues:detail", dialogue.id)
    else:
        form = DialogueCreationForm()

    return render(request, "dialogues/dialogue_create.html", {"form": form})


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


@login_required
def dialogue_detail(request, dialogue_id):
    dialogue = get_object_or_404(Dialogue, id=dialogue_id)

    user = get_user(request)

    if user in dialogue.participants.all() and request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Post.objects.create(
                author=request.user,
                dialogue=dialogue,
                body=body
            )

            if request.headers.get("HX-Request"):
                return HttpResponse("")
            return redirect("dialogues:detail", dialogue_id=dialogue_id)

    posts = Post.objects.filter(dialogue=dialogue).select_related("author")

    if request.user not in dialogue.participants.all():
        dialogue.views += 1
        dialogue.save()

    context = {"dialogue": dialogue, "posts": posts}
    return render(request, "dialogues/dialogue_detail.html", context)


@login_required
def find_dialogue(request):
    pass
