from types import SimpleNamespace
import pytest
from app.services import user_service


class DummyPermService:
    """Service factice pour simuler les permissions disponibles."""
    def __init__(self, perms):
        self.perms = perms

    def user_has_permission(self, user, perm):
        return self.perms.get(perm, False)


class DummyRepository:
    """Service factice pour simuler le dépôt d'utilisateurs."""
    def __init__(self, session):
        self.session = session
        self.created = []
        self.deleted = []
        self.users = []

    def create(self, **kwargs):
        self.created.append(kwargs)
        created = SimpleNamespace(**kwargs)
        created.id = len(self.created)
        self.users.append(created)
        return created

    def get_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
        return SimpleNamespace(id=user_id)

    def get_by_username(self, username):
        return None

    def list_all(self):
        return [SimpleNamespace(id=1, username="foo")]

    def delete(self, user):
        self.deleted.append(user.id)


class DummyAuthService:
    """Service factice pour simuler le service d'authentification."""
    def hash_password(self, password):
        return f"hashed-{password}"


class DummySession:
    """Service factice pour simuler la session de base de données."""
    def __init__(self, contracts=0, events=0, customers=0):
        self._counts = {"contracts": contracts, "events": events, "customers": customers}
        self.rolled_back = False

    def rollback(self):
        self.rolled_back = True

    def query(self, model):
        class DummyQuery:
            def __init__(self, count):
                self.count_value = count

            def filter(self, *args, **kwargs):
                return self

            def count(self):
                return self.count_value

            def one_or_none(self):
                return None

        key = model.__name__.lower()
        return DummyQuery(self._counts.get(key, 0))


class DummyUserCreate:
    """Service factice pour simuler la création d'un utilisateur."""
    def __init__(self, **data):
        self.data = data

    def model_dump(self, **kwargs):
        return dict(self.data)


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    """
    Redirige les dépendances du UserService vers des versions factices
    pour isoler la logique métier lors des tests unitaires.
    """
    monkeypatch.setattr(user_service, "UserRepository", DummyRepository)
    monkeypatch.setattr(user_service, "AuthService", DummyAuthService)
    monkeypatch.setattr(user_service, "UserCreate", DummyUserCreate)


def make_service(session, perms):
    """Construit une instance de UserService avec des permissions factices."""
    perm_service = DummyPermService(perms)
    return user_service.UserService(session, perm_service)


def test_create_requires_permission():
    """Vérifie que la création d'un utilisateur nécessite la permission adéquate."""
    session = DummySession()
    service = make_service(session, {'user:create': False})
    with pytest.raises(PermissionError):
        service.create(SimpleNamespace(id=1), username="foo")


def test_create_hashes_and_normalizes(monkeypatch):
    """Confirme que les champs sont normalisés et le mot de passe hashé lors de la création."""
    session = DummySession()
    service = make_service(session, {'user:create': True})
    # éviter les vérifications additionnelles
    service._ensure_role_exists = lambda role_id: None
    service._check_uniqueness = lambda *args, **kwargs: None
    service._hash_password_if_present = user_service.UserService._hash_password_if_present.__get__(service)  # utiliser la méthode originale
    user = service.create(
        SimpleNamespace(id=1),
        user_first_name=" Alice ",
        user_last_name="Wonder",
        username=" FoO ",
        email="TEST@Example.COM ",
        role_id=2,
        password="pw"
    )
    created = service.repo.created[-1]
    assert created["username"] == "FoO"
    assert created["email"] == "test@example.com"
    assert created["password_hash"] == "hashed-pw"
    assert getattr(user, "id", None) is not None


def test_delete_self_not_allowed():
    """Vérifie que la suppression de son propre compte n'est pas autorisée."""
    session = DummySession()
    service = make_service(session, {'user:delete': True})
    current_user = SimpleNamespace(id=5)
    with pytest.raises(ValueError, match="Vous ne pouvez pas supprimer votre propre compte"):
        service.delete(current_user, 5)


def test_list_all_requires_permission():
    """Vérifie que la liste de tous les utilisateurs nécessite la permission adéquate."""
    session = DummySession()
    service = make_service(session, {'user:read': False})
    with pytest.raises(PermissionError):
        service.list_all(SimpleNamespace(id=1))


def test_list_all_returns_repo(monkeypatch):
    """Confirme que la méthode liste tous les utilisateurs provenant du dépôt."""
    session = DummySession()
    service = make_service(session, {'user:read': True})
    result = service.list_all(SimpleNamespace(id=1))
    assert isinstance(result, list)
    assert result[0].username == "foo"