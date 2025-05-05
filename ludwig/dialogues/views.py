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
    # get dialogue instance, otherwise throw a 404 error
    dialogue = get_object_or_404(Dialogue, id=dialogue_id)

    # get user instance from request
    user = get_user(request)

    if user in dialogue.participants.all() and request.method == "POST":
        post_body = request.POST.get("body", "").strip()

        if post_body:
            # add the post to the database
            Post.objects.create(
                author=request.user,
                dialogue=dialogue,
                body=post_body
            )

        # since the event stream will catch the new post and
        # append it to the dialogue with htmx, if the request is
        # from htmx, simply refresh the form
        if request.headers.get("HX-Request"):
            return render(request, "dialogues/partials/form.html")

        # if js is disabled, htmx is disabled, so just refresh the page
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


@login_required
def dialogue_stream(request, dialogue_id):
    """SSE endpoint for real-time dialogue updates."""
    dialogue = get_object_or_404(Dialogue, id=dialogue_id)

    # Get the latest post ID the client has
    last_post_id = request.GET.get("last_id", "0")
    try:
        last_post_id = int(last_post_id)
    except ValueError:
        last_post_id = 0

    def event_stream():
        nonlocal last_post_id

        while True:
            new_posts = Post.objects.filter(
                dialogue=dialogue,
                id__gt=last_post_id
            ).select_related("author").order_by("id")

            if new_posts.exists():
                for post in new_posts:
                    last_post_id = post.id

                    html = render_to_string(
                        "dialogues/partials/post.html",
                        context={"post": post},
                        request=request
                    ).replace("\n", "")

                    yield f"data: {html} \n\n"

            time.sleep(1)

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"

    return response
