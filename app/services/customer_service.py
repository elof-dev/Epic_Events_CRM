from app.repositories.customer_repository import CustomerRepository
from pydantic import ValidationError
from app.schemas.customer import CustomerCreate, CustomerUpdate
from sqlalchemy.exc import IntegrityError
from typing import Optional




class CustomerService:
    """Service de gestion des clients.

    Rôle : fournir une couche applicative entre les vues (CLI) et le dépôt
    `CustomerRepository`, en vérifiant les permissions générales via
    `permission_service` avant d'effectuer des opérations CRUD.

    Ce que la classe renvoie :
    - `create(user, **fields)` : retourne l'objet `Customer` nouvellement créé.
    - `update(user, customer_id, **fields)` : retourne l'objet `Customer` mis à jour.
    - `delete(user, customer_id)` : ne retourne rien (supprime le client).
    - `list_all(user)` : retourne une liste d'objets `Customer` (tous les clients accessibles).
    - `list_mine(user)` : retourne la liste des clients assignés au commercial (`user.id`).

    Remarques :
    - Cette classe vérifie les permissions générales (CRUD) mais ne gère pas
        l'assignation ou les vérifications fines d'appartenance ; ces règles
        doivent être appliquées par la couche de présentation (CLI/views).
    """

    def __init__(self, session, permission_service):
        self.session = session
        self.repo = CustomerRepository(session)
        self.perm = permission_service

    def create(self, user, **fields):
        if not self.perm.can_create_customer(user):
            raise PermissionError("User not allowed to create customers")
        # creation logic: service does not enforce ownership here; views handle ownership assignment
        try:
            validated = CustomerCreate(**fields).model_dump()
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Invalid customer data: {messages}") from exc
        # normalize and pre-checks
        validated = self._normalize(validated)
        # assign ownership by default when the caller is a sales user and no owner provided
        if not validated.get('user_sales_id') and getattr(user, 'role', None) and getattr(user.role, 'name', None) == 'sales':
            validated['user_sales_id'] = user.id
        self._ensure_sales_user_exists(validated.get('user_sales_id'))
        self._check_uniqueness(validated)

        try:
            return self.repo.create(**validated)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (doublon possible)') from exc

    def update(self, user, customer_id: int, **fields):
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        # ownership check: allow update if owner or has explicit permission
        if getattr(customer, 'user_sales_id', None) != getattr(user, 'id', None) and not self.perm.can_update_customer(user, customer):
            raise PermissionError("User not allowed to update this customer")
        try:
            validated = CustomerUpdate(**fields).model_dump(exclude_none=True)
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Invalid customer data: {messages}") from exc
        # normalize and pre-checks
        validated = self._normalize(validated)
        if 'user_sales_id' in validated:
            self._ensure_sales_user_exists(validated.get('user_sales_id'))
        self._check_uniqueness(validated, exclude_customer_id=customer.id)

        try:
            return self.repo.update(customer, **validated)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (doublon possible)') from exc

    def delete(self, user, customer_id: int):
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        # ownership check: only owner or privileged user can delete
        if getattr(customer, 'user_sales_id', None) != getattr(user, 'id', None) and not self.perm.can_delete_customer(user, customer):
            raise PermissionError("User not allowed to delete this customer")

        # refuse deletion if customer has contracts or events
        from app.models.contract import Contract
        from app.models.event import Event

        contracts_count = self.session.query(Contract).filter(Contract.customer_id == customer_id).count()
        events_count = self.session.query(Event).filter(Event.customer_id == customer_id).count()
        total_refs = contracts_count + events_count
        if total_refs > 0:
            parts = []
            if contracts_count:
                parts.append(f"{contracts_count} contrat(s)")
            if events_count:
                parts.append(f"{events_count} évènement(s)")
            raise ValueError("Impossible de supprimer le client : il est référencé par " + ", ".join(parts) + ".")

        try:
            self.repo.delete(customer)
        except Exception:
            self.session.rollback()
            raise

    def list_all(self, user):
        # visibility handled at CLI/service level; here return all if allowed
        if not self.perm.user_has_permission(user, "customer:read"):
            raise PermissionError("User not allowed to read customers")
        return self.repo.list_all()

    def list_mine(self, user):
        return self.repo.list_by_sales_user(user.id)

    # ---- helpers ----
    def _normalize(self, validated: dict) -> dict:
        for k in ('email', 'phone_number'):
            if k in validated and isinstance(validated[k], str):
                validated[k] = validated[k].strip()
        if 'email' in validated and isinstance(validated.get('email'), str):
            validated['email'] = validated['email'].lower()
        return validated

    def _ensure_sales_user_exists(self, user_id: Optional[int]) -> None:
        if not user_id:
            raise ValueError('user_sales_id est requis')
        from app.models.user import User as UserModel

        u = self.session.query(UserModel).filter(UserModel.id == user_id).one_or_none()
        if not u:
            raise ValueError('Utilisateur commercial (sales) introuvable')

    def _check_uniqueness(self, validated: dict, exclude_customer_id: Optional[int] = None) -> None:
        from app.models.customer import Customer as CustomerModel
        if 'email' in validated and validated.get('email'):
            other = self.session.query(CustomerModel).filter(CustomerModel.email == validated.get('email')).one_or_none()
            if other and (exclude_customer_id is None or other.id != exclude_customer_id):
                raise ValueError('Email déjà utilisé')
        if 'phone_number' in validated and validated.get('phone_number'):
            other = self.session.query(CustomerModel).filter(CustomerModel.phone_number == validated.get('phone_number')).one_or_none()
            if other and (exclude_customer_id is None or other.id != exclude_customer_id):
                raise ValueError('Numéro de téléphone déjà utilisé')
        if 'company_name' in validated and validated.get('company_name'):
            other = self.session.query(CustomerModel).filter(CustomerModel.company_name == validated.get('company_name')).one_or_none()
            if other and (exclude_customer_id is None or other.id != exclude_customer_id):
                raise ValueError('Nom de société déjà utilisé')
