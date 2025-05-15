from django.contrib import admin
from django.urls import include, path

from .views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("auth/", include("ludwig.accounts.urls")),
    path("dashboard/", include("ludwig.dashboard.urls")),
    path("dialogue/", include("ludwig.dialogues.urls")),
]
