import click
from app.db.session import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from cli.views.users import UsersView
from cli.views.customers import CustomersView
from cli.views.contracts import ContractsView
from cli.views.events import EventsView
from cli.helpers import prompt_menu



def prompt_login(session):
    click.echo("Bienvenue sur Epic Events CRM")
    username = click.prompt("Nom d'utilisateur")
    password = click.prompt("Mot de passe", hide_input=True)
    user_repo = UserRepository(session)
    user = user_repo.get_by_username(username)
    auth = AuthService()
    if not user or not auth.verify_password(user.password_hash, password):
        click.echo("Authentification échouée")
        return None
    
    click.echo(f"\nConnecté en tant que {user.username} ({user.role.name})")
    return user


def run_interface():
    """Start the CRM interface: login loop then main menu loop.

    This centralises the UI orchestration and delegates sub-menus to
    handlers in `cli.views`.
    """
    session = get_session()
    try:
        while True:
            user = prompt_login(session)
            if not user:
                continue

            perm_service = PermissionService(session)

            while True:
                services = perm_service.available_menus_for_user(user)
                click.echo('\nMenu principal :\n')
                options = []
                if 'display_menu_users' in services:
                    def users_menu_handler(current_user, db_session, perm_service):
                        UsersView(db_session, perm_service).main_user_menu(current_user)
                    options.append(('Gestion des utilisateurs', users_menu_handler))
                if 'display_menu_customers' in services:
                    def customers_menu_handler(current_user, db_session, perm_service):
                        CustomersView(db_session, perm_service).main_customer_menu(current_user)
                    options.append(('Gestion des clients', customers_menu_handler))
                if 'display_menu_contracts' in services:
                    def contracts_menu_handler(current_user, db_session, perm_service):
                        ContractsView(db_session, perm_service).main_contract_menu(current_user)
                    options.append(('Gestion des contrats', contracts_menu_handler))
                if 'display_menu_events' in services:
                    def events_menu_handler(current_user, db_session, perm_service):
                        EventsView(db_session, perm_service).main_event_menu(current_user)
                    options.append(('Gestion des évènements', events_menu_handler))

                handler = prompt_menu(options, prompt='Choix')
                if handler is None:
                    click.echo("Déconnexion...")
                    break
                handler(user, session, perm_service)
    finally:
        session.close()
