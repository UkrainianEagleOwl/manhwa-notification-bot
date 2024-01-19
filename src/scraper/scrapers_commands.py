from src.scraper.main_scraper import setup_driver
import src.scraper.manga_scans_scraper as ms_scraper
from src.db.constant_manga_websites import AVAILABLE_WEBSITES
from src.utils.log import logging


def scrape_bookmarks(manga_web_site_id, username, password):
    if manga_web_site_id == 1:
        driver = setup_driver()
        ms_scraper.login(driver, username, password)
        bookmarks_data = ms_scraper.scrape_bookmarks(driver)
        logging.info("Got all bookmarks.")
        return bookmarks_data
