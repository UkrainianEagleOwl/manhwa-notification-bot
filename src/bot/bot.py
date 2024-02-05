import os
import asyncio
from telegram import Update, BotCommand
from src.utils.log import logger
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from src.bot.buttons import button
from src.bot.handler import (
    handle_start_command,
    handle_bookmarks_command,
    handle_choose_website_command,
    update_now_command,
    list_and_send_bookmarks_command,
    set_user_active_command,
    set_user_inactive_command,
    check_updates_command,
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


def run_bot() -> None:
    """
    The run_bot function is the main function of this bot. It initializes the bot and starts it.

    :return: None so the return type should be none
    """
    bot_token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(bot_token).build()
    logger.info("Bot is starting up...")

    # Command Handlers
    application.add_handler(CommandHandler("start", handle_start_command))
    application.add_handler(CommandHandler("bookmarks", handle_bookmarks_command))
    application.add_handler(
        CommandHandler("choose_website", handle_choose_website_command)
    )
    application.add_handler(CommandHandler("update_data", update_now_command))
    application.add_handler(
        CommandHandler("show_bookmarks", list_and_send_bookmarks_command)
    )
    application.add_handler(
        CommandHandler("enable_notification", set_user_active_command)
    )
    application.add_handler(
        CommandHandler("disable_notification", set_user_inactive_command)
    )
    application.add_handler(CommandHandler("get_updates_titles", check_updates_command))
    # Callback Query Handler for buttons
    application.add_handler(CallbackQueryHandler(button))

    # Other handlers like MessageHandler, Error Handler, etc.
    application.add_error_handler(error)

    # Define your bot's commands
    commands = [
        BotCommand(command="start", description="Show the start menu"),
        BotCommand(command="bookmarks", description="Show the bookmarks menu"),
        BotCommand(
            command="choose_website", description="Choose the website to login in"
        ),
        BotCommand(command="update_data", description="Update data from website"),
        BotCommand(command="show_bookmarks", description="Get list of your bookmarks"),
        BotCommand(
            command="enable_notification", description="Enable your notifications"
        ),
        BotCommand(
            command="disable_notification", description="Disable your notifications"
        ),
        BotCommand(
            command="get_updates_titles",
            description="Get new updates of your titles for last 24 hours",
        ),
    ]

    # Start the bot
    # Make sure to create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Use `run_until_complete` and `application.run_polling` with the loop
        loop.run_until_complete(application.run_polling())
    finally:
        # Close the loop at the end to clean up properly
        loop.close()
