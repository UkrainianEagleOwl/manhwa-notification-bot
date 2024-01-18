from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def format_bookmarks_page(bookmarks, page, page_size):
    """
    The format_bookmarks_page function takes a list of bookmarks, the page number to display, and the page size.
    It returns a formatted message containing all of the bookmarks on that page.

    :param bookmarks: Pass the list of bookmarks to the function
    :param page: Determine which page of bookmarks to display
    :param page_size: Determine how many bookmarks to show per page
    :return: A string that contains the bookmarks for a page
    """
    # Calculate the starting and ending indices of the bookmarks for this page
    page_start = page * page_size
    page_end = page_start + page_size
    # Initialize the message with a header
    message = "<b>Your Bookmarked Mangas:</b>\n\n"
    # Add each bookmark to the message with HTML formatting for hyperlinks
    for bookmark in bookmarks[page_start:page_end]:
        message += f"<a href='{bookmark['link_on_title']}'>{bookmark['title']}</a> - Last updated: {bookmark['time_of_last_update']}\n"
    return message


def format_update_message(bookmark):
    """
    Formats the details of a manga update into a user-friendly message.

    Args:
    update (dict): A dictionary containing details about the manga update.

    Returns:
    str: A formatted message string.
    """
    # Constructing the message with HTML formatting for Telegram
    message = (
        f"<a href='{bookmark['link_on_title']}'>{bookmark['title']}</a>\n"
        f"Chapter: {bookmark['last_chapter_title']}\n"
        f"Updated: {bookmark['time_of_last_update']}\n"
        f"<a href='{bookmark['link_on_last_chapter']}'>Read Now</a>"
    )
    return message
