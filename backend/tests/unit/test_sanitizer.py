"""[Feature: News Management] [Story: NM-ADMIN-001] Unit tests for HTML sanitizer."""

import pytest

from app.core.sanitizers import sanitize_html


class TestSanitizeHtml:
    """Test cases for HTML sanitization."""

    def test_safe_html_preserved(self):
        """[Feature: News Management] [Story: NM-ADMIN-001] Test that safe HTML is preserved."""
        content = "<p>Safe content</p>"
        sanitized = sanitize_html(content)
        assert sanitized == "<p>Safe content</p>"

    def test_script_tags_removed(self):
        """[Feature: News Management] [Story: NM-ADMIN-001] Test that script tags are removed."""
        content = "<script>alert('xss')</script><p>Safe</p>"
        sanitized = sanitize_html(content)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        assert "<p>Safe</p>" in sanitized

    def test_onclick_attributes_removed(self):
        """[Feature: News Management] [Story: NM-ADMIN-001] Test that onclick attributes are removed."""
        content = "<p onclick=\"alert('xss')\">Click me</p>"
        sanitized = sanitize_html(content)
        assert "onclick" not in sanitized
        assert "<p>Click me</p>" in sanitized

    def test_iframe_tags_removed(self):
        """Test that iframe tags are removed."""
        content = '<iframe src="evil.com"></iframe><p>Safe</p>'
        sanitized = sanitize_html(content)
        assert "<iframe" not in sanitized
        assert "<p>Safe</p>" in sanitized

    def test_allowed_tags_preserved(self):
        """Test that allowed tags are preserved."""
        content = "<h1>Title</h1><strong>Bold</strong><em>Italic</em><p>Paragraph</p>"
        sanitized = sanitize_html(content)
        assert "<h1>" in sanitized
        assert "<strong>" in sanitized
        assert "<em>" in sanitized
        assert "<p>" in sanitized

    def test_img_alt_text_preserved(self):
        """Test that img alt text is preserved."""
        content = '<img src="image.jpg" alt="My image" title="Image title">'
        sanitized = sanitize_html(content)
        assert 'alt="My image"' in sanitized
        assert 'title="Image title"' in sanitized

    def test_link_href_preserved(self):
        """Test that link hrefs are preserved."""
        content = '<a href="https://example.com" title="Link">Click</a>'
        sanitized = sanitize_html(content)
        assert 'href="https://example.com"' in sanitized
        assert 'title="Link"' in sanitized
