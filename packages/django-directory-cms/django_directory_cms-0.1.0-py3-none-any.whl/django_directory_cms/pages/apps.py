"""App configuration for pages."""

from django.apps import AppConfig


class PagesConfig(AppConfig):
    """Configuration for the CMS pages app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_directory_cms.pages"
    label = "django_directory_cms_pages"
    verbose_name = "CMS Pages"
