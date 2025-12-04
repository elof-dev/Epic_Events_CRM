from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.role import Role
from app.services.auth_service import AuthService
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserUpdate
from sqlalchemy.exc import IntegrityError
from typing import Optional


class UserService:
    """Service de gestion des utilisateurs.

   Logique métier :
   - validation des données, vérification des permissions,
   vérification de l'existence du rôle, vérification d'unicité,
    hachage du mot de passe.
    """

    def __init__(self, session, permission_service) -> None:
        self.session = session
        self.repo = UserRepository(session)
        self.perm = permission_service
        self.auth = AuthService()

    def create(self, current_user, **fields) -> User:
        # check permissions
        if not self.perm.user_has_permission(current_user, 'user:create'):
            raise PermissionError('Permission refuseée')
        # validate incoming data via Pydantic (ensures required fields and basic types)
        try:
            validated = UserCreate(**fields).model_dump()
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Données invalides: {messages}") from exc
        # normalize, validate role and uniqueness, hash password
        validated = self._normalize(validated)
        self._ensure_role_exists(validated.get('role_id'))
        self._check_uniqueness(validated)
        self._hash_password_if_present(validated)

        try:
            return self.repo.create(**validated)
        except IntegrityError as exc:
            # race condition or DB-level duplicate; rollback and expose friendly message
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (doublon possible)') from exc

    def update(self, current_user, user_id: int, **fields) -> User:
        if not self.perm.user_has_permission(current_user, 'user:update'):
            raise PermissionError('Permission refusée')
        u = self.repo.get_by_id(user_id)
        if not u:
            raise ValueError('Utilisateur introuvable')
        # validate provided fields via Pydantic (coercion + basic checks)
        try:
            validated = UserUpdate(**fields).model_dump(exclude_none=True)
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Données invalides: {messages}") from exc
        # normalize, validate role (if provided), uniqueness and hash password
        validated = self._normalize(validated)
        if 'role_id' in validated:
            self._ensure_role_exists(validated.get('role_id'))
        self._check_uniqueness(validated, exclude_user_id=u.id)
        self._hash_password_if_present(validated)

        try:
            return self.repo.update(u, **validated)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (doublon possible)') from exc

    # ----- helpers -----
    def _normalize(self, validated: dict) -> dict:
        # trim strings and normalize email/username
        for k in ('username', 'email', 'phone_number'):
            if k in validated and isinstance(validated[k], str):
                validated[k] = validated[k].strip()
        if 'email' in validated and isinstance(validated.get('email'), str):
            validated['email'] = validated['email'].lower()
        return validated

    def _ensure_role_exists(self, role_id: Optional[int]) -> None:
        if not role_id:
            raise ValueError('role_id est requis')
        role = self.session.query(Role).filter(Role.id == role_id).one_or_none()
        if not role:
            raise ValueError('Role introuvable')

    def _check_uniqueness(self, validated: dict, exclude_user_id: Optional[int] = None) -> None:
        from app.models.user import User as UserModel
        if 'username' in validated:
            other = self.repo.get_by_username(validated['username'])
            if other and (exclude_user_id is None or other.id != exclude_user_id):
                raise ValueError('Nom d\'utilisateur déjà utilisé')
        if 'email' in validated and validated.get('email'):
            other = self.session.query(UserModel).filter(UserModel.email == validated.get('email')).one_or_none()
            if other and (exclude_user_id is None or other.id != exclude_user_id):
                raise ValueError('Email déjà utilisé')
        if 'phone_number' in validated and validated.get('phone_number'):
            other = self.session.query(UserModel).filter(UserModel.phone_number == validated.get('phone_number')).one_or_none()
            if other and (exclude_user_id is None or other.id != exclude_user_id):
                raise ValueError('Numéro de téléphone déjà utilisé')
            
    def _hash_password_if_present(self, validated: dict) -> None:
        if 'password' in validated:
            validated['password_hash'] = self.auth.hash_password(validated.pop('password'))

    def delete(self, current_user, user_id: int) -> None:
        if not self.perm.user_has_permission(current_user, 'user:delete'):
            raise PermissionError('Permission refusée')
        if current_user.id == user_id:
            raise ValueError('Vous ne pouvez pas supprimer votre propre compte')
        u = self.repo.get_by_id(user_id)
        if not u:
            raise ValueError('Utilisateur introuvable')
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


    def list_all(self, user) -> list[User]:
        if not self.perm.user_has_permission(user, 'user:read'):
            raise PermissionError('Permission refusée')
        return self.repo.list_all()

    def get_by_id(self, user, user_id: int) -> User:
        if not self.perm.user_has_permission(user, 'user:read'):
            raise PermissionError('Permission refusée')
        return self.repo.get_by_id(user_id)

