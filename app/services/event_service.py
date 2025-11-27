from app.repositories.event_repository import EventRepository


class EventService:
    def __init__(self, session, permission_service):
        self.session = session
        self.repo = EventRepository(session)
        self.perm = permission_service

    def create(self, user, **fields):
        # expects fields to include contract_id
        if "contract_id" not in fields:
            raise ValueError("contract_id is required to create an event")
        contract = self.session.get(__import__("app.models.contract", fromlist=["Contract"]).Contract, fields["contract_id"])
        if not contract:
            raise ValueError("Contract not found")
        if not self.perm.can_create_event(user, contract):
            raise PermissionError("User not allowed to create this event")
        # set customer_id from contract
        fields.setdefault("customer_id", contract.customer_id)
        return self.repo.create(**fields)

    def update(self, user, event_id: int, **fields):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if not self.perm.can_update_event(user, event, list(fields.keys())):
            raise PermissionError("User not allowed to update this event")

        # Business rule: users with role 'management' may only modify `user_support_id`.
        if getattr(user, 'role', None) and getattr(user.role, 'name', None) == 'management':
            allowed = {'user_support_id'}
            invalid = [k for k in fields.keys() if k not in allowed]
            if invalid:
                raise PermissionError("Management can only modify user_support_id")

        return self.repo.update(event, **fields)

    def delete(self, user, event_id: int):
        event = self.repo.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        if not self.perm.user_has_permission(user, "event:delete"):
            raise PermissionError("User not allowed to delete events")
        self.repo.delete(event)

    def list_all(self, user):
        if not self.perm.user_has_permission(user, "event:read"):
            raise PermissionError("User not allowed to read events")
        return self.repo.list_all()

    def list_mine(self, user):
        if user.role.name == "support":
            return self.repo.list_by_support_user(user.id)
        if user.role.name == "sales":
            # sales see events for their customers
            customer_ids = [c.id for c in user.customers]
            events = []
            for cid in customer_ids:
                events.extend(self.repo.list_by_customer(cid))
            return events
        return []
