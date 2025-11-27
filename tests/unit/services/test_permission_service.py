from app.services.permission_service import PermissionService


def test_permission_checks_basic(db_session, role_factory, user_factory):
    perm_svc = PermissionService(db_session)
    # create permissions and roles
    r_sales = role_factory('sales', permissions=['customer:create', 'customer:update'])
    r_mgmt = role_factory('management', permissions=['contract:create', 'user:read', 'user:create', 'user:update', 'user:delete', 'event:read', 'event:create'])
    sales_user = user_factory(username='s1', role_name='sales')
    mgmt_user = user_factory(username='m1', role_name='management')

    assert perm_svc.can_create_customer(sales_user) is True
    assert perm_svc.can_create_customer(mgmt_user) is False
    # can_update_customer for sales on their customer
    from app.models.customer import Customer
    c = Customer(customer_first_name='X', customer_last_name='Y', email='x@y.com', phone_number=None, company_name='Co', user_sales_id=sales_user.id)
    db_session.add(c)
    db_session.flush()
    assert perm_svc.can_update_customer(sales_user, c)
    assert not perm_svc.can_update_customer(mgmt_user, c)
