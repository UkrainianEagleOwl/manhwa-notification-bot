from src.bot import run_bot, runFlask
from threading import Thread

if __name__ == "__main__":
    # Start Flask server in a new thread
    flask_thread = Thread(target=runFlask)
    flask_thread.start()
    run_bot()
