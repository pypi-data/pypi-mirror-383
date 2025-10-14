"""Models for django-directory-cms package."""

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_seo_audit import SEOAuditableMixin

# Constants for magic values
META_DESCRIPTION_MAX_LENGTH = 160  # Maximum characters for auto-generated meta descriptions

# Curated list of Bootstrap icons for navigation menus
# Organized by category for easy selection in admin
MENU_ICON_CHOICES = [
    ("", "No Icon"),
    # Navigation
    ("bi-house-door", "Home"),
    ("bi-grid-3x3-gap", "Grid/Dashboard"),
    ("bi-list-ul", "List"),
    ("bi-compass", "Explore"),
    ("bi-arrow-left", "Back"),
    ("bi-arrow-right", "Forward"),
    # Content Types
    ("bi-book", "Documentation"),
    ("bi-newspaper", "News/Blog"),
    ("bi-file-text", "Document"),
    ("bi-folder", "Folder"),
    ("bi-image", "Image/Gallery"),
    ("bi-play-circle", "Video"),
    ("bi-mic", "Podcast/Audio"),
    # Actions
    ("bi-search", "Search"),
    ("bi-plus-circle", "Add/Create"),
    ("bi-gear", "Settings"),
    ("bi-download", "Download"),
    ("bi-upload", "Upload"),
    ("bi-share", "Share"),
    # User & Social
    ("bi-person", "Profile"),
    ("bi-people", "Team/Community"),
    ("bi-envelope", "Contact/Email"),
    ("bi-chat-dots", "Chat/Messages"),
    ("bi-bell", "Notifications"),
    # Common Pages
    ("bi-info-circle", "About/Info"),
    ("bi-question-circle", "Help/FAQ"),
    ("bi-calendar", "Calendar/Events"),
    ("bi-graph-up", "Analytics/Stats"),
    ("bi-shield-check", "Security/Privacy"),
    ("bi-tag", "Tags/Categories"),
]


class Page(models.Model, SEOAuditableMixin):
    """Highly SEO-optimized static page model for about, team, terms, etc."""

    # Core fields
    title = models.CharField(max_length=250, unique=True, help_text="Display name for the page")
    slug = models.SlugField(max_length=250, unique=True, blank=True, help_text="URL-friendly identifier")
    content = models.TextField(help_text="Main page content (supports HTML)")

    # Publishing controls
    is_active = models.BooleanField(default=True, help_text="Page is active and accessible")
    is_published = models.BooleanField(default=True, help_text="Page is published and visible")

    # SEO Fields - Core SEO
    seo_title = models.CharField(
        max_length=60,
        blank=True,
        default="",
        help_text="Optimized title for search engines (50-60 chars)",
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        default="",
        help_text="Meta description for search results (150-160 chars)",
    )
    h1_tag = models.CharField(
        max_length=70,
        blank=True,
        default="",
        help_text="H1 tag for page (can differ from SEO title)",
    )
    focus_keyphrase = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Primary keyword/phrase to rank for",
    )
    secondary_keywords = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated secondary keywords",
    )
    canonical_url = models.URLField(
        blank=True,
        default="",
        help_text="Canonical URL if different from default",
    )

    # SEO Fields - OpenGraph
    og_title = models.CharField(
        max_length=95,
        blank=True,
        default="",
        help_text="OpenGraph title (up to 95 chars)",
    )
    og_description = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="OpenGraph description",
    )
    og_image = models.ImageField(
        upload_to="og_images/pages/",
        blank=True,
        null=True,
        help_text="OpenGraph image (1200x630px recommended)",
    )
    og_type = models.CharField(
        max_length=20,
        blank=True,
        default="website",
        help_text="OpenGraph type (article, website, etc.)",
    )

    # SEO Fields - Twitter Card
    twitter_card_type = models.CharField(
        max_length=20,
        blank=True,
        default="summary_large_image",
        help_text="Twitter card type",
    )
    twitter_title = models.CharField(
        max_length=70,
        blank=True,
        default="",
        help_text="Twitter card title",
    )
    twitter_description = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Twitter card description",
    )
    twitter_image = models.ImageField(
        upload_to="twitter_images/pages/",
        blank=True,
        null=True,
        help_text="Twitter card image",
    )

    # SEO Fields - Technical & Advanced
    schema_type = models.CharField(
        max_length=50,
        blank=True,
        default="WebPage",
        help_text="Schema.org type (WebPage, AboutPage, ContactPage, etc.)",
    )
    schema_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional structured data in JSON format",
    )
    robots_directive = models.CharField(
        max_length=50,
        blank=True,
        default="index,follow",
        help_text="Robots meta directive",
    )
    breadcrumb_title = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Custom breadcrumb title",
    )
    seo_notes = models.TextField(
        blank=True,
        default="",
        help_text="Internal SEO notes and strategy",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metaclass for Page."""

        ordering = ["title"]
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self) -> str:
        """Return the title of the page."""
        return self.title

    def save(self, *args, **kwargs) -> None:
        """Override save method to automatically generate slug."""
        # Generate slug from title if not provided
        if not self.slug or self.slug != slugify(self.title):
            self.slug = slugify(self.title)

            # Ensure slug is unique
            if Page.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                count = 1
                base_slug = self.slug
                while Page.objects.filter(slug=f"{base_slug}-{count}").exclude(pk=self.pk).exists():
                    count += 1
                self.slug = f"{base_slug}-{count}"

        # Auto-generate SEO title if not provided
        if not self.seo_title:
            self.seo_title = self.title[:60]

        # Auto-generate meta description from content if not provided
        if not self.meta_description and self.content:
            # Strip HTML tags for meta description
            plain_text = re.sub(r"<[^>]+>", "", self.content)
            self.meta_description = plain_text[:META_DESCRIPTION_MAX_LENGTH].strip()
            if len(plain_text) > META_DESCRIPTION_MAX_LENGTH:
                self.meta_description += "..."

        # Auto-generate H1 tag if not provided
        if not self.h1_tag:
            self.h1_tag = self.title

        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Return the absolute URL for the page."""
        return reverse("django_directory_cms:detail", kwargs={"slug": self.slug})

    @property
    def absolute_url(self) -> str:
        """Property alias for get_absolute_url() for consistency."""
        return self.get_absolute_url()


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
        Page,
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
