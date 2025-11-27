from app.services.contract_service import ContractService
from app.services.permission_service import PermissionService


def test_contract_service_unit(db_session, role_factory, user_factory, customer_factory):
    perm = PermissionService(db_session)
    svc = ContractService(db_session, perm)
    r_mgmt = role_factory('management', permissions=['contract:create', 'contract:update', 'contract:delete', 'contract:read'])
    manager = user_factory(username='mgr_u', role_name='management')
    cust = customer_factory(sales_user=None, company_name='CForContract')

    # create
    c = svc.create(manager, customer_id=cust.id, user_management_id=manager.id, contract_number='CTR-1', total_amount=10, balance_due=10, signed=False)
    assert c.contract_number == 'CTR-1'

    # update
    updated = svc.update(manager, c.id, total_amount=20)
    assert updated.total_amount == 20

    # delete
    svc.delete(manager, c.id)
    assert db_session.get(type(c), c.id) is None
