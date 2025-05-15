from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Any, List, Union
from datetime import datetime
from zoneinfo import ZoneInfo

class GuestStatusCounts(BaseModel):
    READY_TO_SEND: int = 0
    SENDING: int = 0
    SENT: int = 0
    SEND_ERROR: int = 0
    DELIVERY_ERROR: int = 0
    MAYBE: int = 0
    GOING: int = 0
    DECLINED: int = 0
    WAITLIST: int = 0
    PENDING_APPROVAL: int = 0
    APPROVED: int = 0
    WITHDRAWN: int = 0
    RESPONDED_TO_FIND_A_TIME: int = 0

class DisplaySettings(BaseModel):
    theme: str = "none"
    effect: str = "none"
    titleFont: str = "display"

class Image(BaseModel):
    url: str
    height: int = None
    width: int = None
    blurHash: str = None
    contentType: str = None

class Event(BaseModel):
    title: str = "Untitled Event"
    startDate: datetime = Field(alias="start_date_utc")
    endDate: Union[datetime, None] = Field(default=None, alias="end_date_utc")
    timezone: str = Field(default="America/Los_Angeles", alias="event_timezone")
    guestStatusCounts: GuestStatusCounts = GuestStatusCounts()
    displaySettings: DisplaySettings = DisplaySettings()
    showHostList: bool = True
    showGuestCount: bool = True
    showGuestList: bool = True
    showActivityTimestamps: bool = True
    displayInviteButton: bool = True
    visibility: str = "public"
    allowGuestPhotoUpload: bool = True
    enableGuestReminders: bool = True
    rsvpsEnabled: bool = True
    allowGuestsToInviteMutuals: bool = True
    image: Image = None
    status: str = "SAVED"
    maxCapacity: int = 100
    enableWaitlist: bool = True

    @field_serializer('startDate', 'endDate', when_used='json')
    def serialize_date_utc_with_z(self, dt: datetime):
        """Serialize datetime to string with 'Z' at the end."""
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    @field_validator('startDate', 'endDate', mode='after')
    @classmethod
    def validate(cls, dt: datetime) -> datetime:
        """Validate that datetime fields have UTC timezone or no timezone."""
        if dt.tzinfo is not None and dt.tzinfo != ZoneInfo('UTC'):
            raise ValueError("start_date_utc must be in UTC timezone")
        return dt

class CreateEventParams(BaseModel):
    event: Event
    saveAsDraft: bool = False
    cohostIds: List[str] = Field(default_factory=list)

class Data(BaseModel):
    params: Union[CreateEventParams, dict]
    userId: str



class RequestBody(BaseModel):
    data: Data

class GetMutualsParams(BaseModel):
    shouldRemoveEventData: bool = False



class Paging(BaseModel):
    maxResults: int = 8
    cursor: str = None


class GetMutualsData(BaseModel):
    params: GetMutualsParams
    paging: Paging
    userId: str
# Example of creating an instance of the RequestBody with defaults
# request_body = RequestBody(
#     data=Data(
#         params=CreateEventParams(
#             event=Event(),  # This will use all default values
#             saveAsDraft=False,
#             cohostIds=[]
#         ),
#         userId="asdfadfadf"  # You can set this to whatever you need
#     )
# )

# To update userId, title, and startDate
# request_body.data.userId = "new_user_id"
# request_body.data.params.event.title = "New Event Title"
# request_body.data.params.event.startDate = "2025-04-20T10:00:00Z"

# print(request_body.json())


# # Example of creating an instance of the RequestBody
# request_body = RequestBody(
#     data=Data(
#         params=CreateEventParams(
#             event=Event(
#                 title="Untitled Event",
#                 startDate="TBD",
#                 timezone="America/Los_Angeles",
#                 guestStatusCounts=GuestStatusCounts(
#                     READY_TO_SEND=0,
#                     SENDING=0,
#                     SENT=0,
#                     SEND_ERROR=0,
#                     DELIVERY_ERROR=0,
#                     MAYBE=0,
#                     GOING=0,
#                     DECLINED=0,
#                     WAITLIST=0,
#                     PENDING_APPROVAL=0,
#                     APPROVED=0,
#                     WITHDRAWN=0,
#                     RESPONDED_TO_FIND_A_TIME=0
#                 ),
#                 displaySettings=DisplaySettings(
#                     theme="grass",
#                     effect="none",
#                     titleFont="display"
#                 ),
#                 showHostList=True,
#                 showGuestCount=True,
#                 showGuestList=True,
#                 showActivityTimestamps=True,
#                 displayInviteButton=True,
#                 visibility="public",
#                 allowGuestPhotoUpload=True,
#                 enableGuestReminders=True,
#                 rsvpsEnabled=True,
#                 allowGuestsToInviteMutuals=True,
#                 status="SAVED"
#             ),
#             saveAsDraft=False,
#             cohostIds=[]
#         ),
#         userId="asdfadfadf"
#     )
# )

# # To update userId, title, and startDate
# request_body.data.userId = "new_user_id"
# request_body.data.params.event.title = "New Event Title"
# request_body.data.params.event.startDate = "2025-04-20T10:00:00Z"

# print(request_body.json())
