from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.role import Role
from app.repositories.customer_repository import CustomerRepository


def make_session():
    engine = create_engine("sqlite:///:memory:")
    # importer les modèles dépendants pour enregistrer toutes les tables dans metadata
    import app.models.permission  # noqa: F401
    import app.models.customer  # noqa: F401
    import app.models.contract  # noqa: F401
    import app.models.event  # noqa: F401
    import app.models.user  # noqa: F401
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_customer_repository_crud():
    session = make_session()
    repo = CustomerRepository(session)
    # create a role and a user to satisfy FK
    r = Role(name="tester")
    session.add(r)
    session.flush()

    # create a user to be the sales owner
    from app.models.user import User
    u = User(role_id=r.id, user_first_name='S', user_last_name='P', email='s@example.com', phone_number='1000', username='sales1', password_hash='h')
    session.add(u)
    session.flush()

    c = repo.create(user_sales_id=u.id, customer_first_name='A', customer_last_name='B', email='a@e.com', phone_number='123', company_name='Acme')
    assert c.id is not None

    fetched = repo.get_by_id(c.id)
    assert fetched is not None and fetched.company_name == 'Acme'

    all_customers = repo.list_all()
    assert isinstance(all_customers, list) and len(all_customers) == 1

    # update
    repo.update(c, customer_first_name='C')
    assert c.customer_first_name == 'C'

    # delete
    repo.delete(c)
    assert repo.get_by_id(c.id) is None
