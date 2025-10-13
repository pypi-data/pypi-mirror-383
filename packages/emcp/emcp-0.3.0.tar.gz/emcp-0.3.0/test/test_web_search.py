import pytest
from unittest.mock import Mock, patch
from emcp.web import web_search, format_search_results
from emcp.utils import MissingOrEmpty


def test_web_search_empty_query():
    """web_search raises error for empty query."""
    with pytest.raises(MissingOrEmpty):
        web_search("")


def test_web_search_with_query():
    """web_search returns formatted results for valid query."""
    mock_results = [
        {
            "title": "Python Programming",
            "href": "https://example.com/python",
            "body": "Learn Python programming language"
        },
        {
            "title": "Python Tutorial",
            "href": "https://example.com/tutorial",
            "body": "Complete Python tutorial for beginners"
        }
    ]

    with patch('emcp.web.DDGS') as mock_ddgs:
        mock_instance = Mock()
        mock_instance.text.return_value = mock_results
        mock_ddgs.return_value = mock_instance

        result = web_search("Python")

        # Verify DDGS was called correctly
        mock_instance.text.assert_called_once_with(
            "Python",
            backend     = 'duckduckgo',
            safesearch  = 'off',
            max_results = 10
        )

        # Verify format
        assert "index: 0" in result
        assert "title: Python Programming" in result
        assert "url: https://example.com/python" in result
        assert "snippet: Learn Python programming language" in result

        assert "index: 1" in result
        assert "title: Python Tutorial" in result


def test_format_search_results_empty():
    """format_search_results returns message for empty results."""
    result = format_search_results([])
    assert result == "No results found."


def test_format_search_results_single():
    """format_search_results formats a single result correctly."""
    results = [
        {
            "title": "Test Title",
            "href": "https://test.com",
            "body": "Test description"
        }
    ]

    result = format_search_results(results)

    assert "index: 0" in result
    assert "title: Test Title" in result
    assert "url: https://test.com" in result
    assert "snippet: Test description" in result


def test_format_search_results_multiple():
    """format_search_results formats multiple results correctly."""
    results = [
        {
            "title": "First Result",
            "href": "https://first.com",
            "body": "First description"
        },
        {
            "title": "Second Result",
            "href": "https://second.com",
            "body": "Second description"
        }
    ]

    result = format_search_results(results)

    # Check first result
    assert "index: 0" in result
    assert "title: First Result" in result
    assert "url: https://first.com" in result
    assert "snippet: First description" in result

    # Check second result
    assert "index: 1" in result
    assert "title: Second Result" in result
    assert "url: https://second.com" in result
    assert "snippet: Second description" in result

    # Check they're separated
    assert result.count("\n\n") >= 1


def test_format_search_results_missing_fields():
    """format_search_results handles missing fields gracefully."""
    results = [
        {
            "title": "Only Title"
            # Missing href and body
        }
    ]

    result = format_search_results(results)

    assert "index: 0" in result
    assert "title: Only Title" in result
    assert "url: No URL" in result
    assert "snippet: No description available" in result


def test_format_search_results_field_order():
    """format_search_results maintains correct field order."""
    results = [
        {
            "title": "Test",
            "href": "https://test.com",
            "body": "Description"
        }
    ]

    result = format_search_results(results)
    lines = result.split('\n')

    assert lines[0].startswith("index:")
    assert lines[1].startswith("title:")
    assert lines[2].startswith("url:")
    assert lines[3].startswith("snippet:")
