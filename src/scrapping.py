from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


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
        print(f"Connectivity check failed: {e}")
        return False


def login(driver, username, password):
    """
    The login function logs into the Manga Scans website.

    :param driver: Pass in the webdriver object
    :param username: Pass the username to the login function
    :param password: Pass the password to the login function
    :return: The driver object
    :doc-author: Trelent
    """

    if check_connectivity("https://manga-scans.com/login"):
        logging.info(
            "Connectivity check to manga website passed. Proceeding with Selenium WebDriver."
        )
    else:
        logging.error(
            "Connectivity check to manga website failed. Cannot reach the login page."
        )

    if check_connectivity("https://www.google.com"):
        logging.info(
            "Connectivity check to google passed. Proceeding with Selenium WebDriver."
        )
    else:
        logging.error(
            "Connectivity check to google failed. Cannot reach the login page."
        )
    # Open the login page
    driver.get("https://manga-scans.com/login")

    # Initialize WebDriverWait
    wait = WebDriverWait(driver, 60)
    logging.info("Selenium WebDriver try reach the login page.")
    # Wait for the username field to be present and visible
    username_field = wait.until(
        EC.visibility_of_element_located((By.ID, "user_login")),
        message="Can not find username field",
    )
    logging.info("Got username field.")

    # Wait for the password field to be present and visible
    password_field = wait.until(
        EC.visibility_of_element_located((By.ID, "user_pass")),
        message="Can not find password field",
    )
    logging.info("Got password field.")
    # Wait for the login button to be present and clickable
    login_button = wait.until(
        EC.element_to_be_clickable((By.ID, "wp-submit")),
        message="Can not find login button",
    )
    logging.info("Got login button.")
    # Enter the login credentials
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Click the login button
    login_button.click()
    logging.info("Login succesfully.")


def scrape_bookmarks(driver):
    """
    The scrape_bookmarks function scrapes the bookmarks page of manga-scans.com and returns a list of dictionaries containing information about each bookmark.

    :param driver: Pass the webdriver object to the function
    :return: A list of dictionaries
    :doc-author: Trelent
    """
    driver.get("https://manga-scans.com/bookmarks/")
    time.sleep(2)
    bookmarks = driver.find_elements(By.CLASS_NAME, "unit")
    logging.info("Bookmarks elements are here.")

    bookmarks_data = []
    for bookmark in bookmarks:
        try:
            link = bookmark.find_element(By.CLASS_NAME, "poster").get_attribute("href")
            image = bookmark.find_element(By.CSS_SELECTOR, ".poster img").get_attribute(
                "src"
            )
            title = bookmark.find_element(By.CSS_SELECTOR, ".info a").text
            chapter_title = bookmark.find_element(By.CLASS_NAME, "richdata").text
            try:
                last_update = bookmark.find_element(By.CLASS_NAME, "dropdown").text
            except:
                last_update = "many time ago"

            bookmarks_data.append(
                {
                    "title": title,
                    "link": link,
                    "chapter_title": chapter_title,
                    "last_update": last_update,
                    "image": image,
                }
            )
            logging.info("Got another one bookmark.")
        except Exception as e:
            logger.error(f"Error processing a bookmark: {e}")

    return bookmarks_data
