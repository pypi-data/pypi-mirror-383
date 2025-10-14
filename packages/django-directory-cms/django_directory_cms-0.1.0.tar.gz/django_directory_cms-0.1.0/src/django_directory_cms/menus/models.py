"""Models for the menus app."""

from django.core.exceptions import ValidationError
from django.db import models

from .constants import MENU_ICON_CHOICES


class MenuItem(models.Model):
    """Hierarchical navigation menu items."""

    # Core fields
    title = models.CharField(
        max_length=200,
        help_text="Display name for admin and tooltips",
    )
    anchor_text = models.CharField(
        max_length=100,
        help_text="Text displayed to users in the menu",
    )

    # Link destination (either page OR url must be provided)
    page = models.ForeignKey(
        "django_directory_cms_pages.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="menu_items",
        help_text="Select a page to link to (URL will be auto-populated from page)",
    )
    url = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="OR enter a custom URL for external links or Django views",
    )

    # Visual customization
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        default="",
        choices=MENU_ICON_CHOICES,
        help_text="Bootstrap icon class (e.g., 'bi-house')",
    )

    # Hierarchy
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        help_text="Parent menu item for hierarchical menus",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)",
    )

    # Control
    is_active = models.BooleanField(
        default=True,
        help_text="Menu item is active and visible",
    )
    is_external = models.BooleanField(
        default=False,
        help_text="Link opens in new tab (for external URLs)",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metaclass for MenuItem."""

        ordering = ["order", "anchor_text"]
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"

    def __str__(self) -> str:
        """Return the anchor text of the menu item."""
        return self.anchor_text

    def clean(self) -> None:
        """Validate that either page or url is provided, but not both."""
        super().clean()

        has_page = self.page is not None
        has_url = bool(self.url and self.url.strip())

        if has_page and has_url:
            msg = "Choose either a page or enter a URL, not both."
            raise ValidationError({"page": msg, "url": msg})

        if not has_page and not has_url:
            msg = "Either select a page or enter a URL."
            raise ValidationError({"page": msg, "url": msg})

    def get_url(self) -> str:
        """Return the URL for this menu item.

        Returns the page's URL if page is set, otherwise returns the manual URL field.
        """
        if self.page:
            return self.page.get_absolute_url()
        return self.url

    @property
    def display_icon(self) -> str:
        """Return the full Bootstrap icon class for templates."""
        if self.icon_class:
            return f"bi {self.icon_class}"
        return ""
