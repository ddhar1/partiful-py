import pytest
from unittest.mock import patch, MagicMock
from PartifulBot import PartifulBot

@pytest.fixture
def bot_fixture():
    """Fixture to set up the PartifulBot instance for testing."""
    with patch('PartifulBot.Chrome') as mock_chrome:
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        bot = PartifulBot(phone_number="+1234567890")
        yield bot, mock_driver

@patch('PartifulBot.Client')
def test_get_verification_code(mock_twilio_client, bot_fixture, monkeypatch):
    """Test the get_verification_code method."""
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "value")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "value")
    bot, _ = bot_fixture
    mock_message = MagicMock()
    mock_message.body = "123456 is your verification code"
    mock_twilio_client.return_value.messages.list.return_value = [mock_message]

    verification_code = bot.get_verification_code()
    assert verification_code == "123456"
    mock_twilio_client.return_value.messages.list.assert_called_once_with(
        to=bot.phone_number,
        limit=1
    )

@patch('PartifulBot.WebDriverWait')
@patch('PartifulBot.PartifulBot.get_verification_code')
def test_login(mock_get_verification_code, mock_webdriver_wait, bot_fixture):
    """Test the login method."""
    bot, mock_driver = bot_fixture
    mock_get_verification_code.return_value = "123456"
    mock_phone_input = MagicMock()
    mock_submit_button = MagicMock()
    mock_verification_input = MagicMock()

    # Mock WebDriverWait behavior
    mock_webdriver_wait.return_value.until.side_effect = [
        mock_phone_input,  # For phone input field
        mock_verification_input  # For verification input field
    ]

    # Mock find_element behavior
    mock_driver.find_element.side_effect = [
        mock_submit_button,  # For submit button
        mock_submit_button  # For verification submit button
    ]

    # Call the login method
    bot.login()

    # Assertions
    mock_driver.get.assert_called_once_with('https://partiful.com/login')
    mock_phone_input.send_keys.assert_called_once_with(bot.phone_number)
    mock_submit_button.click.assert_called()
    mock_verification_input.send_keys.assert_called_once_with("123456")

def test_setup_driver(bot_fixture):
    """Test the setup_driver method."""
    bot, _ = bot_fixture
    driver = bot.setup_driver()
    assert driver is not None

@patch('PartifulBot.PartifulBot.setup_driver')
def test_exit(mock_setup_driver):
    """Test the __exit__ method."""
    mock_driver = MagicMock()
    mock_setup_driver.return_value = mock_driver

    with PartifulBot(phone_number="+1234567890") as bot:
        pass

    mock_driver.quit.assert_called_once()