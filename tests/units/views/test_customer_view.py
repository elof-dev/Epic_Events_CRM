import pytest
from types import SimpleNamespace

# ---------------- Fakes -------------------
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

class FakeCustomerService:
    def __init__(self, customers=None, new_customer=None):
        self.customers = customers or []
        self.new_customer = new_customer
    def create(self, user, **fields):
        return self.new_customer
    def update(self, user, cid, **fields):
        return True
    def delete(self, user, cid):
        return True
    def list_all(self, user):
        return self.customers
    def list_mine(self, user):
        return self.customers

# -----------------------------------------
from cli.views.customers import CustomersView

# ---------------- get_customer_menu_options ---------------
def test_get_customer_menu_options():
    user = SimpleNamespace(role=SimpleNamespace(name="sales"))
    perm = FakePerm({"customer:read", "customer:create"})
    view = CustomersView(None, perm)
    opts = view.get_customer_menu_options(user)
    assert len(opts) >= 2


# ---------------- create_customer -------------------------
def test_create_customer_ok(monkeypatch):
    user = SimpleNamespace(id=1)
    perm = FakePerm({"customer:create"})
    session = FakeSession()

    new_c = SimpleNamespace(id=99)
    monkeypatch.setattr("app.services.customer_service.CustomerService", lambda s, p: FakeCustomerService(new_customer=new_c))

    answers = iter(["Jean", "Durand", "jd@test.com", "SociétéX", "0102030405"])
    monkeypatch.setattr("click.prompt", lambda *a, **k: next(answers))

    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))

    view = CustomersView(session, perm)
    view.create_customer(user)


# ---------------- update_customer -------------------------
def test_update_customer_not_found(monkeypatch):
    user = SimpleNamespace(id=1)
    perm = FakePerm({"customer:update"})
    session = FakeSession(get_map={})

    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))

    view = CustomersView(session, perm)
    view.update_customer(user, 5)
    assert any("introuvable" in (m or "") for m in logs)

# ---------------- delete_customer -------------------------
def test_delete_customer_not_found(monkeypatch):
    user = SimpleNamespace(id=1)
    perm = FakePerm({"customer:delete"})
    session = FakeSession(get_map={})

    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))

    view = CustomersView(session, perm)
    view.delete_customer(user, 10)
    assert any("introuvable" in (m or "") for m in logs)

# ---------------- list_all_customers ----------------------
def test_list_all_customers_empty(monkeypatch):
    user = SimpleNamespace(id=1)
    perm = FakePerm({"customer:read"})
    session = FakeSession()
    fake_service = FakeCustomerService(customers=[])

    monkeypatch.setattr("app.services.customer_service.CustomerService", lambda s, p: fake_service)
    monkeypatch.setattr("cli.helpers.prompt_menu", lambda *a, **k: None)
    monkeypatch.setattr("click.echo", lambda msg=None, **k: None)

    view = CustomersView(session, perm)
    view.list_all_customers(user)

# ---------------- display_detail_customers ----------------
def test_display_detail_customers_not_found(monkeypatch):
    user = SimpleNamespace(id=1)
    perm = FakePerm(set())
    session = FakeSession(get_map={})

    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))

    view = CustomersView(session, perm)
    view.display_detail_customers(user, 3)
    assert any("introuvable" in (m or "") for m in logs)