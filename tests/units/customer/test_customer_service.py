from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
import pytest
from app.models.role import Role
from app.services.customer_service import CustomerService


class DummyPerm:
    def __init__(self, allowed=True):
        self.allowed = allowed

    def can_create_customer(self, user):
        return self.allowed

    def can_update_customer(self, user, customer):
        return self.allowed

    def can_delete_customer(self, user, customer):
        return self.allowed

    def can_read_customer(self, user):
        return self.allowed

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
    import app.models.user  # noqa: F401
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_customer_service_create_and_normalizes_email():
    session = make_session()
    # create role and user
    r = Role(name='sales')
    session.add(r)
    session.flush()

    from app.models.user import User
    user = User(role_id=r.id, user_first_name='S', user_last_name='P', email='s@example.com', phone_number='1000', username='sales1', password_hash='h')
    session.add(user)
    session.flush()

    perm = DummyPerm(allowed=True)
    svc = CustomerService(session, perm)

    current = DummyUser(id=user.id)
    c = svc.create(current, user_sales_id=user.id, customer_first_name='A', customer_last_name='B', email='UPPER@EX.COM', phone_number='123', company_name='Acme')

    assert c.id is not None
    assert c.email == 'upper@ex.com'


def test_customer_service_rejects_duplicate_email():
    session = make_session()
    r = Role(name='sales')
    session.add(r)
    session.flush()

    from app.models.user import User
    user = User(role_id=r.id, user_first_name='S', user_last_name='P', email='s@example.com', phone_number='1000', username='sales1', password_hash='h')
    session.add(user)
    session.flush()

    perm = DummyPerm(allowed=True)
    svc = CustomerService(session, perm)
    current = DummyUser(id=user.id)

    svc.create(current, user_sales_id=user.id, customer_first_name='A', customer_last_name='B', email='dup@e.com', phone_number='123', company_name='Acme')

    with pytest.raises(ValueError):
        svc.create(current, user_sales_id=user.id, customer_first_name='X', customer_last_name='Y', email='dup@e.com', phone_number='124', company_name='Acme2')


def test_customer_service_delete_refuses_if_contract_exists():
    session = make_session()
    r = Role(name='sales')
    session.add(r)
    session.flush()

    from app.models.user import User
    user = User(role_id=r.id, user_first_name='S', user_last_name='P', email='s@example.com', phone_number='1000', username='sales1', password_hash='h')
    session.add(user)
    session.flush()

    perm = DummyPerm(allowed=True)
    svc = CustomerService(session, perm)
    current = DummyUser(id=user.id)

    c = svc.create(current, user_sales_id=user.id, customer_first_name='A', customer_last_name='B', email='a@e.com', phone_number='123', company_name='Acme')

    # create a contract referencing the customer
    from app.models.contract import Contract
    from decimal import Decimal
    ctr = Contract(customer_id=c.id, user_management_id=user.id, total_amount=Decimal('100.00'), balance_due=Decimal('100.00'), signed=False)
    session.add(ctr)
    session.flush()

    with pytest.raises(ValueError):
        svc.delete(current, c.id)
