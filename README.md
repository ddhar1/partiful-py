# Partiful API Client

A Python client for automatically getting partiful auth cres +  interacting with the partiful API
Cursor helped me translate the code from this repo to get me started, https://github.com/cerebralvalley/partiful-api, thank you [cerebralvalley]( https://github.com/cerebralvalley).

`partiful_bot`: helps you get an auth token automatically
`partiful_api`: helps you interact with the auth token and request data from the API

## Installation
You need python >=3.9
1. Clone this repository
2. Install the required dependencies:

```bash
python -m venv venv
pip install -r requirements.txt
```

## Usage

```python
from partiful_api import PartifulApi

# Initialize the client with your auth token
api = PartifulApi(auth_token='your_auth_token', user_id='your_user_id')
# timezone is optional

# Get mutual connections
mutuals = api.get_mutuals()

# Create an event
from datetime import datetime

event = api.create_event(
    event_name='My Event',
    event_date=datetime(2024, 3, 21, 18, 0, 0),  # March 21, 2024 at 6:00 PM
    max_capacity=50,
    description='Join us for a fun evening!',
    cohosts=['cohost_user_id']  # Optional list of cohost user IDs
)

```


## Getting the Auth and user_id values manually

`partiful_bot.py` can help you get your bearer token but you will (as of now), need to set a default_profile using `partiful_bot.partiful_profile` namedtuple. You can find your user id through your partiful profile (your profile page is at `https://partiful.com/u/USER_PROFILE_ID_HERE`) 

### Getting the bearer token manually:
Partiful doesn't have an official API. You need a partiful account and then need to figure out your user_id, and find a currently active auth token
1. Login to the Partiful website
2. Open the developer tools -> network
3. Refresh the page or click on an event
4. Look for a network request that uses the Authentication Bearer token (such as getMutuals).
5. Navigate to the request's headers tab
6. Copy the Authorization header's value (without the Bearer part) + user_id