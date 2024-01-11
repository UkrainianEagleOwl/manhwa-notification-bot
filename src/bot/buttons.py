from src.bot.format_utils import format_bookmarks_page, create_pagination_buttons
from telegram.ext import CallbackContext
from telegram import Update
from src.bot.handler import *


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()  # This is necessary to acknowledge the button press
    chat_id = query.message.chat_id
    data = query.data

    if data == BUTTON_WEBSITE_CHOICE:
        # Handle website choice
        pass
    elif data == BUTTON_DISABLE_USER:
        # Handle user disabling
        pass
    elif data == BUTTON_SHOW_BOOKMARKS:
        # Handle showing all bookmarks
        pass
    elif data == BUTTON_RECENT_UPDATES:
        # Handle showing recent updates
        pass
    elif data == BUTTON_NOTIFICATION_SETTINGS:
        # Handle showing notification settings
        pass
    elif data == BUTTON_UPDATE_DATA_BASE:
        # Handle update data from website
        pass
    elif data == BUTTON_CHOOSE_WEBSITE:
        # Handle showing website choose
        pass
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
