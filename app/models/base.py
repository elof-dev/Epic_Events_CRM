from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime, func


class Base(DeclarativeBase):
    """Classe de base pour les modèles SQLAlchemy."""
    pass


class TimestampMixin:
    """
    Mixin pour ajouter des champs de timestamp aux modèles.
    Fournit created_at et updated_at ainsi que la clé primaire id."""
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
