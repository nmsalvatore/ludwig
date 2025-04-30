from django.urls import path
from . import views

app_name = "dialogues"

urlpatterns = [
    path("", views.dialogue_view, name="dialogue")
]
