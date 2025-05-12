import pytest
from unittest.mock import patch, MagicMock
from partiful_bot import PartifulBot, partiful_profile
from selenium.common.exceptions import ElementClickInterceptedException

@pytest.fixture
def bot_fixture():
    with patch('PartifulBot.Chrome') as mock_chrome:
        test_profile = partiful_profile(name='main', user_id='numberhere')
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        bot = PartifulBot(phone_number="+1234567890", default_profile=test_profile)
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
@patch('PartifulBot.random.uniform', return_value=5)
@patch('PartifulBot.time.sleep', return_value=None)
@patch('PartifulBot.PartifulBot.get_verification_code')
@patch('PartifulBot.PartifulBot._store_logs')
@patch('PartifulBot.PartifulBot.set_bearer_token')
def test_login_success(
    mock_set_bearer_token,
    mock_store_logs,
    mock_get_verification_code,
    mock_sleep,
    mock_uniform,
    mock_webdriver_wait,
    bot_fixture
):
    bot, mock_driver = bot_fixture
    mock_get_verification_code.return_value = "123456"
    mock_phone_input = MagicMock()
    mock_submit_button = MagicMock()
    mock_verification_input = MagicMock()
    mock_ver_submit_button = MagicMock()
    mock_clickable = MagicMock()

    # WebDriverWait.until calls: phone input, verification input, clickable submit
    mock_webdriver_wait.return_value.until.side_effect = [
        mock_phone_input,  # phone input
        mock_verification_input,  # verification input
        mock_clickable  # clickable submit
    ]

    # find_element calls: submit button, verification submit button
    mock_driver.find_element.side_effect = [
        mock_submit_button,  # submit button
        mock_ver_submit_button  # verification submit button
    ]

    bot._bearer_token = "token"  # Simulate token found

    bot.login()

    mock_driver.get.assert_called_once_with('https://partiful.com/login')
    mock_phone_input.send_keys.assert_called_once_with(bot.phone_number)
    mock_submit_button.click.assert_called_once()
    mock_verification_input.send_keys.assert_called_once_with("123456")
    mock_driver.execute_script.assert_called_once_with("arguments[0].scrollIntoView(true);", mock_ver_submit_button)
    mock_store_logs.assert_called_once()
    mock_set_bearer_token.assert_called_once()

@patch('PartifulBot.WebDriverWait')
@patch('PartifulBot.random.uniform', return_value=5)
@patch('PartifulBot.time.sleep', return_value=None)
@patch('PartifulBot.PartifulBot.get_verification_code')
@patch('PartifulBot.PartifulBot._store_logs')
@patch('PartifulBot.PartifulBot.set_bearer_token')
def test_login_no_bearer_token_raises(
    mock_set_bearer_token,
    mock_store_logs,
    mock_get_verification_code,
    mock_sleep,
    mock_uniform,
    mock_webdriver_wait,
    bot_fixture
):
    bot, mock_driver = bot_fixture
    mock_get_verification_code.return_value = "123456"
    mock_phone_input = MagicMock()
    mock_submit_button = MagicMock()
    mock_verification_input = MagicMock()
    mock_ver_submit_button = MagicMock()
    mock_clickable = MagicMock()

    mock_webdriver_wait.return_value.until.side_effect = [
        mock_phone_input,
        mock_verification_input,
        mock_clickable
    ]
    mock_driver.find_element.side_effect = [
        mock_submit_button,
        mock_ver_submit_button
    ]

    bot._bearer_token = None  # Simulate token not found

    with pytest.raises(ValueError, match="Bearer token not found in network logs"):
        bot.login()


def test_setup_driver(bot_fixture):
    """Test the setup_driver method."""
    bot, _ = bot_fixture
    driver = bot._setup_driver()
    assert driver is not None

@patch('PartifulBot.PartifulBot._setup_driver')
def test_exit(mock_setup_driver):
    """Test the __exit__ method."""
    mock_driver = MagicMock()
    mock_setup_driver.return_value = mock_driver
    dummy_profile = partiful_profile(name='main', user_id='numberhere')

    with PartifulBot(phone_number="+1234567890", default_profile=dummy_profile) as bot:
        pass

    mock_driver.quit.assert_called_once()
