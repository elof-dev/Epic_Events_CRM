from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.role import Role
from app.repositories.contract_repository import ContractRepository


def make_session():
    engine = create_engine("sqlite:///:memory:")
    # importer les modèles dépendants
    import app.models.permission  # noqa: F401
    import app.models.customer  # noqa: F401
    import app.models.contract  # noqa: F401
    import app.models.event  # noqa: F401
    import app.models.user  # noqa: F401
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_contract_repository_crud():
    session = make_session()
    repo = ContractRepository(session)
    r = Role(name="tester")
    session.add(r)
    session.flush()

    from app.models.user import User
    u = User(role_id=r.id, user_first_name='M', user_last_name='G', email='m@example.com', phone_number='1', username='m', password_hash='h')
    session.add(u)
    session.flush()

    from app.models.customer import Customer
    cust = Customer(user_sales_id=u.id, customer_first_name='A', customer_last_name='B', email='a@e.com', phone_number='123', company_name='Acme')
    session.add(cust)
    session.flush()

    c = repo.create(total_amount=100, balance_due=100, signed=False, customer_id=cust.id, user_management_id=u.id)
    assert c.id is not None

    fetched = repo.get_by_id(c.id)
    assert fetched.id == c.id

    allc = repo.list_all()
    assert isinstance(allc, list) and len(allc) == 1

    repo.update(c, total_amount=200)
    assert c.total_amount == 200

    repo.delete(c)
    assert repo.get_by_id(c.id) is None
