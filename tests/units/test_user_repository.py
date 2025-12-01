from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.role import Role
from app.repositories.user_repository import UserRepository


def make_session():
    engine = create_engine("sqlite:///:memory:")
    # importer les modèles dépendants pour enregistrer toutes les tables dans metadata
    import app.models.permission  # noqa: F401
    import app.models.customer  # noqa: F401
    import app.models.contract  # noqa: F401
    import app.models.event  # noqa: F401
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_user_repository_crud():
    session = make_session()
    repo = UserRepository(session)
    # create a role to satisfy FK
    r = Role(name="tester")
    session.add(r)
    session.flush()

    u = repo.create(user_first_name='A', user_last_name='B', username='ab', email='a@e.com', phone_number='123', password_hash='h', role_id=r.id)
    assert u.id is not None

    fetched = repo.get_by_username('ab')
    assert fetched is not None and fetched.username == 'ab'

    byid = repo.get_by_id(u.id)
    assert byid.id == u.id

    all_users = repo.list_all()
    assert isinstance(all_users, list) and len(all_users) == 1

    # update
    repo.update(u, user_first_name='C')
    assert u.user_first_name == 'C'

    # delete
    repo.delete(u)
    assert repo.get_by_id(u.id) is None
