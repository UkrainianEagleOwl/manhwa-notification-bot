import logging
from logging.handlers import RotatingFileHandler
import os


# Create a custom logging handler that stores logs in memory
class HealthCheckHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.error_logs = []

    def emit(self, record):
        # Only store records of level ERROR or higher
        if record.levelno >= logging.ERROR:
            self.error_logs.append(self.format(record))

    def get_error_logs(self):
        return self.error_logs

    def clear_error_logs(self):
        self.error_logs = []


# Enable logging and set up the formatter
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Instantiate the logger
logger = logging.getLogger(__name__)

# Set up a rotating file handler (optional) for persistent logging
log_file_path = os.path.join(os.path.dirname(__file__), "bot.log")
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=1024 * 1024 * 5, backupCount=2
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Create and add the health check handler
health_check_handler = HealthCheckHandler()
logger.addHandler(health_check_handler)


# Use this function in your server.py to check the bot's health
def check_bot_health():
    # If there are any error logs, we consider the bot to be unhealthy
    return len(health_check_handler.get_error_logs()) == 0


# Clear the error logs after health check
def clear_error_logs():
    health_check_handler.clear_error_logs()
