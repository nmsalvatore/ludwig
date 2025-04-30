from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from .views import home_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("ludwig.accounts.urls")),
    path("dashboard/", include("ludwig.dashboard.urls")),
    path("d/", include("ludwig.dialogues.urls")),
    path("", home_view, name="home")
]
