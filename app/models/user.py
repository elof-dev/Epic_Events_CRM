from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    user_first_name = Column(String(100), nullable=False)
    user_last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(50), unique=True, nullable=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    role = relationship("Role", back_populates="users")
    customers = relationship("Customer", back_populates="sales_user", foreign_keys="Customer.user_sales_id")
    managed_contracts = relationship("Contract", back_populates="manager", foreign_keys="Contract.user_management_id")
    support_events = relationship("Event", back_populates="support_user", foreign_keys="Event.user_support_id")

    def __repr__(self):
        return f"<User {self.username} ({self.user_first_name} {self.user_last_name})>"
