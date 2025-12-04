from app.repositories.contract_repository import ContractRepository
from pydantic import ValidationError
from app.schemas.contract import ContractCreate, ContractUpdate
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.models.contract import Contract


class ContractService:
    """
    Service de gestion des contrats.

    Fournit :
    - validation via Pydantic avec messages lisibles,
    - vérification des permissions via `permission_service`,
    - normalisation légère des données,
    - gestion des erreurs de contrainte en base (rollback et message utilisateur).
    """

    def __init__(self, session, permission_service) -> None:
        self.session = session
        self.repo = ContractRepository(session)
        self.perm = permission_service

    def create(self, user, **fields) -> Contract:
        if not self.perm.user_has_permission(user, 'contract:create'):
            raise PermissionError("Permission refusée")
        if not fields.get('user_management_id'):
            if getattr(getattr(user, 'role', None), 'name', None) == 'management':
                fields['user_management_id'] = getattr(user, 'id', None)

        try:
            validated = ContractCreate(**fields).model_dump()
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Données invalides : {messages}") from exc

        validated = self._normalize(validated)
        self._ensure_management_user_exists(validated.get('user_management_id'))
        self._ensure_customer_exists(validated.get('customer_id'))


        try:
            return self.repo.create(**validated)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (doublon ou référence invalide possible)') from exc

    def update(self, user, contract_id: int, **fields) -> Contract:
        contract = self.repo.get_by_id(contract_id)
        
        if not self.perm.user_has_permission(user, 'contract:update'):
            raise PermissionError("Permission refusée")
        if not contract:
            raise ValueError("Contrat non trouvé")
        self._ensure_sales_contract_owner(contract, user)

        try:
            validated = ContractUpdate(**fields).model_dump(exclude_none=True)
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Données invalides : {messages}") from exc

        validated = self._normalize(validated)
        if 'user_management_id' in validated:
            self._ensure_management_user_exists(validated.get('user_management_id'))
        if 'customer_id' in validated:
            self._ensure_customer_exists(validated.get('customer_id'))

        try:
            return self.repo.update(contract, **validated)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (doublon ou référence invalide possible)') from exc

    def delete(self, user, contract_id: int) -> None:
        contract = self.repo.get_by_id(contract_id)

        if not self.perm.user_has_permission(user, 'contract:delete'):
            raise PermissionError("Permission refusée")
        if not contract:
            raise ValueError("Contrat non trouvé")


        # refuse deletion if contract has events
        from app.models.event import Event
        events_count = self.session.query(Event).filter(Event.contract_id == contract_id).count()
        if events_count > 0:
            raise ValueError(f"Impossible de supprimer le contrat : référencé par {events_count} évènement(s).")

        try:
            self.repo.delete(contract)
        except Exception:
            self.session.rollback()
            raise

    def list_all(self, user) -> list[Contract]:
        if not self.perm.user_has_permission(user, 'contract:read'):
            raise PermissionError("Utilisateur non autorisé à lire les contrats")
        return self.repo.list_all()


    def list_by_management_user(self, user, user_id: int) -> list[Contract]:
        if not self.perm.user_has_permission(user, 'contract:read'):
            raise PermissionError("Utilisateur non autorisé à lire les contrats")
        return self.repo.list_by_management_user(user_id)

    def list_by_customer_ids(self, user, customer_ids: list) -> list[Contract]:
        if not self.perm.user_has_permission(user, 'contract:read'):
            raise PermissionError("Utilisateur non autorisé à lire les contrats")
        return self.repo.list_by_customer_ids(customer_ids)

    # ---- helpers ----
    def _normalize(self, validated: dict) -> dict:
        # currently no string fields to strip, but keep hook for future
        return validated

    def _ensure_sales_contract_owner(self, contract, user) -> None:
        if getattr(user, 'role', None) and getattr(user.role, 'name', None) == 'sales':
            customer_ids = {c.id for c in getattr(user, 'customers', [])}
            if contract.customer_id not in customer_ids:
                raise PermissionError("Action réservée au commercial propriétaire")

    def _ensure_management_user_exists(self, user_id: Optional[int]) -> None:
        if not user_id:
            raise ValueError('user_management_id est requis')
        from app.models.user import User as UserModel

        u = self.session.query(UserModel).filter(UserModel.id == user_id).one_or_none()
        if not u:
            raise ValueError('Utilisateur gestionnaire introuvable')
    
    def _ensure_customer_exists(self, customer_id: Optional[int]) -> None:
        if not customer_id:
            raise ValueError('customer_id est requis')
        from app.models.customer import Customer as CustomerModel

        c = self.session.query(CustomerModel).filter(CustomerModel.id == customer_id).one_or_none()
        if not c:
            raise ValueError('Client introuvable')
