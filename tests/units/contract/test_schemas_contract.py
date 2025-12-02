import pytest
from pydantic import ValidationError
from app.schemas.contract import ContractCreate, ContractUpdate


def test_negative_amount_invalid():
    with pytest.raises(ValidationError):
        ContractCreate(total_amount=-1, balance_due=0, customer_id=1, user_management_id=1)


def test_balance_greater_than_total_invalid():
    with pytest.raises(ValidationError):
        ContractCreate(total_amount=100, balance_due=200, customer_id=1, user_management_id=1)


def test_contractupdate_allows_optional_fields():
    u = ContractUpdate()
    assert u.total_amount is None
    u2 = ContractUpdate(balance_due=10)
    assert u2.balance_due == 10
