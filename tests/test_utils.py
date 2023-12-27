import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, Mock
from src.utils import (
    format_update_message,
    format_bookmarks_page,
    check_for_updates,
)  # Replace with your actual import


def test_format_update_message():
    # Given a sample manga update
    sample_update = {
        "title": "My Manga Title",
        "chapter_title": "Chapter 123",
        "last_update": "10 mins ago",
        "link": "http://example.com/manga/chapter123",
    }

    # When format_update_message is called with this sample
    result = format_update_message(sample_update)

    # Then the result should be a formatted string
    expected_message = (
        "<b>My Manga Title</b>\n"
        "Chapter: Chapter 123\n"
        "Updated: 10 mins ago\n"
        "<a href='http://example.com/manga/chapter123'>Read Now</a>"
    )

    assert result == expected_message


@pytest.mark.asyncio
async def test_format_bookmarks_page():
    # Given a sample list of bookmarks
    sample_bookmarks = [
        {
            "title": "Manga 1",
            "link": "http://example.com/manga1",
            "last_update": "1 hour ago",
        },
        {
            "title": "Manga 2",
            "link": "http://example.com/manga2",
            "last_update": "2 hours ago",
        },
        {
            "title": "Manga 3",
            "link": "http://example.com/manga3",
            "last_update": "3 hours ago",
        }
        # ... add more if needed for the test
    ]

    # Page and page size for the test
    page = 0  # First page
    page_size = 2  # Two items per page

    # When format_bookmarks_page is called
    result = await format_bookmarks_page(sample_bookmarks, page, page_size)

    # Then the result should be a formatted string for the first page
    expected_message = (
        "<b>Your Bookmarked Mangas:</b>\n\n"
        "<a href='http://example.com/manga1'>Manga 1</a> - Last updated: 1 hour ago\n"
        "<a href='http://example.com/manga2'>Manga 2</a> - Last updated: 2 hours ago\n"
    )

    assert result == expected_message


@patch("src.utils.setup_driver")
@patch("src.utils.login")
@patch("src.utils.scrape_bookmarks")
def test_check_for_updates(
    mock_scrape_bookmarks, mock_login, mock_setup_driver, mock_driver
):
    # Setup mock
    mock_setup_driver.return_value = mock_driver
    mock_scrape_bookmarks.return_value = [
        {
            "title": "Manga 1",
            "link": "http://example.com/manga1",
            "last_update": "1 hour ago",
        },
        {
            "title": "Manga 2",
            "link": "http://example.com/manga2",
            "last_update": "1 day ago",
        },
        {
            "title": "Manga 3",
            "link": "http://example.com/manga3",
            "last_update": "15 min ago",
        },
        {
            "title": "Manga 4",
            "link": "http://example.com/manga4",
            "last_update": "5 week ago",
        },
    ]

    # Call the function
    updates = check_for_updates("username", "password")

    # Verify
    mock_setup_driver.assert_called_once()
    mock_login.assert_called_once_with(mock_driver, "username", "password")
    mock_scrape_bookmarks.assert_called_once_with(mock_driver)
    mock_driver.quit.assert_called_once()

    # Check if updates are filtered correctly
    assert len(updates) == 2
    assert updates[0]["title"] == "Manga 1"
    assert updates[1]["title"] == "Manga 3"
