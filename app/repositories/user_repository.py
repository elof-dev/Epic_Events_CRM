from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """
    Repository pour l'entité User — fournis des opérations de lecture/écriture via une session SQLAlchemy.
    Responsabilités
    - Encapsuler l'accès à la base de données pour l'entité User.
    - Fournir des opérations CRUD courantes sans gérer la transaction (flush effectué, commit/rollback laissé à l'appelant).

    """
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, **fields) -> User:
        u = User(**fields)
        self.session.add(u)
        self.session.flush()
        return u

    def update(self, user: User, **fields) -> User:
        for k, v in fields.items():
            if hasattr(user, k):
                setattr(user, k, v)
        self.session.flush()
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.flush()

    def get_by_username(self, username: str) -> User | None:
        return self.session.query(User).filter(User.username == username).one_or_none()

    def list_all(self) -> list[User]:
        return self.session.query(User).all()

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.query(User).filter(User.id == user_id).one_or_none()


