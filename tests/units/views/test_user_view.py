import pytest
from types import SimpleNamespace

# Fakes -------------------------------------------------
class FakePerm:
    def __init__(self, perms):
        self.perms = perms
    def user_has_permission(self, user, perm):
        return perm in self.perms

class FakeSession:
    def __init__(self, get_map=None, roles=None, users=None):
        self.get_map = get_map or {}
        self.roles = roles or []
        self.users = users or []
    def get(self, model, _id):
        return self.get_map.get(_id)
    def query(self, model):
        return SimpleNamespace(all=lambda: self.roles)

class FakeUserService:
    def __init__(self, return_user=None, list_result=None):
        self.return_user = return_user
        self.list_result = list_result or []
    def create(self, user, **fields):
        return self.return_user
    def update(self, user, uid, **fields):
        return True
    def delete(self, user, uid):
        return True
    def list_all(self, user):
        return self.list_result
    def get_by_id(self, user, uid):
        for u in self.list_result:
            if u.id == uid:
                return u
        return None

# -------------------------------------------------------
from cli.views.users import UsersView

# ---------------- get_user_menu_options -----------------
def test_get_user_menu_options_read_and_create():
    user = SimpleNamespace()
    perm = FakePerm({"user:read", "user:create"})
    view = UsersView(session=None, perm_service=perm)
    opts = view.get_user_menu_options(user)
    assert len(opts) == 3

def test_get_user_menu_options_none():
    user = SimpleNamespace()
    perm = FakePerm(set())
    view = UsersView(session=None, perm_service=perm)
    opts = view.get_user_menu_options(user)
    assert opts == []

# ---------------- main_user_menu ------------------------
def test_main_user_menu_exit(monkeypatch):
    user = SimpleNamespace()
    perm = FakePerm({})
    session = FakeSession()
    view = UsersView(session=session, perm_service=perm)
    called = {"list_all": False, "filter_id": False, "create": False}
    monkeypatch.setattr("cli.helpers.prompt_select_option", lambda opts, prompt: None)
    monkeypatch.setattr(view, "list_all_users", lambda u: called.__setitem__("list_all", True))
    monkeypatch.setattr(view, "filter_user_by_id", lambda u: called.__setitem__("filter_id", True))
    monkeypatch.setattr(view, "create_user", lambda u: called.__setitem__("create", True))
    view.main_user_menu(user)
    assert called == {"list_all": False, "filter_id": False, "create": False}

# ---------------- create_user ---------------------------
def test_create_user_no_roles(monkeypatch):
    user = SimpleNamespace()
    session = FakeSession(roles=[])
    perm = FakePerm(set())
    view = UsersView(session=session, perm_service=perm)

    monkeypatch.setattr("click.prompt", lambda *a, **k: "x")
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))
    monkeypatch.setattr("cli.helpers.prompt_select_option", lambda *a, **k: None)

    view.create_user(user)
    assert any("Aucun rôle" in (m or "") for m in logs)

def test_create_user_nominal(monkeypatch):
    user = SimpleNamespace()
    fake_created = SimpleNamespace(id=10)
    fake_service = FakeUserService(return_user=fake_created)

    # Patch UserService
    monkeypatch.setattr("app.services.user_service.UserService", lambda s, p: fake_service)

    # session with one role
    session = FakeSession(roles=[SimpleNamespace(name="admin", id=1)])
    perm = FakePerm(set())
    view = UsersView(session=session, perm_service=perm)

    # prompts
    answers = iter(["a", "b", "c", "d", "e", "pwd"])  # first/last/username/email/phone/password
    monkeypatch.setattr("click.prompt", lambda *a, **k: next(answers))
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))
    monkeypatch.setattr("cli.helpers.prompt_select_option", lambda *a, **k: 1)

    view.create_user(user)

# ---------------- update_user ---------------------------
def test_update_user_not_found(monkeypatch):
    user = SimpleNamespace()
    perm = FakePerm(set())
    session = FakeSession(get_map={})
    view = UsersView(session=session, perm_service=perm)
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))
    view.update_user(user, 99)
    assert any("introuvable" in (m or "") for m in logs)



# ---------------- delete_user ----------------------------
def test_delete_user_not_found(monkeypatch):
    user = SimpleNamespace()
    session = FakeSession(get_map={})
    perm = FakePerm(set())
    view = UsersView(session=session, perm_service=perm)
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))
    view.delete_user(user, 5)
    assert any("introuvable" in (m or "") for m in logs)

def test_delete_user_confirm(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name="management"))
    target = SimpleNamespace(id=3)
    session = FakeSession(get_map={3: target})
    perm = FakePerm({"user:delete"})
    view = UsersView(session=session, perm_service=perm)

    monkeypatch.setattr("app.services.user_service.UserService", lambda s, p: FakeUserService())
    monkeypatch.setattr("click.prompt", lambda *a, **k: "o")
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))

    view.delete_user(user, 3)


# ---------------- list_all_users -------------------------
def test_list_all_users_empty(monkeypatch):
    user = SimpleNamespace()
    fake_service = FakeUserService(list_result=[])
    session = FakeSession()
    perm = FakePerm(set())
    view = UsersView(session=session, perm_service=perm)
    monkeypatch.setattr("app.services.user_service.UserService", lambda s, p: fake_service)
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))
    monkeypatch.setattr("cli.helpers.prompt_list_or_empty", lambda *a, **k: None)
    view.list_all_users(user)


# ---------------- filter_user_by_id ----------------------
def test_filter_user_by_id_return(monkeypatch):
    user = SimpleNamespace()
    session = FakeSession()
    perm = FakePerm(set())
    view = UsersView(session=session, perm_service=perm)
    monkeypatch.setattr("click.prompt", lambda *a, **k: 0)
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))
    view.filter_user_by_id(user)
    # Pas d'effet attendu, juste pas d'exception et pas de message "introuvable"
    assert not any("introuvable" in (m or "") for m in logs)

# ---------------- display_detail_users -------------------
def test_display_detail_users_not_found(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name="management"))
    session = FakeSession(get_map={})
    perm = FakePerm(set())
    view = UsersView(session=session, perm_service=perm)
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))
    view.display_detail_users(user, 1)
    assert any("introuvable" in (m or "") for m in logs)
