from django.shortcuts import render


def dialogue_view(request):
    return render(request, "dialogues/dialogue.html")
