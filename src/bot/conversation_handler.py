from telegram.ext import ConversationHandler, CallbackContext
from telegram import Update
from src.utils.log import logging
from src.db.db import get_db
from src.db.repository import update_user_website

# Define states
USERNAME, PASSWORD = range(2)


async def start_set_credentials(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "For getting information about your bookmarks from manga-scans, please write your credentials."
        "They will be encrypted and stored for your all time available use. They will not be given any third person's or used in any ways."
    )
    await query.message.reply_text("Enter your username for manga-scans:")
    return USERNAME


async def username(update, context):
    text = update.message.text
    context.user_data["username"] = text
    await update.message.reply_text("Now, enter your password:")
    return PASSWORD


async def password(update, context):
    username = context.user_data.get("username")
    password = update.message.text
    chat_id = update.message.chat_id

    if username is not None:
        # Save the credentials, encrypt them, etc.
        try:
            with get_db() as db:
                update_user_website(db, chat_id, 1, username, password)
            context.user_data.clear()
            await update.message.reply_text(
                "All done! Now you can get information about your bookmarks."
            )
        except Exception as e:
            logging.error(f"Error saving credentials: {e}")
            await update.message.reply_text(
                "There was an error saving your credentials. Please try again."
            )
    else:
        await update.message.reply_text("No username found. Please start over.")

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Operation cancelled."
    )

    # Clear any stored data you may have.
    context.user_data.clear()

    return ConversationHandler.END
