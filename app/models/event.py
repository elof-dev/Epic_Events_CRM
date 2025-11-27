from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    user_support_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_name = Column(String(255), nullable=False)
    event_number = Column(String(100), unique=True, nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=True)
    attendees = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)

    contract = relationship("Contract", back_populates="events")
    customer = relationship("Customer", back_populates="events")
    support_user = relationship("User", back_populates="support_events")

    def __repr__(self):
        return f"<Event {self.event_number} {self.event_name}>"
