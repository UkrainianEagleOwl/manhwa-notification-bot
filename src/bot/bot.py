import os
from telegram import Update
from src.utils.log import logger
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from src.bot.format_utils import format_bookmarks_page, create_pagination_buttons
from src.bot.handler import (
    list_and_send_bookmarks_command,
    check_updates_command,
    start,
)


bot_context = None


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
        await list_and_send_bookmarks_command(
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
    logger.info("Bot is starting up...")

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check_updates", check_updates_command))
    application.add_handler(
        CommandHandler("list_bookmarks", list_and_send_bookmarks_command)
    )

    # Callback Query Handler for buttons
    application.add_handler(CallbackQueryHandler(button))

    # Other handlers like MessageHandler, Error Handler, etc.
    application.add_error_handler(error)

    # Start the bot
    application.run_polling()
