import click
from app.db.session import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from cli.views.users import main_user_menu
from cli.views.customers import main_customer_menu
from cli.views.contracts import main_contract_menu
from cli.views.events import main_event_menu



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
    click.echo(f"Connecté en tant que {user.username} ({user.role.name})")
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
                click.echo('\nMenu principal :')
                options = []
                if 'display_menu_users' in services:
                    options.append(('Gestion des utilisateurs', main_user_menu))
                if 'display_menu_customers' in services:
                    options.append(('Gestion des clients', main_customer_menu))
                if 'display_menu_contracts' in services:
                    options.append(('Gestion des contrats', main_contract_menu))
                if 'display_menu_events' in services:
                    options.append(('Gestion des évènements', main_event_menu))

                click.echo('0. Déconnexion')
                for idx, (label, _) in enumerate(options, start=1):
                    click.echo(f"{idx}. {label}")
                choice = click.prompt("Choix", type=int)
                if choice == 0:
                    click.echo("Déconnexion...")
                    break
                if 1 <= choice <= len(options):
                    _, handler = options[choice - 1]
                    handler(user, session, perm_service)
                else:
                    click.echo("Choix invalide")
    finally:
        session.close()
