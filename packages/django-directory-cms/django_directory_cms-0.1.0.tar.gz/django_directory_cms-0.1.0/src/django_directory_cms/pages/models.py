"""Models for the pages app."""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_seo_audit import SEOAuditableMixin

# Constants for magic values
META_DESCRIPTION_MAX_LENGTH = 160  # Maximum characters for auto-generated meta descriptions


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
            import re

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
        return reverse("django_directory_cms_pages:detail", kwargs={"slug": self.slug})

    @property
    def absolute_url(self) -> str:
        """Property alias for get_absolute_url() for consistency."""
        return self.get_absolute_url()
