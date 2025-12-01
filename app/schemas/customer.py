from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class CustomerBase(BaseModel):
    """Schéma Pydantic minimal pour Customer."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_sales_id: int
    customer_first_name: str
    customer_last_name: str
    email: str
    phone_number: Optional[str] = None
    company_name: str


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_sales_id: Optional[int] = None
    customer_first_name: Optional[str] = None
    customer_last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None


__all__ = ["CustomerBase", "CustomerCreate", "CustomerUpdate", "ValidationError"]
