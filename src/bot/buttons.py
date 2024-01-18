from src.bot.format_utils import format_bookmarks_page, create_pagination_buttons
from telegram.ext import CallbackContext
from telegram import Update
from src.bot.handler import *

# Define the button callback data


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()  # This is necessary to acknowledge the button press
    chat_id = query.message.chat_id
    data = query.data

    if data == BUTTON_START_BOOKMARKS:
        handle_bookmarks_command(update, context)
    elif data == BUTTON_START_DISABLE_USER:
        set_user_inactive_command(update, context)
    elif data == BUTTON_START_ENABLE_USER:
        set_user_active_command(update, context)
    elif data == BUTTON_START_NOTIFICATION_TIME:
        # Handle showing recent updates
        pass
    elif data == BUTTON_START_UPDATE_DATA_BASE:
        update_now_command(update, context, chat_id)
    elif data == BUTTON_MANGA_WEBSITE_CHOICE:
        handle_choose_website_command(update, context)
    elif data == BUTTON_MANGA_RECENT_UPDATE:
        check_updates_command(update, context)
    elif data == BUTTON_MANGA_WEBSITE_MANGA_SCANS:
        set_user_manga_scans_credentials_command(update, context)
        update_now_command(update, context, chat_id)
    elif data == BUTTON_MANGA_ALL_BOOKMARKS:
        list_and_send_bookmarks_command(update, context)
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
