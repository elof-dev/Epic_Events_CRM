from app.repositories.event_repository import EventRepository
from app.repositories.contract_repository import ContractRepository
from pydantic import ValidationError
from app.schemas.event import EventCreate, EventUpdate
from sqlalchemy.exc import IntegrityError
from typing import Optional


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

    def create(self, user, **fields):
        if not self.perm.user_has_permission(user, "event:create"):
            raise PermissionError("Permission refusée")
        try:
            validated = EventCreate(**fields).model_dump()
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Données invalides : {messages}") from exc

        # utiliser ContractRepository pour vérifier l'existence du contrat et les droits
        contract_repo = ContractRepository(self.session)
        contract = contract_repo.get_by_id(validated["contract_id"])
        if not contract:
            raise ValueError("Contrat non trouvé")

        # vérifier que le client existe et qu'il appartient au contrat
        self._ensure_customer_exists(validated.get("customer_id"))
        if contract.customer_id != validated.get("customer_id"):
            raise ValueError("Le contrat n'est pas lié au client spécifié")

        # les commerciaux ne peuvent créer des événements que pour leurs propres clients
        self._ensure_customer_belongs_to_sales_user(validated.get("customer_id"), user)

        try:
            return self.repo.create(**validated)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (référence invalide possible)') from exc

    def update(self, user, event_id: int, **fields):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Événement non trouvé")
        # contrôles d'appartenance et restrictions de champs selon le rôle :
        role_name = None
        try:
            role_name = getattr(user, 'role').name
        except Exception:
            # tenter de charger le rôle de l'utilisateur depuis la BDD si l'appelant est un DTO sans rôle
            try:
                from app.models.user import User as UserModel

                if getattr(user, 'id', None) is not None:
                    u = self.session.query(UserModel).filter(UserModel.id == user.id).one_or_none()
                    role_name = getattr(u.role, 'name', None) if u else None
            except Exception:
                role_name = None

        keys = list(fields.keys())

        # support : ne peut modifier que les événements qui lui sont assignés et ne peut pas changer `user_support_id`
        if role_name == 'support':
            if getattr(event, 'user_support_id', None) != getattr(user, 'id', None):
                raise PermissionError('Permission refusée: événement non assigné à ce support')
            if 'user_support_id' in keys:
                raise PermissionError('Support ne peut pas réassigner le champ user_support_id')

        # management : peut modifier n'importe quel événement mais uniquement le champ `user_support_id`
        if role_name == 'management':
            allowed = {'user_support_id'}
            if any(k not in allowed for k in keys):
                raise PermissionError('Management ne peut mettre à jour que le champ user_support_id')


        # sinon : vérification générique des permissions pour les autres rôles
        if role_name not in ('support', 'management', 'sales') and not self.perm.can_update_event(user, event, keys):
            raise PermissionError("User not allowed to update this event")

        # valider les champs fournis via Pydantic
        try:
            validated = EventUpdate(**fields).model_dump(exclude_none=True)
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Données invalides : {messages}") from exc

        # s'assurer que le contrat/client référencé (si modifié) existent et sont cohérents
        if 'contract_id' in validated:
            from app.repositories.contract_repository import ContractRepository as CR

            c = CR(self.session).get_by_id(validated.get('contract_id'))
            if not c:
                raise ValueError('Contract not found')

        if 'customer_id' in validated:
            self._ensure_customer_exists(validated.get('customer_id'))

        # si l'un ou les deux sont fournis, s'assurer que contract.customer_id correspond au customer_id
        new_contract_id = validated.get('contract_id', getattr(event, 'contract_id', None))
        new_customer_id = validated.get('customer_id', getattr(event, 'customer_id', None))
        if new_contract_id is not None and new_customer_id is not None:
            cr = ContractRepository(self.session).get_by_id(new_contract_id)
            if not cr or cr.customer_id != new_customer_id:
                raise ValueError('contract_id does not belong to the given customer_id')

        try:
            return self.repo.update(event, **validated)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (référence invalide possible)') from exc

    def delete(self, user, event_id: int):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if not self.perm.user_has_permission(user, "event:delete"):
            raise PermissionError("User not allowed to delete events")
        self.repo.delete(event)

    def list_by_support_user(self, user_id: int):
        return self.repo.list_by_support_user(user_id)

    def list_by_customer(self, customer_id: int):
        return self.repo.list_by_customer(customer_id)



    def list_all(self, user):
        if not self.perm.user_has_permission(user, "event:read"):
            raise PermissionError("User not allowed to read events")
        return self.repo.list_all()

    def list_mine(self, user):
        # conservé pour compatibilité ; les vues doivent gérer rôle/appartenance et appeler des wrappers appropriés
        return []

    # ---- fonctions utilitaires ----
    def _ensure_customer_exists(self, customer_id: Optional[int]) -> None:
        if not customer_id:
            raise ValueError('customer_id est requis')
        from app.models.customer import Customer as CustomerModel

        c = self.session.query(CustomerModel).filter(CustomerModel.id == customer_id).one_or_none()
        if not c:
            raise ValueError('Client introuvable')

    def _ensure_customer_belongs_to_sales_user(self, customer_id: Optional[int], user) -> None:
        # si l'appelant est un commercial, vérifier que le client lui appartient ; autres rôles ignorés
        role_name = None
        try:
            role_name = getattr(user, 'role').name
        except Exception:
            try:
                from app.models.user import User as UserModel

                if getattr(user, 'id', None) is not None:
                    u = self.session.query(UserModel).filter(UserModel.id == user.id).one_or_none()
                    role_name = getattr(u.role, 'name', None) if u else None
            except Exception:
                role_name = None

        if role_name != 'sales':
            return

        from app.models.customer import Customer as CustomerModel

        c = self.session.query(CustomerModel).filter(CustomerModel.id == customer_id).one_or_none()
        if not c:
            raise ValueError('Client introuvable')
        if getattr(c, 'user_sales_id', None) != getattr(user, 'id', None):
            raise PermissionError('Le commercial ne peut créer/modifier que ses clients')
