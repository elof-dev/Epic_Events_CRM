from types import SimpleNamespace
import pytest
from app.services import customer_service


class DummyPermService:
    """Service factice pour contrôler simplement les permissions demandées."""
    def __init__(self, perms):
        self.perms = perms

    def user_has_permission(self, user, perm):
        return self.perms.get(perm, False)


class DummyQuery:
    """Représente une requête SQLAlchemy minimale pour les tests."""
    def __init__(self, count_result=None, record=None):
        self._count_result = count_result
        self._record = record

    def filter(self, *args, **kwargs):
        return self

    def count(self):
        return self._count_result or 0

    def one_or_none(self):
        return self._record


class DummySession:
    """Simule la session SQLAlchemy avec des comptes de références configurables."""
    def __init__(self, user_exists=True, contracts=0, events=0):
        self.user_exists = user_exists
        self.contracts = contracts
        self.events = events
        self.rollback_called = False

    def rollback(self):
        self.rollback_called = True

    def query(self, model):
        if model.__name__ == "User":
            record = SimpleNamespace(id=1) if self.user_exists else None
            return DummyQuery(record=record)
        if model.__name__ == "Contract":
            return DummyQuery(count_result=self.contracts)
        if model.__name__ == "Event":
            return DummyQuery(count_result=self.events)
        return DummyQuery()


class DummyCustomerRepository:
    """Simule les opérations CRUD essentielles d’un dépôt client."""
    def __init__(self, session):
        self.session = session
        self.created = []
        self.deleted = []
        self.existing_customer = None

    def create(self, **kwargs):
        self.created.append(kwargs)
        return SimpleNamespace(id=len(self.created), **kwargs)

    def get_by_id(self, customer_id):
        return self.existing_customer

    def update(self, customer, **kwargs):
        return SimpleNamespace(id=customer.id, **kwargs)

    def delete(self, customer):
        self.deleted.append(customer.id)

    def list_all(self):
        return [SimpleNamespace(id=1, company_name="Acme")]

    def list_by_sales_user(self, user_id):
        return [SimpleNamespace(id=2, user_sales_id=user_id)]


class DummyCustomerCreate:
    """Imite la validation Pydantic de création d’un client."""
    def __init__(self, **data):
        self._data = data

    def model_dump(self, **kwargs):
        return dict(self._data)


class DummyCustomerUpdate(DummyCustomerCreate):
    """Même logique que la création pour les tests (exclusion None)."""
    def model_dump(self, **kwargs):
        return {k: v for k, v in self._data.items() if v is not None}


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """Redirige les dépendances lourdes vers des implémentations factices."""
    monkeypatch.setattr(customer_service, "CustomerRepository", DummyCustomerRepository)
    monkeypatch.setattr(customer_service, "CustomerCreate", DummyCustomerCreate)
    monkeypatch.setattr(customer_service, "CustomerUpdate", DummyCustomerUpdate)


def make_service(session, perms):
    """Construit un service client avec un permission_service factice."""
    perm_service = DummyPermService(perms)
    return customer_service.CustomerService(session, perm_service)


def test_create_requires_permission():
    """La création doit échouer si la permission `customer:create` n’est pas accordée."""
    session = DummySession()
    service = make_service(session, {'customer:create': False})
    user = SimpleNamespace(id=1, role=SimpleNamespace(name="sales"))
    with pytest.raises(PermissionError):
        service.create(user, customer_first_name="A")


def test_create_assigne_proprietaire_sales_et_normalise(monkeypatch):
    """Vérifie que le propriétaire est affecté automatiquement et que l’email est normalisé."""
    session = DummySession()
    service = make_service(session, {'customer:create': True})
    user = SimpleNamespace(id=7, role=SimpleNamespace(name="sales"))
    customer = service.create(
        user,
        customer_first_name="Alice",
        customer_last_name="Wonder",
        company_name="Acme",
        email=" TEST@EXAMPLE.COM ",
        phone_number=" 0123456 ",
    )
    created = service.repo.created[-1]
    assert created['user_sales_id'] == user.id
    assert created['email'] == "test@example.com"
    assert created['phone_number'] == "0123456"
    assert customer.id == 1


def test_update_verifie_proprietaire_et_permissions():
    """L’utilisateur non propriétaire ne peut pas mettre à jour un client."""
    session = DummySession()
    service = make_service(session, {'customer:update': True})
    customer = SimpleNamespace(id=1, user_sales_id=5)
    service.repo.existing_customer = customer
    current_user = SimpleNamespace(id=7)
    with pytest.raises(PermissionError):
        service.update(current_user, customer.id, company_name="Nouveau")


def test_delete_refuse_si_references(monkeypatch):
    """Interdit la suppression lorsque des contrats ou événements pointent encore le client."""
    session = DummySession(contracts=1, events=1)
    service = make_service(session, {'customer:delete': True})
    service.repo.existing_customer = SimpleNamespace(id=9, user_sales_id=5)
    current_user = SimpleNamespace(id=5)
    with pytest.raises(ValueError, match="référencé"):
        service.delete(current_user, 9)


def test_list_all_demande_permission():
    """N’autorise pas l’accès à la liste sans `customer:read`."""
    session = DummySession()
    service = make_service(session, {'customer:read': False})
    with pytest.raises(PermissionError):
        service.list_all(SimpleNamespace(id=1))


def test_list_mine_appelle_les_clients_du_commercial():
    """Retourne les clients assignés au commercial courant quand la permission existe."""
    session = DummySession()
    service = make_service(session, {'customer:read': True})
    current_user = SimpleNamespace(id=17)
    result = service.list_mine(current_user)
    assert len(result) == 1
    assert result[0].user_sales_id == current_user.id