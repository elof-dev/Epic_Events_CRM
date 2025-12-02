from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
import pytest
from app.models.role import Role
from app.services.contract_service import ContractService


class DummyPerm:
    def __init__(self, allowed=True):
        self.allowed = allowed

    def can_create_contract(self, user):
        return self.allowed

    def can_update_contract(self, user, contract=None):
        return self.allowed

    def can_delete_contract(self, user, contract=None):
        return self.allowed

    def user_has_permission(self, user, perm):
        return self.allowed


class DummyUser:
    def __init__(self, id=1):
        self.id = id


def make_session():
    engine = create_engine("sqlite:///:memory:")
    import app.models.permission  # noqa: F401
    import app.models.customer  # noqa: F401
    import app.models.contract  # noqa: F401
    import app.models.event  # noqa: F401
    import app.models.user  # noqa: F401
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_contract_service_create_injects_manager():
    session = make_session()
    # create role and user
    r = Role(name='management')
    session.add(r)
    session.flush()

    from app.models.user import User
    manager = User(role_id=r.id, user_first_name='M', user_last_name='G', email='m@example.com', phone_number='1', username='mgr', password_hash='h')
    session.add(manager)
    session.flush()

    from app.models.customer import Customer
    cust = Customer(user_sales_id=manager.id, customer_first_name='A', customer_last_name='B', email='a@e.com', phone_number='123', company_name='Acme')
    session.add(cust)
    session.flush()

    perm = DummyPerm(allowed=True)
    svc = ContractService(session, perm)

    current = DummyUser(id=manager.id)
    c = svc.create(current, total_amount=100, balance_due=100, customer_id=cust.id)

    assert c.id is not None
    assert c.user_management_id == manager.id


def test_contract_service_create_fails_on_missing_customer():
    session = make_session()
    r = Role(name='management')
    session.add(r)
    session.flush()

    from app.models.user import User
    manager = User(role_id=r.id, user_first_name='M', user_last_name='G', email='m@example.com', phone_number='1', username='mgr', password_hash='h')
    session.add(manager)
    session.flush()

    perm = DummyPerm(allowed=True)
    svc = ContractService(session, perm)
    current = DummyUser(id=manager.id)
    with pytest.raises(ValueError):
        svc.create(current, total_amount=10, balance_due=10)


def test_contract_service_delete_refuses_if_events_exist():
    session = make_session()
    r = Role(name='management')
    session.add(r)
    session.flush()

    from app.models.user import User
    manager = User(role_id=r.id, user_first_name='M', user_last_name='G', email='m@example.com', phone_number='1', username='mgr', password_hash='h')
    session.add(manager)
    session.flush()

    from app.models.customer import Customer
    cust = Customer(user_sales_id=manager.id, customer_first_name='A', customer_last_name='B', email='a@e.com', phone_number='123', company_name='Acme')
    session.add(cust)
    session.flush()

    perm = DummyPerm(allowed=True)
    svc = ContractService(session, perm)
    current = DummyUser(id=manager.id)

    c = svc.create(current, total_amount=100, balance_due=100, customer_id=cust.id)

    from app.models.event import Event
    from datetime import datetime, timedelta
    start = datetime.utcnow()
    ev = Event(contract_id=c.id, customer_id=cust.id, user_support_id=manager.id, event_name='E1', start_datetime=start, end_datetime=start + timedelta(hours=1), location='L', attendees=10)
    session.add(ev)
    session.flush()

    with pytest.raises(ValueError):
        svc.delete(current, c.id)
