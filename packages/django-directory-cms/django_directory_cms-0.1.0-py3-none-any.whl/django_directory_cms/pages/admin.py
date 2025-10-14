"""Admin configuration for pages app."""

from django.contrib import admin

from .models import Page


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
