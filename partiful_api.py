import requests
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

partiful_event_prefix = "https://partiful.com/e/"

class PartifulApi:
    def __init__(self, auth_token: str, user_id: str,
                 timezone: str = 'America/Los_Angeles'):
        self.auth_token = auth_token
        self.user_id = user_id

    def create_event(self, event_name: str, 
                     event_date: datetime,
                     max_capacity: int,
                     description: str = "",
                     cohosts: List[str] = None
                     ) -> str:

        # Convert from PST to UTC using proper timezone handling
        pst_date = event_date.replace(tzinfo=ZoneInfo("America/Los_Angeles"))
        utc_date = pst_date.astimezone(ZoneInfo("UTC"))
        formatted_date = utc_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        url = 'https://api.partiful.com/createEvent'

        response = requests.post(
            url,
            headers={
                'Content-Type': 'application/json',
                'authorization': f'Bearer {self.auth_token}'
            },
            json={
                'data': {
                    'params': {
                        'event': {
                            'title': event_name,
                            'startDate': formatted_date,
                            'timezone': 'America/Los_Angeles',
                            'guestStatusCounts': {
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
                            'showHostList': True,
                            'showGuestCount': True,
                            'showGuestList': True,
                            'showActivityTimestamps': True,
                            'displayInviteButton': True,
                            'visibility': 'public',
                            'allowGuestPhotoUpload': True,
                            'enableGuestReminders': True,
                            'rsvpsEnabled': True,
                            'allowGuestsToInviteMutuals': True,
                            'status': 'PUBLISHED', #SAVED
                            'endDate': None,
                            'maxCapacity': max_capacity,
                            'enableWaitlist': True,
                            'description': description
                        },
                        'saveAsDraft': False,
                        'cohostIds': cohosts
                    },
                    'userId': self.user_id
                }
            }
        )

        if response.status_code != 200:
            raise Exception(f"Error creating event: {response.json()}")
        elif response.status_code == 200:
            response_json = response.json()
            try:
                response_json['event_id'] = response_json['result']['data']    
            except KeyError:
                raise KeyError(f"Error creating event: {response.json()}, expected key 'result' or subkey 'data' not in json")
            except Exception as e:
                raise Exception(f"Error creating event: {response.json()}" + str(e))
        output_url = partiful_event_prefix + response_json['event_id']

        return output_url

    def get_mutuals(self) -> Dict[str, Any]:
        """Get mutual connections."""
        url = 'https://api.partiful.com/getMutuals'
        
        response = requests.post(
            url,
            headers={
                'Content-Type': 'application/json',
                'authorization': f'Bearer {self.auth_token}'
            },
            json={
                'data': {
                    'params': {},
                    'paging': {'cursor': None, 'maxResults': 8},
                    "userId": self.user_id
                }
            }
        )
        
        if response.status_code == 404:
            raise Exception("Error - maybe URL is not working")
        return response.json()


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
    #                     'excludePartyStats': exclude_party_stats,
    #                     'ids': ids,
    #                     'includePartyStats': include_party_stats
    #                 }
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

    # def get_guests_csv(
    #     self,
    #     event_id: str,
    #     statuses: List[str] = None,
    #     questionnaire: bool = True
    # ) -> str:
    #     """Get guest information in CSV format."""
    #     if statuses is None:
    #         statuses = ['APPROVED', 'PENDING_APPROVAL', 'GOING', 'MAYBE', 'WAITLIST', 'DECLINED']

    #     allowed_statuses = ['APPROVED', 'PENDING_APPROVAL', 'GOING', 'MAYBE', 'WAITLIST', 'DECLINED']
        
    #     # Build the base URL
    #     url = f'https://us-central1-getpartiful.cloudfunctions.net/getGuestsCsvV2?eventId={event_id}&questionnaire={str(questionnaire).lower()}'
        
    #     # Add valid statuses to the URL
    #     for status in statuses:
    #         if status in allowed_statuses:
    #             url += f'&statuses={status}'
        
    #     response = requests.get(
    #         url,
    #         headers={
    #             'authorization': f'Bearer {quote(self.auth_token)}'
    #         }
    #     )
        
    #     return response.text

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
