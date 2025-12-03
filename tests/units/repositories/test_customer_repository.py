from types import SimpleNamespace
from app.repositories import customer_repository

class FakeSession:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.flushed = 0
        self.last_query = None
    def add(self, obj):
        self.added.append(obj)
    def delete(self, obj):
        self.deleted.append(obj)
    def flush(self):
        self.flushed += 1
    def query(self, model):
        self.last_query = SimpleNamespace(filters=[])
        class Query:
            def __init__(self, parent):
                self.parent = parent
            def filter(self, *args, **kwargs):
                self.parent.filters.append(args)
                return self
            def one_or_none(self):
                return f"{model.__name__}-one"
            def all(self):
                return [f"{model.__name__}-all"]
        return Query(self.last_query)

class FakeCustomer:
    def __init__(self, **fields):
        self.__dict__.update(fields)

def test_customer_crud(monkeypatch):
    """Teste les méthodes create/update/delete sur un modèle factice."""
    session = FakeSession()
    monkeypatch.setattr(customer_repository, "Customer", FakeCustomer)
    repo = customer_repository.CustomerRepository(session)
    cust = repo.create(company_name="Acme")
    repo.update(cust, company_name="Acme V2")
    repo.delete(cust)
    assert cust.company_name == "Acme V2"
    assert session.flushed == 3

def test_customer_listes_requete():
    """Vérifie que les listes et get_by_id passent bien par query()."""
    session = FakeSession()
    repo = customer_repository.CustomerRepository(session)
    assert repo.get_by_id(1) == "Customer-one"
    assert repo.list_all() == ["Customer-all"]
    assert repo.list_by_sales_user(3) == ["Customer-all"]