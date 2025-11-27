from app.repositories.contract_repository import ContractRepository


def test_contract_repository_crud(db_session, contract_factory):
    repo = ContractRepository(db_session)
    c = contract_factory(contract_number="RN-1")
    got = repo.get_by_id(c.id)
    assert got.contract_number == "RN-1"
    assert any(x.contract_number == "RN-1" for x in repo.list_all())
