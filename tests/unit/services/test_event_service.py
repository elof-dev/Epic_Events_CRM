from app.services.event_service import EventService
from app.services.permission_service import PermissionService
from datetime import datetime, timezone


def test_event_service_unit(db_session, role_factory, user_factory, contract_factory):
    perm = PermissionService(db_session)
    svc = EventService(db_session, perm)
    # sales role with event:create
    r_sales = role_factory('sales', permissions=['event:create', 'event:read', 'event:delete'])
    sales = user_factory(username='sales_e', role_name='sales')
    # create a signed contract for this sales' customer
    cust = db_session.query(__import__('app.models.customer', fromlist=['Customer']).Customer).filter_by(user_sales_id=sales.id).one_or_none()
    if not cust:
        # create customer
        from app.models.customer import Customer
        cust = Customer(customer_first_name='Cc', customer_last_name='Ll', email='c@e.com', phone_number=None, company_name='C1', user_sales_id=sales.id)
        db_session.add(cust)
        db_session.flush()
    manager = user_factory(username='mgr_for_event', role_name='management')
    contract = contract_factory(customer=cust, manager=manager, signed=True, contract_number='EV-CTR-1')

    e = svc.create(sales, contract_id=contract.id, event_name='Ev1', event_number='EV-1', start_datetime=datetime.now(timezone.utc), end_datetime=datetime.now(timezone.utc))
    assert e.event_number == 'EV-1'

    # sales cannot create for unsigned contract
    unsigned = contract_factory(customer=cust, manager=manager, signed=False, contract_number='UN-1')
    import pytest
    with pytest.raises(PermissionError):
        svc.create(sales, contract_id=unsigned.id, event_name='Bad', event_number='E-BAD', start_datetime=datetime.now(timezone.utc), end_datetime=datetime.now(timezone.utc))

    # delete
    svc.delete(sales, e.id)
    assert db_session.get(type(e), e.id) is None
