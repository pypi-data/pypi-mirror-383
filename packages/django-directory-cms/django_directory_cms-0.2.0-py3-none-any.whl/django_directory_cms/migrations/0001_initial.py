"""Initial migration for django-directory-cms unified app."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Create Page and MenuItem tables."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Page",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Display name for the page", max_length=250, unique=True)),
                ("slug", models.SlugField(blank=True, help_text="URL-friendly identifier", max_length=250, unique=True)),
                ("content", models.TextField(help_text="Main page content (supports HTML)")),
                ("is_active", models.BooleanField(default=True, help_text="Page is active and accessible")),
                ("is_published", models.BooleanField(default=True, help_text="Page is published and visible")),
                (
                    "seo_title",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Optimized title for search engines (50-60 chars)",
                        max_length=60,
                    ),
                ),
                (
                    "meta_description",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Meta description for search results (150-160 chars)",
                        max_length=160,
                    ),
                ),
                (
                    "h1_tag",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="H1 tag for page (can differ from SEO title)",
                        max_length=70,
                    ),
                ),
                (
                    "focus_keyphrase",
                    models.CharField(
                        blank=True, default="", help_text="Primary keyword/phrase to rank for", max_length=100
                    ),
                ),
                (
                    "secondary_keywords",
                    models.TextField(blank=True, default="", help_text="Comma-separated secondary keywords"),
                ),
                (
                    "canonical_url",
                    models.URLField(blank=True, default="", help_text="Canonical URL if different from default"),
                ),
                (
                    "og_title",
                    models.CharField(
                        blank=True, default="", help_text="OpenGraph title (up to 95 chars)", max_length=95
                    ),
                ),
                ("og_description", models.CharField(blank=True, default="", help_text="OpenGraph description", max_length=200)),
                (
                    "og_image",
                    models.ImageField(
                        blank=True,
                        help_text="OpenGraph image (1200x630px recommended)",
                        null=True,
                        upload_to="og_images/pages/",
                    ),
                ),
                (
                    "og_type",
                    models.CharField(
                        blank=True,
                        default="website",
                        help_text="OpenGraph type (article, website, etc.)",
                        max_length=20,
                    ),
                ),
                (
                    "twitter_card_type",
                    models.CharField(
                        blank=True, default="summary_large_image", help_text="Twitter card type", max_length=20
                    ),
                ),
                ("twitter_title", models.CharField(blank=True, default="", help_text="Twitter card title", max_length=70)),
                (
                    "twitter_description",
                    models.CharField(blank=True, default="", help_text="Twitter card description", max_length=200),
                ),
                (
                    "twitter_image",
                    models.ImageField(
                        blank=True, help_text="Twitter card image", null=True, upload_to="twitter_images/pages/"
                    ),
                ),
                (
                    "schema_type",
                    models.CharField(
                        blank=True,
                        default="WebPage",
                        help_text="Schema.org type (WebPage, AboutPage, ContactPage, etc.)",
                        max_length=50,
                    ),
                ),
                (
                    "schema_data",
                    models.JSONField(blank=True, help_text="Additional structured data in JSON format", null=True),
                ),
                (
                    "robots_directive",
                    models.CharField(
                        blank=True, default="index,follow", help_text="Robots meta directive", max_length=50
                    ),
                ),
                ("breadcrumb_title", models.CharField(blank=True, default="", help_text="Custom breadcrumb title", max_length=100)),
                ("seo_notes", models.TextField(blank=True, default="", help_text="Internal SEO notes and strategy")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Page",
                "verbose_name_plural": "Pages",
                "ordering": ["title"],
            },
        ),
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Display name for admin and tooltips", max_length=200)),
                ("anchor_text", models.CharField(help_text="Text displayed to users in the menu", max_length=100)),
                (
                    "url",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="OR enter a custom URL for external links or Django views",
                        max_length=500,
                    ),
                ),
                (
                    "icon_class",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "No Icon"),
                            ("bi-house-door", "Home"),
                            ("bi-grid-3x3-gap", "Grid/Dashboard"),
                            ("bi-list-ul", "List"),
                            ("bi-compass", "Explore"),
                            ("bi-arrow-left", "Back"),
                            ("bi-arrow-right", "Forward"),
                            ("bi-book", "Documentation"),
                            ("bi-newspaper", "News/Blog"),
                            ("bi-file-text", "Document"),
                            ("bi-folder", "Folder"),
                            ("bi-image", "Image/Gallery"),
                            ("bi-play-circle", "Video"),
                            ("bi-mic", "Podcast/Audio"),
                            ("bi-search", "Search"),
                            ("bi-plus-circle", "Add/Create"),
                            ("bi-gear", "Settings"),
                            ("bi-download", "Download"),
                            ("bi-upload", "Upload"),
                            ("bi-share", "Share"),
                            ("bi-person", "Profile"),
                            ("bi-people", "Team/Community"),
                            ("bi-envelope", "Contact/Email"),
                            ("bi-chat-dots", "Chat/Messages"),
                            ("bi-bell", "Notifications"),
                            ("bi-info-circle", "About/Info"),
                            ("bi-question-circle", "Help/FAQ"),
                            ("bi-calendar", "Calendar/Events"),
                            ("bi-graph-up", "Analytics/Stats"),
                            ("bi-shield-check", "Security/Privacy"),
                            ("bi-tag", "Tags/Categories"),
                        ],
                        default="",
                        help_text="Bootstrap icon class (e.g., 'bi-house')",
                        max_length=50,
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0, help_text="Display order (lower numbers appear first)")),
                ("is_active", models.BooleanField(default=True, help_text="Menu item is active and visible")),
                ("is_external", models.BooleanField(default=False, help_text="Link opens in new tab (for external URLs)")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "page",
                    models.ForeignKey(
                        blank=True,
                        help_text="Select a page to link to (URL will be auto-populated from page)",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="menu_items",
                        to="django_directory_cms.page",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        help_text="Parent menu item for hierarchical menus",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="django_directory_cms.menuitem",
                    ),
                ),
            ],
            options={
                "verbose_name": "Menu Item",
                "verbose_name_plural": "Menu Items",
                "ordering": ["order", "anchor_text"],
            },
        ),
    ]
