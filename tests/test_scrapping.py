import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import unittest
from unittest.mock import patch, MagicMock
from src.scrapping import (
    setup_driver,
    login,
    scrape_bookmarks,
)  # Replace with your actual import
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

@patch("src.scrapping.webdriver.Chrome")
@patch("src.scrapping.ChromeDriverManager")
def test_setup_driver(mock_chromedriver_manager, mock_chrome):
    # Create a mock for the Chrome options
    mock_options = MagicMock()
    mock_chrome.return_value = MagicMock()  # Mock return value for Chrome WebDriver

    # Call the setup_driver function
    driver = setup_driver()

    # Assert ChromeDriverManager is initialized
    mock_chromedriver_manager.assert_called_once()

    # Assert webdriver.Chrome is called with correct options
    mock_chrome.assert_called_once()
    args, kwargs = mock_chrome.call_args
    assert "--headless" in kwargs["options"].arguments
    assert "--disable-gpu" in kwargs["options"].arguments
    assert "--no-sandbox" in kwargs["options"].arguments

    # Optionally, assert that a WebDriver object is returned
    assert driver is not None


@pytest.fixture
def mock_driver_login():
    # Create mock web elements
    mock_username_field = MagicMock()
    mock_password_field = MagicMock()
    mock_login_button = MagicMock()

    # Create a mock web driver
    mock = MagicMock()
    # Mock the find_element method to return the mock elements
    mock.find_element.side_effect = lambda by, value: {
        (By.ID, "user_login"): mock_username_field,
        (By.ID, "user_pass"): mock_password_field,
        (By.ID, "wp-submit"): mock_login_button,
    }.get(
        (by, value), MagicMock()
    )  # Return a default MagicMock if the ID doesn't match
    return mock


def test_login(mock_driver_login):
    # Mock username and password
    username = "testuser"
    password = "testpass"

    # Call the login function
    login(mock_driver_login, username, password)

    # Verify that the driver navigated to the login page
    mock_driver_login.get.assert_called_once_with("https://manga-scans.com/login")

    # Verify that the username and password fields were found and filled in
    username_field = mock_driver_login.find_element(By.ID, "user_login")
    password_field = mock_driver_login.find_element(By.ID, "user_pass")
    username_field.send_keys.assert_called_once_with(username)
    password_field.send_keys.assert_called_once_with(password)

    # Verify that the login button was clicked
    login_button = mock_driver_login.find_element(By.ID, "wp-submit")
    login_button.click.assert_called_once()


@pytest.fixture
def mock_driver():
    # Create mock web elements for bookmarks
    mock_bookmark1 = MagicMock()
    mock_bookmark1.find_element.side_effect = lambda by, value: {
        (By.CLASS_NAME, "poster"): MagicMock(
            get_attribute=MagicMock(return_value="http://example.com/manga1")
        ),  # link
        (By.CSS_SELECTOR, ".info a"): MagicMock(text="Title 1"),  # title
        (By.CLASS_NAME, "richdata"): MagicMock(text="Chapter 1"),  # chapter_title
        (By.CLASS_NAME, "dropdown"): MagicMock(text="1 hour ago"),  # last_update
        (By.CSS_SELECTOR, ".poster img"): MagicMock(
            get_attribute=MagicMock(return_value="http://example.com/img1")
        ),  # image
    }[by, value]

    mock_bookmark2 = MagicMock()
    mock_bookmark2.find_element.side_effect = lambda by, value: {
        (By.CLASS_NAME, "poster"): MagicMock(
            get_attribute=MagicMock(return_value="http://example.com/manga2")
        ),  # link
        (By.CSS_SELECTOR, ".info a"): MagicMock(text="Title 2"),  # title
        (By.CLASS_NAME, "richdata"): MagicMock(text="Chapter 2"),  # chapter_title
        (By.CLASS_NAME, "dropdown"): MagicMock(text="2 min ago"),  # last_update
        (By.CSS_SELECTOR, ".poster img"): MagicMock(
            get_attribute=MagicMock(return_value="http://example.com/img2")
        ),  # image
    }[by, value]

    # Mock the driver's methods
    mock = MagicMock()
    mock.get = MagicMock()
    mock.find_elements.return_value = [mock_bookmark1, mock_bookmark2]

    return mock

class TestScrapeBookmarks(unittest.TestCase):
    @patch("src.scrapping.logger")
    @patch("src.scrapping.time.sleep", return_value=None)  # Mock sleep to bypass time delay
    def test_scrape_bookmarks(self, mock_sleep, mock_logger):
        # Mock the webdriver and the elements it will find
        mock_driver = MagicMock()
        mock_bookmark_element = MagicMock()

        # Set up the side effects for the happy path
        mock_bookmark_element.find_element.side_effect = [
            MagicMock(get_attribute=MagicMock(return_value="http://example.com/manga")),
            MagicMock(get_attribute=MagicMock(return_value="http://example.com/image.jpg")),
            MagicMock(text="Manga Title"),
            MagicMock(text="Chapter 123"),
            MagicMock(text="1 hour ago"),  # This will be returned for last_update in the first iteration
        ]

        # Set up the side effects for when the last_update is not found
        mock_bookmark_element_missing_last_update = MagicMock()
        mock_bookmark_element_missing_last_update.find_element.side_effect = [
            MagicMock(get_attribute=MagicMock(return_value="http://example.com/manga2")),
            MagicMock(get_attribute=MagicMock(return_value="http://example.com/image2.jpg")),
            MagicMock(text="Manga Title 2"),
            MagicMock(text="Chapter 456"),
            NoSuchElementException("No such element")  # Simulate an element not found exception for last_update
        ]

        # Simulate an exception during processing of a bookmark
        mock_bookmark_element_error = MagicMock()
        mock_bookmark_element_error.find_element.side_effect = Exception("Unexpected error")

        # Return the mock elements in a list as find_elements would
        mock_driver.find_elements.return_value = [
            mock_bookmark_element,
            mock_bookmark_element_missing_last_update,
            mock_bookmark_element_error  # This will cause an error during processing
        ]

        # Call the function to be tested
        result = scrape_bookmarks(mock_driver)

        # Assertions for the happy path
        self.assertEqual(result[0]["title"], "Manga Title")
        self.assertEqual(result[0]["link"], "http://example.com/manga")
        self.assertEqual(result[0]["chapter_title"], "Chapter 123")
        self.assertEqual(result[0]["last_update"], "1 hour ago")
        self.assertEqual(result[0]["image"], "http://example.com/image.jpg")

        # Assertions for the missing last_update scenario
        self.assertEqual(result[1]["title"], "Manga Title 2")
        self.assertEqual(result[1]["link"], "http://example.com/manga2")
        self.assertEqual(result[1]["chapter_title"], "Chapter 456")
        self.assertEqual(result[1]["last_update"], "many time ago")  # Fallback text
        self.assertEqual(result[1]["image"], "http://example.com/image2.jpg")

        # Now there should be a call to logger.error due to the processing error
        mock_logger.error.assert_called_once_with("Error processing a bookmark: Unexpected error")