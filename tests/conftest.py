import pytest


@pytest.fixture(scope="module")
def seeded_session():
    # initialize DB and seed (idempotent for tests)
    from app.db.init_db import main as init_main
    init_main()
    from app.db.session import create_engine_and_session
    engine, SessionLocal = create_engine_and_session()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
