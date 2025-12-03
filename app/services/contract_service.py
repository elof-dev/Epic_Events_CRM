from app.repositories.contract_repository import ContractRepository
from pydantic import ValidationError
from app.schemas.contract import ContractCreate, ContractUpdate
from sqlalchemy.exc import IntegrityError
from typing import Optional


class ContractService:
    """
    Service de gestion des contrats.

    Fournit :
    - validation via Pydantic avec messages lisibles,
    - vérification des permissions via `permission_service`,
    - normalisation légère des données,
    - gestion des erreurs de contrainte en base (rollback et message utilisateur).
    """

    def __init__(self, session, permission_service):
        self.session = session
        self.repo = ContractRepository(session)
        self.perm = permission_service

    def create(self, user, **fields):
        if not self.perm.can_create_contract(user):
            raise PermissionError("Permission refusée")
        # injection si l'appelant est du rôle 'management'
        if not fields.get('user_management_id'):
            is_management = False
            if getattr(user, 'role', None) and getattr(user.role, 'name', None) == 'management':
                is_management = True
            else:
                # si `user` est un DTO sans rôle, tenter de charger l'utilisateur en base
                try:
                    from app.models.user import User as UserModel

                    if getattr(user, 'id', None) is not None:
                        u = self.session.query(UserModel).filter(UserModel.id == user.id).one_or_none()
                        if u and getattr(u.role, 'name', None) == 'management':
                            is_management = True
                except Exception:
                    is_management = False

            if is_management:
                fields['user_management_id'] = user.id

        try:
            validated = ContractCreate(**fields).model_dump()
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Données invalides : {messages}") from exc

        validated = self._normalize(validated)

        # assignation par défaut du manager lorsque l'appelant est du rôle 'management' et n'a pas fourni d'ID
        # (historique) : le champ doit maintenant être déjà injecté dans `fields` si nécessaire
        # s'assurer que l'utilisateur gestionnaire référencé existe
        self._ensure_management_user_exists(validated.get('user_management_id'))
        # vérifier que le client existe
        self._ensure_customer_exists(validated.get('customer_id'))

        try:
            return self.repo.create(**validated)
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError('Violation de contrainte en base (doublon ou référence invalide possible)') from exc

    def update(self, user, contract_id: int, **fields):
        contract = self.repo.get_by_id(contract_id)
        
        if not self.perm.can_update_contract(user, contract):
            raise PermissionError("Permission refusée")
        if not contract:
            raise ValueError("Contrat non trouvé")
        
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

    def delete(self, user, contract_id: int):
        contract = self.repo.get_by_id(contract_id)

        if not self.perm.can_delete_contract(user, contract):
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

    def list_all(self, user):
        if not self.perm.can_read_contract(user):
            raise PermissionError("Utilisateur non autorisé à lire les contrats")
        return self.repo.list_all()


    def list_by_management_user(self, user, user_id: int):
        if not self.perm.can_read_contract(user):
            raise PermissionError("Utilisateur non autorisé à lire les contrats")
        return self.repo.list_by_management_user(user_id)

    def list_by_customer_ids(self, user, customer_ids: list):
        if not self.perm.can_read_contract(user):
            raise PermissionError("Utilisateur non autorisé à lire les contrats")
        return self.repo.list_by_customer_ids(customer_ids)

    # ---- helpers ----
    def _normalize(self, validated: dict) -> dict:
        # currently no string fields to strip, but keep hook for future
        return validated

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
