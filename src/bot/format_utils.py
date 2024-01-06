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
        message += f"<a href='{bookmark['link']}'>{bookmark['title']}</a> - Last updated: {bookmark['last_update']}\n"
    return message


def format_update_message(update):
    """
    Formats the details of a manga update into a user-friendly message.

    Args:
    update (dict): A dictionary containing details about the manga update.

    Returns:
    str: A formatted message string.
    """
    # Constructing the message with HTML formatting for Telegram
    message = (
        f"<b>{update['title']}</b>\n"
        f"Chapter: {update['chapter_title']}\n"
        f"Updated: {update['last_update']}\n"
        f"<a href='{update['link']}'>Read Now</a>"
    )
    return message


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
