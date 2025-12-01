from sqlalchemy import Column, String, Table, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


# Association table pour la relation many-to-many entre Role et Permission
# Cette table n'a pas de modèle dédié car elle ne contient que des clés étrangères
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class Role(TimestampMixin, Base):
    """
    Modèle représentant un rôle attribué aux utilisateurs, avec des permissions associées.
    """
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False)

    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")
    users = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role {self.name}>"
