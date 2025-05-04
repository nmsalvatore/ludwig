from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_view(request):
    user = get_user(request)
    user_dialogues = user.dialogues.all()
    context = {
        "user_dialogues": user_dialogues
    }
    return render(request, "dashboard/dashboard.html", context)
