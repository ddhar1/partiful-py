import json
from os import environ
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from twilio.rest import Client

TWILIO_ACCOUNT_SID = environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = environ['TWILIO_AUTH_TOKEN']
PARTIFUL_ACCT_NUM = environ['PARTIFUL_ACCT_NUM']

class PartifulBot:
    def __init__(self, phone_number):
        self.phone_number = phone_number # must be a twilio number to access verification code
        self.bearer_token = None
        self.selenium_driver = self.setup_driver()
        
    def setup_driver(self) -> Chrome:
        """Set up and return a configured Chrome WebDriver."""
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--no-sandbox")
        #chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        return Chrome(options=chrome_options)

    def login(self):
        """Navigate to website and submit phone number"""
        self.selenium_driver.get('https://partiful.com/login')
        
        # Wait for phone input field and enter phone number
        phone_input = WebDriverWait(self.selenium_driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='tel']")) #[@name='phoneNumber']
        )
        
        phone_input.send_keys(self.phone_number)
        
        # Submit form
        submit_button = self.selenium_driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Get verification code, and submit it
        time.sleep(5)
        verification_code = self.get_verification_code()
        verification_input = WebDriverWait(self.selenium_driver, 10).until(
            EC.presence_of_element_located((By.ID, "verification_input"))
        )
        verification_input.send_keys(verification_code)
        submit_button = self.selenium_driver.find_element(By.ID, "submit_button")
        submit_button.click()

        # get api.partiful.com bearer token through network logs 
        log_entries = self.selenium_driver.get_log("performance")
        for entry in log_entries:
            try:
                obj_serialized: str = entry.get("message")
                obj = json.loads(obj_serialized)
                message = obj.get("message")
                method = message.get("method")
                if method in ['Network.requestWillBeSentExtraInfo' or 'Network.requestWillBeSent']:
                    try:
                        if message['params']['headers'][':authority'] == 'api.partiful.com':
                            #x = message['params']['headers']['authorization']
                            if 'authorization' in message['params']['headers'].keys():
                                self.bearer_token = message['params']['headers']['authorization'].split()[-1]
                    except:
                        continue # try a different entry
            except Exception as e:
                raise e("Setting bearer token failed")

    def get_verification_code(self) -> str:
        """Get the verification code from Twilio phone number."""
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        messages = client.messages.list(
            to=self.phone_number,
            limit=1
        )
        # Extract verification code from message
        verification_code = messages[0].body.split(" ")[0]
        return verification_code

    def __enter__(self):
        self.selenium_driver = self.setup_driver()
        return self
     
    def __exit__(self, exc_type, exc_value, traceback):
        self.selenium_driver.quit()