"""URL configuration for the core project."""
from django.contrib import admin
from django.urls import path

from data.views import percentile_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/percentile/", percentile_view),
]
