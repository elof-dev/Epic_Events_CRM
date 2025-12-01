from sqlalchemy.orm import Session
from app.models.customer import Customer


class CustomerRepository:
    """
    Repository pour l'entité Customer — fournis des opérations de lecture/écriture via une session SQLAlchemy.
    Responsabilités
    - Encapsuler l'accès à la base de données pour l'entité Customer.
    - Fournir des opérations CRUD courantes sans gérer la transaction (flush effectué, commit/rollback laissé à l'appelant).

    """
    
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, **fields) -> Customer:
        c = Customer(**fields)
        self.session.add(c)
        self.session.flush()
        return c

    def update(self, customer: Customer, **fields) -> Customer:
        for k, v in fields.items():
            setattr(customer, k, v)
        self.session.flush()
        return customer

    def delete(self, customer: Customer) -> None:
        self.session.delete(customer)
        self.session.flush()
    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.session.query(Customer).filter(Customer.id == customer_id).one_or_none()

    def list_all(self) -> list[Customer]:
        return self.session.query(Customer).all()

    def list_by_sales_user(self, user_id: int) -> list[Customer]:
        return self.session.query(Customer).filter(Customer.user_sales_id == user_id).all()

    
