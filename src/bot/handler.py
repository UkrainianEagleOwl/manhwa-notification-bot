from src.utils.log import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import CallbackContext, CommandHandler
from src.bot.format_utils import (
    format_update_message,
    format_bookmarks_page,
    create_pagination_buttons,
)
from src.db.db import get_db
from src.bot.telegram_db_connector import manual_update
from src.db.repository import (
    get_last_update_info_for_user,
    get_user_by_chat_id,
    get_all_user_bookmarks,
    create_user,
    set_user_status,
    get_recent_bookmarks,
    update_user_website,
)

BUTTON_START_BOOKMARKS = "bookmarks"
BUTTON_START_DISABLE_USER = "disable_notifications"
BUTTON_START_ENABLE_USER = "enable_notifications"
BUTTON_START_NOTIFICATION_TIME = "set_notification_time"
BUTTON_START_UPDATE_DATA_BASE = "update_data_base"

BUTTON_MANGA_WEBSITE_CHOICE = "choose_website"
BUTTON_MANGA_RECENT_UPDATE = "recent_update"
BUTTON_MANGA_ALL_BOOKMARKS = "all_bookmarks"

BUTTON_MANGA_WEBSITE_MANGA_SCANS = "manga-scans.com"


# Define the asynchronous start command handler
async def handle_start_command(update, context):
    chat_id = update.message.chat_id
    with get_db() as db:
        try:
            user = get_user_by_chat_id(db, chat_id)
            last_time_update_data = get_last_update_info_for_user(db, chat_id)
            if user and user.is_active and (len(user.websites) > 0):
                greeting = "Welcome back! Ready to check out the latest manga?\n"
                greeting += last_time_update_data;
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Bookmarks", callback_data=BUTTON_START_BOOKMARKS
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Disable notifications",
                            callback_data=BUTTON_START_DISABLE_USER,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Set notification time",
                            callback_data=BUTTON_START_NOTIFICATION_TIME,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Update Data", callback_data=BUTTON_START_UPDATE_DATA_BASE
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
                    greeting = "Welcome back! Ready to check out the latest manga?"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Bookmarks", callback_data=BUTTON_START_BOOKMARKS
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Enable notifications",
                            callback_data=BUTTON_START_ENABLE_USER,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Set notification time",
                            callback_data=BUTTON_START_NOTIFICATION_TIME,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Update Data", callback_data=BUTTON_START_UPDATE_DATA_BASE
                        )
                    ],
                ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id, text=greeting, reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"An error occurred while handling /start command: {e}")


# Define the asynchronous handle_bookmarks_command handler
async def handle_bookmarks_command(update, context):
    try:
        if update.message:
            chat_id = update.message.chat_id
        else:
            query = update.callback_query
            chat_id = query.message.chat_id
        message_text = "What you want to do with your bookmarks?"
        keyboard = [
            [
                InlineKeyboardButton(
                    "Choose website",
                    callback_data=BUTTON_MANGA_WEBSITE_CHOICE,
                )
            ],
            [
                InlineKeyboardButton(
                    "Get recent updates",
                    callback_data=BUTTON_MANGA_RECENT_UPDATE,
                )
            ],
            [
                InlineKeyboardButton(
                    "Get all bookmarks", callback_data=BUTTON_MANGA_ALL_BOOKMARKS
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id, text=message_text, reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"An error occurred while handling /bookmarks command: {e}")


async def handle_choose_website_command(update, context):
    try:
        if update.message:
            chat_id = update.message.chat_id
        else:
            query = update.callback_query
            chat_id = query.message.chat_id
        message_text = "Please choose your website from the variants"
        keyboard = [
            [
                InlineKeyboardButton(
                    "Manga-scans",
                    callback_data=BUTTON_MANGA_WEBSITE_MANGA_SCANS,
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id, text=message_text, reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(
            f"An error occurred while handling /handle_choose_website_command command: {e}"
        )


async def set_user_manga_scans_credentials_command(update, context):
    try:
        query = update.callback_query
        chat_id = query.message.chat_id
        await query.answer()
        await query.message.reply_text(
            """For getting information about you bookmarks from manga-scans, please write your credentials. They will be encrypted and stored for your all time available use. They will not be given any third person's or used in any ways."""
        )
        await query.message.reply_text("Enter your username for manga-scans:")
        text = update.message.text
        context.user_data["username"] = text
        await update.message.reply_text("Now, enter your password:")
        if "username" in context.user_data:
            # User is entering password
            username = context.user_data["username"]
            password = text
            with get_db() as db:
                update_user_website(db, chat_id, 1, username, password)
            context.user_data.clear()
        await update.message.reply_text(
            "All done! Now you can get your information about your bookmarks."
        )
    except Exception as e:
        context.user_data.clear()
        logging.error(
            f"An error occurred while handling set_user_manga_scans_credentials_command command: {e}"
        )


async def update_now_command(update, context):
    try:
        if update.message:
            chat_id = update.message.chat_id
        else:
            query = update.callback_query
            chat_id = query.message.chat_id
        manual_update(chat_id)
    except Exception as e:
        logging.error(f"An error occurred while handling update now command: {e}")
    await update.message.reply_text("All your bookmarks have been updated.")


async def list_and_send_bookmarks_command(
    update: Update, context: CallbackContext, page=0, page_size=10
) -> None:
    """
    This function combines the functionalities of listing bookmarks and sending them in a paginated form.
    It first scrapes the bookmarks, then sends them in a paginated manner.

    :param update: Update: The update object from the callback context.
    :param context: CallbackContext: The context of the function.
    :param page: The current page number for pagination.
    :param page_size: The number of bookmarks to display per page.
    """

    async def send_paginated_message(message: Message, bookmarks, page, page_size):
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

    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = query.message.chat_id
    query = update.callback_query
    with get_db() as db:
        try:
            bookmarks_list = get_all_user_bookmarks(db, chat_id)
        except Exception as e:
            logging.error(
                f"An error occurred while handling get all bookmarks command: {e}"
            )
    logging.info("Got all bookmarks.")

    context.user_data["bookmarks"] = bookmarks_list

    await send_paginated_message(query.message, bookmarks_list, page, page_size)


async def set_user_active_command(update: Update, context: CallbackContext):
    if update.message:
        chat_id = update.message.chat_id
    else:
        query = update.callback_query
        chat_id = query.message.chat_id
    with get_db() as db:
        try:
            set_user_status(db, chat_id, True)
            message_text = "Your notification status setup active"
            await context.bot.send_message(chat_id, text=message_text)
        except Exception as e:
            logging.error(
                f"An error occurred while handling set user active command: {e}"
            )


async def set_user_inactive_command(update: Update, context: CallbackContext):
    if update.message:
        chat_id = update.message.chat_id
    else:
        query = update.callback_query
        chat_id = query.message.chat_id
    with get_db() as db:
        try:
            set_user_status(db, chat_id, False)
            message_text = "Your notification status setup inactive"
            await context.bot.send_message(chat_id, text=message_text)
        except Exception as e:
            logging.error(
                f"An error occurred while handling set user inactive command: {e}"
            )


async def check_updates_command(update: Update, context: CallbackContext) -> None:
    if update.message:
        chat_id = update.message.chat_id
    else:
        query = update.callback_query
        chat_id = query.message.chat_id
    with get_db() as db:
        try:
            recent_updates = get_recent_bookmarks(db, chat_id)
            # Now use 'query.message' to send a reply
            for manga_update in recent_updates:
                message = format_update_message(manga_update)
                await query.message.reply_photo(
                    photo=manga_update["image"], caption=message, parse_mode="HTML"
                )
        except Exception as e:
            logging.error(
                f"An error occurred while handling set user inactive command: {e}"
            )
