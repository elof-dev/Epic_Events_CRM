from contextlib import contextmanager

@contextmanager
def transactional(session):
    """
    Context manager to commit the given SQLAlchemy session on success,
    or rollback on exception.

    Usage:
        with transactional(session):
            # perform DB operations using `session`
            service.create(...)
    """
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
