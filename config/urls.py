from django.contrib import admin
from django.urls import include, path

from .views import index_redirect_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index_redirect_view, name="index"),
    path("auth/", include("ludwig.accounts.urls")),
    path("dashboard/", include("ludwig.dashboard.urls")),
    path("dialogue/", include("ludwig.dialogues.urls")),
]
