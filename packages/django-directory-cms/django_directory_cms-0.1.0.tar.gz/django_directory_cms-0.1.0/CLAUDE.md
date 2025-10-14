# CLAUDE.md - Django Directory CMS Package

This file provides guidance to Claude Code when working with the `django-directory-cms` package.

## Project Overview

**Django Directory CMS** is a standalone Django package providing SEO-optimized pages and hierarchical menus with Bootstrap Icons support. Extracted from the Directory Platform ecosystem for reusability.

**Key Features**:
- Protocol-based SEO integration via `django-seo-audit`
- Clean Django table namespacing (`django_directory_cms_*`)
- Zero domain coupling - works in any Django project
- Bootstrap Icons with 42 curated choices
- Hierarchical menu system with parent/child relationships

## Package Structure

```
django-directory-cms/
├── src/django_directory_cms/
│   ├── pages/              # SEO-optimized static pages
│   │   ├── models.py       # Page model (16 SEO fields)
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── menus/              # Hierarchical navigation menus
│   │   ├── models.py       # MenuItem model
│   │   ├── admin.py
│   │   ├── constants.py    # Bootstrap icon choices
│   │   ├── context_processors.py
│   │   └── migrations/
│   └── templates/django_directory_cms/
│       └── pages/
│           ├── page_detail.html
│           └── page_list.html
└── tests/
    ├── settings.py         # Test Django configuration
    ├── manage.py           # Django test runner
    └── urls.py
```

## Development Setup

This package is part of the Directory Platform workspace. Use UV for dependency management:

```bash
# From package directory
cd django-directory-cms
uv sync --extra dev

# Or from workspace root
uv sync
```

## Code Patterns

### App Labels and Namespacing

Apps use explicit labels to avoid conflicts:

```python
# pages/apps.py
class PagesConfig(AppConfig):
    name = "django_directory_cms.pages"
    label = "django_directory_cms_pages"  # Database prefix

# menus/apps.py
class MenusConfig(AppConfig):
    name = "django_directory_cms.menus"
    label = "django_directory_cms_menus"  # Database prefix
```

**Result**: Clean table names without `db_table` hacks:
- `django_directory_cms_pages_page`
- `django_directory_cms_menus_menuitem`

### ForeignKey References

Menus reference Pages using app label:

```python
# menus/models.py
page = models.ForeignKey(
    "django_directory_cms_pages.Page",  # Use app label
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
)
```

### SEO Integration

Pages inherit from `SEOAuditableMixin`:

```python
from django_seo_audit import SEOAuditableMixin

class Page(models.Model, SEOAuditableMixin):
    # Automatically gets:
    # - get_seo_title()
    # - get_meta_description()
    # - get_og_image_url()
    # - get_twitter_card()
    # + 20 more SEO methods
```

## Critical Constraints

### NEVER Do These

- ❌ Add `db_table` to models (we want clean namespacing)
- ❌ Import from `directory-builder` apps (must be standalone)
- ❌ Use inline imports
- ❌ Break the Page-Menu ForeignKey dependency

### ALWAYS Do These

- ✅ Use proper app labels in ForeignKeys
- ✅ Run `make check` before committing
- ✅ Update migrations after model changes
- ✅ Keep tests passing
- ✅ Follow django-seo-audit patterns

## Common Commands

```bash
# Development
make install         # Install dependencies
make migrate         # Run migrations
make shell           # Django shell
make makemigrations  # Create migrations

# Quality
make lint            # Ruff linting
make format          # Auto-format code
make check           # All quality checks
make test            # Run test suite

# Package
make build           # Build package
make clean           # Clean generated files
```

## Testing

```bash
# Run all tests
make test

# Verbose output
make test-verbose

# Specific test
PYTHONPATH=. uv run python tests/manage.py test tests.test_pages
```

## Architecture Decisions

### Why Two Apps in One Package?

Menus depend on Pages via ForeignKey. Bundling them avoids circular dependencies and provides complete CMS functionality.

### Why No db_table Override?

This is a greenfield extraction. We want proper Django conventions from day one:
- Clean table names
- Standard Django patterns
- Future-proof architecture

### Why Context Processor?

Menus need to be available site-wide in templates. Context processor is the Django-recommended approach for global template data.

## Extension Points

Users can:
1. **Extend Page model**: Use Profile Pattern with OneToOneField
2. **Custom menu icons**: Add to `MENU_ICON_CHOICES` via settings
3. **Override templates**: Place in project's `templates/django_directory_cms/`
4. **Add SEO rules**: Create custom rules that check Page model

## Publishing to PyPI (Automated)

This package uses **GitHub Actions** to automatically publish to PyPI when a release is created.

### Release Process

**1. Update Version Number**

```bash
# Edit version in both files
vim pyproject.toml  # [project] version = "0.1.1"
vim src/django_directory_cms/__init__.py  # __version__ = "0.1.1"
```

**2. Pre-Release Checks**

```bash
make check  # Run all quality checks
make test   # Ensure tests pass
```

**3. Commit and Tag**

```bash
git add pyproject.toml src/django_directory_cms/__init__.py
git commit -m "Bump version to 0.1.1"
git push origin master

# Create release
gh release create v0.1.1 \
  --title "Release v0.1.1" \
  --notes "Release notes here"
```

**4. Verify Workflow**

GitHub Actions will automatically:
1. Verify version matches tag
2. Run tests
3. Build package
4. Publish to PyPI

Monitor at: https://github.com/directory-platform/django-directory-cms/actions

## Related Files

- **workspace CLAUDE.md**: `/Users/samtexas/src/directory-platform/CLAUDE.md`
- **directory-builder CLAUDE.md**: `/Users/samtexas/src/directory-platform/directory-builder/CLAUDE.md`
- **django-seo-audit CLAUDE.md**: `/Users/samtexas/src/directory-platform/django-seo-audit/CLAUDE.md`
- **README.md**: User-facing documentation
- **pyproject.toml**: Package configuration

## Quick Reference

**Import patterns:**
```python
from django_directory_cms.pages.models import Page
from django_directory_cms.menus.models import MenuItem
from django_directory_cms.menus.context_processors import menu_items
```

**URL patterns:**
```python
# Include in project urls.py
path("pages/", include("django_directory_cms.pages.urls")),
```

**Settings:**
```python
INSTALLED_APPS = [
    "django_directory_cms.pages",
    "django_directory_cms.menus",
    "django_seo_audit",  # Required dependency
]

TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            'django_directory_cms.menus.context_processors.menu_items',
        ],
    },
}]
```

## Code Style

- Line length: 120 characters
- Python 3.12+ syntax
- Type hints on public methods
- Google-style docstrings
- Use double quotes for strings

## Dependencies

**Runtime:**
- Django 4.2+
- django-seo-audit 0.2.0+
- Pillow 10.0.0+ (for ImageField)

**Development:**
- ruff (linting and formatting)
- mypy (type checking)
- django-stubs (Django type stubs)

## Troubleshooting

**Migrations not applying:**
- Check app is in INSTALLED_APPS
- Verify app label is correct
- Run `make migrate`

**Menu items not showing in templates:**
- Verify context processor is registered
- Check MenuItem.is_active = True
- Ensure menu items exist in database

**Import errors:**
- Run `uv sync` to install dependencies
- Check PYTHONPATH in tests
- Verify package is in workspace members
