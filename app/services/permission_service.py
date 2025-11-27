from typing import List
from app.models.permission import Permission


class PermissionService:
    def __init__(self, session):
        self.session = session

    def user_has_permission(self, user, permission_name: str) -> bool:
        # load permissions via role
        for p in user.role.permissions:
            if p.name == permission_name:
                return True
        return False

    def available_services_for_user(self, user) -> List[str]:
        services = []
        # map high level services to permission checks
        if self.user_has_permission(user, "user:read"):
            services.append("manage_users")
        if self.user_has_permission(user, "customer:read") or self.user_has_permission(user, "customer:create"):
            services.append("manage_customers")
        if self.user_has_permission(user, "contract:read") or self.user_has_permission(user, "contract:create"):
            services.append("manage_contracts")
        if self.user_has_permission(user, "event:read") or self.user_has_permission(user, "event:create"):
            services.append("manage_events")
        return services

    # Business-level permission checks
    def can_create_customer(self, user) -> bool:
        return user.role.name == "sales" and self.user_has_permission(user, "customer:create")

    def can_update_customer(self, user, customer) -> bool:
        if not self.user_has_permission(user, "customer:update"):
            return False
        if user.role.name == "sales":
            return customer.user_sales_id == user.id
        # management and support do not update customers per rules
        return False

    def can_delete_customer(self, user, customer) -> bool:
        if not self.user_has_permission(user, "customer:delete"):
            return False
        if user.role.name == "sales":
            return customer.user_sales_id == user.id
        return False

    def can_create_contract(self, user) -> bool:
        return user.role.name == "management" and self.user_has_permission(user, "contract:create")

    def can_update_contract(self, user, contract) -> bool:
        if not self.user_has_permission(user, "contract:update"):
            return False
        if user.role.name == "management":
            return True
        if user.role.name == "sales":
            # sales can update contracts linked to their customers
            return contract.customer.user_sales_id == user.id
        return False

    def can_delete_contract(self, user) -> bool:
        if not self.user_has_permission(user, "contract:delete"):
            return False
        return user.role.name == "management"

    def can_create_event(self, user, contract) -> bool:
        # sales may create events for their clients only and only when the contract is signed
        if not self.user_has_permission(user, "event:create"):
            return False
        if user.role.name != "sales":
            return False
        return contract.signed and contract.customer.user_sales_id == user.id

    def can_update_event(self, user, event, fields_to_update: list) -> bool:
        if not self.user_has_permission(user, "event:update"):
            return False
        if user.role.name == "management":
            # management can only update support assignment
            allowed = {"user_support_id"}
            return set(fields_to_update).issubset(allowed)
        if user.role.name == "support":
            # support can update events they are assigned to
            return event.user_support_id == user.id
        return False

    def can_read_event(self, user, event) -> bool:
        # everyone with event:read can read; sales can read their clients' events
        if not self.user_has_permission(user, "event:read"):
            return False
        if user.role.name == "sales":
            return event.customer.user_sales_id == user.id
        return True
