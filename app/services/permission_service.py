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


    """

    def __init__(self, session):
        # initialisation du service avec la session DB
        self.session = session

    def user_has_permission(self, user, permission_name: str) -> bool:
        """
        Vérifie si l'utilisateur possède la permission spécifiée.
        Par exemple, "customer:create", "contract:read", etc.
        Retourne True si l'utilisateur a la permission, False sinon.
        """
        # vérifie que l'utilisateur est authentifié
        if not self._is_authenticated(user):
            return False
        # parcourt les permissions associées au rôle de l'utilisateur
        for permission in user.role.permissions:
            # vérifie si le nom de la permission correspond à celui recherché
            if permission.name == permission_name:
                return True
        return False

    def _is_authenticated(self, user) -> bool:
        # vérifie que l'utilisateur n'est pas None et a un ID valide
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
