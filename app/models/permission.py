from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Permission(TimestampMixin, Base):
    """
    Modèle représentant une permission pouvant être associée à un rôle.
    """
    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False)

    roles = relationship("Role", secondary="role_permission", back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.name}>"
