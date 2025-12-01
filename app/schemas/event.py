from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, ValidationError


class EventBase(BaseModel):
    """Schéma minimal Pydantic pour Event."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    contract_id: int
    customer_id: int
    user_support_id: Optional[int] = None
    event_name: str
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str] = None
    attendees: Optional[int] = None
    note: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    contract_id: Optional[int] = None
    customer_id: Optional[int] = None
    user_support_id: Optional[int] = None
    event_name: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[int] = None
    note: Optional[str] = None


__all__ = ["EventBase", "EventCreate", "EventUpdate", "ValidationError"]
