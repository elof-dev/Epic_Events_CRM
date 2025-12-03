from types import SimpleNamespace
from cli.views import events as event_view

class DummyPermService:
    """Service factice permettant de contrôler les permissions."""
    def __init__(self, perms):
        self.perms = perms
    def user_has_permission(self, user, perm):
        return self.perms.get(perm, False)

def test_get_event_menu_options_varie_selon_role():
    """Confirme que le menu affiche les options attendues pour management/support/sales."""
    support_user = SimpleNamespace(role=SimpleNamespace(name="support"))
    perm_service = DummyPermService({'event:read': True, 'event:create': False})
    options = event_view.get_event_menu_options(support_user, perm_service)
    assert ('Afficher tous les évènements', 'all') in options
    assert ('Mes évènements', 'mine') in options
    management_user = SimpleNamespace(role=SimpleNamespace(name="management"))
    perm_service = DummyPermService({'event:read': True})
    options = event_view.get_event_menu_options(management_user, perm_service)
    assert ('Evènements sans support assigned', 'nosupport') in options

def test_list_all_events_format(monkeypatch):
    """Vérifie que la liste des événements provient bien du service et est formatée."""
    recorded = {}
    class FakeEventService:
        def __init__(self, session, perm_service):
            recorded['init'] = True
        def list_all(self, user):
            return [SimpleNamespace(id=10, event_name="Lancement produit")]
    def fake_prompt_list_or_empty(options, **kwargs):
        recorded['options'] = options
        return None
    monkeypatch.setattr(event_view, "EventService", FakeEventService)
    monkeypatch.setattr(event_view, "prompt_list_or_empty", fake_prompt_list_or_empty)

    event_view.list_all_events(SimpleNamespace(role=SimpleNamespace(name="management")), None, None)
    assert recorded['init'] is True
    assert recorded['options'][0][0].startswith("10: Lancement produit")

def test_display_detail_events_actions(monkeypatch):
    """S’assure que les actions de mise à jour ou suppression apparaissent avec les bonnes permissions."""
    current_user = SimpleNamespace(role=SimpleNamespace(name="support"), id=5)
    event = SimpleNamespace(
        id=3,
        event_name="Demo",
        contract_id=1,
        customer_id=2,
        start_datetime="2025-12-05 10:00",
        end_datetime="2025-12-05 12:00",
        location="Paris",
        attendees=20,
        user_support_id=5
    )
    session = SimpleNamespace(get=lambda model, pk: event)
    perm_service = DummyPermService({'event:update': True, 'event:delete': True})
    recorded = {}
    def fake_prompt_detail_actions(actions, **kwargs):
        recorded['actions'] = actions
        return None
    monkeypatch.setattr(event_view, "prompt_detail_actions", fake_prompt_detail_actions)

    event_view.display_detail_events(current_user, session, perm_service, event.id)
    assert ('Modifier', 'update') in recorded['actions']
    assert ('Supprimer', 'delete') in recorded['actions']