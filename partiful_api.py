import requests
from datetime import datetime
from typing import List, Dict, Any
from partiful_bot import PartifulBot, partiful_profile
from Partiful_Types import CreateEventParams, Event, Data, RequestBody
from zoneinfo import ZoneInfo
from requests.exceptions import JSONDecodeError
import json

EVENT_PREFIX_URL = "https://partiful.com/e/"
PARTIFUL_API_URL = "https://api.partiful.com/"

# create_event_inputs = {'event_name': str, 'event_date': datetime, 'max_capacity': int, 'end_date': datetime, 'description': str, 'cohosts': List[str]}

class PartifulAPI:
    def __init__(self,
                 default_profile: partiful_profile,
                 auth_token: str,
                 local_timezone: str = 'America/Los_Angeles',
                 ):
        self.default_profile = default_profile
        self.auth_token = auth_token
        self.user_id = default_profile.user_id
        self.timezone = ZoneInfo(local_timezone)
        self.headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_token}',
                'Referer': 'https://partiful.com/',
                'Origin': 'https://partiful.com',
                'Accept-Language': 'en-US,en;q=0.5',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0'
            }
        
    def create_event(self, event_name: str, 
                     event_date: datetime,
                     max_capacity: int,
                     end_date: datetime = None,
                     description: str = "",
                     cohosts: List[str] = []
                     ) -> str:
        def check_tz(dt: datetime) -> datetime:
            """Convert datetime to UTC string."""
            if dt.tzinfo is None:
                # assume UTC
                return dt.replace(tzinfo=ZoneInfo('UTC'))
            return dt.astimezone(ZoneInfo('UTC'))
        
        start_utc_str = check_tz(event_date)
        end_utc_str = check_tz(end_date) if end_date else None
        
        url = PARTIFUL_API_URL+ 'createEvent'

        event = Event(
                        title=event_name,
                        start_date_utc=start_utc_str,
                        endDate=end_utc_str,
                        timezone=self.timezone,
                        guestStatusCounts={
                            'READY_TO_SEND': 0,
                            'SENDING': 0,
                            'SENT': 0,
                            'SEND_ERROR': 0,
                            'DELIVERY_ERROR': 0,
                            'MAYBE': 0,
                            'GOING': 0,
                            'DECLINED': 0,
                            'WAITLIST': 0,
                            'PENDING_APPROVAL': 0,
                            'APPROVED': 0,
                            'WITHDRAWN': 0,
                            'RESPONDED_TO_FIND_A_TIME': 0
                        },
                        showHostList=True,
                        showGuestCount=True,
                        showGuestList=True,
                        showActivityTimestamps=True,
                        displayInviteButton=True,
                        visibility='public',
                        allowGuestPhotoUpload=True,
                        enableGuestReminders=True,
                        rsvpsEnabled=True,
                        allowGuestsToInviteMutuals=True,
                        status='PUBLISHED', #SAVED
                        maxCapacity=max_capacity,
                        enableWaitlist=True,
                        description=description
                    )
        
        request_body = RequestBody(
                        data=Data(
                                params=CreateEventParams(event=event,
                                    saveAsDraft=False,
                                    cohostIds=cohosts
                                    ),
                                userId=self.user_id
                            )
                        )
        response_json = self.call_api(url, method='POST', data=request_body.model_dump_json())


        try:
            response_json['event_id'] = response_json['result']['data']    
        except KeyError:
            raise KeyError(f"Error creating event: {response_json}, expected key 'result' or subkey 'data' not in json")
        except Exception as e:
            raise Exception(f"Error creating event: {response_json}" + str(e))
        output_url = EVENT_PREFIX_URL + response_json['event_id']

        return output_url

    def get_mutuals(self) -> Dict[str, Any]:
        """Get mutual connections."""
        url = PARTIFUL_API_URL+'getMutuals'
        
        request_body = json.dumps({
            'data': {
                'params': {},
                'paging': {'cursor': None, 'maxResults': 100},
                "userId": self.user_id
            }
            })

        response_json = self.call_api(url, method='POST', data=request_body)

        return response_json

    def get_rsvps(self) -> Any:
        """
        Get events you have RSVP-ed to 
        """
        url = PARTIFUL_API_URL + "getMyRsvps"    

        response = self.call_api(url, method='POST', data=RequestBody(data=Data(params={}, userId=self.user_id)).model_dump_json())

        return response

    def call_api(self, url: str, method: str = 'GET', data: Dict[str, Any] = None) -> Any:
        """Generic API call."""
        if method == 'GET':
            response = requests.get(url, headers=self.headers)
        elif method == 'POST':
            response = requests.post(url, headers=self.headers, json=data)
        else:
            raise ValueError("Unsupported HTTP method - only GET and POST are supported.")
        
        if response.status_code != 200:
            try:
                resp_json = response.json()
            except JSONDecodeError:
                resp_json = None
            raise Exception(f"Error calling API: {response.status_code} {response}, - {response.text} =  {resp_json}")
        if response.headers.get("Content-Type", "").startswith("application/json"):
            resp_json = response.json()
            if "error" in resp_json:
                raise Exception(f"API Error: {resp_json['error'].get('message', 'Unknown error')}")
        else:
            raise Exception(f"Expected JSON response but got: {response.text}")
        return response.json()

    def get_guests_csv(
        self,
        event_id: str,
        statuses: List[str] = None,
        questionnaire: bool = True
    ) -> str:
        """Get guest information in CSV format."""
        if statuses is None:
            statuses = ['APPROVED', 'PENDING_APPROVAL', 'GOING', 'MAYBE', 'WAITLIST', 'DECLINED']

        allowed_statuses = ['APPROVED', 'PENDING_APPROVAL', 'GOING', 'MAYBE', 'WAITLIST', 'DECLINED']
        
        # Build the base URL
        url = f'https://api.partiful.com/getGuestsCsv?eventId={event_id}&questionnaire={str(questionnaire).lower()}'
        
        # Add valid statuses to the URL
        for status in statuses:
            if status in allowed_statuses:
                url += f'&statuses={status}'
        
        response = self.call_api( url, method='GET')
        
        return response.text

    # def get_event(self, event_id: str) -> Dict[str, Any]:
    
    #     """Get event information."""
    #     url = f'https://partiful.com/e/{event_id}'
    #     response = requests.get(url)
    #     soup = BeautifulSoup(response.text, 'html.parser')

    #     name = soup.select_one('h1 span').text if soup.select_one('h1 span') else None
    #     time_element = soup.find('time')
    #     date_time = time_element.get('datetime') if time_element else None
    #     start_datetime = datetime.fromisoformat(date_time).isoformat() if date_time else None

    #     event = {
    #         'id': event_id,
    #         'name': name,
    #         'startDateTime': start_datetime,
    #         'url': url
    #     }

    #     return event 

    # def get_users(
    #     self, 
    #     ids: List[str], 
    #     exclude_party_stats: bool = False, 
    #     include_party_stats: bool = True
    # ) -> Dict[str, Any]:
    #     """Get user information for specified user IDs."""
    #     url = 'https://us-central1-getpartiful.cloudfunctions.net/getUsersV2'
        
    #     response = requests.post(
    #         url,
    #         headers={
    #             'Content-Type': 'application/json',
    #             'authorization': f'Bearer {quote(self.auth_token)}'
    #         },
    #         json={
    #             'data': {
    #                 'params': {
    #                     'ids': ids,
    #                     'includePartyStats': include_party_stats
    #                 },
    #               "userId": self.user_id
    #             }
    #         }
    #     )
        
    #     return response.json()

    # def get_invitable_contacts(
    #     self, 
    #     event_id: str, 
    #     skip: int = 0, 
    #     limit: int = 100
    # ) -> Dict[str, Any]:
    #     """Get contacts that can be invited to an event."""
    #     url = 'https://us-central1-getpartiful.cloudfunctions.net/getInvitableContactsV2'
        
    #     response = requests.post(
    #         url,
    #         headers={
    #             'Content-Type': 'application/json',
    #             'authorization': f'Bearer {quote(self.auth_token)}'
    #         },
    #         json={
    #             'data': {
    #                 'params': {
    #                     'skip': skip,
    #                     'limit': limit,
    #                     'eventId': event_id
    #                 }
    #             }
    #         }
    #     )
        
    #     return response.json()



