def test_permission_checks(seeded_session):
    from app.services.permission_service import PermissionService
    from app.models.user import User

    perm = PermissionService(seeded_session)

    sales1 = seeded_session.query(User).filter_by(username="sales1").one()
    sales2 = seeded_session.query(User).filter_by(username="sales2").one()
    manager1 = seeded_session.query(User).filter_by(username="manager1").one()
    support1 = seeded_session.query(User).filter_by(username="support1").one()

    # sales can create customers
    assert perm.can_create_customer(sales1)
    assert not perm.can_create_customer(manager1)
    assert not perm.can_create_customer(support1)

    # sales can update their own customers only
    from app.models.customer import Customer
    cust_b = seeded_session.query(Customer).filter_by(company_name="Company B").one()
    assert perm.can_update_customer(sales2, cust_b)
    assert not perm.can_update_customer(sales1, cust_b)


def test_customer_service_crud(seeded_session):
    from app.services.permission_service import PermissionService
    from app.services.customer_service import CustomerService
    from app.models.user import User
    from app.models.customer import Customer
    import pytest

    perm = PermissionService(seeded_session)
    service = CustomerService(seeded_session, perm)

    sales2 = seeded_session.query(User).filter_by(username="sales2").one()
    sales1 = seeded_session.query(User).filter_by(username="sales1").one()

    # create new customer as sales2
    new = service.create(sales2, customer_first_name="Test", customer_last_name="User", email="testuser@example.com", phone_number="+33000000099", company_name="Company Test")
    assert isinstance(new, Customer)
    assert new.user_sales_id == sales2.id

    # update by owner allowed
    updated = service.update(sales2, new.id, customer_first_name="Test2")
    assert updated.customer_first_name == "Test2"

    # update by another sales not allowed
    with pytest.raises(PermissionError):
        service.update(sales1, new.id, customer_first_name="Hacker")

    # cleanup
    service.delete(sales2, new.id)
    assert seeded_session.query(Customer).filter_by(id=new.id).one_or_none() is None


def test_contract_service_permissions(seeded_session):
    from app.services.permission_service import PermissionService
    from app.services.contract_service import ContractService
    from app.models.user import User
    from app.models.customer import Customer
    import pytest

    perm = PermissionService(seeded_session)
    service = ContractService(seeded_session, perm)

    manager1 = seeded_session.query(User).filter_by(username="manager1").one()
    sales2 = seeded_session.query(User).filter_by(username="sales2").one()
    cust_b = seeded_session.query(Customer).filter_by(company_name="Company B").one()

    # management can create contract
    c = service.create(manager1, customer_id=cust_b.id, user_management_id=manager1.id, contract_number="TEST-C-1", total_amount=100, balance_due=100, signed=False)
    assert c.contract_number == "TEST-C-1"

    # sales cannot create contract
    with pytest.raises(PermissionError):
        service.create(sales2, customer_id=cust_b.id, user_management_id=manager1.id, contract_number="TEST-C-2", total_amount=100, balance_due=100, signed=False)

    # cleanup
    service.delete(manager1, c.id)


def test_event_service_create_rules(seeded_session):
    from app.services.permission_service import PermissionService
    from app.services.event_service import EventService
    from app.models.user import User
    from app.models.contract import Contract
    import pytest

    perm = PermissionService(seeded_session)
    service = EventService(seeded_session, perm)

    sales3 = seeded_session.query(User).filter_by(username="sales3").one()
    manager2 = seeded_session.query(User).filter_by(username="manager2").one()

    # find a signed contract for sales3's customer
    signed = seeded_session.query(Contract).filter(Contract.user_management_id != None).filter(Contract.signed == True).all()
    # choose a contract that belongs to sales3's customers
    target = None
    for c in signed:
        if c.customer.user_sales_id == sales3.id:
            target = c
            break
    assert target is not None

    # sales3 can create an event for this signed contract
    e = service.create(sales3, contract_id=target.id, event_name="Test Event", event_number="E-TEST-1", start_datetime=target.created_at, end_datetime=target.created_at, location="Test", attendees=1)
    assert e.event_number == "E-TEST-1"

    # sales cannot create event for an unsigned contract
    unsigned = seeded_session.query(Contract).filter(Contract.signed == False).first()
    if unsigned:
        with pytest.raises(PermissionError):
            service.create(sales3, contract_id=unsigned.id, event_name="Bad Event", event_number="E-BAD-1", start_datetime=unsigned.created_at, end_datetime=unsigned.created_at, location="Test", attendees=1)

    # cleanup (deleted by sales who created the event / has event:delete permission)
    service.delete(sales3, e.id)
