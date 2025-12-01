from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Customer(TimestampMixin, Base):
    """
    Modèle représentant un client créé par un utilisateur commercial qui lui est associé.
    """
    __tablename__ = "customers"

    user_sales_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_first_name = Column(String(100), nullable=False)
    customer_last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(50), unique=True, nullable=False)
    company_name = Column(String(255), unique=True, nullable=False)

    sales_user = relationship("User", back_populates="customers")
    contracts = relationship("Contract", back_populates="customer")
    events = relationship("Event", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.company_name} ({self.customer_first_name} {self.customer_last_name})>"
