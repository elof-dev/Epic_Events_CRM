from types import SimpleNamespace
import pytest
from app.repositories import user_repository

class FakeSession:
    """Simule les appels fondamentaux utilisés par les repositories."""
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

class ColumnProxy:
    """Simule une colonne SQLAlchemy avec un __eq__ exploitable."""
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        return f"{self.name} == {other}"
    def __repr__(self):
        return f"<Column {self.name}>"

class FakeUser:
    username = ColumnProxy("username")
    id = ColumnProxy("id")
    email = ColumnProxy("email")
    def __init__(self, **fields):
        self.__dict__.update(fields)

@pytest.fixture(autouse=True)
def patch_model(monkeypatch):
    """Remplace le modèle SQLAlchemy par un simple conteneur."""
    monkeypatch.setattr(user_repository, "User", FakeUser)

def test_create_enregistre_lobjet():
    """Vérifie que create ajoute/lance flush et retourne l’instance."""
    session = FakeSession()
    repo = user_repository.UserRepository(session)
    user = repo.create(username="alice")
    assert session.added[-1] is user
    assert session.flushed == 1
    assert user.username == "alice"

def test_update_modifie_les_champs_existants():
    """Vérifie que update met à jour les attributs existants puis flush."""
    session = FakeSession()
    repo = user_repository.UserRepository(session)
    user = FakeUser(id=1, username="old")
    updated = repo.update(user, username="new")
    assert updated.username == "new"
    assert session.flushed == 1

def test_delete_supprime_et_flush():
    """S’assure que delete appelle delete et flush sur la session."""
    session = FakeSession()
    repo = user_repository.UserRepository(session)
    user = FakeUser(id=1)
    repo.delete(user)
    assert session.deleted == [user]
    assert session.flushed == 1


def test_requetes_renvoient_query(monkeypatch):
    """Vérifie la chaîne query().filter().one_or_none()/all()."""
    session = FakeSession()
    repo = user_repository.UserRepository(session)
    model_name = user_repository.User.__name__
    assert repo.get_by_username("bob") == f"{model_name}-one"
    assert repo.get_by_id(2) == f"{model_name}-one"
    assert repo.list_all() == [f"{model_name}-all"]
