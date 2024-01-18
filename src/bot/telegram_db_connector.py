from src.scraper.main_scraper import scrape_bookmarks
from src.db.repository import (
    add_or_update_bookmarks,
    get_user_credentials,
    get_active_user_with_websites,
)
from src.db.db import get_db
from src.utils.log import logging


def manual_update(chat_id):
    with get_db() as db:
        user_with_websites = get_active_user_with_websites(db, chat_id)
        if not user_with_websites:
            logging.error(f"No active websites found for user with chat_id {chat_id}.")
            return  # Or handle this case as needed

        # If the user has no websites, this list will be empty and the loop will not run
        for user_website in user_with_websites.websites:
            decrypted_username, decrypted_password = get_user_credentials(
                db, chat_id, user_website.website_id
            )
            # You'll need to implement a function that prepares the scraper based on the website details
            bookmarks_data = scrape_bookmarks(
                user_website.website_id, decrypted_username, decrypted_password
            )
            # Make sure to handle the case where scraping fails and bookmarks_data is not as expected
            if bookmarks_data:
                add_or_update_bookmarks(
                    db, chat_id, user_website.website_id, bookmarks_data
                )



