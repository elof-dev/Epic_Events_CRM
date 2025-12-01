from app.repositories.customer_repository import CustomerRepository
from pydantic import ValidationError
from app.schemas.customer import CustomerCreate, CustomerUpdate


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
        return self.repo.create(**validated)

    def update(self, user, customer_id: int, **fields):
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        if not self.perm.can_update_customer(user, customer):
            raise PermissionError("User not allowed to update this customer")
        try:
            validated = CustomerUpdate(**fields).model_dump(exclude_none=True)
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Invalid customer data: {messages}") from exc
        return self.repo.update(customer, **validated)

    def delete(self, user, customer_id: int):
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        if not self.perm.can_delete_customer(user, customer):
            raise PermissionError("User not allowed to delete this customer")
        self.repo.delete(customer)

    def list_all(self, user):
        # visibility handled at CLI/service level; here return all if allowed
        if not self.perm.user_has_permission(user, "customer:read"):
            raise PermissionError("User not allowed to read customers")
        return self.repo.list_all()

    def list_mine(self, user):
        return self.repo.list_by_sales_user(user.id)
