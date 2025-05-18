from django.urls import path

from . import views

app_name = "dialogues"

urlpatterns = [
    path("create/", views.create_dialogue, name="create_dialogue"),
    path("find/", views.find_dialogue, name="find_dialogue"),
    path("search-users/", views.search_users, name="search_users"),
    path("<str:dialogue_id>/", views.dialogue_detail, name="dialogue_detail"),
    path("new-posts/<str:dialogue_id>", views.new_posts, name="new_posts")
]
