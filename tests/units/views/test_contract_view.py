import pytest
from types import SimpleNamespace

# Fakes -------------------------------------------------
class FakePerm:
    def __init__(self, perms):
        self.perms = perms
    def user_has_permission(self, user, perm):
        return perm in self.perms

class FakeSession:
    def __init__(self, get_map=None):
        self.get_map = get_map or {}
    def get(self, model, _id):
        return self.get_map.get(_id)

class FakeContractService:
    def __init__(self, return_contract=None, list_result=None):
        self.return_contract = return_contract
        self.list_result = list_result or []
    def create(self, user, **fields):
        return self.return_contract
    def update(self, user, cid, **fields):
        return True
    def delete(self, user, cid):
        return True
    def list_all(self, user):
        return self.list_result
    def list_by_management_user(self, user, uid=None):
        return self.list_result
    def list_by_customer_ids(self, user, ids):
        return self.list_result

# -------------------------------------------------------
from cli.views.contracts import ContractsView

# ---------------- get_contracts_menu_options -----------------
def test_get_contracts_menu_options_basic():
    user = SimpleNamespace(role=SimpleNamespace(name='sales'))
    perm = FakePerm({'contract:read', 'contract:create'})
    view = ContractsView(session=None, perm_service=perm)
    opts = view.get_contracts_menu_options(user)
    assert len(opts) >= 1


# ---------------- create_contract -----------------
def test_create_contract(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name='sales'))
    fake_contract = SimpleNamespace(id=1)
    monkeypatch.setattr('app.services.contract_service.ContractService', lambda s, p: FakeContractService(return_contract=fake_contract))
    answers = iter(['100', 'o', '100', '10'])
    monkeypatch.setattr('click.prompt', lambda *a, **k: next(answers))
    logs = []
    monkeypatch.setattr('click.echo', lambda msg=None, **k: logs.append(msg))
    view = ContractsView(session=SimpleNamespace(), perm_service=FakePerm(set()))
    view.create_contract(user)


# ---------------- update_contract -----------------
def test_update_contract_not_found(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name='sales'))
    session = FakeSession(get_map={})
    view = ContractsView(session=session, perm_service=FakePerm(set()))
    logs = []
    monkeypatch.setattr('click.echo', lambda msg=None, **k: logs.append(msg))
    view.update_contract(user, 1)
    assert any('introuvable' in (m or '') for m in logs)

# ---------------- delete_contract -----------------
def test_delete_contract_not_found(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name='sales'))
    session = FakeSession(get_map={})
    view = ContractsView(session=session, perm_service=FakePerm(set()))
    logs = []
    monkeypatch.setattr('click.echo', lambda msg=None, **k: logs.append(msg))
    view.delete_contract(user, 1)
    assert any('introuvable' in (m or '') for m in logs)

def test_delete_contract_confirm(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name='sales'))
    target = SimpleNamespace(id=1)
    session = FakeSession(get_map={1: target})
    monkeypatch.setattr('app.services.contract_service.ContractService', lambda s, p: FakeContractService())
    monkeypatch.setattr('click.prompt', lambda *a, **k: 'o')
    logs = []
    monkeypatch.setattr('click.echo', lambda msg=None, **k: logs.append(msg))
    view = ContractsView(session=session, perm_service=FakePerm({'contract:delete'}))
    view.delete_contract(user, 1)


# ---------------- list_all_contracts -----------------
def test_list_all_contracts_empty(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name='sales'))
    session = SimpleNamespace()
    view = ContractsView(session=session, perm_service=FakePerm(set()))
    monkeypatch.setattr('app.services.contract_service.ContractService', lambda s, p: FakeContractService(list_result=[]))
    monkeypatch.setattr('cli.helpers.prompt_menu', lambda *a, **k: None)
    logs = []
    monkeypatch.setattr('click.echo', lambda msg=None, **k: logs.append(msg))
    view.list_all_contracts(user)