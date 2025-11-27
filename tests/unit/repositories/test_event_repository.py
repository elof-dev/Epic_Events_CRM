from app.repositories.event_repository import EventRepository


def test_event_repository_crud(db_session, event_factory):
    repo = EventRepository(db_session)
    e = event_factory(event_number="EV-REPO-1")
    got = repo.get_by_id(e.id)
    assert got.event_number == "EV-REPO-1"
    assert any(x.event_number == "EV-REPO-1" for x in repo.list_all())
