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
        return self.repo.get_by_id(user_id)

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

        # hash password and delegate to repo
        fields['password_hash'] = self.auth.hash_password(password)
        return self.repo.create(**fields)

    def update(self, current_user, user_id: int, **fields):
        if not self.perm.user_has_permission(current_user, 'user:update'):
            raise PermissionError('Not allowed to update users')
        if current_user.role.name != 'management':
            raise PermissionError('Only management can update users')
        u = self.repo.get_by_id(user_id)
        if not u:
            raise ValueError('User not found')
        if 'password' in fields:
            u.password_hash = self.auth.hash_password(fields.pop('password'))
        if 'role_name' in fields:
            role = self.session.query(Role).filter(Role.name == fields.pop('role_name')).one_or_none()
            if not role:
                raise ValueError('Role not found')
            u.role_id = role.id
        return self.repo.update(u, **fields)

    def delete(self, current_user, user_id: int):
        if not self.perm.user_has_permission(current_user, 'user:delete'):
            raise PermissionError('Not allowed to delete users')
        if current_user.role.name != 'management':
            raise PermissionError('Only management can delete users')
        if current_user.id == user_id:
            raise ValueError('Cannot delete yourself')
        u = self.repo.get_by_id(user_id)
        if not u:
            raise ValueError('User not found')
        # Conservative behaviour: refuse deletion if the user is referenced
        # by contracts, events or customers. Provide a clear error message
        # instead of letting the DB raise IntegrityError and put the
        # session into a dirty state.
        from app.models.contract import Contract
        from app.models.event import Event
        from app.models.customer import Customer

        contracts_count = self.session.query(Contract).filter(Contract.user_management_id == user_id).count()
        events_count = self.session.query(Event).filter(Event.user_support_id == user_id).count()
        customers_count = self.session.query(Customer).filter(Customer.user_sales_id == user_id).count()

        total_refs = contracts_count + events_count + customers_count
        if total_refs > 0:
            parts = []
            if contracts_count:
                parts.append(f"{contracts_count} contrat(s)")
            if events_count:
                parts.append(f"{events_count} évènement(s)")
            if customers_count:
                parts.append(f"{customers_count} client(s)")
            raise ValueError(
                "Impossible de supprimer l'utilisateur : il est référencé par " + ", ".join(parts) + "."
            )

        try:
            self.repo.delete(u)
        except Exception:
            # Ensure session is usable after unexpected DB errors
            self.session.rollback()
            raise
