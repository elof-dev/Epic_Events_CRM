import pytest
from app.db.init_db import main as init_main
from app.db.session import create_engine_and_session
from app.models.role import Role
from app.models.user import User
from app.models.customer import Customer
from app.models.contract import Contract
from app.models.event import Event


def test_init_and_seed():
    # init db and seed
    init_main()
    engine, SessionLocal = create_engine_and_session()
    session = SessionLocal()
    try:
        roles = session.query(Role).all()
        users = session.query(User).all()
        customers = session.query(Customer).all()
        contracts = session.query(Contract).all()
        events = session.query(Event).all()

        assert len(roles) == 3
        assert len(users) == 7
        assert len(customers) == 3
        assert len(contracts) == 6
        assert len(events) == 4
    finally:
        session.close()
