from app.repositories.customer_repository import CustomerRepository


def test_customer_repository_crud(db_session, customer_factory):
    repo = CustomerRepository(db_session)
    c = customer_factory(company_name="RepoCo")
    got = repo.get_by_id(c.id)
    assert got.company_name == "RepoCo"
    lst = repo.list_all()
    assert any(x.company_name == "RepoCo" for x in lst)
