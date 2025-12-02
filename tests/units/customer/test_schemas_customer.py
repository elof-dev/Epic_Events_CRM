import pytest
from pydantic import ValidationError
from app.schemas.customer import BaseCustomer, CustomerCreate, CustomerUpdate


def test_basecustomer_name_validators_accept_valid_names():
    data = {
        "customer_first_name": "Élodie",
        "customer_last_name": "Dupont"
    }
    b = BaseCustomer(**data)
    assert b.customer_first_name == "Élodie"
    assert b.customer_last_name == "Dupont"


@pytest.mark.parametrize("bad_name", ["", "123", "Jean@", "A" * 101])
def test_basecustomer_name_invalid_raises(bad_name):
    with pytest.raises(ValidationError):
        BaseCustomer(customer_first_name=bad_name)


def test_phone_validator_accepts_numbers_and_plus():
    b = BaseCustomer(phone_number="+33123456789")
    assert b.phone_number == "+33123456789"


@pytest.mark.parametrize("bad_phone", ["abc", "12-34", "", "+"])
def test_phone_invalid_raises(bad_phone):
    with pytest.raises(ValidationError):
        BaseCustomer(phone_number=bad_phone)


def test_company_name_length_constraints():
    long_name = "C" * 101
    with pytest.raises(ValidationError):
        BaseCustomer(company_name=long_name)


def test_customercreate_requires_fields():
    # missing required fields should raise
    with pytest.raises(ValidationError):
        CustomerCreate()


def test_customerupdate_allows_optional_fields():
    u = CustomerUpdate()
    assert u.customer_first_name is None
    # partial update should validate individual fields
    u2 = CustomerUpdate(company_name="Acme")
    assert u2.company_name == "Acme"
