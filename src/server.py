from flask import Flask
from threading import Thread
from sqlalchemy import text
from src.bot.bot import run_bot
from src.utils.log import check_bot_health, clear_error_logs
from src.db.db import get_db
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from src.db.repository import (
    get_all_active_users_with_websites,
    add_or_update_bookmarks,
    get_user_credentials,
    synchronize_websites,
)
from src.scraper.main_scraper import driver, scrape_bookmarks
from datetime import datetime
import atexit
from src.utils.log import logging


app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file


@app.route("/health")
def health_check():
    bot_healthy = check_bot_health()
    database_healty = get_db().execute(text("SELECT 1")).fetchone()
    # Optionally clear the error logs after a health check
    clear_error_logs()
    health_status = {
        "flask_server": "operational",
        "databas": "operational" if database_healty else "down",
        "bot_status": "operational" if bot_healthy else "down",
    }
    return health_status, 200 if bot_healthy else 500


def update_websites_list_actual():
    with get_db() as db_session:
        if synchronize_websites(db_session=db_session):
            logging.info("Sync websites successfully")


def update_bookmarks_for_all_users():
    with get_db() as db_session:
        users_with_websites = get_all_active_users_with_websites(db_session)
        if not users_with_websites:
            logging.info("No active users with associated websites found.")
            return
        for user in users_with_websites:
            if not user.websites:
                logging.info(
                    f"User {user.chat_id} has no associated websites to scrape."
                )
                continue
            for user_website in user.websites:
                # Assuming you have a method to decrypt the credentials
                decrypted_username, decrypted_password = get_user_credentials(
                    db_session, user.chat_id, user_website.website_id
                )
                # Now scrape bookmarks using the decrypted credentials
                bookmarks_data = scrape_bookmarks(
                    user_website.website_id,
                    decrypted_username,
                    decrypted_password,
                )
                # Ensure that the bookmarks_data is in the correct format for add_or_update_bookmarks
                add_or_update_bookmarks(
                    db_session,
                    user.chat_id,
                    user_website.website_id,
                    bookmarks_data,
                )


def runFlask():
    # Set up the scheduler with your desired configuration
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_bookmarks_for_all_users,
        "interval",
        hours=6,
        next_run_time=datetime.now(),  # Start the job right away
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    # Start the bot in a separate thread so that it doesn't block the Flask server
    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    # Run Flask app in the main thread
    app.run(host="0.0.0.0", port=8000, debug=False)
    update_websites_list_actual()
    # Ensure the scheduler is safely shut down when the app exits
