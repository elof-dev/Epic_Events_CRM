from types import SimpleNamespace
import pytest
from app.services import event_service

class DummyPermService:
    """Contrôle manuel des permissions demandées dans les tests."""
    def __init__(self, perms):
        self.perms = perms
    def user_has_permission(self, user, perm):
        return self.perms.get(perm, False)

class DummyEventRepository:
    """Contrôle des appels CRUD exécutés par le service."""
    def __init__(self, session):
        self.session = session
        self.events = {1: SimpleNamespace(id=1, user_support_id=5, contract_id=1, customer_id=10)}
        self.deleted = []
        self.updated = []
    def create(self, **kwargs):
        event = SimpleNamespace(id=2, **kwargs)
        self.events[event.id] = event
        return event
    def get_by_id(self, event_id):
        return self.events.get(event_id)
    def update(self, event, **kwargs):
        self.updated.append((event, kwargs))
        updated = SimpleNamespace(id=event.id, **kwargs)
        self.events[event.id] = updated
        return updated
    def delete(self, event):
        self.deleted.append(event.id)
    def list_all(self):
        return list(self.events.values())

class DummyContractRepository:
    """Simule la vérification d’existence d’un contrat."""
    def __init__(self, session):
        self.session = session
    def get_by_id(self, contract_id):
        if contract_id == 1:
            return SimpleNamespace(id=1, customer_id=10)
        return None

class DummyEventCreate:
    """Remplace la validation Pydantic pour la création."""
    def __init__(self, **data):
        self._data = data
    def model_dump(self):
        return dict(self._data)

class DummyEventUpdate(DummyEventCreate):
    """Remplace la validation Pydantic pour la mise à jour."""
    def model_dump(self, exclude_none=False):
        return {k: v for k, v in self._data.items() if v is not None}

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """Injecte des implémentations factices pour isoler la logique métier."""
    monkeypatch.setattr(event_service, "EventRepository", DummyEventRepository)
    monkeypatch.setattr(event_service, "ContractRepository", DummyContractRepository)
    monkeypatch.setattr(event_service, "EventCreate", DummyEventCreate)
    monkeypatch.setattr(event_service, "EventUpdate", DummyEventUpdate)

def make_service(perms):
    """Construit un EventService avec un PermissionService factice."""
    perm_service = DummyPermService(perms)
    return event_service.EventService(session=SimpleNamespace(), permission_service=perm_service)

def test_create_requiert_permission():
    """Doit refuser la création si `event:create` n’est pas accordée."""
    service = make_service({'event:create': False})
    with pytest.raises(PermissionError):
        service.create(SimpleNamespace(role=SimpleNamespace(name="sales")), contract_id=1, customer_id=10)

def test_create_injecte_contrat_et_customer(monkeypatch):
    """Vérifie qu’un contrat existant est requis et que la création appelle le dépôt."""
    service = make_service({'event:create': True})
    service._ensure_customer_exists = lambda customer_id: None
    service._ensure_customer_belongs_to_sales_user = lambda customer_id, user: None
    current_user = SimpleNamespace(id=5, role=SimpleNamespace(name="sales"))
    event = service.create(current_user, contract_id=1, customer_id=10, event_name="Lancement")
    assert event.event_name == "Lancement"
    assert event.contract_id == 1

def test_update_refuse_evenement_inexistant():
    """La mise à jour échoue si l’événement n’existe pas."""
    service = make_service({'event:update': True})
    service.repo.events.clear()
    with pytest.raises(ValueError, match="Événement non trouvé"):
        service.update(SimpleNamespace(role=SimpleNamespace(name="sales")), 99, event_name="Nouveau")

def test_update_support_assigne_autre_event():
    """Un support ne peut pas modifier un événement qui ne lui appartient pas."""
    service = make_service({'event:update': True})
    support_user = SimpleNamespace(id=1, role=SimpleNamespace(name="support"))
    with pytest.raises(PermissionError):
        service.update(support_user, 1, event_name="Autre")

def test_delete_demande_permission():
    """La suppression exige `event:delete`."""
    service = make_service({'event:delete': False})
    with pytest.raises(PermissionError):
        service.delete(SimpleNamespace(role=SimpleNamespace(name="management")), 1)

def test_list_all_verifie_permission():
    """L’accès à la liste complète est conditionné à `event:read`."""
    service = make_service({'event:read': False})
    with pytest.raises(PermissionError):
        service.list_all(SimpleNamespace())