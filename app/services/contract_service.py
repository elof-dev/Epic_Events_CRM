from app.repositories.contract_repository import ContractRepository


class ContractService:
    def __init__(self, session, permission_service):
        self.session = session
        self.repo = ContractRepository(session)
        self.perm = permission_service

    def create(self, user, **fields):
        if not self.perm.can_create_contract(user):
            raise PermissionError("User not allowed to create contracts")
        return self.repo.create(**fields)

    def update(self, user, contract_id: int, **fields):
        contract = self.repo.get_by_id(contract_id)
        if not contract:
            raise ValueError("Contract not found")
        if not self.perm.can_update_contract(user, contract):
            raise PermissionError("User not allowed to update this contract")
        return self.repo.update(contract, **fields)

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
        if user.role.name == "management":
            return self.repo.list_by_management_user(user.id)
        if user.role.name == "sales":
            # find contracts for this sales user's customers
            customer_ids = [c.id for c in user.customers]
            return self.repo.list_by_customer_ids(customer_ids)
        if user.role.name == "support":
            # support sees contracts linked to events they manage (handled at higher level)
            return []
        return []
