"""[Feature: News Management] [Story: NM-ADMIN-001] HTML sanitization utility for XSS prevention."""

import bleach

# Allowed HTML tags for news content
ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "em",
    "u",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "a",
    "img",
}

# Allowed attributes
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
}


def sanitize_html(content: str) -> str:
    """
    [Feature: News Management] [Story: NM-ADMIN-001] Sanitize HTML content to prevent XSS.

    Args:
        content: Raw HTML content.

    Returns:
        Sanitized HTML content with dangerous tags and attributes removed.
    """
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )
