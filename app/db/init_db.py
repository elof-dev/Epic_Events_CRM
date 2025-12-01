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
    """
    Supprime puis crée la base de données MySQL utilisée par l'application

    """
    # ouvre une connexion MySQL qui va chercher les identifiants dans .env
    conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS or "")
    try:
        # envoie les commandes SQL DROP/CREATE DATABASE
        with conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
            # Create with utf8mb4 for full Unicode support to handle all characters
            cur.execute(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
    finally:
        conn.close()


def seed(session):
    """
    Remplit la base de données avec des données de démonstration (seed).

    Paramètre :
    - `session` : une session SQLAlchemy active sur laquelle les objets seront
        créés et persistés.
        session.add_all(...) ajoute les objets à la session en attente de commit.
        session.flush() force l'envoi des INSERTs pour obtenir les IDs.
        session.commit() persiste définitivement les changements.

    Comportement :
    - crée des rôles, permissions, utilisateurs, clients, contrats et événements
        conformément au jeu de données attendu par l'application.
    - appelle `session.commit()` à la fin pour persister toutes les entités.

    Récapitulatif des données créées :
    - Rôles : management, sales, support
    - Permissions : une liste complète de permissions CRUD pour les entités.
    - Utilisateurs : 2 managers, 3 sales, 2 support.
    - Clients : 2 clients pour sales2 (aucun pour sales1), 1 client pour sales3.
    - Contrats : 4 contrats pour un client de sales2, 2 contrats pour le client de sales3.
    - Événements : 2 événements pour un contrat de sales2, 2 événements pour un contrat de sales3.

    """
    # roles
    role_management = Role(name="management")
    role_sales = Role(name="sales")
    role_support = Role(name="support")
    session.add_all([role_management, role_sales, role_support])
    session.flush()

    # permissions
    permissions_list = [
        "user:create", "user:read", "user:update", "user:delete",
        "customer:create", "customer:read", "customer:update", "customer:delete",
        "contract:create", "contract:read", "contract:update", "contract:delete",
        "event:create", "event:read", "event:update", "event:delete",
    ]
    # creation des objets Permission pour chaque nom dans la liste
    permission_objects = {name: Permission(name=name) for name in permissions_list}
    session.add_all(permission_objects.values())
    session.flush()

    management_permissions = [permission_objects[p] for p in [
        "user:create", "user:read", "user:update", "user:delete",
        "contract:create", "contract:read", "contract:update", "contract:delete",
        "customer:read", 
        "event:read", "event:update",
    ]]
    role_management.permissions = management_permissions

    sales_permissions = [permission_objects[p] for p in [
        "customer:create", "customer:read", "customer:update", "customer:delete",
        "contract:read", "contract:update",
        "event:create", "event:read", "event:delete",
    ]]
    role_sales.permissions = sales_permissions

    support_permissions = [permission_objects[p] for p in [
        "customer:read", 
        "contract:read", 
        "event:read", "event:update",
    ]]
    role_support.permissions = support_permissions

    session.flush()

    # create users: 3 sales, 2 management, 2 support
    auth = AuthService()
    users = []
    # management
    manager1 = User(role_id=role_management.id, user_first_name="Manager", user_last_name="One", email="manager1@example.com", phone_number="+33100000001", username="manager1", password_hash=auth.hash_password("password"))
    manager2 = User(role_id=role_management.id, user_first_name="Manager", user_last_name="Two", email="manager2@example.com", phone_number="+33100000002", username="manager2", password_hash=auth.hash_password("password"))
    users.extend([manager1, manager2])

    # sales
    sales1 = User(role_id=role_sales.id, user_first_name="Sales", user_last_name="One", email="sales1@example.com", phone_number="+33100000011", username="sales1", password_hash=auth.hash_password("password"))
    sales2 = User(role_id=role_sales.id, user_first_name="Sales", user_last_name="Two", email="sales2@example.com", phone_number="+33100000012", username="sales2", password_hash=auth.hash_password("password"))
    sales3 = User(role_id=role_sales.id, user_first_name="Sales", user_last_name="Three", email="sales3@example.com", phone_number="+33100000013", username="sales3", password_hash=auth.hash_password("password"))
    users.extend([sales1, sales2, sales3])

    # support
    support1 = User(role_id=role_support.id, user_first_name="Support", user_last_name="One", email="support1@example.com", phone_number="+33100000021", username="support1", password_hash=auth.hash_password("password"))
    support2 = User(role_id=role_support.id, user_first_name="Support", user_last_name="Two", email="support2@example.com", phone_number="+33100000022", username="support2", password_hash=auth.hash_password("password"))
    users.extend([support1, support2])

    session.add_all(users)
    session.flush()

    # Customers and contracts/events distribution per spec
    # sales1: no client

    # sales2: 2 clients
    customer_a = Customer(user_sales_id=sales2.id, customer_first_name="Client", customer_last_name="A", email="clienta@example.com", phone_number="+33900000001", company_name="Company A")
    customer_b = Customer(user_sales_id=sales2.id, customer_first_name="Client", customer_last_name="B", email="clientb@example.com", phone_number="+33900000002", company_name="Company B")
    session.add_all([customer_a, customer_b])
    session.flush()

    # cust_a: no contract no event

    # customer_b: 4 contracts created by manager1
    contract_1 = Contract(customer_id=customer_b.id, user_management_id=manager1.id, total_amount=Decimal("1000.00"), balance_due=Decimal("1000.00"), signed=False)
    contract_2 = Contract(customer_id=customer_b.id, user_management_id=manager1.id, total_amount=Decimal("2000.00"), balance_due=Decimal("1000.00"), signed=True)
    contract_3 = Contract(customer_id=customer_b.id, user_management_id=manager1.id, total_amount=Decimal("3000.00"), balance_due=Decimal("0.00"), signed=True)
    contract_4 = Contract(customer_id=customer_b.id, user_management_id=manager1.id, total_amount=Decimal("4000.00"), balance_due=Decimal("0.00"), signed=True)
    session.add_all([contract_1, contract_2, contract_3, contract_4])
    session.flush()

    # c4 has 2 events: one without support, one with support assigned
    now = datetime.datetime.now(datetime.timezone.utc)
    event_1 = Event(contract_id=contract_4.id, customer_id=customer_b.id, user_support_id=None, event_name="Name_Event_1", start_datetime=now, end_datetime=now + datetime.timedelta(hours=2), location="Paris", attendees=50, note="No support assigned")
    event_2 = Event(contract_id=contract_4.id, customer_id=customer_b.id, user_support_id=support1.id, event_name="Name_Event_2", start_datetime=now + datetime.timedelta(days=1), end_datetime=now + datetime.timedelta(days=1, hours=4), location="Lyon", attendees=80, note="With support assigned")
    session.add_all([event_1, event_2])

    # sales3: 1 client with 2 contracts created by manager2
    customer_c = Customer(user_sales_id=sales3.id, customer_first_name="Client", customer_last_name="C", email="clientc@example.com", phone_number="+33900000003", company_name="Company C")
    session.add(customer_c)
    session.flush()

    contract_5 = Contract(customer_id=customer_c.id, user_management_id=manager2.id, total_amount=Decimal("1500.00"), balance_due=Decimal("1500.00"), signed=True)
    contract_6 = Contract(customer_id=customer_c.id, user_management_id=manager2.id, total_amount=Decimal("2500.00"), balance_due=Decimal("0.00"), signed=True)
    session.add_all([contract_5, contract_6])
    session.flush()

    # c6 has 2 events: one with other support assigned, one without support
    event_3 = Event(contract_id=contract_6.id, customer_id=customer_c.id, user_support_id=support2.id, event_name="Name_Event_3", start_datetime=now + datetime.timedelta(days=2), end_datetime=now + datetime.timedelta(days=2, hours=3), location="Nice", attendees=30, note="Support2 assigned")
    event_4 = Event(contract_id=contract_6.id, customer_id=customer_c.id, user_support_id=None, event_name="Name_Event_4", start_datetime=now + datetime.timedelta(days=3), end_datetime=now + datetime.timedelta(days=3, hours=2), location="Bordeaux", attendees=20, note="No support assigned")
    session.add_all([event_3, event_4])

    session.commit()


def main():
    """
    Point d'entrée d'initialisation de la base de données.

    Étapes exécutées :
    1. suppression/création de la base MySQL via `drop_create_database()` ;
    2. création des tables SQLAlchemy (`Base.metadata.create_all` sur l'engine) ;
    3. exécution du `seed(session)` pour pré-remplir les données ;
    4. fermeture propre de la session.

    """

    drop_create_database()
    engine, SessionLocal = create_engine_and_session()
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        seed(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
