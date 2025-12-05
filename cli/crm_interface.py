import click
from pathlib import Path
from app.db.session import get_session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.permission_service import PermissionService
from app.models.user import User
from cli.views.users import UsersView
from cli.views.customers import CustomersView
from cli.views.contracts import ContractsView
from cli.views.events import EventsView
from cli.helpers import prompt_menu


_TOKEN_FILE = Path(__file__).resolve().parent.parent / ".epic_events_token"


def _read_token() -> str | None:
    """
    Lit le token d'authentification depuis le fichier local. Retourne None si le fichier n'existe pas
    ou en cas d'erreur de lecture
    """
    try:
        data = _TOKEN_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    except OSError:
        return None
    return data or None


def _write_token(token: str) -> None:
    """
    Écrit le token d'authentification dans un fichier local. Ignore les erreurs d'écriture.
    """
    try:
        _TOKEN_FILE.write_text(token.strip(), encoding="utf-8")
    except OSError:
        pass


def _clear_token() -> None:
    """
    Supprime le fichier de token d'authentification local. Ignore les erreurs de suppression.
    """
    try:
        _TOKEN_FILE.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _user_from_token(session, auth_service: AuthService):
    """
    Tente de récupérer l'utilisateur correspondant au token d'authentification
    """

    token = _read_token()
    if not token:
        return None
    try:
        payload = auth_service.decode_token(token)
        user_id = int(payload.get("sub", ""))
    except Exception:
        _clear_token()
        return None
    if not user_id:
        _clear_token()
        return None
    user = session.get(User, user_id)
    if not user:
        _clear_token()
        return None
    return user


def prompt_login(session, auth_service: AuthService):
    """
    Invite l'utilisateur à se connecter en demandant son nom d'utilisateur et son mot de passe.
    Vérifie les informations d'identification et retourne l'utilisateur si l'authentification réussit.
    """
    click.echo("Bienvenue sur Epic Events CRM")
    username = click.prompt("Nom d'utilisateur")
    password = click.prompt("Mot de passe", hide_input=True)
    user_repo = UserRepository(session)
    user = user_repo.get_by_username(username)
    if not user or not auth_service.verify_password(user.password_hash, password):
        click.echo("Authentification échouée")
        return None
    
    click.echo(f"\nConnecté en tant que {user.username} ({user.role.name})")
    return user


def run_interface():
    """
    Lance l'interface CLI principale, gérant l'authentification et la navigation
    entre les différents menus en fonction des permissions de l'utilisateur.
    """
    # initialise la session DB et le service d'authentification
    session = get_session()
    # initialise le service d'authentification
    auth = AuthService()
    # boucle principale de l'interface CLI
    try:
        while True:
            user = _user_from_token(session, auth)
            if user:
                click.echo(f"\nSession restaurée pour {user.username} ({user.role.name})")
            else:
                user = prompt_login(session, auth)
            if not user:
                continue
            token = auth.create_token(user.id)
            _write_token(token)

            # initialise le service de permissions
            perm_service = PermissionService(session)

            while True:
                # affiche le menu principal selon les permissions de l'utilisateur
                services = perm_service.available_menus_for_user(user)
                click.echo('\n=== Menu principal ===\n')
                options = []
                # si l'utilisateur a accès à la gestion des utilisateurs
                if 'display_menu_users' in services:
                    # gestion des utilisateurs
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

                handler = prompt_menu(options, prompt='Choix', return_label='0=Déconnexion')
                if handler is None:
                    click.echo("Déconnexion...")
                    _clear_token()
                    break
                handler(user, session, perm_service)
    finally:
        session.close()
