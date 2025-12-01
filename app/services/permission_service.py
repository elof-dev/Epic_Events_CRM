from typing import List
from app.models.permission import Permission


class PermissionService:
    """Service de gestion des permissions.

    Rôle : centraliser les vérifications de permissions basées sur le rôle
    d'un utilisateur. Les permissions sont lues via `user.role.permissions`.

    Ce que la classe renvoie / fournit :
    - `user_has_permission(user, permission_name) -> bool` : indique si l'utilisateur
        possède la permission passée en paramètre (vérification via son rôle).
    - `available_services_for_user(user) -> List[str]` : liste des sections
        applicatives accessibles par l'utilisateur (ex. `manage_users`).
    - Méthodes utilitaires nommées `can_create_*`, `can_update_*`, `can_delete_*`
        qui retournent un booléen indiquant si l'utilisateur a la permission CRUD
        correspondante. 
    """

    def __init__(self, session):
        self.session = session

    def user_has_permission(self, user, permission_name: str) -> bool:
        """
        Vérifie si l'utilisateur possède la permission spécifiée.
        Par exemple, "customer:create", "contract:read", etc.
        Retourne True si l'utilisateur a la permission, False sinon.
        """
        for p in user.role.permissions:
            if p.name == permission_name:
                return True
        return False

    def available_services_for_user(self, user) -> List[str]:
        """
        Retourne la liste des sections applicatives accessibles par l'utilisateur.
        Utilisé pour afficher dynamiquement les options dans l'interface CLI.
        """
        services = []
        if self.user_has_permission(user, "user:read"):
            services.append("manage_users")
        if self.user_has_permission(user, "customer:read"):
            services.append("manage_customers")
        if self.user_has_permission(user, "contract:read"):
            services.append("manage_contracts")
        if self.user_has_permission(user, "event:read"):
            services.append("manage_events")
        return services

    
    def can_create_customer(self, user) -> bool:
        return self.user_has_permission(user, "customer:create")

    def can_update_customer(self, user, customer) -> bool:
        return self.user_has_permission(user, "customer:update")

    def can_delete_customer(self, user, customer) -> bool:
        return self.user_has_permission(user, "customer:delete")

    def can_create_contract(self, user) -> bool:
        return self.user_has_permission(user, "contract:create")

    def can_update_contract(self, user, contract) -> bool:
        return self.user_has_permission(user, "contract:update")

    def can_delete_contract(self, user) -> bool:
        return self.user_has_permission(user, "contract:delete")

    def can_create_event(self, user, contract) -> bool:
        return self.user_has_permission(user, "event:create")

    def can_update_event(self, user, event, fields_to_update: list) -> bool:
        return self.user_has_permission(user, "event:update")

    def can_read_event(self, user, event) -> bool:
        # everyone with event:read can read; sales can read their clients' events
        return self.user_has_permission(user, "event:read")
