from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging


logger = logging.getLogger(__name__)


def login(driver, username, password):
    # Open the login page
    driver.get("https://manga-scans.com/login")

    # Wait for the login elements to load
    time.sleep(2)

    # Locate the username and password fields and the login button
    username_field = driver.find_element(By.ID, "user_login")
    password_field = driver.find_element(By.ID, "user_pass")
    login_button = driver.find_element(By.ID, "wp-submit")

    # Enter the login credentials
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Click the login button
    login_button.click()

    # Wait for the login to complete and page to load
    time.sleep(2)


def scrape_bookmarks(driver):
    driver.get("https://manga-scans.com/bookmarks/")
    time.sleep(2)
    bookmarks = driver.find_elements(By.CLASS_NAME, "unit")

    bookmarks_data = []
    for bookmark in bookmarks:
        try:
            link = bookmark.find_element(By.CLASS_NAME, "poster").get_attribute("href")
            image = bookmark.find_element(By.CSS_SELECTOR, ".poster img").get_attribute(
                "src"
            )
            title = bookmark.find_element(By.CSS_SELECTOR, ".info a").text
            chapter_title = bookmark.find_element(By.CLASS_NAME, "richdata").text
            last_update = bookmark.find_element(By.CLASS_NAME, "dropdown").text

            bookmarks_data.append(
                {
                    "title": title,
                    "link": link,
                    "chapter_title": chapter_title,
                    "last_update": last_update,
                    "image": image,
                }
            )
        except Exception as e:
            logger.error(f"Error processing a bookmark: {e}")

    return bookmarks_data


def format_bookmarks_data(bookmarks_data):
    formatted_message = ""
    for bookmark in bookmarks_data:
        formatted_message += f"Title: {bookmark['title']}\n"
        formatted_message += f"Chapter: {bookmark['chapter_title']}\n"
        formatted_message += f"Last Update: {bookmark['last_update']}\n"
        formatted_message += f"Image: {bookmark['image']}\n"  # Add the image URL
        formatted_message += f"Link: {bookmark['link']}\n\n"
    return formatted_message


def setup_driver():
    # Set up the ChromeDriver options
    options = Options()
    options.add_argument(
        "--headless"
    )  # Run in headless mode, if you don't need a browser UI
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Initialize a new browser session with ChromeDriverManager
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    return driver