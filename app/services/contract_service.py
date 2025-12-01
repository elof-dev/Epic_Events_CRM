from app.repositories.contract_repository import ContractRepository
from pydantic import ValidationError
from app.schemas.contract import ContractCreate, ContractUpdate


class ContractService:
    """
    Service de gestion des contrats.

    Rôle : encapsuler la logique applicative liée aux contrats en utilisant
    le dépôt `ContractRepository` pour les opérations CRUD et en s'appuyant
    sur `permission_service` pour vérifier les permissions générales.

    Ce que la classe renvoie :
    - `create(user, **fields)` : retourne l'objet `Contract` nouvellement créé.
    - `update(user, contract_id, **fields)` : retourne l'objet `Contract` mis à jour.
    - `delete(user, contract_id)` : ne retourne rien (supprime le contrat).
    - `list_all(user)` : retourne une liste d'objets `Contract` (tous les contrats accessibles).
    - `list_mine(user)` : alias de compatibilité qui retourne une liste d'objets `Contract` ;
        la logique de filtrage par propriétaire/role doit être effectuée au niveau des vues.
    - `list_by_management_user(user_id)` : retourne une liste d'objets `Contract` gérés
        par un utilisateur donné (utilisé pour les vues administratives).
    - `list_by_customer_ids(customer_ids)` : retourne les contrats associés aux clients
        dont les identifiants sont fournis.
    """

    def __init__(self, session, permission_service):
        self.session = session
        self.repo = ContractRepository(session)
        self.perm = permission_service

    def create(self, user, **fields):
        if not self.perm.can_create_contract(user):
            raise PermissionError("User not allowed to create contracts")
        try:
            validated = ContractCreate(**fields).model_dump()
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Invalid contract data: {messages}") from exc
        return self.repo.create(**validated)

    def update(self, user, contract_id: int, **fields):
        contract = self.repo.get_by_id(contract_id)
        if not contract:
            raise ValueError("Contract not found")
        if not self.perm.can_update_contract(user, contract):
            raise PermissionError("User not allowed to update this contract")
        try:
            validated = ContractUpdate(**fields).model_dump(exclude_none=True)
        except ValidationError as exc:
            errors = exc.errors()
            messages = "; ".join(f"{'.'.join(map(str, e.get('loc', [])))}: {e.get('msg')}" for e in errors)
            raise ValueError(f"Invalid contract data: {messages}") from exc
        return self.repo.update(contract, **validated)

    def delete(self, user, contract_id: int):
        contract = self.repo.get_by_id(contract_id)
        if not contract:
            raise ValueError("Contract not found")
        if not self.perm.can_delete_contract(user):
            raise PermissionError("User not allowed to delete this contract")
        self.repo.delete(contract)

    def list_all(self, user):
        if not self.perm.user_has_permission(user, "contract:read"):
            raise PermissionError("User not allowed to read contracts")
        return self.repo.list_all()

    def list_mine(self, user):
        return self.repo.list_all()

    def list_by_management_user(self, user_id: int):
        return self.repo.list_by_management_user(user_id)

    def list_by_customer_ids(self, customer_ids: list):
        return self.repo.list_by_customer_ids(customer_ids)
