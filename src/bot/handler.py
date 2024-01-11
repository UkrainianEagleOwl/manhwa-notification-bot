import os
from src.utils.log import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import CallbackContext, CommandHandler
from src.scraper.main_scraper import setup_driver, scrape_bookmarks
from src.bot.format_utils import (
    format_bookmarks_page,
    format_update_message,
    create_pagination_buttons,
)
from src.db.db import get_db
from src.db.repository import (
    add_or_update_bookmarks,
    get_user_credentials,
    get_active_user_with_websites,
    get_user_by_chat_id,
    create_user,
)

# Define the button callback data
BUTTON_WEBSITE_CHOICE = "choose_website"
BUTTON_DISABLE_USER = "disable_user"
BUTTON_SHOW_BOOKMARKS = "show_bookmarks"
BUTTON_RECENT_UPDATES = "recent_updates"
BUTTON_NOTIFICATION_SETTINGS = "notification_settings"
BUTTON_UPDATE_DATA_BASE = "update_data_base"
BUTTON_CHOOSE_WEBSITE = "choose_website"


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


# Define the asynchronous start command handler
def handle_start_command(update, context):
    chat_id = update.message.chat_id
    with get_db() as db:
        try:
            user = get_user_by_chat_id(db, chat_id)
            if user and user.is_active:
                greeting = "Welcome back! Ready to check out the latest manga?"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Show All Bookmarks", callback_data=BUTTON_SHOW_BOOKMARKS
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Get Recent Updates", callback_data=BUTTON_RECENT_UPDATES
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Notification Settings",
                            callback_data=BUTTON_NOTIFICATION_SETTINGS,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Disable User", callback_data=BUTTON_DISABLE_USER
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Update Data", callback_data=BUTTON_UPDATE_DATA_BASE
                        )
                    ],
                ]
            else:
                if user is None:
                    create_user(
                        db,
                        chat_id=chat_id,
                        notification_time=None,
                        is_active=True,
                    )
                    greeting = "Hello! Welcome to Manga Bot. Let's get you started."
                else:
                    # If the user exists but is not active, reactivate the user
                    user.is_active = True
                    db.commit()
                    greeting = "Welcome back! Your account is now active again."

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Choose Website", callback_data=BUTTON_WEBSITE_CHOICE
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Disable User", callback_data=BUTTON_DISABLE_USER
                        )
                    ],
                ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id, text=greeting, reply_markup=reply_markup)
        except Exception as e:
            logging.error(f"An error occurred while handling /start command: {e}")


async def update_now_command(update, context, chat_id):
    manual_update(chat_id)
    await update.message.reply_text("All your bookmarks have been updated.")


# async def check_updates_command(update: Update, context: CallbackContext) -> None:
#     """
#     The check_updates_command function is a callback function that will be called when the user clicks on the &quot;Check for Updates&quot; button.
#     It will check for updates and send them to the user.

#     :param update: Update: Get the update object from the callback query
#     :param context: CallbackContext: Pass the context in which this function is called
#     :return: None, so the bot doesn't know what to do with it
#     :doc-author: Trelent
#     """
#     query = update.callback_query
#     recent_updates = ms_scraper.check_for_updates(
#         os.getenv("WORK_USER_LOGIN"), os.getenv("WORK_USER_PASSWORD")
#     )

#     # Now use 'query.message' to send a reply
#     for manga_update in recent_updates:
#         message = format_update_message(manga_update)
#         await query.message.reply_photo(
#             photo=manga_update["image"], caption=message, parse_mode="HTML"
#         )


# async def list_and_send_bookmarks_command(
#     update: Update, context: CallbackContext, page=0, page_size=10
# ) -> None:
#     """
#     This function combines the functionalities of listing bookmarks and sending them in a paginated form.
#     It first scrapes the bookmarks, then sends them in a paginated manner.

#     :param update: Update: The update object from the callback context.
#     :param context: CallbackContext: The context of the function.
#     :param page: The current page number for pagination.
#     :param page_size: The number of bookmarks to display per page.
#     """

#     async def send_paginated_message(message: Message, bookmarks, page, page_size):
#         total_pages = max(
#             1, len(bookmarks) // page_size + (1 if len(bookmarks) % page_size else 0)
#         )
#         formatted_message = await format_bookmarks_page(bookmarks, page, page_size)
#         reply_markup = create_pagination_buttons(page, total_pages)
#         await message.reply_text(
#             formatted_message,
#             reply_markup=reply_markup,
#             parse_mode="HTML",
#             disable_web_page_preview=True,
#         )

#     query = update.callback_query
#     driver = setup_driver()
#     ms_scraper.login(
#         driver, os.getenv("WORK_USER_LOGIN"), os.getenv("WORK_USER_PASSWORD")
#     )
#     bookmarks = ms_scraper.scrape_bookmarks(driver)
#     logging.info("Got all bookmarks.")
#     driver.quit()

#     context.user_data["bookmarks"] = bookmarks

#     await send_paginated_message(query.message, bookmarks, page, page_size)
