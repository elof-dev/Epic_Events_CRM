from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_username(self, username: str):
        return self.session.query(User).filter(User.username == username).one_or_none()

    def list_all(self):
        return self.session.query(User).all()

    def get_by_id(self, user_id: int):
        return self.session.query(User).filter(User.id == user_id).one_or_none()

    def create(self, **fields):
        u = User(**fields)
        self.session.add(u)
        self.session.flush()
        return u

    def update(self, user: User, **fields):
        for k, v in fields.items():
            if hasattr(user, k):
                setattr(user, k, v)
        self.session.flush()
        return user

    def delete(self, user: User):
        self.session.delete(user)
        self.session.flush()
