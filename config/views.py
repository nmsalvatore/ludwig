from django.shortcuts import redirect, render


def index_redirect_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return redirect("accounts:login")
