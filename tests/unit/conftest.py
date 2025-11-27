import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base


@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# simple factories
@pytest.fixture
def role_factory(db_session):
    def _create(name, permissions=None):
        from app.models.role import Role
        from app.models.permission import Permission
        r = Role(name=name, description=f"role {name}")
        db_session.add(r)
        db_session.flush()
        if permissions:
            for p_name in permissions:
                p = db_session.query(Permission).filter_by(name=p_name).one_or_none()
                if not p:
                    p = Permission(name=p_name, description=p_name)
                    db_session.add(p)
                    db_session.flush()
                r.permissions.append(p)
        db_session.flush()
        return r

    return _create


@pytest.fixture
def user_factory(db_session, role_factory):
    def _create(username="u1", role_name="sales"):
        from app.models.user import User
        role = db_session.query(__import__("app.models.role", fromlist=["Role"]).Role).filter_by(name=role_name).one_or_none()
        if not role:
            role = role_factory(role_name)
        u = User(user_first_name="First", user_last_name="Last", email=f"{username}@example.com", phone_number=None, username=username, password_hash="x", role_id=role.id)
        db_session.add(u)
        db_session.flush()
        return u

    return _create


@pytest.fixture
def customer_factory(db_session, user_factory):
    def _create(sales_user=None, company_name="CoTest"):
        from app.models.customer import Customer
        if sales_user is None:
            sales_user = user_factory(username="sales_tmp", role_name="sales")
        c = Customer(customer_first_name="CFirst", customer_last_name="CLast", email="cust@example.com", phone_number=None, company_name=company_name, user_sales_id=sales_user.id)
        db_session.add(c)
        db_session.flush()
        return c

    return _create


@pytest.fixture
def contract_factory(db_session, customer_factory, user_factory):
    def _create(customer=None, manager=None, signed=False, contract_number="C-1"):
        from app.models.contract import Contract
        if customer is None:
            customer = customer_factory()
        if manager is None:
            manager = user_factory(username="manager_tmp", role_name="management")
        c = Contract(contract_number=contract_number, total_amount=100, balance_due=100, signed=signed, customer_id=customer.id, user_management_id=manager.id)
        db_session.add(c)
        db_session.flush()
        return c

    return _create


@pytest.fixture
def event_factory(db_session, contract_factory, user_factory):
    def _create(contract=None, support=None, event_number="E-1"):
        from app.models.event import Event
        from datetime import datetime, timezone
        if contract is None:
            contract = contract_factory(signed=True)
        if support is None:
            support = user_factory(username="support_tmp", role_name="support")
        e = Event(contract_id=contract.id, customer_id=contract.customer_id, user_support_id=support.id, event_name="Ev", event_number=event_number, start_datetime=datetime.now(timezone.utc), end_datetime=datetime.now(timezone.utc))
        db_session.add(e)
        db_session.flush()
        return e

    return _create
