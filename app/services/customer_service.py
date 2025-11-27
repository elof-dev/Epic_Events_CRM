from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, session, permission_service):
        self.session = session
        self.repo = CustomerRepository(session)
        self.perm = permission_service

    def create(self, user, **fields):
        if not self.perm.can_create_customer(user):
            raise PermissionError("User not allowed to create customers")
        # ensure sales user is set
        if user.role.name == "sales":
            fields.setdefault("user_sales_id", user.id)
        return self.repo.create(**fields)

    def update(self, user, customer_id: int, **fields):
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        if not self.perm.can_update_customer(user, customer):
            raise PermissionError("User not allowed to update this customer")
        return self.repo.update(customer, **fields)

    def delete(self, user, customer_id: int):
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        if not self.perm.can_delete_customer(user, customer):
            raise PermissionError("User not allowed to delete this customer")
        self.repo.delete(customer)

    def list_all(self, user):
        # visibility handled at CLI/service level; here return all if allowed
        if not self.perm.user_has_permission(user, "customer:read"):
            raise PermissionError("User not allowed to read customers")
        return self.repo.list_all()

    def list_mine(self, user):
        return self.repo.list_by_sales_user(user.id)
