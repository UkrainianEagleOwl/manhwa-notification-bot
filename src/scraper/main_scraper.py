from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from src.utils.log import logging
import requests
import src.scraper.manga_scans_scraper as ms_scraper
from src.db.constant_manga_websites import AVAILABLE_WEBSITES


def setup_driver():
    """
    The setup_driver function initializes a new browser session with ChromeDriverManager.
    It also sets up the ChromeDriver options to run in headless mode, if you don't need a browser UI.


    :return: A chromedriver instance
    :doc-author: Trelent
    """
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


def check_connectivity(url):
    try:
        response = requests.get(url, timeout=15)
        return response.status_code == 200
    except requests.RequestException as e:
        logging.info(f"Connectivity check failed: {e}")
        return False


def scrape_bookmarks(manga_web_site_id, username, password):
    if manga_web_site_id == 1:
        driver = setup_driver()
        ms_scraper.login(driver, username, password)
        bookmarks_data = ms_scraper.scrape_bookmarks(driver)
        logging.info("Got all bookmarks.")
        return bookmarks_data
