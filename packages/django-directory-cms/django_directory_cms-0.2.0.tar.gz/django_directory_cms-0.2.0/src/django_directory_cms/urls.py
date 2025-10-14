"""URL configuration for django-directory-cms package."""

from django.urls import path

from . import views

app_name = "django_directory_cms"

urlpatterns = [
    path("", views.page_list, name="list"),
    path("<slug:slug>/", views.page_detail, name="detail"),
]
