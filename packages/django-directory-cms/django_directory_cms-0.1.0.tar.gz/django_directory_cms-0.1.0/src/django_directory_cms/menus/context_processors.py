"""Context processors for the menus app."""

from .models import MenuItem


def menu_items(request):  # noqa: ARG001
    """Add menu items to the template context globally.

    Returns a structured menu with top-level items and their children.
    Top-level items have parent=None, children have parent set.

    Args:
        request: HttpRequest object (required by Django context processor signature).

    """
    # Fetch all active menu items
    all_menu_items = MenuItem.objects.filter(is_active=True).select_related("parent").order_by("order", "anchor_text")

    # Separate top-level items from child items
    top_level_items = []
    children_by_parent = {}

    for item in all_menu_items:
        if item.parent is None:
            # Top-level menu item
            top_level_items.append(item)
        else:
            # Child item - group by parent
            parent_id = item.parent.id
            if parent_id not in children_by_parent:
                children_by_parent[parent_id] = []
            children_by_parent[parent_id].append(item)

    # Attach children to their parent items for easy template access
    for item in top_level_items:
        item.menu_children = children_by_parent.get(item.id, [])

    return {
        "menu_items": top_level_items,
    }
