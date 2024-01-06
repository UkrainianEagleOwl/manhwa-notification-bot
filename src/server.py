from flask import Flask
from threading import Thread
from sqlalchemy import text
from src.bot.bot import run_bot
from src.utils.log import check_bot_health, clear_error_logs
from src.db.db import get_db
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file

# Placeholder for database setup
# This will eventually involve initializing the database connection
# and providing a session or engine for the Flask app to use.
# For now, it's just a placeholder to show where this will go.
# from src.db import initialize_db
# initialize_db(app)


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


def runFlask():
    # Start the bot in a separate thread so that it doesn't block the Flask server
    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    # Run Flask app in the main thread
    app.run(host="0.0.0.0", port=8000, debug=False)
