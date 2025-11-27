import click
from app.db.session import create_engine_and_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from app.services.customer_service import CustomerService
from app.services.contract_service import ContractService
from app.services.event_service import EventService
from cli.views import (
    manage_users_menu,
    manage_customers_menu,
    manage_contracts_menu,
    manage_events_menu,
)


def get_session():
    engine, SessionLocal = create_engine_and_session()
    return SessionLocal()


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


def show_main_menu(user, session):
    perm_service = PermissionService(session)
    cust_service = CustomerService(session, perm_service)
    contract_service = ContractService(session, perm_service)
    event_service = EventService(session, perm_service)

    while True:
        services = perm_service.available_services_for_user(user)
        click.echo('\nMenu principal :')
        options = []
        if 'manage_users' in services:
            options.append(('Gestion des utilisateurs', manage_users_menu))
        if 'manage_customers' in services:
            options.append(('Gestion des clients', manage_customers_menu))
        if 'manage_contracts' in services:
            options.append(('Gestion des contrats', manage_contracts_menu))
        if 'manage_events' in services:
            options.append(('Gestion des évènements', manage_events_menu))
        for idx, (label, _) in enumerate(options, start=1):
            click.echo(f"{idx}. {label}")
        click.echo(f"{len(options)+1}. Déconnexion")
        choice = click.prompt("Choix", type=int)
        if choice == len(options) + 1:
            click.echo("Déconnexion...")
            break
        if 1 <= choice <= len(options):
            _, handler = options[choice-1]
            handler(user, session, perm_service)
        else:
            click.echo("Choix invalide")




@click.group()
def cli():
    pass


@cli.command()
def run():
    """Lancer l'interface CLI en français"""
    session = get_session()
    try:
        user = prompt_login(session)
        if not user:
            return
        show_main_menu(user, session)
    finally:
        session.close()


if __name__ == "__main__":
    cli()
