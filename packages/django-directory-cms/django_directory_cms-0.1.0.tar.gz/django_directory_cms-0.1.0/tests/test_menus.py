"""Tests for menus app."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from django_directory_cms.menus.models import MenuItem
from django_directory_cms.pages.models import Page


class MenuItemModelTest(TestCase):
    """Test MenuItem model functionality."""

    def setUp(self):
        """Create test page for menu linking."""
        self.page = Page.objects.create(
            title="Test Page",
            content="Test content",
        )

    def test_menuitem_with_page(self):
        """Test creating menu item linked to a page."""
        menu_item = MenuItem.objects.create(
            title="Home",
            anchor_text="Home",
            page=self.page,
            order=1,
        )
        self.assertEqual(menu_item.anchor_text, "Home")
        self.assertEqual(menu_item.page, self.page)
        self.assertTrue(menu_item.is_active)

    def test_menuitem_with_url(self):
        """Test creating menu item with custom URL."""
        menu_item = MenuItem.objects.create(
            title="External Link",
            anchor_text="Google",
            url="https://google.com",
            is_external=True,
        )
        self.assertEqual(menu_item.url, "https://google.com")
        self.assertTrue(menu_item.is_external)

    def test_menuitem_validation_both_page_and_url(self):
        """Test that having both page and URL raises validation error."""
        menu_item = MenuItem(
            title="Invalid",
            anchor_text="Invalid",
            page=self.page,
            url="https://example.com",
        )
        with self.assertRaises(ValidationError):
            menu_item.clean()

    def test_menuitem_validation_neither_page_nor_url(self):
        """Test that having neither page nor URL raises validation error."""
        menu_item = MenuItem(
            title="Invalid",
            anchor_text="Invalid",
        )
        with self.assertRaises(ValidationError):
            menu_item.clean()

    def test_get_url_from_page(self):
        """Test that get_url returns page URL when page is set."""
        menu_item = MenuItem.objects.create(
            title="Home",
            anchor_text="Home",
            page=self.page,
        )
        self.assertEqual(menu_item.get_url(), self.page.get_absolute_url())

    def test_get_url_from_url_field(self):
        """Test that get_url returns URL field when page is not set."""
        menu_item = MenuItem.objects.create(
            title="External",
            anchor_text="External",
            url="/custom/url/",
        )
        self.assertEqual(menu_item.get_url(), "/custom/url/")

    def test_hierarchical_menu(self):
        """Test parent/child menu relationships."""
        parent = MenuItem.objects.create(
            title="Resources",
            anchor_text="Resources",
            url="/resources/",
            order=1,
        )
        child = MenuItem.objects.create(
            title="Blog",
            anchor_text="Blog",
            url="/blog/",
            parent=parent,
            order=1,
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())

    def test_menu_icon(self):
        """Test menu icon functionality."""
        menu_item = MenuItem.objects.create(
            title="Home",
            anchor_text="Home",
            url="/",
            icon_class="bi-house-door",
        )
        self.assertEqual(menu_item.icon_class, "bi-house-door")
        self.assertEqual(menu_item.display_icon, "bi bi-house-door")

    def test_menu_icon_empty(self):
        """Test menu with no icon."""
        menu_item = MenuItem.objects.create(
            title="Home",
            anchor_text="Home",
            url="/",
        )
        self.assertEqual(menu_item.display_icon, "")

    def test_menu_ordering(self):
        """Test that menu items are ordered correctly."""
        MenuItem.objects.create(title="Third", anchor_text="Third", url="/third/", order=3)
        MenuItem.objects.create(title="First", anchor_text="First", url="/first/", order=1)
        MenuItem.objects.create(title="Second", anchor_text="Second", url="/second/", order=2)

        items = list(MenuItem.objects.all())
        self.assertEqual(items[0].anchor_text, "First")
        self.assertEqual(items[1].anchor_text, "Second")
        self.assertEqual(items[2].anchor_text, "Third")


class MenuContextProcessorTest(TestCase):
    """Test menu context processor."""

    def setUp(self):
        """Create test menu items."""
        self.parent = MenuItem.objects.create(
            title="Parent",
            anchor_text="Parent",
            url="/parent/",
            order=1,
            is_active=True,
        )
        self.child = MenuItem.objects.create(
            title="Child",
            anchor_text="Child",
            url="/child/",
            parent=self.parent,
            order=1,
            is_active=True,
        )
        self.inactive = MenuItem.objects.create(
            title="Inactive",
            anchor_text="Inactive",
            url="/inactive/",
            is_active=False,
        )

    def test_context_processor_includes_active_menus(self):
        """Test that context processor includes active menu items."""
        from django_directory_cms.menus.context_processors import menu_items

        context = menu_items(None)
        self.assertIn("menu_items", context)
        menu_list = context["menu_items"]

        # Should only include active top-level items
        self.assertEqual(len(menu_list), 1)
        self.assertEqual(menu_list[0], self.parent)

    def test_context_processor_attaches_children(self):
        """Test that context processor attaches children to parents."""
        from django_directory_cms.menus.context_processors import menu_items

        context = menu_items(None)
        parent_item = context["menu_items"][0]

        # Children should be attached
        self.assertTrue(hasattr(parent_item, "menu_children"))
        self.assertEqual(len(parent_item.menu_children), 1)
        self.assertEqual(parent_item.menu_children[0], self.child)
