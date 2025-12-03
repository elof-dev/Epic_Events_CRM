from types import SimpleNamespace
import pytest
from cli.views import users as users_view

class DummyPermService:
    def __init__(self, perms):
        self.perms = perms
    def user_has_permission(self, user, perm):
        return self.perms.get(perm, False)

def test_get_user_menu_options_gere_permissions():
    user = SimpleNamespace(role=SimpleNamespace(name="management"))
    perm_service = DummyPermService({'user:read': True, 'user:create': True})
    options = users_view.get_user_menu_options(user, perm_service)
    assert len(options) == 3
    assert ('Créer un utilisateur', 'create') in options

    perm_service = DummyPermService({'user:read': False})
    options = users_view.get_user_menu_options(user, perm_service)
    assert options == []

def test_list_all_users_formate_bien(monkeypatch):
    recorded = {}
    class FakeUserService:
        def __init__(self, session, perm_service):
            recorded['init'] = True
        def list_all(self, user):
            return [
                SimpleNamespace(id=1, user_first_name="Alice", user_last_name="Liddell", username="alice"),
            ]
    def fake_prompt_list_or_empty(options, **kwargs):
        recorded['options'] = options
        return None
    monkeypatch.setattr(users_view, "UserService", FakeUserService)
    monkeypatch.setattr(users_view, "prompt_list_or_empty", fake_prompt_list_or_empty)

    users_view.list_all_users(SimpleNamespace(role=SimpleNamespace(name="management")), None, None)
    assert recorded['init'] is True
    assert recorded['options'][0][0].startswith("1: Alice")

def test_display_detail_users_affiche_actions(monkeypatch):
    user_role = SimpleNamespace(name="management")
    current_user = SimpleNamespace(role=user_role)
    target = SimpleNamespace(
        id=1,
        user_first_name="Bob",
        user_last_name="Builder",
        username="bob",
        email="bob@example.com",
        phone_number="000",
        role_id=1,
        role=user_role,
    )
    class FakePermService(DummyPermService):
        pass
    perm_service = FakePermService({'user:update': True, 'user:delete': True})
    session = SimpleNamespace(get=lambda model, pk: target)
    recorded = {}
    def fake_prompt_detail_actions(actions, **kwargs):
        recorded['actions'] = actions
        return None
    monkeypatch.setattr(users_view, "prompt_detail_actions", fake_prompt_detail_actions)
    users_view.display_detail_users(current_user, session, perm_service, target.id)
    assert ('Modifier', 'update') in recorded['actions']
    assert ('Supprimer', 'delete') in recorded['actions']