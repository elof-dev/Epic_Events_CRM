from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.role import Role
from app.services.auth_service import AuthService


class UserService:
    def __init__(self, session, permission_service):
        self.session = session
        self.repo = UserRepository(session)
        self.perm = permission_service
        self.auth = AuthService()

    def list_all(self, user):
        if not self.perm.user_has_permission(user, 'user:read'):
            raise PermissionError('Not allowed to list users')
        return self.repo.list_all()

    def get_by_id(self, user, user_id: int):
        if not self.perm.user_has_permission(user, 'user:read'):
            raise PermissionError('Not allowed to read users')
        return self.session.get(User, user_id)

    def create(self, current_user, **fields):
        # only management may create users
        if not self.perm.user_has_permission(current_user, 'user:create'):
            raise PermissionError('Not allowed to create users')
        if current_user.role.name != 'management':
            raise PermissionError('Only management can create users')
        # require username, password, role_id or role_name
        password = fields.pop('password', None)
        if not password:
            raise ValueError('Password is required')
        role_id = fields.get('role_id')
        role_name = fields.pop('role_name', None)
        if role_name and not role_id:
            role = self.session.query(Role).filter(Role.name == role_name).one_or_none()
            if not role:
                raise ValueError('Role not found')
            fields['role_id'] = role.id

        # hash password
        fields['password_hash'] = self.auth.hash_password(password)
        u = User(**fields)
        self.session.add(u)
        self.session.flush()
        return u

    def update(self, current_user, user_id: int, **fields):
        if not self.perm.user_has_permission(current_user, 'user:update'):
            raise PermissionError('Not allowed to update users')
        if current_user.role.name != 'management':
            raise PermissionError('Only management can update users')
        u = self.session.get(User, user_id)
        if not u:
            raise ValueError('User not found')
        if 'password' in fields:
            u.password_hash = self.auth.hash_password(fields.pop('password'))
        if 'role_name' in fields:
            role = self.session.query(Role).filter(Role.name == fields.pop('role_name')).one_or_none()
            if not role:
                raise ValueError('Role not found')
            u.role_id = role.id
        for k, v in fields.items():
            if hasattr(u, k):
                setattr(u, k, v)
        self.session.flush()
        return u

    def delete(self, current_user, user_id: int):
        if not self.perm.user_has_permission(current_user, 'user:delete'):
            raise PermissionError('Not allowed to delete users')
        if current_user.role.name != 'management':
            raise PermissionError('Only management can delete users')
        if current_user.id == user_id:
            raise ValueError('Cannot delete yourself')
        u = self.session.get(User, user_id)
        if not u:
            raise ValueError('User not found')
        self.session.delete(u)
        self.session.flush()
