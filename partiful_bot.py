from collections import namedtuple
import json
from os import environ
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import time
from twilio.rest import Client
import random

TWILIO_ACCOUNT_SID = environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = environ['TWILIO_AUTH_TOKEN']

partiful_profile = namedtuple('PartifulProfile', ['name', 'user_id'])

class PartifulBot:
    def __init__(self, phone_number: str, default_profile: partiful_profile):
        """
        Initialize the PartifulBot with a phone number and optional profiles.

        :param phone_number: The phone number to use for login. 
            Assumptions: 
             * Twilio number, so can get verification code from Twilio API
             * USACA number WITHOUT country code - bot cannot select for non-US country codes use non-US number
        :param default_profile: User profile you want to use for API calls. 
            # TODO: make this optional and default
            # TODO: consider making userId used for API calls not tied to class instantiation
        """
        self.phone_number = phone_number # must be a twilio number to access verification code
        self._bearer_token = None
        self.default_profile = default_profile if default_profile else None

        self._service = Service(ChromeDriverManager().install())
        self._selenium_driver = self._setup_driver()
        self._logs = []
        
        
    def _setup_driver(self) -> Chrome:
        """Set up and return a configured Chrome WebDriver."""
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('--log-level=0')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        chrome_options.add_argument("--headless=new")
        #chrome_options.add_argument("--no-sandbox")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        #chrome_options.add_argument("--disable-gpu")
        return Chrome(service=self._service, options=chrome_options)

    def _is_driver_alive(self) -> bool:
        """
        Check if the Selenium driver is still active and functional.
        If not, reinitialize it.
        """
        try:
            self._selenium_driver.current_url
            return True
        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"Selenium driver is not functional due to error: {e}. You can reinit with self._selenium_driver = self._setup_driver() & logging in again")
            self._selenium_driver.quit()
            return False
        return False

    def login(self):
        """
        Navigate to website and submit phone number + verification code.
        Get bearer token from network logs.
        """
        self._selenium_driver.get('https://partiful.com/login') # 
        
        # Wait for phone input field, enter phone num,  and submit
        print("Inputting phone number...")
        time.sleep(5) # wait for page to load
        phone_input = WebDriverWait(self._selenium_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='tel']")) #[@name='phoneNumber']
        )
        phone_input.send_keys(self.phone_number)
        time.sleep(random.uniform(4, 12)) # wait for page to load
        submit_button = self._selenium_driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Get verification code, and submit it
        print("Waiting for verification code...")
        time.sleep(5)
        verification_code = self.get_verification_code()
        verification_input = WebDriverWait(self._selenium_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='authCode']"))
        )
        verification_input.send_keys(verification_code)
        time.sleep(random.uniform(4, 12)) # wait for page to load
        submit_verification_button = self._selenium_driver.find_element(By.XPATH, "//button[@type='submit']")
        # scroll button into view
        self._selenium_driver.execute_script("arguments[0].scrollIntoView(true);", submit_verification_button)

        try:
            WebDriverWait(self._selenium_driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        except ElementClickInterceptedException as e:
            self._selenium_driver.save_screenshot("error_screenshot.png")  # Save a screenshot for debugging
            raise e("Login button was not clickable, cannot proceed")
            
        print("Waiting for login to complete...")
        time.sleep(10) # wait for page to load

        self._store_logs() # store logs for debugging
        self.set_bearer_token() # set bearer token using network logs
        # TODO: can elegantly set default user_id 
        if self._bearer_token is None:
            raise ValueError("Bearer token not found in network logs. Please check the login process. You will not be able to use some partiful functionalities")

    def get_verification_code(self) -> str:
        """
        Get the verification code from Twilio phone number.
        """
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        messages = client.messages.list(
            to=self.phone_number,
            limit=1
        )
        # Extract verification code from message
        verification_code = messages[0].body.split(" ")[0]
        return verification_code
    
    def _store_logs(self):
        """
        Store the logs in a file for debugging purposes.
        """
        log_entries = self._selenium_driver.get_log("performance")
        self._logs = []
        for entry in log_entries:
            try:
                self._logs.append(json.loads(entry["message"])["message"])
            except json.JSONDecodeError:
                continue  # Skip entries that fail to load
            except Exception as e: # unsure about other exceptions
                print(f"Error processing log entry: {e}")
                continue
        # Filter out logs that are not relevant
        
        # Save logs to a file for debugging
        with open("network_logs.json", "w") as log_file:
            json.dump(self._logs, log_file, indent=4)

    def set_bearer_token(self):
        """
        Set the bearer token using network logs from the Selenium driver.
        This is a workaround for the fact that Partiful does not have an official API for login.
        """
        # get api.partiful.com bearer token through network logs
        attempts = 3  # Number of attempts to refresh logs
        for _ in range(attempts):
            for message in self._logs:
                try:
                    method = message.get("method")
                    if method in ['Network.requestWillBeSentExtraInfo', 'Network.requestWillBeSent']:
                        try:
                            if message['params']['headers'][':authority'] == 'api.partiful.com':
                                if 'authorization' in message['params']['headers']:
                                    self._bearer_token = message['params']['headers']['authorization'].split()[-1]
                                    return  # Exit once the bearer token is found
                        except KeyError:
                            continue  # Try a different entry
                except Exception:
                    continue  # Ignore malformed log entries
            # Refresh the page to get new logs if token is not found
            self._selenium_driver.refresh()
            time.sleep(5)  # Wait for the page to reload
        raise Exception("Bearer token not found in network logs after multiple attempts.")



    def __enter__(self):
        self._selenium_driver = self._setup_driver()
        return self
     
    def __exit__(self, exc_type, exc_value, traceback):
        self._selenium_driver.quit()