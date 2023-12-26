import logging
import os
import threading
import schedule
import time
from telegram import Update, ext
from dotenv import load_dotenv
from scrapping import setup_driver, login, scrape_bookmarks, format_bookmarks_data

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

username = os.getenv("WORK_USER_LOGIN")
password = os.getenv("WORK_USER_PASSWORD")

# Global variable to store the bot's context
bot_context = None


# Placeholder for your scraping functions
def check_for_updates():
    # Your scraping logic here
    return "Sample updates"


def get_bookmarks_list():
    # Your scraping logic to list bookmarks
    return "Sample list of bookmarks"


# Define the asynchronous start command handler
async def start(update: Update, context: ext.CallbackContext) -> None:
    global bot_context
    bot_context = context
    user = update.effective_user
    logger.info(f"User {user.id} started the bot.")
    await context.bot.send_message(
        chat_id=user.id,
        text="Hello! This is your Manhwa Update Notifier Bot. Your chat ID is "
        + str(user.id),
    )


async def check_updates_command(update: Update, context: ext.CallbackContext) -> None:
    updates = check_for_updates()  # Replace with your actual scraping function
    await update.message.reply_text(f"Updates: {updates}")


async def list_bookmarks_command(update: Update, context: ext.CallbackContext) -> None:
    driver = setup_driver()  # Function to set up the Selenium driver
    login(driver, username, password)
    bookmarks = scrape_bookmarks(driver)
    driver.quit()

    # Initialize an empty string for the summary message
    summary_message = ""

    for bookmark in bookmarks:
        # Format each line as: Title (hyperlinked) - Last Chapter - Date Update
        summary_message += f"<a href='{bookmark['link']}'>{bookmark['title']}</a> - {bookmark['chapter_title']} - {bookmark['last_update']}\n"

        # Check if message is too long and send in parts if necessary
        if len(summary_message) >= 4000:
            await update.message.reply_text(
                summary_message, parse_mode="HTML", disable_web_page_preview=True
            )
            summary_message = ""  # Reset summary message

    # Send any remaining part of the summary message
    if summary_message:
        await update.message.reply_text(
            summary_message, parse_mode="HTML", disable_web_page_preview=True
        )


async def echo(update: Update, context: ext.CallbackContext) -> None:
    await update.message.reply_text(update.message.text)


async def error(update: Update, context: ext.CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def scheduled_check():
    if bot_context:
        updates = check_for_updates()  # Replace with your actual scraping function
        if updates:
            bot_context.bot.send_message(
                chat_id=os.getenv("SHEDULE_CHAT_ID"),
                text=f"Daily Updates: {updates}",  # Replace 'your_chat_id' with your actual chat ID
            )


# Schedule the job
schedule.every().day.at("09:00").do(scheduled_check)


# Run the schedule in a separate thread
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


def main() -> None:
    bot_token = os.getenv("BOT_TOKEN")
    application = ext.Application.builder().token(bot_token).build()

    application.add_handler(ext.CommandHandler("start", start))
    application.add_handler(ext.CommandHandler("check_updates", check_updates_command))
    application.add_handler(
        ext.CommandHandler("list_bookmarks", list_bookmarks_command)
    )
    application.add_handler(ext.MessageHandler(ext.filters.TEXT, echo))
    application.add_error_handler(error)

    application.run_polling()

    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()


if __name__ == "__main__":
    main()
