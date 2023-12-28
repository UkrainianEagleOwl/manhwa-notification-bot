import schedule
import time
import os
from src.utils import check_for_updates


def scheduled_check(bot_context):
    """
    The scheduled_check function is a function that checks for updates every day at midnight.
    If there are any updates, it sends them to the chat ID specified in the SHEDULE_CHAT_ID environment variable.

    :return: A list of updates
    :doc-author: Trelent
    """
    if bot_context:
        updates = check_for_updates()  # Replace with your actual scraping function
        if updates:
            bot_context.bot.send_message(
                chat_id=os.getenv("SCHEDULE_CHAT_ID"),
                text=f"Daily Updates: {updates}",  # Replace 'your_chat_id' with your actual chat ID
            )


# Run the schedule in a separate thread
def run_schedule():
    """
    The run_schedule function is a simple while loop that runs the schedule.run_pending() function every second.
    The run_schedule function is called in the main thread of execution, and it will block until all scheduled jobs have been executed.

    :return: The schedule
    :doc-author: Trelent
    """
    while True:
        schedule.run_pending()
        time.sleep(1)


# Schedule the job
schedule.every().day.at("09:00").do(scheduled_check)
