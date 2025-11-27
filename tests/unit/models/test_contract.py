from app.models.contract import Contract


def test_contract_fields_and_repr():
    c = Contract(contract_number="CN", total_amount=200, balance_due=200, signed=False, customer_id=1, user_management_id=1)
    assert c.contract_number == "CN"
    assert "CN" in repr(c)
