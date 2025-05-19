from django.urls import path

from . import views

app_name = "dialogues"

urlpatterns = [
    path("create/", views.CreateDialogueView.as_view(), name="create_dialogue"),
    path("search-users/", views.SearchForUsersView.as_view(), name="search_users"),
    path("<str:dialogue_id>/", views.DialogueDetailView.as_view(), name="dialogue_detail"),
    path("new-posts/<str:dialogue_id>", views.NewPostsPollingView.as_view(), name="new_posts")
]
