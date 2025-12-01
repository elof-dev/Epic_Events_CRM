from sqlalchemy.orm import Session
from app.models.event import Event


class EventRepository:
    """
    Repository pour l'entité Event — fournis des opérations de lecture/écriture via une session SQLAlchemy.
    Responsabilités
    - Encapsuler l'accès à la base de données pour l'entité Event.
    - Fournir des opérations CRUD courantes sans gérer la transaction (flush effectué, commit/rollback laissé à l'appelant).

    """
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, event_id: int) -> Event | None:
        return self.session.query(Event).filter(Event.id == event_id).one_or_none()

    def list_all(self) -> list[Event]:
        return self.session.query(Event).all()

    def list_by_support_user(self, user_id: int) -> list[Event]:
        return self.session.query(Event).filter(Event.user_support_id == user_id).all()

    def list_by_customer(self, customer_id: int) -> list[Event]:
        return self.session.query(Event).filter(Event.customer_id == customer_id).all()

    def create(self, **fields) -> Event:
        e = Event(**fields)
        self.session.add(e)
        self.session.flush()
        return e

    def update(self, event: Event, **fields) -> Event:
        for k, v in fields.items():
            setattr(event, k, v)
        self.session.flush()
        return event

    def delete(self, event: Event) -> None:
        self.session.delete(event)
        self.session.flush()
