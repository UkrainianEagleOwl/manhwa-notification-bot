# Manhwa Update Notifier Bot

## About
The Manhwa Update Notifier Bot is a Telegram bot designed to notify users about new chapters of their bookmarked Manhwa titles. It scrapes updates from a user-specified website and sends a message to the user with the latest chapter information.

## Features
- Login to user's account on a Manhwa tracking website.
- Scrape the latest updates of bookmarked Manhwa.
- Send a notification through Telegram with the title, image, chapter, and link.

## Setup
1. Install the required Python packages:
   pip install selenium python-dotenv
2. Configure your `.env` file with the following variables:
   - `WORK_USER_LOGIN` - Your login for the Manhwa website.
   - `WORK_USER_PASSWORD` - Your password for the Manhwa website.
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token.
   - `TELEGRAM_USER_ID` - Your Telegram user ID to receive notifications.

3. Run the bot:
   python bot.py

## Usage
The bot will automatically check for updates at regular intervals and send notifications if new chapters are available.

## Contributing
Contributions to the Manhwa Update Notifier Bot are welcome! Please feel free to fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
