"""App configuration for django-directory-cms package."""

from django.apps import AppConfig


class DjangoDirectoryCmsConfig(AppConfig):
    """Configuration for django-directory-cms app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_directory_cms"
    verbose_name = "Content Management System"
