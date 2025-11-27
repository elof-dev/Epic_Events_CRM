from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    roles = relationship("Role", secondary="role_permission", back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.name}>"
