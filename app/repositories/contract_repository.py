from sqlalchemy.orm import Session
from app.models.contract import Contract


class ContractRepository:
    """
    Repository pour l'entité Contract — fournis des opérations de lecture/écriture via une session SQLAlchemy.
    Responsabilités
    - Encapsuler l'accès à la base de données pour l'entité Contract.
    - Fournir des opérations CRUD courantes sans gérer la transaction (flush effectué, commit/rollback laissé à l'appelant).

    """
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, contract_id: int) -> Contract | None:
        return self.session.query(Contract).filter(Contract.id == contract_id).one_or_none()

    def list_all(self) -> list[Contract]:
        return self.session.query(Contract).all()

    def list_by_management_user(self, user_id: int) -> list[Contract]:
        return self.session.query(Contract).filter(Contract.user_management_id == user_id).all()

    def list_by_customer_ids(self, customer_ids: list[int]) -> list[Contract]:
        return self.session.query(Contract).filter(Contract.customer_id.in_(customer_ids)).all()

    def create(self, **fields) -> Contract:
        c = Contract(**fields)
        self.session.add(c)
        self.session.flush()
        return c

    def update(self, contract: Contract, **fields) -> Contract:
        for k, v in fields.items():
            setattr(contract, k, v)
        self.session.flush()
        return contract

    def delete(self, contract: Contract) -> None:
        self.session.delete(contract)
        self.session.flush()
