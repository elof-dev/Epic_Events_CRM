import click
from app.db.session import create_engine_and_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from app.services.customer_service import CustomerService
from app.services.contract_service import ContractService
from app.services.event_service import EventService
from cli.crm_interface import run_interface
from app.db import init_db as init_db_module


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


# The main top-level orchestration has been moved to `cli.crm_interface.run_interface`.
# This keeps `cli.main` as a thin CLI entrypoint.




@click.group()
def cli():
    pass


@cli.command()
def run():
    """Lancer l'interface CLI"""
    # delegate to crm_interface
    run_interface()


@cli.command('init-db')
def init_db():
    """Initialiser la base de données (DROP + CREATE + SEED)."""
    click.echo('Initialisation de la base de données (DROP + CREATE + SEED)...')
    init_db_module.main()
    click.echo('Initialisation terminée.')


if __name__ == "__main__":
    cli()
