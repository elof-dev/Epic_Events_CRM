from app.repositories.event_repository import EventRepository
from app.repositories.contract_repository import ContractRepository
from pydantic import ValidationError
from app.schemas.event import EventCreate, EventUpdate


class EventService:
    """Service de gestion des événements.

    Rôle : exposer la logique applicative liée aux événements (événements liés
    à des contrats/clients) en utilisant `EventRepository` pour les opérations
    de persistance et `permission_service` pour vérifier les permissions
    générales. Cette couche prépare et valide les données (par ex. vérifie
    l'existence du contrat lors de la création) mais ne réalise pas les
    vérifications fines d'appartenance qui sont gérées par la couche CLI/views.

    Ce que la classe renvoie :
    - `create(user, **fields)` : retourne l'objet `Event` nouvellement créé (doit
            contenir `contract_id` dans `fields`).
    - `update(user, event_id, **fields)` : retourne l'objet `Event` mis à jour.
    - `delete(user, event_id)` : ne retourne rien (supprime l'événement).
    - `list_all(user)` : retourne une liste d'objets `Event` (tous les événements accessibles).
    - `list_by_support_user(user_id)` : retourne la liste des événements assignés
            à un utilisateur support.
    - `list_by_customer(customer_id)` : retourne la liste des événements d'un client.

    Remarques :
    - Les contrôles d'appartenance (par ex. ``sales`` ne pouvant modifier que
        ses propres clients) doivent être effectués par les vues avant d'appeler
        ces méthodes.
    - Les méthodes lèvent `PermissionError` ou `ValueError` selon les cas.
    """

    def __init__(self, session, permission_service):
        self.session = session
        self.repo = EventRepository(session)
        self.perm = permission_service

    def list_by_support_user(self, user_id: int):
        return self.repo.list_by_support_user(user_id)

    def list_by_customer(self, customer_id: int):
        return self.repo.list_by_customer(customer_id)

    def create(self, user, **fields):
        # validate incoming fields via Pydantic first (coercion + validation)
        try:
            validated = EventCreate(**fields).model_dump()
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Invalid event data: {messages}") from exc

        # use ContractRepository to verify contract existence/rights
        contract_repo = ContractRepository(self.session)
        contract = contract_repo.get_by_id(validated["contract_id"])
        if not contract:
            raise ValueError("Contract not found")
        if not self.perm.can_create_event(user, contract):
            raise PermissionError("User not allowed to create this event")
        # set customer_id from contract if not provided
        validated.setdefault("customer_id", contract.customer_id)
        return self.repo.create(**validated)

    def update(self, user, event_id: int, **fields):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if not self.perm.can_update_event(user, event, list(fields.keys())):
            raise PermissionError("User not allowed to update this event")
        # validate any provided fields via Pydantic
        try:
            validated = EventUpdate(**fields).model_dump(exclude_none=True)
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Invalid event data: {messages}") from exc

        # Note: role-based ownership/field restrictions are enforced at the view layer.
        return self.repo.update(event, **validated)

    def delete(self, user, event_id: int):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if not self.perm.user_has_permission(user, "event:delete"):
            raise PermissionError("User not allowed to delete events")
        self.repo.delete(event)

    def list_all(self, user):
        if not self.perm.user_has_permission(user, "event:read"):
            raise PermissionError("User not allowed to read events")
        return self.repo.list_all()

    def list_mine(self, user):
        # kept for compatibility; views should handle role/ownership and call appropriate wrappers
        return []
