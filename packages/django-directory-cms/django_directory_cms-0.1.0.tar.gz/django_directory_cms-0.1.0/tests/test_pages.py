"""Tests for pages app."""

from django.test import TestCase
from django.urls import reverse

from django_directory_cms.pages.models import Page


class PageModelTest(TestCase):
    """Test Page model functionality."""

    def test_page_creation(self):
        """Test creating a basic page."""
        page = Page.objects.create(
            title="About Us",
            content="<p>Welcome to our site!</p>",
        )
        self.assertEqual(page.title, "About Us")
        self.assertEqual(page.slug, "about-us")
        self.assertTrue(page.is_active)
        self.assertTrue(page.is_published)

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from title."""
        page = Page.objects.create(title="Test Page Title")
        self.assertEqual(page.slug, "test-page-title")

    def test_slug_uniqueness(self):
        """Test that slugs are unique."""
        page1 = Page.objects.create(title="Test Page")
        page2 = Page.objects.create(title="Another Page")
        self.assertNotEqual(page1.slug, page2.slug)
        self.assertEqual(page1.slug, "test-page")
        self.assertEqual(page2.slug, "another-page")

    def test_seo_title_auto_generation(self):
        """Test that SEO title is auto-generated if not provided."""
        page = Page.objects.create(title="My Test Page")
        self.assertEqual(page.seo_title, "My Test Page")

    def test_meta_description_auto_generation(self):
        """Test that meta description is auto-generated from content."""
        page = Page.objects.create(
            title="Test",
            content="<p>This is the content of my page with HTML tags.</p>",
        )
        # Should strip HTML and truncate
        self.assertIn("This is the content", page.meta_description)
        self.assertNotIn("<p>", page.meta_description)

    def test_h1_tag_auto_generation(self):
        """Test that H1 tag defaults to title."""
        page = Page.objects.create(title="Test Page")
        self.assertEqual(page.h1_tag, "Test Page")

    def test_get_absolute_url(self):
        """Test that get_absolute_url returns correct URL."""
        page = Page.objects.create(title="About")
        url = page.get_absolute_url()
        self.assertEqual(url, reverse("django_directory_cms_pages:detail", kwargs={"slug": "about"}))

    def test_seo_mixin_methods(self):
        """Test that SEOAuditableMixin methods work."""
        page = Page.objects.create(
            title="Test Page",
            seo_title="Custom SEO Title",
            meta_description="Custom meta description",
        )
        # These methods come from SEOAuditableMixin
        self.assertEqual(page.get_seo_title(), "Custom SEO Title")
        self.assertEqual(page.get_meta_description(), "Custom meta description")

    def test_opengraph_fields(self):
        """Test OpenGraph fields."""
        page = Page.objects.create(
            title="Test",
            og_title="OG Title",
            og_description="OG Description",
            og_type="article",
        )
        self.assertEqual(page.og_title, "OG Title")
        self.assertEqual(page.og_description, "OG Description")
        self.assertEqual(page.og_type, "article")

    def test_twitter_card_fields(self):
        """Test Twitter Card fields."""
        page = Page.objects.create(
            title="Test",
            twitter_title="Twitter Title",
            twitter_description="Twitter Description",
            twitter_card_type="summary_large_image",
        )
        self.assertEqual(page.twitter_title, "Twitter Title")
        self.assertEqual(page.twitter_card_type, "summary_large_image")

    def test_schema_fields(self):
        """Test schema.org fields."""
        page = Page.objects.create(
            title="Test",
            schema_type="AboutPage",
            schema_data={"name": "About Us", "description": "Learn more"},
        )
        self.assertEqual(page.schema_type, "AboutPage")
        self.assertIsInstance(page.schema_data, dict)


    def test_absolute_url_property(self):
        """Test the absolute_url property alias."""
        page = Page.objects.create(title="Test")
        self.assertEqual(page.absolute_url, page.get_absolute_url())
