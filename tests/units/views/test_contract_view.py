from types import SimpleNamespace
from cli.views import contracts as contract_view

class DummyPermService:
    """Permet de contrôler facilement les permissions retournées."""
    def __init__(self, perms):
        self.perms = perms

    def user_has_permission(self, user, perm):
        return self.perms.get(perm, False)

def test_get_contracts_menu_options_management():
    """Vérifie que le menu contract affiche toutes les entrées avec les permissions adéquates."""
    user = SimpleNamespace(role=SimpleNamespace(name="management"))
    perm_service = DummyPermService({
        'contract:read': True,
        'contract:create': True,
    })
    options = contract_view.get_contracts_menu_options(user, perm_service)
    labels = [label for label, _ in options]
    assert 'Créer un contrat' in labels
    assert 'Afficher tous les contrats' in labels
    assert 'Mes contrats' in labels

def test_list_all_contracts_format(monkeypatch):
    """S’assure que la liste formatée contient bien les contrats provenant du service."""
    recorded = {}
    class FakeContractService:
        def __init__(self, session, perm_service):
            recorded['initialized'] = True
        def list_all(self, user):
            customer = SimpleNamespace(company_name="Acme Corp")
            return [SimpleNamespace(id=42, customer=customer)]
    def fake_prompt_list_or_empty(options, **kwargs):
        recorded['options'] = options
        return None
    monkeypatch.setattr(contract_view, "ContractService", FakeContractService)
    monkeypatch.setattr(contract_view, "prompt_list_or_empty", fake_prompt_list_or_empty)

    contract_view.list_all_contracts(SimpleNamespace(role=SimpleNamespace(name="management")), None, None)
    assert recorded['initialized'] is True
    assert recorded['options'][0][0].startswith("42: lié au client Acme Corp")

def test_display_detail_contracts_actions(monkeypatch):
    """S’assure que les actions de mise à jour/suppression apparaissent avec les bonnes permissions."""
    user = SimpleNamespace(role=SimpleNamespace(name="sales"), id=1, customers=[SimpleNamespace(id=100)])
    contract = SimpleNamespace(
        id=7,
        total_amount=1000,
        balance_due=200,
        signed=False,
        customer_id=100,
        user_management_id=5,
        customer=SimpleNamespace(company_name="Acme"),
    )
    session = SimpleNamespace(get=lambda model, pk: contract)
    perm_service = DummyPermService({'contract:update': True, 'contract:delete': True})
    recorded = {}
    def fake_prompt_detail_actions(actions, **kwargs):
        recorded['actions'] = actions
        return None
    monkeypatch.setattr(contract_view, "prompt_detail_actions", fake_prompt_detail_actions)

    contract_view.display_detail_contracts(user, session, perm_service, contract.id)
    assert ('Modifier', 'update') in recorded['actions']
    assert ('Supprimer', 'delete') in recorded['actions']