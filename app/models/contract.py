from sqlalchemy import Column, Integer, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Contract(TimestampMixin, Base):
    """
    Modèle représentant un contrat relié à un client et géré par un utilisateur de gestion.
    """
    __tablename__ = "contracts"

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    user_management_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    balance_due = Column(Numeric(10, 2), nullable=False)
    signed = Column(Boolean, default=False, nullable=False)

    customer = relationship("Customer", back_populates="contracts")
    manager = relationship("User", back_populates="managed_contracts")
    events = relationship("Event", back_populates="contract")

    def __repr__(self):
        return f"<Contract cust={self.customer_id} amt={self.total_amount}>"
