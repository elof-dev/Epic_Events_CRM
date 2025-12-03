from types import SimpleNamespace
import pytest
from cli.views import customers as customer_view

class DummyPermService:
    """Service factice pour simuler les permissions disponibles."""
    def __init__(self, perms):
        self.perms = perms
    def user_has_permission(self, user, perm):
        return self.perms.get(perm, False)

def test_get_customer_menu_options_sales(monkeypatch):
    """Vérifie que le menu affiche les options attendues pour un sales."""
    user = SimpleNamespace(role=SimpleNamespace(name="sales"), id=10)
    perm_service = DummyPermService({'customer:read': True, 'customer:create': True})
    options = customer_view.get_customer_menu_options(user, perm_service)
    assert ('Afficher tous les clients', 'list_all') in options
    assert ('Mes clients', 'mine') in options
    assert ('Créer un client', 'create') in options

def test_list_all_customers_format(monkeypatch):
    """Confirme que la liste des clients renvoyée est formatée correctement."""
    recorded = {}
    class FakeCustomerService:
        def __init__(self, session, perm_service):
            recorded['init'] = True
        def list_all(self, user):
            return [SimpleNamespace(id=1, customer_first_name="Alice", customer_last_name="Wonder", company_name="Acme")]
    def fake_prompt_list_or_empty(options, **kwargs):
        recorded['options'] = options
        return None
    monkeypatch.setattr(customer_view, "CustomerService", FakeCustomerService)
    monkeypatch.setattr(customer_view, "prompt_list_or_empty", fake_prompt_list_or_empty)
    customer_view.list_all_customers(SimpleNamespace(role=SimpleNamespace(name="management")), None, None)
    assert recorded['init'] is True
    assert recorded['options'][0][0].startswith("1: Alice")

def test_display_detail_customers_actions(monkeypatch):
    """Assure que les actions sont proposées quand l'utilisateur peut modifier/supprimer."""
    user_role = SimpleNamespace(name="sales")
    current_user = SimpleNamespace(role=user_role, id=42)
    customer = SimpleNamespace(
        id=7,
        customer_first_name="Bob",
        customer_last_name="Builder",
        company_name="Builders Inc",
        email="bob@example.com",
        user_sales_id=42
    )
    session = SimpleNamespace(get=lambda model, pk: customer)
    perm_service = DummyPermService({'customer:update': True, 'customer:delete': True})
    recorded = {}
    def fake_prompt_detail_actions(actions, **kwargs):
        recorded['actions'] = actions
        return None
    monkeypatch.setattr(customer_view, "prompt_detail_actions", fake_prompt_detail_actions)
    customer_view.display_detail_customers(current_user, session, perm_service, customer.id)
    assert ('Modifier', 'update') in recorded['actions']
    assert ('Supprimer', 'delete') in recorded['actions']