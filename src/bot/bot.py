import os
from telegram import Update
from src.utils.log import logger
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from src.bot.buttons import button
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
