from sqlalchemy.orm import Session
from app.models.contract import Contract


class ContractRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, contract_id: int):
        return self.session.query(Contract).filter(Contract.id == contract_id).one_or_none()

    def list_all(self):
        return self.session.query(Contract).all()

    def list_by_management_user(self, user_id: int):
        return self.session.query(Contract).filter(Contract.user_management_id == user_id).all()

    def list_by_customer_ids(self, customer_ids: list):
        return self.session.query(Contract).filter(Contract.customer_id.in_(customer_ids)).all()

    def create(self, **fields):
        c = Contract(**fields)
        self.session.add(c)
        self.session.flush()
        return c

    def update(self, contract: Contract, **fields):
        for k, v in fields.items():
            setattr(contract, k, v)
        self.session.flush()
        return contract

    def delete(self, contract: Contract):
        self.session.delete(contract)
        self.session.flush()
