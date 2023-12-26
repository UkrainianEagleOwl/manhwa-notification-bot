from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv

load_dotenv()

# User credentials (you'll want to secure these, perhaps using environment variables)
username = os.getenv("WORK_USER_LOGIN")
password = os.getenv("WORK_USER_PASSWORD")

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
    # Navigate to the bookmarks page
    driver.get("https://manga-scans.com/bookmarks/")

    # Wait for the page elements to load
    time.sleep(2)

    # Locate the bookmark elements using the class 'unit'
    bookmarks = driver.find_elements(By.CLASS_NAME, "unit")

    # Loop through the bookmark elements and extract the details
    for bookmark in bookmarks:
        # Extract the link to the manga (href attribute of an anchor tag with the class 'poster')
        link = bookmark.find_element(By.CLASS_NAME, "poster").get_attribute("href")

        # Extract the image (src attribute of an img tag within a div with the class 'poster')
        image = bookmark.find_element(By.CSS_SELECTOR, ".poster img").get_attribute(
            "src"
        )

        # Extract the title (text within the 'info' class, which might be within an anchor tag)
        title = bookmark.find_element(By.CSS_SELECTOR, ".info a").text

        # Extract the chapter title (text from an element with the class 'richdata')
        chapter_title = bookmark.find_element(By.CLASS_NAME, "richdata").text

        # Extract the date of the last update (text from a div with the class 'dropdown')
        last_update = bookmark.find_element(By.CLASS_NAME, "dropdown").text

        # Print the details (or process them as needed)
        print(
            f"Title: {title}, Link: {link}, Chapter: {chapter_title}, Last Update: {last_update}"
        )


# Login to the website
login(driver, username, password)

# Scrape the bookmarks
scrape_bookmarks(driver)

# Close the browser when done
driver.quit()
