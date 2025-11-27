import pytest


def test_user_service_create_update_delete(seeded_session):
    from app.services.permission_service import PermissionService
    from app.services.user_service import UserService
    from app.services.auth_service import AuthService
    from app.models.user import User

    perm = PermissionService(seeded_session)
    service = UserService(seeded_session, perm)
    auth = AuthService()

    # get a management user from seed
    manager = seeded_session.query(User).filter_by(username="manager1").one()
    sales = seeded_session.query(User).filter_by(username="sales1").one()

    # manager can create a user
    new_fields = {
        'user_first_name': 'UT',
        'user_last_name': 'Test',
        'username': 'ut_test_user',
        'email': 'ut_test@example.com',
        'phone_number': '+33000000100',
        'role_name': 'sales',
        'password': 'S3cret!'
    }
    new_u = service.create(manager, **new_fields)
    assert new_u.id is not None
    # password hashed and verifyable
    assert auth.verify_password(new_u.password_hash, 'S3cret!')

    # sales cannot create users
    with pytest.raises(PermissionError):
        service.create(sales, **{**new_fields, 'username': 'bad_create'})

    # manager can update user
    updated = service.update(manager, new_u.id, user_first_name='UT2')
    assert updated.user_first_name == 'UT2'

    # update password
    service.update(manager, new_u.id, password='N3wP@ss')
    reloaded = seeded_session.get(User, new_u.id)
    assert auth.verify_password(reloaded.password_hash, 'N3wP@ss')

    # cannot delete self
    with pytest.raises(ValueError):
        service.delete(manager, manager.id)

    # delete created user
    service.delete(manager, new_u.id)
    assert seeded_session.get(User, new_u.id) is None


def test_user_service_role_resolution(seeded_session):
    from app.services.permission_service import PermissionService
    from app.services.user_service import UserService
    from app.models.user import User

    perm = PermissionService(seeded_session)
    service = UserService(seeded_session, perm)

    manager = seeded_session.query(User).filter_by(username="manager1").one()

    # creating with explicit role_name that doesn't exist should raise
    with pytest.raises(ValueError):
        service.create(manager, user_first_name='X', user_last_name='Y', username='badrole', email='bad@example.com', password='pwd', role_name='no_such_role')
