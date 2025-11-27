import pymysql
from sqlalchemy import text
from app.db.session import create_engine_and_session, get_database_url
from app.models.base import Base
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.models.customer import Customer
from app.models.contract import Contract
from app.models.event import Event
from app.services.auth_service import AuthService
from decimal import Decimal
import datetime
from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME


def drop_create_database():
    # connect to server without specifying a DB
    conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS or "")
    try:
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
            cur.execute(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
    finally:
        conn.close()


def seed(session):
    # roles
    r_management = Role(name="management")
    r_sales = Role(name="sales")
    r_support = Role(name="support")
    session.add_all([r_management, r_sales, r_support])
    session.flush()

    # permissions (crud names)
    perms = [
        "user:create", "user:read", "user:update", "user:delete",
        "customer:create", "customer:read", "customer:update", "customer:delete",
        "contract:create", "contract:read", "contract:update", "contract:delete",
        "event:create", "event:read", "event:update", "event:delete",
    ]
    perm_objs = {name: Permission(name=name) for name in perms}
    session.add_all(perm_objs.values())
    session.flush()

    # assign permissions according to permissions.md
    # management: user CRUD, contract CRUD, customer read, event read/update (only support id)
    mg_perms = [
        perm_objs[p] for p in ["user:create","user:read","user:update","user:delete",
        "contract:create","contract:read","contract:update","contract:delete",
        "customer:read","event:read","event:update"]
    ]
    r_management.permissions = mg_perms

    # sales: customer create/read/update/delete (only own), contract read/update (linked to their clients), event create (only for their clients when contract signed), event read
    sales_perms = [perm_objs[p] for p in ["customer:create","customer:read","customer:update","customer:delete","contract:read","contract:update","event:create","event:read","event:delete"]]
    r_sales.permissions = sales_perms

    # support: customer read, contract read, event read/update (only those linked)
    support_perms = [perm_objs[p] for p in ["customer:read","contract:read","event:read","event:update"]]
    r_support.permissions = support_perms

    session.flush()

    # create users: 3 sales, 2 management, 2 support
    auth = AuthService()
    users = []
    # management
    manager1 = User(role_id=r_management.id, user_first_name="Manager", user_last_name="One", email="manager1@example.com", phone_number="+33100000001", username="manager1", password_hash=auth.hash_password("password"))
    manager2 = User(role_id=r_management.id, user_first_name="Manager", user_last_name="Two", email="manager2@example.com", phone_number="+33100000002", username="manager2", password_hash=auth.hash_password("password"))
    users.extend([manager1, manager2])

    # sales
    sales1 = User(role_id=r_sales.id, user_first_name="Sales", user_last_name="One", email="sales1@example.com", phone_number="+33100000011", username="sales1", password_hash=auth.hash_password("password"))
    sales2 = User(role_id=r_sales.id, user_first_name="Sales", user_last_name="Two", email="sales2@example.com", phone_number="+33100000012", username="sales2", password_hash=auth.hash_password("password"))
    sales3 = User(role_id=r_sales.id, user_first_name="Sales", user_last_name="Three", email="sales3@example.com", phone_number="+33100000013", username="sales3", password_hash=auth.hash_password("password"))
    users.extend([sales1, sales2, sales3])

    # support
    support1 = User(role_id=r_support.id, user_first_name="Support", user_last_name="One", email="support1@example.com", phone_number="+33100000021", username="support1", password_hash=auth.hash_password("password"))
    support2 = User(role_id=r_support.id, user_first_name="Support", user_last_name="Two", email="support2@example.com", phone_number="+33100000022", username="support2", password_hash=auth.hash_password("password"))
    users.extend([support1, support2])

    session.add_all(users)
    session.flush()

    # Customers and contracts/events distribution per spec
    # sales1: no client

    # sales2: 2 clients
    cust_a = Customer(user_sales_id=sales2.id, customer_first_name="ClientA", customer_last_name="Alpha", email="clienta@example.com", phone_number="+33900000001", company_name="Company A")
    cust_b = Customer(user_sales_id=sales2.id, customer_first_name="ClientB", customer_last_name="Beta", email="clientb@example.com", phone_number="+33900000002", company_name="Company B")
    session.add_all([cust_a, cust_b])
    session.flush()

    # cust_a: no contract no event

    # cust_b: 4 contracts created by manager1
    c1 = Contract(customer_id=cust_b.id, user_management_id=manager1.id, contract_number="C-B-1", total_amount=Decimal("1000.00"), balance_due=Decimal("1000.00"), signed=False)
    c2 = Contract(customer_id=cust_b.id, user_management_id=manager1.id, contract_number="C-B-2", total_amount=Decimal("2000.00"), balance_due=Decimal("1000.00"), signed=True)
    c3 = Contract(customer_id=cust_b.id, user_management_id=manager1.id, contract_number="C-B-3", total_amount=Decimal("3000.00"), balance_due=Decimal("0.00"), signed=True)
    c4 = Contract(customer_id=cust_b.id, user_management_id=manager1.id, contract_number="C-B-4", total_amount=Decimal("4000.00"), balance_due=Decimal("0.00"), signed=True)
    session.add_all([c1, c2, c3, c4])
    session.flush()

    # c4 has 2 events: one without support, one with support assigned
    now = datetime.datetime.now(datetime.timezone.utc)
    e1 = Event(contract_id=c4.id, customer_id=cust_b.id, user_support_id=None, event_name="Event B4-1", event_number="E-B4-1", start_datetime=now, end_datetime=now + datetime.timedelta(hours=2), location="Paris", attendees=50, note="No support assigned")
    e2 = Event(contract_id=c4.id, customer_id=cust_b.id, user_support_id=support1.id, event_name="Event B4-2", event_number="E-B4-2", start_datetime=now + datetime.timedelta(days=1), end_datetime=now + datetime.timedelta(days=1, hours=4), location="Lyon", attendees=80, note="With support assigned")
    session.add_all([e1, e2])

    # sales3: 1 client with 2 contracts created by manager2
    cust_c = Customer(user_sales_id=sales3.id, customer_first_name="ClientC", customer_last_name="Gamma", email="clientc@example.com", phone_number="+33900000003", company_name="Company C")
    session.add(cust_c)
    session.flush()

    c5 = Contract(customer_id=cust_c.id, user_management_id=manager2.id, contract_number="C-C-1", total_amount=Decimal("1500.00"), balance_due=Decimal("1500.00"), signed=True)
    c6 = Contract(customer_id=cust_c.id, user_management_id=manager2.id, contract_number="C-C-2", total_amount=Decimal("2500.00"), balance_due=Decimal("0.00"), signed=True)
    session.add_all([c5, c6])
    session.flush()

    # c6 has 2 events: one with other support assigned, one without support
    e3 = Event(contract_id=c6.id, customer_id=cust_c.id, user_support_id=support2.id, event_name="Event C6-1", event_number="E-C6-1", start_datetime=now + datetime.timedelta(days=2), end_datetime=now + datetime.timedelta(days=2, hours=3), location="Nice", attendees=30, note="Support2 assigned")
    e4 = Event(contract_id=c6.id, customer_id=cust_c.id, user_support_id=None, event_name="Event C6-2", event_number="E-C6-2", start_datetime=now + datetime.timedelta(days=3), end_datetime=now + datetime.timedelta(days=3, hours=2), location="Bordeaux", attendees=20, note="No support assigned")
    session.add_all([e3, e4])

    session.commit()


def main():
    drop_create_database()
    engine, SessionLocal = create_engine_and_session()
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        seed(session)
        print("Database initialized and seeded.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
