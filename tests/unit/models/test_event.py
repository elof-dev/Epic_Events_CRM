from app.models.event import Event
from datetime import datetime, timezone


def test_event_fields_and_repr():
    now = datetime.now(timezone.utc)
    e = Event(contract_id=1, customer_id=1, user_support_id=None, event_name="E1", event_number="EN1", start_datetime=now, end_datetime=now)
    assert e.event_name == "E1"
    assert "EN1" in repr(e)
