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
)
from src.scraper.main_scraper import driver
import src.scraper.manga_scans_scraper as ms_scraper
from datetime import datetime
import atexit


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


# Example route using the database session
@app.route("/example")
def example():
    # Get a session
    db_session = next(get_db())
    # Perform database operations here...
    # Close the session
    db_session.close()
    return "This is an example route."


def update_bookmarks_for_all_users():
    db_session = next(get_db())
    try:
        users_with_websites = get_all_active_users_with_websites(db_session)
        for user in users_with_websites:
            for user_website in user.websites:
                # Ensure you have a scraper function that can handle the website details
                if user_website.website == 1:
                    bookmarks_data = ms_scraper.scrape_bookmarks(driver)
                    # Update the bookmarks in the database
                    add_or_update_bookmarks(
                        db_session,
                        user.chat_id,
                        user_website.website_id,
                        bookmarks_data,
                    )
    finally:
        db_session.close()


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

    # Ensure the scheduler is safely shut down when the app exits
