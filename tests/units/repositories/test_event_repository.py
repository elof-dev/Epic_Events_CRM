from types import SimpleNamespace
from app.repositories import event_repository

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

class FakeEvent:
    def __init__(self, **attrs):
        self.__dict__.update(attrs)

def test_event_create_et_update(monkeypatch):
    """Contrôle create/update/delete en isolant le modèle."""
    session = FakeSession()
    monkeypatch.setattr(event_repository, "Event", FakeEvent)
    repo = event_repository.EventRepository(session)
    event = repo.create(event_name="test")
    assert session.added[-1] is event
    repo.update(event, event_name="modifié")
    assert event.event_name == "modifié"
    repo.delete(event)
    assert session.deleted[-1] is event

def test_event_query_utilise_filters():
    """S’assure que les listes retournent les résultats gérés par la query factice."""
    session = FakeSession()
    repo = event_repository.EventRepository(session)
    assert repo.list_all() == ["Event-all"]
    assert repo.list_by_support_user(5) == ["Event-all"]
    assert repo.list_by_customer(10) == ["Event-all"]
    assert session.last_query.filters  # filtres effectivement enregistrés