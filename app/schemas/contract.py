from decimal import Decimal
from typing import Optional, Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, ValidationError


class ContractBase(BaseModel):
    """Schéma de base pour les contrats.

    Pattern utilisé :
    - `ContractBase` : champs optionnels + validateurs
    - `ContractCreate` : champs requis pour la création
    - `ContractUpdate` : tous les champs optionnels pour les mises à jour
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_amount: Optional[Annotated[Decimal, Field(ge=0)]] = None
    balance_due: Optional[Annotated[Decimal, Field(ge=0)]] = None
    signed: Optional[bool] = False
    customer_id: Optional[Annotated[int, Field(ge=1)]] = None
    user_management_id: Optional[Annotated[int, Field(ge=1)]] = None

    @field_validator('total_amount', 'balance_due')
    def _validate_amounts(cls, v):
        if v is None:
            return None
        if v < 0:
            raise ValueError('Montant doit être >= 0')
        return v

    @model_validator(mode='after')
    def _check_balance_vs_total(self):
        ta = self.total_amount
        bd = self.balance_due
        if ta is not None and bd is not None:
            if bd > ta:
                raise ValueError('Le solde dû ne peut pas être supérieur au montant total')
        return self


class ContractCreate(ContractBase):
    total_amount: Annotated[Decimal, Field(ge=0)]
    balance_due: Annotated[Decimal, Field(ge=0)]
    customer_id: Annotated[int, Field(ge=1)]
    user_management_id: Annotated[int, Field(ge=1)]
    signed: bool = False


class ContractUpdate(ContractBase):
    # tous les champs optionnels pour update
    pass


__all__ = ["ContractBase", "ContractCreate", "ContractUpdate", "ValidationError"]
