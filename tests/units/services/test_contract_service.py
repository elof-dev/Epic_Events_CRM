from types import SimpleNamespace
import pytest
from app.services import contract_service

class DummyPermService:
    """Permets de contrôler rapidement les permissions retournées."""
    def __init__(self, perms):
        self.perms = perms
    def user_has_permission(self, user, perm):
        return self.perms.get(perm, False)

class DummyContractRepository:
    """Simule les opérations CRUD basiques du dépôt de contrats."""
    def __init__(self, session):
        self.session = session
        self.created = []
        self.updated = []
        self.deleted = []
        self.with_events = False
        self.contract = SimpleNamespace(id=1, customer_id=10, user_management_id=2)
    def create(self, **kwargs):
        self.created.append(kwargs)
        return SimpleNamespace(id=1, **kwargs)
    def get_by_id(self, contract_id):
        return self.contract if contract_id == self.contract.id else None
    def update(self, contract, **kwargs):
        self.updated.append((contract, kwargs))
        updated = SimpleNamespace(id=contract.id, **kwargs)
        return updated
    def delete(self, contract):
        self.deleted.append(contract.id)
    def list_all(self):
        return [SimpleNamespace(id=1)]
    def list_by_management_user(self, user_id):
        return [SimpleNamespace(id=2, user_management_id=user_id)]
    def list_by_customer_ids(self, customer_ids):
        return [SimpleNamespace(customer_id=cid) for cid in customer_ids]

class DummyContractCreate:
    """Remplace ContractCreate pour les tests."""
    def __init__(self, **data):
        self._data = data
    def model_dump(self):
        return dict(self._data)

class DummyContractUpdate(DummyContractCreate):
    def model_dump(self, exclude_none=False):
        return {k: v for k, v in self._data.items() if v is not None}

class DummySession:
    """Requêtes factices pour `_ensure_*` et suppression d’évènements."""
    def __init__(self, events=0):
        self.events = events
        self.rolled_back = False
    def rollback(self):
        self.rolled_back = True
    def query(self, model):
        class DummyQuery:
            def __init__(self, count):
                self._count = count
            def filter(self, *args, **kwargs):
                return self
            def one_or_none(self):
                return SimpleNamespace(id=2, role=SimpleNamespace(name="management"))
            def count(self):
                return self._count
        if getattr(model, "__name__", "") == "Event":
            return DummyQuery(self.events)
        return DummyQuery(0)

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """Injecte des dépendances factices pour isoler la logique métier."""
    monkeypatch.setattr(contract_service, "ContractRepository", DummyContractRepository)
    monkeypatch.setattr(contract_service, "ContractCreate", DummyContractCreate)
    monkeypatch.setattr(contract_service, "ContractUpdate", DummyContractUpdate)

def make_service(session, perms):
    """Construit l'instance du service avec un permission_service factice."""
    perm_service = DummyPermService(perms)
    return contract_service.ContractService(session, perm_service)

def test_create_requiert_permission():
    """Doit refuser la création sans `contract:create`."""
    session = DummySession()
    service = make_service(session, {'contract:create': False})
    user = SimpleNamespace(role=SimpleNamespace(name="sales"), id=1)
    with pytest.raises(PermissionError):
        service.create(user, customer_id=1, total_amount=10)

def test_create_injecte_user_management_quand_management(monkeypatch):
    """Injecte automatiquement `user_management_id` quand l’appelant est management."""
    session = DummySession()
    service = make_service(session, {'contract:create': True})
    service._ensure_management_user_exists = lambda user_id: None
    service._ensure_customer_exists = lambda customer_id: None
    management_user = SimpleNamespace(role=SimpleNamespace(name="management"), id=42)
    contract = service.create(management_user, customer_id=10, total_amount=100)
    assert contract.user_management_id == management_user.id
    assert service.repo.created[-1]['user_management_id'] == 42

def test_update_verifie_permissions_et_proprietaire():
    """Un commercial ne peut modifier que ses contrats."""
    session = DummySession()
    service = make_service(session, {'contract:update': True})
    contract = service.repo.contract
    contract.customer_id = 99
    contract.user_management_id = 2
    sales_user = SimpleNamespace(id=3, role=SimpleNamespace(name="sales"), customers=[SimpleNamespace(id=1)])
    with pytest.raises(PermissionError):
        service.update(sales_user, contract.id, total_amount=200)

def test_delete_refuse_si_evenements_associes(monkeypatch):
    """Interdit la suppression lorsqu’un évènement référence le contrat."""
    session = DummySession(events=2)
    service = make_service(session, {'contract:delete': True})
    service._ensure_management_user_exists = lambda user_id: None
    contract = service.repo.contract
    with pytest.raises(ValueError, match="référencé"):
        service.delete(SimpleNamespace(id=5), contract.id)

def test_list_all_ne_marche_pas_sans_permission():
    """Liste des contrats accessible uniquement avec `contract:read`."""
    session = DummySession()
    service = make_service(session, {'contract:read': False})
    with pytest.raises(PermissionError):
        service.list_all(SimpleNamespace(id=1))

def test_list_all_retourne_de_la_repo():
    """Retourne la liste fournie par le dépôt quand la permission est accordée."""
    session = DummySession()
    service = make_service(session, {'contract:read': True})
    result = service.list_all(SimpleNamespace(id=1))
    assert result and result[0].id == 1