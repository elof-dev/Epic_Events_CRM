from app.services.customer_service import CustomerService
from app.services.permission_service import PermissionService


def test_customer_service_unit(db_session, role_factory, user_factory):
    perm = PermissionService(db_session)
    svc = CustomerService(db_session, perm)
    r_sales = role_factory('sales', permissions=['customer:create', 'customer:update', 'customer:delete', 'customer:read'])
    sales = user_factory(username='sales_u', role_name='sales')

    # create
    new = svc.create(sales, customer_first_name='CF', customer_last_name='CL', email='c@e.com', company_name='CoU')
    assert new.company_name == 'CoU'

    # update by owner
    updated = svc.update(sales, new.id, customer_first_name='X')
    assert updated.customer_first_name == 'X'

    # cannot update by other
    other = user_factory(username='sales_other', role_name='sales')
    import pytest
    with pytest.raises(PermissionError):
        svc.update(other, new.id, customer_first_name='NO')

    # delete by owner
    svc.delete(sales, new.id)
    assert db_session.get(type(new), new.id) is None
