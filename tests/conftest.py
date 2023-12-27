import pytest
import time
from unittest.mock import Mock, patch, call

@pytest.fixture
def mock_driver():
    driver = Mock()
    driver.quit = Mock()
    return driver
