from src.scrapping import setup_driver, login, scrape_bookmarks


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


def check_for_updates(username,password):
    """
    The check_for_updates function checks for updates to the bookmarks on your account.
    It returns a list of dictionaries, each dictionary containing information about a bookmark that has been updated recently.
    The keys in each dictionary are: 'title', 'url', and 'last_update'.


    :return: A list of dictionaries
    """
    driver = setup_driver()
    login(driver, username, password)
    bookmarks_data = scrape_bookmarks(driver)
    driver.quit()

    recent_updates = []
    for bookmark in bookmarks_data:
        # Check if 'last_update' indicates a recent update (within hours or minutes)
        if "hour" in bookmark["last_update"] or "min" in bookmark["last_update"]:
            recent_updates.append(bookmark)

    return recent_updates
