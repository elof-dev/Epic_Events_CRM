import pytest
from types import SimpleNamespace

# Fakes -------------------------------------------------
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

class FakeEventService:
    def __init__(self, events=None, new_event=None):
        self.events = events or []
        self.new_event = new_event
    def create(self, user, **fields):
        return self.new_event
    def list_all(self, user):
        return self.events
    def list_by_support_user(self, uid):
        return self.events
    def list_by_customer(self, cid):
        return self.events
    def update(self, user, event_id, **fields):
        return True
    def delete(self, user, event_id):
        return True

# -------------------------------------------------------
from cli.views.events import EventsView

# ---------------- get_event_menu_options -----------------
def test_get_event_menu_options():
    user = SimpleNamespace(role=SimpleNamespace(name="sales"))
    perm = FakePerm({"event:read", "event:create"})
    view = EventsView(session=None, perm_service=perm)
    opts = view.get_event_menu_options(user)
    assert len(opts) >= 2

# ---------------- main_event_menu ------------------------
def test_main_event_menu_exit(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name="sales"))
    perm = FakePerm({})
    view = EventsView(session=None, perm_service=perm)
    monkeypatch.setattr("cli.helpers.prompt_select_option", lambda opts, prompt: None)
    view.main_event_menu(user)

# ---------------- create_event ---------------------------
def test_create_event_contract_not_found(monkeypatch):
    user = SimpleNamespace(id=1)
    perm = FakePerm({"event:create"})
    session = FakeSession(get_map={})
    view = EventsView(session=session, perm_service=perm)

    answers = iter(["1", "1", "ev", "", "", "", "0", ""])
    monkeypatch.setattr("click.prompt", lambda *a, **k: next(answers))

    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))

    monkeypatch.setattr("app.services.event_service.EventService", lambda s, p: FakeEventService())

    view.create_event(user)
    assert any("introuvable" in (m or "") for m in logs)

# ---------------- list_all_events ------------------------
def test_list_all_events_empty(monkeypatch):
    user = SimpleNamespace()
    perm = FakePerm({"event:read"})
    session = FakeSession()
    fake_service = FakeEventService(events=[])

    view = EventsView(session=session, perm_service=perm)
    monkeypatch.setattr("app.services.event_service.EventService", lambda s, p: fake_service)

    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))
    monkeypatch.setattr("cli.helpers.prompt_list_or_empty", lambda *a, **k: None)

    view.list_all_events(user)

# ---------------- display_detail_events ------------------
def test_display_detail_events_not_found(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name="management"))
    perm = FakePerm(set())
    session = FakeSession(get_map={})

    view = EventsView(session=session, perm_service=perm)
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))

    view.display_detail_events(user, 5)
    assert any("introuvable" in (m or "") for m in logs)

# ---------------- delete_event ----------------------------
def test_delete_event_not_found(monkeypatch):
    user = SimpleNamespace(role=SimpleNamespace(name="management"))
    perm = FakePerm({"event:delete"})
    session = FakeSession(get_map={})

    view = EventsView(session=session, perm_service=perm)
    logs = []
    monkeypatch.setattr("click.echo", lambda msg=None, **k: logs.append(msg))

    view.delete_event(user, 2)
    assert any("introuvable" in (m or "") for m in logs)