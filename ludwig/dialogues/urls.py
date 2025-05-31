from django.urls import path

from . import views

app_name = "dialogues"

urlpatterns = [
    path("create/", views.CreateDialogueView.as_view(), name="create_dialogue"),
    path("search-users/", views.SearchForUsersView.as_view(), name="search_users"),
    path("<str:dialogue_id>/", views.DialogueDetailView.as_view(), name="dialogue_detail"),
    path("polling/<str:dialogue_id>", views.PollingView.as_view(), name="polling"),
    path("delete/<str:dialogue_id>", views.DeleteDialogueView.as_view(), name="delete_dialogue"),
    path("toggle-visibility/<str:dialogue_id>", views.ToggleVisibilityView.as_view(), name="toggle_visibility"),
]
