from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from src.utils.log import logging
import requests



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



