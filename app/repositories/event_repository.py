from sqlalchemy.orm import Session
from app.models.event import Event


class EventRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, event_id: int):
        return self.session.query(Event).filter(Event.id == event_id).one_or_none()

    def list_all(self):
        return self.session.query(Event).all()

    def list_by_support_user(self, user_id: int):
        return self.session.query(Event).filter(Event.user_support_id == user_id).all()

    def list_by_customer(self, customer_id: int):
        return self.session.query(Event).filter(Event.customer_id == customer_id).all()

    def create(self, **fields):
        e = Event(**fields)
        self.session.add(e)
        self.session.flush()
        return e

    def update(self, event: Event, **fields):
        for k, v in fields.items():
            setattr(event, k, v)
        self.session.flush()
        return event

    def delete(self, event: Event):
        self.session.delete(event)
        self.session.flush()
