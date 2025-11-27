from app.services.user_service import UserService
from app.services.permission_service import PermissionService


def test_user_service_unit_crud(db_session, role_factory):
    perm = PermissionService(db_session)
    svc = UserService(db_session, perm)
    # create management role with permissions
    r = role_factory('management', permissions=['user:create', 'user:read', 'user:update', 'user:delete'])
    # create manager user directly
    from app.models.user import User
    manager = User(user_first_name='M', user_last_name='G', email='m@g.com', phone_number=None, username='mgr_local', password_hash='x', role_id=r.id)
    db_session.add(manager)
    db_session.flush()

    # create new user
    new = svc.create(manager, user_first_name='A', user_last_name='B', username='u_unit', email='u@example.com', password='pw', role_name='sales')
    assert new.username == 'u_unit'

    # update
    updated = svc.update(manager, new.id, user_first_name='A2')
    assert updated.user_first_name == 'A2'

    # delete
    svc.delete(manager, new.id)
    assert db_session.get(User, new.id) is None

    # cannot create without permission: create a non-management user context
    r2 = role_factory('sales', permissions=[])
    user_no_perm = User(user_first_name='S', user_last_name='L', email='s@e.com', phone_number=None, username='sales_ctx', password_hash='x', role_id=r2.id)
    db_session.add(user_no_perm)
    db_session.flush()
    import pytest
    with pytest.raises(PermissionError):
        svc.create(user_no_perm, user_first_name='X', user_last_name='Y', username='x1', email='x1@example.com', password='p', role_name='sales')
