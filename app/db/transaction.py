from contextlib import contextmanager

@contextmanager
def transactional(session):
    """
    Gestionnaire de contexte transactionnel pour une `session` SQLAlchemy.

    Cela permet de s'assurer que les opérations effectuées dans le bloc `with`
    sont engagées (commit) si tout se passe bien, ou annulées (rollback) en cas
    d'exception.
        """
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
