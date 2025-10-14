"""Admin configuration for django-directory-cms package."""

from django.contrib import admin

from .models import MenuItem, Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Admin for the Page model."""

    list_display = ("title", "slug", "is_active", "is_published", "created_at", "updated_at")
    list_editable = ("is_active", "is_published")
    list_filter = ("is_active", "is_published", "created_at")
    search_fields = ("title", "slug", "content", "seo_title", "meta_description")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("title", "slug", "content", "is_active", "is_published"),
            },
        ),
        (
            "Core SEO",
            {
                "fields": ("seo_title", "meta_description", "h1_tag", "focus_keyphrase", "secondary_keywords"),
                "classes": ("collapse",),
            },
        ),
        (
            "OpenGraph / Social Media",
            {
                "fields": ("og_title", "og_description", "og_image", "og_type"),
                "classes": ("collapse",),
            },
        ),
        (
            "Twitter Card",
            {
                "fields": ("twitter_card_type", "twitter_title", "twitter_description", "twitter_image"),
                "classes": ("collapse",),
            },
        ),
        (
            "Technical SEO",
            {
                "fields": ("canonical_url", "robots_directive", "schema_type", "schema_data", "breadcrumb_title"),
                "classes": ("collapse",),
            },
        ),
        (
            "Internal Notes",
            {
                "fields": ("seo_notes",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


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
