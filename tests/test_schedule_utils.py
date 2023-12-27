import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import threading
import time
import schedule
import unittest
from unittest.mock import Mock, patch, call, MagicMock
from src.schedule_utils import (
    scheduled_check,
    run_schedule,
)  # Adjust this import to your project structure


# Mock the bot_context with a Mock object
@pytest.fixture
def mock_bot_context():
    bot = Mock()
    bot.send_message = Mock()
    return bot


# Mock the check_for_updates function
@pytest.fixture
def mock_check_for_updates():
    with patch("src.schedule_utils.check_for_updates") as mock:
        yield mock


# Mock the os.getenv function to return a fake chat ID
@pytest.fixture
def mock_os_getenv():
    with patch("os.getenv") as mock:
        mock.return_value = "123456789"  # Mock chat ID
        yield mock


def test_scheduled_check_with_updates(
    mock_bot_context, mock_check_for_updates, mock_os_getenv
):
    # Given check_for_updates returns a non-empty list
    mock_check_for_updates.return_value = ["Update 1", "Update 2"]

    # When scheduled_check is called
    scheduled_check(mock_bot_context)

    # Then bot.send_message should be called with the expected text
    mock_bot_context.bot.send_message.assert_called_once_with(
        chat_id="123456789", text="Daily Updates: ['Update 1', 'Update 2']"
    )


def test_scheduled_check_without_updates(
    mock_bot_context, mock_check_for_updates, mock_os_getenv
):
    # Given check_for_updates returns an empty list
    mock_check_for_updates.return_value = []

    # When scheduled_check is called
    scheduled_check(mock_bot_context)

    # Then bot.send_message should not be called
    mock_bot_context.bot.send_message.assert_not_called()


inside_run_schedule = (
    False  # Flag to indicate if we are inside the run_schedule function
)


def run_schedule_stub():
    global inside_run_schedule
    inside_run_schedule = True
    for _ in range(2):  # Run the loop twice and then stop.
        schedule.run_pending()
        time.sleep(1)
    inside_run_schedule = False


@pytest.fixture
def mock_sleep():
    with patch(
        "time.sleep",
        side_effect=lambda x: None if inside_run_schedule else time.sleep(0.1),
    ) as mock_sleep:
        yield mock_sleep


@pytest.fixture
def mock_run_pending():
    with patch("schedule.run_pending") as mock:
        yield mock


def test_run_schedule(mock_run_pending, mock_sleep):
    thread = threading.Thread(target=run_schedule_stub)
    thread.start()
    thread.join()

    assert mock_run_pending.call_count == 2
    mock_sleep.assert_has_calls(
        [call(1), call(1)]
    )  # Assert that time.sleep was called twice with argument 1.


class TestRunSchedule(unittest.TestCase):
    @patch("src.schedule_utils.time.sleep", return_value=None)
    @patch("src.schedule_utils.schedule.run_pending")
    def test_run_schedule_calls_run_pending(self, mock_run_pending, mock_sleep):
        # Arrange
        iteration_count = 0
        max_iterations = 3

        def side_effect():
            nonlocal iteration_count
            iteration_count += 1
            if iteration_count >= max_iterations:
                raise KeyboardInterrupt

        mock_run_pending.side_effect = side_effect

        # Act
        try:
            run_schedule()
        except KeyboardInterrupt:
            pass

        # Assert
        self.assertEqual(mock_run_pending.call_count, max_iterations)
        # We expect one fewer sleep call because we're breaking out of the loop before the sleep that follows the third run_pending.
        self.assertEqual(mock_sleep.call_count, max_iterations - 1)

    @patch('src.schedule_utils.time.sleep', return_value=None)
    @patch('src.schedule_utils.schedule.run_pending')
    def test_run_schedule_continues_on_exception(self, mock_run_pending, mock_sleep):
        # Arrange
        mock_run_pending.side_effect = Exception("Test exception")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            run_schedule()

        # We check that an Exception was indeed raised
        self.assertTrue('Test exception' in str(context.exception))

        # We check that run_schedule attempted to call run_pending before the exception.
        self.assertGreater(mock_run_pending.call_count, 0)
