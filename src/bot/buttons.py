from src.bot.format_utils import format_bookmarks_page, create_pagination_buttons
from telegram.ext import CallbackContext
from telegram import Update
from src.bot.handler import *
from src.bot.conversation_handler import start_set_credentials

# Define the button callback data


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()  # This is necessary to acknowledge the button press
    chat_id = query.message.chat_id
    data = query.data

    if data == BUTTON_START_BOOKMARKS:
        await handle_bookmarks_command(update, context)
    elif data == BUTTON_START_DISABLE_USER:
        await set_user_inactive_command(update, context)
    elif data == BUTTON_START_ENABLE_USER:
        await set_user_active_command(update, context)
    elif data == BUTTON_START_NOTIFICATION_TIME:
        # Handle showing recent updates
        pass
    elif data == BUTTON_START_UPDATE_DATA_BASE:
        await update_now_command(update, context, chat_id)
    elif data == BUTTON_MANGA_WEBSITE_CHOICE:
        await handle_choose_website_command(update, context)
    elif data == BUTTON_MANGA_RECENT_UPDATE:
        await check_updates_command(update, context)
    elif data == BUTTON_MANGA_WEBSITE_MANGA_SCANS:
        await start_set_credentials(update, context)
        await update_now_command(update, context, chat_id)
    elif data == BUTTON_MANGA_ALL_BOOKMARKS:
        await list_and_send_bookmarks_command(update, context)
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
