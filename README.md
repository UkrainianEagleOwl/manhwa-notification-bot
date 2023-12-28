# Manga Notification Bot

## About
The Manhwa Update Notifier Bot is a Telegram bot designed to notify users about new chapters of their bookmarked Manhwa titles. It scrapes updates from a user-specified website and sends a message to the user with the latest chapter information.

## Features
- **Login to website**:  Login to user's account on a Manhwa tracking website.
- **Live Manga Updates**: Scrape the latest updates of bookmarked Manhwa and send them to user.
- **Send schedule notification**: Send a notification through Telegram with the title, image, chapter, and link every day at 09:00 about all updates for the last 24 hours.

## Installation

To set up the Manga Notification Bot, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/UkrainianEagleOwl/manhwa-notification-bot.git
   cd manhwa-notification-bot
   ```

2. Install dependencies using [Poetry](https://python-poetry.org/):
   ```sh
   poetry install
   ```

3. Copy the `.env.example` file to `.env` and fill in the necessary environment variables.

4. Run the bot:
   ```sh
   poetry run python main.py
   ```

## Usage

Interact with the bot on Telegram using the following commands:

- `/start`: Register to begin receiving updates.
- `/check_updates`: Get updates for last 24 hours.
- `/list_bookmarks`: Display your bookmarks.

## Configuration

This project is configured using environment variables. Ensure the following are set:

- `TELEGRAM_TOKEN`: Your unique Telegram bot token.

## Contributing

Contributions to the Manga Notification Bot are welcome! To contribute:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Create a new Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

If you have any questions or suggestions, please reach out to Dmytro Filin at dmitriy.fillin@gmail.com.

## Acknowledgments

- Thanks to the creators and contributors of the `python-telegram-bot` and `selenium` libraries that made this project possible.
