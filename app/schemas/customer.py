from typing import Optional, Annotated
import re
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

"""
Schémas Pydantic pour l'entité Customer.
Pattern suivi : `BaseCustomer` (champs optionnels + validateurs) puis
`CustomerCreate` (champs requis) et `CustomerUpdate` (tous optionnels).
"""


NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$")
PHONE_PATTERN = re.compile(r"^\+?\d+$")


class BaseCustomer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_sales_id: Optional[Annotated[int, Field(ge=1)]] = None
    customer_first_name: Optional[Annotated[str, Field(max_length=100)]] = None
    customer_last_name: Optional[Annotated[str, Field(max_length=100)]] = None
    email: Optional[Annotated[EmailStr, Field(max_length=255)]] = None
    phone_number: Optional[Annotated[str, Field(max_length=20)]] = None
    company_name: Optional[Annotated[str, Field(max_length=100)]] = None

    @field_validator('customer_first_name', 'customer_last_name')
    def _validate_name(cls, v):
        if v is None:
            return None
        s = v.strip().lower().capitalize()
        if not (1 <= len(s) <= 100):
            raise ValueError('Doit contenir entre 1 et 100 caractères')
        if not NAME_PATTERN.match(s):
            raise ValueError("Caractères autorisés : lettres, espaces, apostrophes et tirets")
        return s

    @field_validator('phone_number')
    def _validate_phone(cls, v):
        if v is None:
            return None
        s = v.strip()
        if not (1 <= len(s) <= 20):
            raise ValueError('Téléphone : longueur invalide (max 20)')
        if not PHONE_PATTERN.match(s):
            raise ValueError('Téléphone : uniquement chiffres et un préfixe + optionnel')
        return s
    
    @field_validator('email')
    def normalize_email(cls, v):
        if v is None:
            return None
        return v.strip().lower()
    
    
    @field_validator('company_name')
    def _validate_company_name(cls, v):
        if v is None:
            return None
        s = v.strip().lower().capitalize()
        if not (1 <= len(s) <= 100):
            raise ValueError('Nom de l\'entreprise : longueur invalide (max 100)')
        return s


class CustomerCreate(BaseCustomer):
    # rendre obligatoires les champs pour la création
    user_sales_id: Annotated[int, Field(ge=1)]
    customer_first_name: Annotated[str, Field(max_length=100)]
    customer_last_name: Annotated[str, Field(max_length=100)]
    email: Annotated[EmailStr, Field(max_length=255)]
    phone_number: Annotated[str, Field(max_length=20)]
    company_name: Annotated[str, Field(max_length=100)]


class CustomerUpdate(BaseCustomer):
    # héritage pur : tous les champs optionnels
    pass


__all__ = ["BaseCustomer", "CustomerCreate", "CustomerUpdate"]
