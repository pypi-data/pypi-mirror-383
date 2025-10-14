"""Constants for the menus app."""

# Curated list of Bootstrap icons for navigation menus
# Organized by category for easy selection in admin
# Icons are displayed visually in admin via custom widget
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
