from types import SimpleNamespace
from app.repositories import contract_repository

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

class FakeContract:
    def __init__(self, **fields):
        self.__dict__.update(fields)

def test_contract_crud(monkeypatch):
    """Confirme create/update/delete sur le modèle factice."""
    session = FakeSession()
    monkeypatch.setattr(contract_repository, "Contract", FakeContract)
    repo = contract_repository.ContractRepository(session)
    contract = repo.create(total_amount=100)
    repo.update(contract, total_amount=150)
    repo.delete(contract)
    assert contract.total_amount == 150
    assert session.flushed == 3

def test_contract_requetes():
    """Vérifie list_all + filtres spécialisés utilisent bien la query factice."""
    session = FakeSession()
    repo = contract_repository.ContractRepository(session)
    assert repo.get_by_id(1) == "Contract-one"
    assert repo.list_all() == ["Contract-all"]
    assert repo.list_by_management_user(2) == ["Contract-all"]
    assert repo.list_by_customer_ids([5,6]) == ["Contract-all"]
    assert session.last_query.filters