import logging
import os
import threading
import schedule
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
from scrapping import setup_driver, login, scrape_bookmarks

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


def scheduled_check():
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
                chat_id=os.getenv("SHEDULE_CHAT_ID"),
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


def check_for_updates():
    """
    The check_for_updates function checks for updates to the bookmarks on your account.
    It returns a list of dictionaries, each dictionary containing information about a bookmark that has been updated recently.
    The keys in each dictionary are: 'title', 'url', and 'last_update'.


    :return: A list of dictionaries
    :doc-author: Trelent
    """
    driver = setup_driver()
    login(driver, username, password)
    bookmarks_data = scrape_bookmarks(driver)
    driver.quit()

    recent_updates = []
    for bookmark in bookmarks_data:
        # Check if 'last_update' indicates a recent update (within hours or minutes)
        if "hour" in bookmark["last_update"] or "min" in bookmark["last_update"]:
            recent_updates.append(bookmark)

    return recent_updates


def format_update_message(update):
    """
    Formats the details of a manga update into a user-friendly message.

    Args:
    update (dict): A dictionary containing details about the manga update.

    Returns:
    str: A formatted message string.
    """
    # Constructing the message with HTML formatting for Telegram
    message = (
        f"<b>{update['title']}</b>\n"
        f"Chapter: {update['chapter_title']}\n"
        f"Updated: {update['last_update']}\n"
        f"<a href='{update['link']}'>Read Now</a>"
    )
    return message


# Define the asynchronous start command handler
async def start(update, context):
    # Friendly greeting message
    greeting_message = "Welcome to MangaMate! 📚✨\nYour personal assistant for staying updated with your favorite Manga. What would you like to do today?"

    # Keyboard with buttons for different actions
    keyboard = [
        [InlineKeyboardButton("Get Latest Update", callback_data="get_update")],
        [InlineKeyboardButton("Get My Manga List", callback_data="get_all_list")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the greeting message followed by the keyboard
    await update.message.reply_text(greeting_message, reply_markup=reply_markup)


async def check_updates_command(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    recent_updates = check_for_updates()

    # Now use 'query.message' to send a reply
    for manga_update in recent_updates:
        message = format_update_message(manga_update)
        await query.message.reply_photo(
            photo=manga_update["image"], caption=message, parse_mode="HTML"
        )


async def list_bookmarks_command(update: Update, context: CallbackContext) -> None:
    query = update.callback_query  # Get the callback query from the update
    driver = setup_driver()  # Function to set up the Selenium driver
    login(driver, username, password)
    bookmarks = scrape_bookmarks(driver)
    driver.quit()

    # You should save the bookmarks to the user_data to be used in pagination
    context.user_data["bookmarks"] = bookmarks

    # Now use 'query.message' to send a reply
    await send_paginated_bookmarks(
        query.message, context, bookmarks, page=0, page_size=10
    )


async def error(update: Update, context: CallbackContext) -> None:
    """
    The error function is called when a telegram update causes an error.
        Args:
            update (Update): The telegram Update object that caused the error.
            context (ext.CallbackContext): The CallbackContext object for this update.

    :param update: Update: Get the update object
    :param context: ext.CallbackContext: Pass the context in which a handler is being run
    :return: None, which is the default return value for functions in python
    :doc-author: Trelent
    """
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def create_pagination_buttons(current_page, total_pages):
    button_list = []
    if total_pages == 0:
        return InlineKeyboardMarkup([])
    # 'Previous' button if not on the first page
    if current_page > 0:
        button_list.append(
            InlineKeyboardButton(
                "⬅️ Previous", callback_data=f"prev_{current_page - 1}"
            )
        )
    # Current page button (disabled)
    button_list.append(
        InlineKeyboardButton(
            f"Page {current_page + 1} of {total_pages}", callback_data="noop"
        )
    )
    # 'Next' button if not on the last page
    if current_page < total_pages - 1:
        button_list.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"next_{current_page + 1}")
        )
    return InlineKeyboardMarkup([button_list])


async def send_paginated_bookmarks(
    message: Message, context: CallbackContext, bookmarks, page=0, page_size=10
):
    # Avoid division by zero if there are no bookmarks
    total_pages = max(
        1, len(bookmarks) // page_size + (1 if len(bookmarks) % page_size else 0)
    )
    formatted_message = await format_bookmarks_page(bookmarks, page, page_size)
    reply_markup = create_pagination_buttons(page, total_pages)
    await message.reply_text(
        formatted_message, reply_markup=reply_markup, parse_mode="HTML",disable_web_page_preview=True
    )


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    # Check if the callback data is for the start menu
    if data == "get_update":
        await check_updates_command(update, context)
    elif data == "get_all_list":
        # Perform the scraping only if the bookmarks are not already stored.
        if "bookmarks" not in context.user_data:
            driver = setup_driver()
            login(driver, username, password)
            context.user_data["bookmarks"] = scrape_bookmarks(driver)
            driver.quit()

        await send_paginated_bookmarks(
            query.message, context, context.user_data["bookmarks"], page=0, page_size=10
        )

    # If the user is navigating the pages, use the stored data.
    elif data.startswith("prev_") or data.startswith("next_"):
        # Extract the action and page number from the callback data
        action, page_str = data.split("_")
        page = int(page_str)
        bookmarks = context.user_data.get("bookmarks", [])

        # Pagination logic
        if action in ["prev", "next"]:
            # Edit the message to the new page of bookmarks
            message = await format_bookmarks_page(bookmarks, page, page_size=10)
            reply_markup = create_pagination_buttons(
                page,
                total_pages=len(bookmarks) // 10 + (1 if len(bookmarks) % 10 else 0),
            )
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="HTML",
                disable_web_page_preview=True,  # Add this to disable web page previews
            )


async def format_bookmarks_page(bookmarks, page, page_size):
    # Calculate the starting and ending indices of the bookmarks for this page
    page_start = page * page_size
    page_end = page_start + page_size
    # Initialize the message with a header
    message = "<b>Your Bookmarked Mangas:</b>\n\n"
    # Add each bookmark to the message with HTML formatting for hyperlinks
    for bookmark in bookmarks[page_start:page_end]:
        message += f"<a href='{bookmark['link']}'>{bookmark['title']}</a> - Last updated: {bookmark['last_update']}\n"
    return message


def main() -> None:
    bot_token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check_updates", check_updates_command))
    application.add_handler(CommandHandler("list_bookmarks", list_bookmarks_command))

    # Callback Query Handler for buttons
    application.add_handler(CallbackQueryHandler(button))

    # Other handlers like MessageHandler, Error Handler, etc.
    application.add_error_handler(error)

    # Start the bot
    application.run_polling()

    # Schedule thread for scheduled tasks
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()


if __name__ == "__main__":
    main()
