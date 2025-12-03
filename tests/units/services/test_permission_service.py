from types import SimpleNamespace
import pytest
from app.services.permission_service import PermissionService

def make_permission(name):
    return SimpleNamespace(name=name)

def make_user(role, user_id=1):
    return SimpleNamespace(id=user_id, role=role)

def test_user_has_permission_valide():
    """Confirme que l’utilisateur authentifié possède bien la permission attendue."""
    role = SimpleNamespace(permissions=[make_permission("customer:read")])
    user = make_user(role)
    service = PermissionService(session=None)
    assert service.user_has_permission(user, "customer:read") is True

def test_user_has_permission_false_si_non_authentifie():
    """Retourne False quand l’objet user est vide ou sans id."""
    service = PermissionService(session=None)
    assert service.user_has_permission(SimpleNamespace(role=SimpleNamespace(permissions=[]), id=None), "user:read") is False
    assert service.user_has_permission(None, "user:read") is False

def test_available_menus_filtre_bien_selon_permissions():
    """Liste uniquement les sections correspondant aux permissions accordées."""
    role = SimpleNamespace(
        permissions=[
            make_permission("user:read"),
            make_permission("contract:read"),
        ]
    )
    user = make_user(role)
    service = PermissionService(session=None)
    menus = service.available_menus_for_user(user)
    assert "display_menu_users" in menus
    assert "display_menu_contracts" in menus
    assert "display_menu_customers" not in menus
    assert "display_menu_events" not in menus