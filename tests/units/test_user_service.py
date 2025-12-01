from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
import pytest
from app.models.role import Role
from app.services.user_service import UserService


class DummyPerm:
    def __init__(self, allowed=True):
        self.allowed = allowed

    def user_has_permission(self, user, perm):
        return self.allowed


class DummyUser:
    def __init__(self, id=1):
        self.id = id


def make_session():
    engine = create_engine("sqlite:///:memory:")
    # importer les modèles dépendants pour enregistrer toutes les tables dans metadata
    import app.models.permission  # noqa: F401
    import app.models.customer  # noqa: F401
    import app.models.contract  # noqa: F401
    import app.models.event  # noqa: F401
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_user_service_create_hashes_password_and_persists(monkeypatch):
    session = make_session()
    # create role
    r = Role(name='r')
    session.add(r)
    session.flush()

    perm = DummyPerm(allowed=True)
    svc = UserService(session, perm)
    # monkeypatch the auth hasher to a deterministic value
    monkeypatch.setattr(svc.auth, 'hash_password', lambda pw: 'hashed-'+pw)

    current = DummyUser(id=999)
    u = svc.create(current, user_first_name='A', user_last_name='B', username='ab', email='a@b.com', phone_number='123', role_id=r.id, password='secretpwd')

    assert u.id is not None
    assert u.password_hash == 'hashed-secretpwd'


def test_user_service_create_rejects_duplicate_username(monkeypatch):
    session = make_session()
    r = Role(name='r')
    session.add(r)
    session.flush()

    perm = DummyPerm(allowed=True)
    svc = UserService(session, perm)
    monkeypatch.setattr(svc.auth, 'hash_password', lambda pw: 'h')

    current = DummyUser(id=1)
    # create first user
    svc.create(current, user_first_name='A', user_last_name='B', username='dup', email='d1@e.com', phone_number='100', role_id=r.id, password='password1')

    # attempt to create another with same username
    with pytest.raises(ValueError):
        svc.create(current, user_first_name='X', user_last_name='Y', username='dup', email='d2@e.com', phone_number='101', role_id=r.id, password='password2')


def test_user_service_create_fails_on_missing_role():
    session = make_session()
    perm = DummyPerm(allowed=True)
    svc = UserService(session, perm)
    current = DummyUser(id=1)
    with pytest.raises(ValueError):
        svc.create(current, user_first_name='A', user_last_name='B', username='u1', email='u1@e.com', phone_number='1', role_id=9999, password='password')
