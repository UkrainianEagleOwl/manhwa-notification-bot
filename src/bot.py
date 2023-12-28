import logging
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from dotenv import load_dotenv

from src.scrapping import setup_driver, login, scrape_bookmarks
from src.utils import format_bookmarks_page, format_update_message, check_for_updates
from src.schedule_utils import run_schedule

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
app = Flask(__name__)

username = os.getenv("WORK_USER_LOGIN")
password = os.getenv("WORK_USER_PASSWORD")

# Global variable to store the bot's context
bot_context = None


@app.route("/health")
def health_check():
    return "OK", 200


def runFlask():
    app.run(host="0.0.0.0", port=8000, debug=False)


# Define the asynchronous start command handler
async def start(update, context):
    """
    The start function is the first function that gets called when a user interacts with the bot.
    It sends a greeting message and an inline keyboard to choose from different actions.

    :param update: Get the message sent by the user
    :param context: Pass the context of the message to this function
    :return: A conversationhandler object
    :doc-author: Trelent
    """
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
    """
    The check_updates_command function is a callback function that will be called when the user clicks on the &quot;Check for Updates&quot; button.
    It will check for updates and send them to the user.

    :param update: Update: Get the update object from the callback query
    :param context: CallbackContext: Pass the context in which this function is called
    :return: None, so the bot doesn't know what to do with it
    :doc-author: Trelent
    """
    query = update.callback_query
    recent_updates = check_for_updates(username, password)

    # Now use 'query.message' to send a reply
    for manga_update in recent_updates:
        message = format_update_message(manga_update)
        await query.message.reply_photo(
            photo=manga_update["image"], caption=message, parse_mode="HTML"
        )


async def list_bookmarks_command(update: Update, context: CallbackContext) -> None:
    """
    The list_bookmarks_command function is a callback function that will be called when the user clicks on the &quot;List Bookmarks&quot; button.
    It will scrape all of the bookmarks from your account and send them to you in paginated form.

    :param update: Update: Get the update object from the callback context
    :param context: CallbackContext: Pass the context of the function
    :return: None, so you need to remove the return statement
    """
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

    :param update: Update: Get the update object that caused the error
    :param context: CallbackContext: Pass the context in which a handler is being run
    :return: None
    """
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def create_pagination_buttons(current_page, total_pages):
    """
    The create_pagination_buttons function creates a list of InlineKeyboardButtons
    for pagination. It takes two arguments: current_page and total_pages.
    current_page is the page number that the user is currently viewing, while total_pages
    is the maximum number of pages available for pagination (i.e., if there are 100 items,
    and each page can display 10 items at most, then there will be 10 pages). The function
    returns an InlineKeyboardMarkup object containing a list of buttons to be displayed in
    the Telegram chat window.

    :param current_page: Determine which page we are on
    :param total_pages: Know how many pages there are in total
    :return: An inlinekeyboardmarkup object
    """
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
    """
    The send_paginated_bookmarks function sends a paginated list of bookmarks to the user.

    :param message: Message: Send the paginated bookmarks to the user
    :param context: CallbackContext: Pass the context of the callback query to this function
    :param bookmarks: Get the bookmarks to be displayed
    :param page: Determine which page of bookmarks to display
    :param page_size: Determine how many bookmarks to display per page
    :return: The formatted_message
    """
    # Avoid division by zero if there are no bookmarks
    total_pages = max(
        1, len(bookmarks) // page_size + (1 if len(bookmarks) % page_size else 0)
    )
    formatted_message = await format_bookmarks_page(bookmarks, page, page_size)
    reply_markup = create_pagination_buttons(page, total_pages)
    await message.reply_text(
        formatted_message,
        reply_markup=reply_markup,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def button(update: Update, context: CallbackContext) -> None:
    """
    The button function is used to handle the callback queries from the inline keyboard.

    :param update: Update: Get the update object, which contains information about the incoming update
    :param context: CallbackContext: Pass the context object to the function
    :return: None
    """
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


def run_bot() -> None:
    """
    The run_bot function is the main function of this bot. It initializes the bot and starts it.

    :return: None so the return type should be none
    """
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
