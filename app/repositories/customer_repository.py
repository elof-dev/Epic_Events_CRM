from sqlalchemy.orm import Session
from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, customer_id: int):
        return self.session.query(Customer).filter(Customer.id == customer_id).one_or_none()

    def list_all(self):
        return self.session.query(Customer).all()

    def list_by_sales_user(self, user_id: int):
        return self.session.query(Customer).filter(Customer.user_sales_id == user_id).all()

    def create(self, **fields):
        c = Customer(**fields)
        self.session.add(c)
        self.session.flush()
        return c

    def update(self, customer: Customer, **fields):
        for k, v in fields.items():
            setattr(customer, k, v)
        self.session.flush()
        return customer

    def delete(self, customer: Customer):
        self.session.delete(customer)
        self.session.flush()
