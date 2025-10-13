"""Unit tests for seminars module helper functions."""

from aws_blackbelt_mcp_server.tools.seminars import (
    _extract_categories_from_tags,
    _extract_youtube_id_from_url,
    _extract_youtube_url,
)


def test_extract_categories_valid():
    """Extract categories from tags."""
    tags = [
        {"tagNamespaceId": "GLOBAL#aws-tech-category", "name": "Machine Learning"},
        {"tagNamespaceId": "GLOBAL#aws-tech-category", "name": "Compute"},
    ]
    result = _extract_categories_from_tags(tags)
    assert result == ["Machine Learning", "Compute"]


def test_extract_categories_with_invalid_namespaces_and_names():
    """Handle empty tags and edge cases."""
    tags = [
        {"tagNamespaceId": "INVAIID_ID", "name": "INVALID_CATEGORY"},
        {"tagNamespaceId": "GLOBAL#aws-tech-category"},
        {"tagNamespaceId": "GLOBAL#aws-tech-category", "name": None},
        {"tagNamespaceId": "GLOBAL#aws-tech-category", "name": ""},
    ]
    assert _extract_categories_from_tags(tags) == []


def test_extract_categories_duplicates():
    """Remove duplicate categories."""
    tags = [
        {"tagNamespaceId": "GLOBAL#aws-tech-category", "name": "Lambda"},
        {"tagNamespaceId": "GLOBAL#aws-tech-category", "name": "Lambda"},
    ]
    assert _extract_categories_from_tags(tags) == ["Lambda"]


def test_extract_youtube_url_valid():
    """Extract valid YouTube URLs."""
    body = '<a href="https://youtu.be/abc123">Youtube</a>'
    assert _extract_youtube_url(body) == "https://youtu.be/abc123"

    # With parameters
    body = '<a href="https://youtu.be/abc123?t=30">Youtube</a>'
    assert _extract_youtube_url(body) == "https://youtu.be/abc123?t=30"


def test_extract_youtube_url_none():
    """Return None for invalid cases."""
    assert _extract_youtube_url("") is None
    assert _extract_youtube_url("No video links") is None


def test_extract_youtube_id_valid():
    """Extract YouTube video ID from valid youtu.be URLs."""
    # Basic youtu.be URL
    assert _extract_youtube_id_from_url("https://youtu.be/abc123") == "abc123"

    # With query parameters
    assert _extract_youtube_id_from_url("https://youtu.be/xyz789?t=30") == "xyz789"
    assert _extract_youtube_id_from_url("https://youtu.be/def456?t=30&feature=share") == "def456"


def test_extract_youtube_id_invalid():
    """Return None for invalid or unsupported URLs."""
    # Empty or None input
    assert _extract_youtube_id_from_url("") is None
    assert _extract_youtube_id_from_url(None) is None

    # Invalid URLs
    assert _extract_youtube_id_from_url("https://example.com") is None
