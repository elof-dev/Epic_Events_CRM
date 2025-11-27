from app.models.customer import Customer


def test_customer_fields_and_repr():
    c = Customer(customer_first_name="CF", customer_last_name="CL", email="c@example.com", phone_number=None, company_name="Comp", user_sales_id=1)
    assert c.company_name == "Comp"
    assert "Comp" in repr(c) or c.customer_first_name in repr(c)
