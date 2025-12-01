from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class ContractBase(BaseModel):
    """Schéma de base pour les contrats
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_amount: Decimal
    balance_due: Decimal
    signed: bool = False
    customer_id: int
    user_management_id: int


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_amount: Optional[Decimal] = None
    balance_due: Optional[Decimal] = None
    signed: Optional[bool] = None
    customer_id: Optional[int] = None
    user_management_id: Optional[int] = None


__all__ = ["ContractBase", "ContractCreate", "ContractUpdate", "ValidationError"]
