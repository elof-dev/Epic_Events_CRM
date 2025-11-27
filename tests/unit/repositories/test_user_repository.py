from app.repositories.user_repository import UserRepository


def test_user_repository_crud(db_session, user_factory):
    repo = UserRepository(db_session)
    u = user_factory(username="repo_user", role_name="sales")
    got = repo.get_by_username("repo_user")
    assert got is not None
    allu = repo.list_all()
    assert any(x.username == "repo_user" for x in allu)
