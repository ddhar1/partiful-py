# Partiful API Client

A Python client for interacting with the Partiful API.
Cursor helped me translate the code from this repo to get me started, https://github.com/cerebralvalley/partiful-api, thank you [cerebralvalley]( https://github.com/cerebralvalley).

## Getting the Auth and user_id values

Partiful doesn't have an official API. You need a partiful account and then need to figure out your user_id, and find a currently active auth token
1. Login to the Partiful website
2. Open the developer tools -> network
3. Refresh the page or click on an event
4. Look for a network request that uses the Authentication Bearer token (such as getMutuals).
5. Navigate to the request's headers tab
6. Copy the Authorization header's value (without the Bearer part) + user_id

Note: this token expires after a while, so you'll need to repeat this process about at least once a day. Mainly using this when I have to make 5 events in a row.

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

## Dependencies

- requests
- beautifulsoup4
- urllib3

