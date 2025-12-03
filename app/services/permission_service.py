from typing import List
from app.models.permission import Permission


class PermissionService(Permission):
    """Service de gestion des permissions.

    Rôle : centraliser les vérifications de permissions basées sur le rôle
    d'un utilisateur. Les permissions sont lues via `user.role.permissions`.

    Ce que la classe renvoie / fournit :
    - `user_has_permission(user, permission_name) -> bool` : indique si l'utilisateur
        possède la permission passée en paramètre (vérification via son rôle).
    - `available_services_for_user(user) -> List[str]` : liste des sections
        applicatives accessibles par l'utilisateur (ex. `display_menu_users`).
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
        for permission in user.role.permissions:
            if permission.name == permission_name:
                return True
        return False

    def _is_authenticated(self, user) -> bool:
        """Détection simple d'authentification : un utilisateur est considéré
        authentifié si l'objet `user` existe et possède un `id` non vide.
        """
        return user is not None and getattr(user, 'id', None) is not None

    def available_menus_for_user(self, user) -> List[str]:
        """
        Fonction appelée uniquement pour afficher les grandes sections
        des menus (CLI/views) selon les permissions de l'utilisateur.
        Par exemple, vu qu'il n'y a que le role management qui a la permission
        "user:read", seul ce rôle verra la section de gestion des utilisateurs.
        Il s'agit ici de faire un premeir filtrage global des sections
        """
        menus = []
        if self.user_has_permission(user, "user:read"):
            menus.append("display_menu_users")
        if self.user_has_permission(user, "customer:read"):
            menus.append("display_menu_customers")
        if self.user_has_permission(user, "contract:read"):
            menus.append("display_menu_contracts")
        if self.user_has_permission(user, "event:read"):
            menus.append("display_menu_events")
        return menus

# ------PERMISSIONS POUR LES CLIENTS
    
    def can_read_customer(self, user) -> bool:
        # Règle métier : lecture autorisée pour tout utilisateur authentifié
        return self._is_authenticated(user)
    
    def can_create_customer(self, user) -> bool:
        # Règle métier : seul le rôle 'sales' peut créer un client
        if not self._is_authenticated(user):
            return False
        return getattr(user, 'role', None) is not None and user.role.name == 'sales'

    def can_update_customer(self, user, customer) -> bool:
        # Règle métier : seul le sales propriétaire du client peut le mettre à jour
        if not self._is_authenticated(user):
            return False
        if getattr(user, 'role', None) is None or user.role.name != 'sales':
            return False
        # customer.user_sales_id doit correspondre à l'id de l'utilisateur
        return getattr(customer, 'user_sales_id', None) == user.id

    def can_delete_customer(self, user, customer) -> bool:
        # Même règle que pour update : seul le sales propriétaire peut supprimer
        if not self._is_authenticated(user):
            return False
        if getattr(user, 'role', None) is None or user.role.name != 'sales':
            return False
        return getattr(customer, 'user_sales_id', None) == user.id

# ------PERMISSIONS POUR LES CONTRATS

    def can_read_contract(self, user) -> bool:
        # lecture autorisée pour tout utilisateur authentifié
        return self._is_authenticated(user)

    def can_create_contract(self, user) -> bool:
        # Règle métier : seule la role 'management' peut créer un contrat
        if not self._is_authenticated(user):
            return False
        return getattr(user, 'role', None) is not None and user.role.name == 'management'

    def can_update_contract(self, user, contract) -> bool:
        # Règle métier : seule la role 'management' peut mettre à jour un contrat
        if not self._is_authenticated(user):
            return False
        return getattr(user, 'role', None) is not None and user.role.name == 'management'

    def can_delete_contract(self, user) -> bool:
        # Règle métier : seule la role 'management' peut supprimer un contrat
        if not self._is_authenticated(user):
            return False
        return getattr(user, 'role', None) is not None and user.role.name == 'management'


# ------PERMISSIONS POUR LES ÉVÉNEMENTS

    def can_read_event(self, user) -> bool:
        # lecture autorisée pour tout utilisateur authentifié
        return self._is_authenticated(user)

    def can_create_event(self, user, contract=None) -> bool:
        """
        Vérifie si `user` peut créer un événement. Si `contract` est fourni,
        vérifie que le commercial (`sales`) est bien propriétaire du client
        lié au contrat.
        """
        if not self._is_authenticated(user):
            return False

        if getattr(user, 'role', None) is None:
            return False

        role_name = getattr(user.role, 'name', None)
        # uniquement les commerciaux créent des events pour leurs clients
        if role_name == 'sales':
            # si aucun contrat fourni, autoriser la création (contexte externe
            # doit contrôler la validité du contrat/du client)
            if contract is None:
                return True

            # Si un contrat est fourni, vérifier que le customer du contrat
            # appartient bien au sales (via customer.user_sales_id)
            customer = getattr(contract, 'customer', None)
            if customer is None:
                try:
                    from app.models.customer import Customer as CustomerModel

                    customer = self.session.query(CustomerModel).filter(
                        CustomerModel.id == getattr(contract, 'customer_id', None)
                    ).one_or_none()
                except Exception:
                    customer = None

            if customer is None:
                return False

            return getattr(customer, 'user_sales_id', None) == user.id

        return False

    def can_update_event(self, user, event, fields_to_update: list) -> bool:
        # Règles métier fines :
        # - utilisateur doit être authentifié
        # - 'management' peut mettre à jour uniquement le champ `user_support_id`
        # - 'support' peut mettre à jour tout sauf `user_support_id`, uniquement pour ses événements
        # - 'sales' peut mettre à jour uniquement si c'est le sales propriétaire du client lié
        if not self._is_authenticated(user):
            return False

        if getattr(user, 'role', None) is None:
            return False

        role_name = getattr(user.role, 'name', None)
        if role_name == 'management':
            # management only allowed to change the support assignment
            allowed = {'user_support_id'}
            return all(k in allowed for k in (fields_to_update or []))

        if role_name == 'support':
            # must be assigned to the event and cannot change the assignment
            if getattr(event, 'user_support_id', None) != user.id:
                return False
            if 'user_support_id' in (fields_to_update or []):
                return False
            return True

        if role_name == 'sales':
            # vérifier que le sales est bien le propriétaire du customer lié à l'event
            customer = getattr(event, 'customer', None)
            if customer is None:
                try:
                    from app.models.customer import Customer as CustomerModel

                    customer = self.session.query(CustomerModel).filter(CustomerModel.id == getattr(event, 'customer_id', None)).one_or_none()
                except Exception:
                    customer = None
            if customer is not None:
                return getattr(customer, 'user_sales_id', None) == user.id
            return False

        return False

    def can_delete_event(self, user, event) -> bool:
        # Règle métier : seule la role 'management' peut supprimer un événement
        if not self._is_authenticated(user):
            return False
        return getattr(user, 'role', None) is not None and user.role.name == 'management'
