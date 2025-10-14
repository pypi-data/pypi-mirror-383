"""App configuration for menus."""

from django.apps import AppConfig


class MenusConfig(AppConfig):
    """Configuration for the CMS menus app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_directory_cms.menus"
    label = "django_directory_cms_menus"
    verbose_name = "CMS Menus"
