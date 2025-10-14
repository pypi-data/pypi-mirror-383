"""Admin configuration for menus app."""

from django.contrib import admin

from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Admin for the MenuItem model."""

    list_display = (
        "anchor_text",
        "title",
        "page",
        "url",
        "icon_class",
        "parent",
        "order",
        "is_active",
        "is_external",
    )
    list_editable = ("order", "is_active", "is_external")
    list_filter = ("is_active", "is_external", "parent")
    search_fields = ("title", "anchor_text", "url")
    ordering = ("order", "anchor_text")
    autocomplete_fields = ["page"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("title", "anchor_text"),
                "description": "Core menu item information",
            },
        ),
        (
            "Link Destination",
            {
                "fields": ("page", "url"),
                "description": (
                    "Select a page from the dropdown OR enter a custom URL. "
                    "Page links automatically update if the page URL changes."
                ),
            },
        ),
        (
            "Visual Customization",
            {
                "fields": ("icon_class",),
                "description": "Icon to display next to menu item",
            },
        ),
        (
            "Menu Structure",
            {
                "fields": ("parent", "order"),
                "description": "Hierarchical organization and display order",
            },
        ),
        (
            "Settings",
            {
                "fields": ("is_active", "is_external"),
                "description": "Menu item behavior and visibility",
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
                "description": "Automatically tracked timestamps",
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")
