import pytest
from datetime import datetime, timezone, timedelta
from Partiful_Types import Event, CreateEventParams, Data, RequestBody, GuestStatusCounts, DisplaySettings

def test_event_defaults():
    event = Event(start_date_utc= datetime(2025, 5, 1, 17, 45, tzinfo=timezone.utc),)
    assert event.title == "Untitled Event"
    assert event.timezone == "America/Los_Angeles"
    assert event.visibility == "public"
    assert event.showHostList is True
    assert event.allowGuestPhotoUpload is True
    assert event.status == "SAVED"
    assert isinstance(event.guestStatusCounts, GuestStatusCounts)
    assert isinstance(event.displaySettings, DisplaySettings)
    

def test_event_custom_values():
    custom_date =datetime(2025, 5, 5, 00, 45, tzinfo=timezone.utc)
    event = Event(
        title="Custom Event",
        start_date_utc=custom_date,
        end_date_utc=custom_date,
        event_timezone="Europe/London",
        visibility="private",
        showHostList=False,
        allowGuestPhotoUpload=False,
        status="PUBLISHED"
    )
    assert event.title == "Custom Event"
    assert event.startDate == custom_date
    assert event.endDate == custom_date
    assert event.timezone == "Europe/London"
    assert event.visibility == "private"
    assert event.showHostList is False
    assert event.allowGuestPhotoUpload is False
    assert event.status == "PUBLISHED"

def test_create_event_params_defaults():
    custom_date = datetime(2022, 4, 20, 10, 0, 0, tzinfo=timezone.utc)
    params = CreateEventParams(event=Event(start_date_utc=custom_date))
    assert params.saveAsDraft is False
    assert params.cohostIds == []

def test_data_with_create_event_params():
    custom_date = datetime(2022, 4, 20, 10, 0, 0, tzinfo=timezone.utc)
    params = CreateEventParams(event=Event(start_date_utc=custom_date))
    data = Data(params=params, userId="test_user")
    assert data.userId == "test_user"
    assert isinstance(data.params, CreateEventParams)

def test_request_body():
    custom_date = datetime(2022, 4, 20, 10, 0, 0, tzinfo=timezone.utc)
    params = CreateEventParams(event=Event(start_date_utc=custom_date))
    data = Data(params=params, userId="test_user")
    request_body = RequestBody(data=data)
    assert request_body.data.userId == "test_user"
    assert isinstance(request_body.data.params, CreateEventParams)

def test_event_date_serialization():
    custom_date = datetime(2025, 4, 20, 10, 0, tzinfo=timezone.utc)
    event = Event(start_date_utc=custom_date, end_date_utc=custom_date)
    serialized_start_date = event.serialize_date_utc_with_z(event.startDate)
    serialized_end_date = event.serialize_date_utc_with_z(event.endDate)
    assert serialized_start_date == "2025-04-20T10:00:00.000Z"
    assert serialized_end_date == "2025-04-20T10:00:00.000Z"

def test_event_non_utc_timezone_fails():
    non_utc_date = datetime(2025, 5, 1, 17, 45)  # No timezone specified
    event = Event(start_date_utc=non_utc_date)
    assert event.startDate == non_utc_date
    test_date = datetime(2025, 5, 1, 17, 45, tzinfo=timezone(timedelta(hours=8)))
    print("test tzinfo", test_date.tzinfo)
    with pytest.raises(ValueError):
        Event(start_date_utc=test_date)


