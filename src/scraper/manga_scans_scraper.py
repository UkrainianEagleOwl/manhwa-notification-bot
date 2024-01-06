import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils.log import logging, logger
from src.scraper.main_scraper import check_connectivity,setup_driver


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
    # if check_connectivity("https://www.google.com"):
    #     logging.info(
    #         "Connectivity check to google passed. Proceeding with Selenium WebDriver."
    #     )
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


def check_for_updates(username, password):
    """
    The check_for_updates function checks for updates to the bookmarks on your account.
    It returns a list of dictionaries, each dictionary containing information about a bookmark that has been updated recently.
    The keys in each dictionary are: 'title', 'url', and 'last_update'.


    :return: A list of dictionaries
    """
    driver = setup_driver()
    login(driver, username, password)
    bookmarks_data = scrape_bookmarks(driver)
    logging.info("Got all bookmarks.")
    driver.quit()

    recent_updates = []
    for bookmark in bookmarks_data:
        # Check if 'last_update' indicates a recent update (within hours or minutes)
        if "hour" in bookmark["last_update"] or "min" in bookmark["last_update"]:
            recent_updates.append(bookmark)

    return recent_updates
