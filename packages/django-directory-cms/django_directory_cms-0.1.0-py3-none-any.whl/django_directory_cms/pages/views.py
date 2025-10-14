"""Views for the pages app."""

from django.shortcuts import get_object_or_404, render

from .models import Page


def page_detail(request, slug):
    """Display a single page by slug."""
    page = get_object_or_404(Page, slug=slug, is_active=True, is_published=True)

    context = {
        "page": page,
        "seo_title": page.get_seo_title(),
        "meta_description": page.get_meta_description(),
        "canonical_url": page.get_canonical_url(),
        "h1_tag": page.get_h1_tag(),
        "og_title": page.get_og_title(),
        "og_description": page.get_og_description(),
        "og_image_url": page.get_og_image_url(),
        "og_type": page.get_og_type(),
        "twitter_title": page.get_twitter_title(),
        "twitter_description": page.get_twitter_description(),
        "twitter_image_url": page.get_twitter_image_url(),
        "twitter_card_type": page.get_twitter_card_type(),
        "robots_directive": page.get_robots_directive(),
        "breadcrumb_title": page.get_breadcrumb_title(),
        "structured_data_json": page.get_structured_data_json(),
    }

    return render(request, "django_directory_cms/pages/page_detail.html", context)


def page_list(request):
    """Display a list of all published pages."""
    pages = Page.objects.filter(is_active=True, is_published=True).order_by("title")

    context = {
        "pages": pages,
    }

    return render(request, "django_directory_cms/pages/page_list.html", context)
