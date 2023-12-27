import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.bot import (
    start,
    check_updates_command,
    list_bookmarks_command,
    create_pagination_buttons,
    send_paginated_bookmarks,
    button,
    run_bot,
)
from src.utils import format_update_message
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv


load_dotenv()


@pytest.mark.asyncio
async def test_start():
    # Mock update and context objects
    mock_update = MagicMock()
    mock_update.message = MagicMock()
    mock_update.message.reply_text = AsyncMock()

    mock_context = MagicMock()

    # Call the start function
    await start(mock_update, mock_context)

    # Verify that reply_text was called with the expected message and keyboard
    greeting_message = "Welcome to MangaMate! 📚✨\nYour personal assistant for staying updated with your favorite Manga. What would you like to do today?"
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Get Latest Update", callback_data="get_update")],
            [InlineKeyboardButton("Get My Manga List", callback_data="get_all_list")],
        ]
    )

    mock_update.message.reply_text.assert_awaited_once_with(
        greeting_message, reply_markup=keyboard
    )


@pytest.mark.asyncio
@patch("src.bot.check_for_updates")
async def test_check_updates_command(mock_check_for_updates):
    # Setup mock for check_for_updates
    mock_check_for_updates.return_value = [
        {
            "title": "Manga 1",
            "image": "http://example.com/img1",
            "chapter_title": "Chapter 1",
            "last_update": "1 hour ago",
            "link": "http://example.com/manga1",
        },
        # ... other mock manga updates
    ]

    # Mock update and query objects
    mock_query = MagicMock()
    mock_query.message = MagicMock()
    mock_query.message.reply_photo = AsyncMock()

    mock_update = MagicMock()
    mock_update.callback_query = mock_query

    # Call the check_updates_command function
    await check_updates_command(mock_update, MagicMock())

    # Assert that reply_photo is called for each manga update
    assert mock_query.message.reply_photo.call_count == len(
        mock_check_for_updates.return_value
    )
    for manga_update in mock_check_for_updates.return_value:
        message = format_update_message(manga_update)
        mock_query.message.reply_photo.assert_any_await(
            photo=manga_update["image"], caption=message, parse_mode="HTML"
        )


@pytest.mark.asyncio
@patch("src.bot.setup_driver")
@patch("src.bot.login")
@patch("src.bot.scrape_bookmarks")
@patch("src.bot.send_paginated_bookmarks")
async def test_list_bookmarks_command(
    mock_send_paginated_bookmarks, mock_scrape_bookmarks, mock_login, mock_setup_driver
):
    # Setup mocks
    username = os.getenv("WORK_USER_LOGIN")
    password = os.getenv("WORK_USER_PASSWORD")
    mock_driver = MagicMock()
    mock_setup_driver.return_value = mock_driver
    mock_scrape_bookmarks.return_value = [
        {
            "title": "Bookmark 1",
            "link": "http://example.com/bookmark1",
            "last_update": "1 hour ago",
        },
    ]

    # Mock update and context objects
    mock_query = MagicMock()
    mock_query.message = MagicMock()
    mock_query.message.reply_text = AsyncMock()

    mock_update = MagicMock()
    mock_update.callback_query = mock_query

    mock_context = MagicMock()
    mock_context.user_data = {}

    # Call the list_bookmarks_command function
    await list_bookmarks_command(mock_update, mock_context)

    # Verify web scraping functions were called
    mock_setup_driver.assert_called_once()
    mock_login.assert_called_once_with(mock_driver, username, password)
    mock_scrape_bookmarks.assert_called_once_with(mock_driver)
    mock_driver.quit.assert_called_once()

    # Verify that send_paginated_bookmarks was called
    mock_send_paginated_bookmarks.assert_awaited_once_with(
        mock_query.message,
        mock_context,
        mock_scrape_bookmarks.return_value,
        page=0,
        page_size=10,
    )


def test_create_pagination_buttons():
    # Test for the first page
    buttons_first_page = create_pagination_buttons(0, 3)
    assert len(buttons_first_page.inline_keyboard[0]) == 2  # 'Page 1 of 3' and 'Next'
    assert buttons_first_page.inline_keyboard[0][1].text == "Next ➡️"
    assert buttons_first_page.inline_keyboard[0][1].callback_data == "next_1"

    # Test for a middle page
    buttons_middle_page = create_pagination_buttons(1, 3)
    assert (
        len(buttons_middle_page.inline_keyboard[0]) == 3
    )  # 'Previous', 'Page 2 of 3', and 'Next'
    assert buttons_middle_page.inline_keyboard[0][0].text == "⬅️ Previous"
    assert buttons_middle_page.inline_keyboard[0][0].callback_data == "prev_0"
    assert buttons_middle_page.inline_keyboard[0][2].text == "Next ➡️"
    assert buttons_middle_page.inline_keyboard[0][2].callback_data == "next_2"

    # Test for the last page
    buttons_last_page = create_pagination_buttons(2, 3)
    assert (
        len(buttons_last_page.inline_keyboard[0]) == 2
    )  # 'Previous' and 'Page 3 of 3'
    assert buttons_last_page.inline_keyboard[0][0].text == "⬅️ Previous"
    assert buttons_last_page.inline_keyboard[0][0].callback_data == "prev_1"

    # Test when there are no pages
    buttons_no_pages = create_pagination_buttons(0, 0)
    assert len(buttons_no_pages.inline_keyboard) == 0  # No buttons


@pytest.mark.asyncio
@patch("src.bot.format_bookmarks_page")
@patch("src.bot.create_pagination_buttons")
async def test_send_paginated_bookmarks(
    mock_create_pagination_buttons, mock_format_bookmarks_page
):
    # Mock data
    bookmarks = [
        {"title": "Bookmark 1", "link": "http://example.com/bookmark1"}
    ] * 20  # Example bookmarks
    page = 0
    page_size = 10
    formatted_message = "Formatted bookmarks page"
    reply_markup = MagicMock()

    # Setup mocks
    mock_format_bookmarks_page.return_value = formatted_message
    mock_create_pagination_buttons.return_value = reply_markup

    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()

    mock_context = MagicMock()

    # Call the function
    await send_paginated_bookmarks(
        mock_message, mock_context, bookmarks, page, page_size
    )

    # Verify that format_bookmarks_page was called correctly
    mock_format_bookmarks_page.assert_called_once_with(bookmarks, page, page_size)

    # Verify that create_pagination_buttons was called correctly
    total_pages = 2  # Based on 20 bookmarks and 10 per page
    mock_create_pagination_buttons.assert_called_once_with(page, total_pages)

    # Verify that the message was sent with correct parameters
    mock_message.reply_text.assert_awaited_once_with(
        formatted_message,
        reply_markup=reply_markup,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@pytest.mark.asyncio
@patch("src.bot.check_updates_command")
@patch("src.bot.send_paginated_bookmarks")
@patch("src.bot.format_bookmarks_page")
@patch("src.bot.create_pagination_buttons")
@patch("src.bot.setup_driver")
@patch("src.bot.login")
@patch("src.bot.scrape_bookmarks")
async def test_button(
    mock_scrape_bookmarks,
    mock_login,
    mock_setup_driver,
    mock_create_pagination_buttons,
    mock_format_bookmarks_page,
    mock_send_paginated_bookmarks,
    mock_check_updates_command,
):
    username = os.getenv("WORK_USER_LOGIN")
    password = os.getenv("WORK_USER_PASSWORD")
    # Prepare mocks for update and context
    mock_query = MagicMock()
    mock_query.answer = AsyncMock()
    mock_query.edit_message_text = AsyncMock()  # Use AsyncMock here
    mock_update = MagicMock()
    mock_update.callback_query = mock_query
    mock_context = MagicMock()
    mock_context.user_data = {}

    # Setup for web scraping
    mock_driver = MagicMock()
    mock_setup_driver.return_value = mock_driver
    mock_scrape_bookmarks.return_value = [
        {"title": "Bookmark 1", "link": "http://example.com/bookmark1"},
        # ... other mock bookmarks
    ]

    # Test "get_update" scenario
    mock_query.data = "get_update"
    await button(mock_update, mock_context)
    mock_check_updates_command.assert_awaited_once_with(mock_update, mock_context)

    # Test "get_all_list" scenario
    mock_query.data = "get_all_list"
    await button(mock_update, mock_context)
    mock_setup_driver.assert_called_once()
    mock_login.assert_called_once_with(
        mock_driver, username, password
    )  # Replace with actual credentials
    mock_scrape_bookmarks.assert_called_once_with(mock_driver)
    mock_driver.quit.assert_called_once()
    mock_send_paginated_bookmarks.assert_awaited_once_with(
        mock_query.message,
        mock_context,
        mock_scrape_bookmarks.return_value,
        page=0,
        page_size=10,
    )

    # Reset mocks for pagination test
    mock_check_updates_command.reset_mock()
    mock_send_paginated_bookmarks.reset_mock()

    # Test "next_" scenario
    mock_query.data = "next_1"
    mock_context.user_data["bookmarks"] = mock_scrape_bookmarks.return_value
    await button(mock_update, mock_context)
    mock_format_bookmarks_page.assert_awaited_once_with(
        mock_context.user_data["bookmarks"], 1, page_size=10
    )
    mock_create_pagination_buttons.assert_called_once()
    mock_query.edit_message_text.assert_awaited_once()

    # Reset mocks for previous page test
    mock_format_bookmarks_page.reset_mock()
    mock_create_pagination_buttons.reset_mock()
    mock_query.edit_message_text.reset_mock()

    # Test "prev_" scenario
    mock_query.data = "prev_0"
    await button(mock_update, mock_context)
    mock_format_bookmarks_page.assert_awaited_once_with(
        mock_context.user_data["bookmarks"], 0, page_size=10
    )
    mock_create_pagination_buttons.assert_called_once()
    mock_query.edit_message_text.assert_awaited_once()


@patch("src.bot.Application")
@patch("src.bot.CommandHandler")
@patch("src.bot.CallbackQueryHandler")
@patch("src.bot.error")
@patch("src.bot.run_schedule")
@patch("os.getenv", return_value="test_bot_token")
def test_run_bot(
    mock_getenv,
    mock_run_schedule,
    mock_error,
    mock_CallbackQueryHandler,
    mock_CommandHandler,
    mock_Application,
):
    # Mocking Application and its methods
    mock_application = MagicMock()
    mock_Application.builder.return_value.token.return_value.build.return_value = (
        mock_application
    )

    # Call the function
    run_bot()

    # Check if environment variable BOT_TOKEN is retrieved
    mock_getenv.assert_called_once_with("BOT_TOKEN")

    # Verify that command handlers are added
    assert mock_CommandHandler.call_count == 3  # start, check_updates, list_bookmarks

    # Verify that callback query handler is added
    mock_CallbackQueryHandler.assert_called_once()

    # Verify that the error handler is added
    mock_application.add_error_handler.assert_called_once_with(mock_error)

    # Verify that the bot is started
    mock_application.run_polling.assert_called_once()

    # Verify that the schedule thread is started
    mock_run_schedule.assert_called_once()
