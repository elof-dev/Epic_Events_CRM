from app.services.user_service import UserService
import click
from cli.helpers import prompt_select_option
from app.db.transaction import transactional


def get_user_menu_options(user, perm_service):
    options = []
    if perm_service.user_has_permission(user, 'user:read'):
        options.append(('Afficher tous les utilisateurs', 'list_all'))
        options.append(('Filtrer par ID', 'filter_id'))
    if perm_service.user_has_permission(user, 'user:create'):
        options.append(('Créer un utilisateur', 'create'))
    return options


def main_user_menu(user, session, perm_service):
    click.echo('\n=== Gestion des utilisateurs ===')
    while True:
        options = get_user_menu_options(user, perm_service)
        action = prompt_select_option(options, prompt='Choix')
        if action is None:
            return
        if action == 'list_all':
            list_all_users(user, session, perm_service)
        elif action == 'filter_id':
            filter_user_by_id(user, session, perm_service)
        elif action == 'create':
            create_user(user, session, perm_service)


def create_user(user, session, perm_service):
    user_service = UserService(session, perm_service)
    # commence par vérifier les permissions, même si en théorie le menu ne propose cette action
    # que si l'utilisateur a la permission
    if not perm_service.user_has_permission(user, 'user:create') or user.role.name != 'management':
        click.echo("Permission refusée: création impossible")
        return
    try:
        click.echo('Règles de saisie :')
        click.echo("- Prénom/Nom : max 100 caractères. Autorisés : lettres, espaces, apostrophes, tirets")
        click.echo("- Nom d'utilisateur : max 100 caractères. Autorisés : lettres et chiffres seulement")
        click.echo("- Email : format email, max 255 caractères")
        click.echo("- Téléphone : max 20 caractères. Autorisés : chiffres et un préfixe + optionnel")
        first = click.prompt('Prénom')
        last = click.prompt('Nom')
        username = click.prompt('Nom d\'utilisateur')
        email = click.prompt('Email')
        phone = click.prompt('Téléphone')
        # sélection du rôle parmi ceux en base et pas en dur
        from app.models.role import Role
        roles = session.query(Role).all()
        if not roles:
            click.echo('Aucun rôle disponible en base, annulation')
            return
        role_options = [(r.name, r.id) for r in roles]
        role_id = prompt_select_option(role_options, prompt='Choisir rôle')
        if role_id is None:
            click.echo('Annulé')
            return
        # mot de passe avec saisie masquée
        password = click.prompt('Mot de passe', hide_input=True)
        fields = {
            'user_first_name': first,
            'user_last_name': last,
            'username': username,
            'email': email,
            'phone_number': phone,
            'role_id': role_id,
            'password': password,
        }
        with transactional(session):
            new_user = user_service.create(user, **fields)
        click.echo(f'Utilisateur créé id={new_user.id}')
    except Exception as e:
        click.echo(f'Erreur création: {e}')

def update_user(current_user, session, perm_service, target_user_id):
    from app.models.user import User
    user_service = UserService(session, perm_service)
    target = session.get(User, target_user_id)
    if not target:
        click.echo('Utilisateur introuvable')
        return
    if not perm_service.user_has_permission(current_user, 'user:update'):
        click.echo('Permission refusée')
        return
    update_fields = [
        ('Prénom', 'user_first_name'),
        ('Nom', 'user_last_name'),
        ('Nom d\'utilisateur', 'username'),
        ('Email', 'email'),
        ('Téléphone', 'phone_number'),
        ('Role', 'role_id'),
        ('Mot de passe', 'password'),
    ]
    while True:
        field_opts = [(label, field) for label, field in update_fields]
        field_choice = prompt_select_option(field_opts, prompt='Choisir champ')
        if field_choice is None:
            break
        label = next(lbl for lbl, fld in update_fields if fld == field_choice)
        field = field_choice
        if field == 'password':
            new_val = click.prompt(f"{label} (laisser vide pour annuler)", hide_input=True, default='')
            if not new_val:
                click.echo('Annulé')
                continue
            upd = {'password': new_val}
        else:
            current_val = getattr(target, field) if field != 'role_id' else getattr(target.role, 'name', '')
            if field == 'role_id':
                # fetch roles from DB and propose selection (return id)
                from app.models.role import Role
                roles = session.query(Role).all()
                role_opts = [(r.name, r.id) for r in roles]
                new_val = prompt_select_option(role_opts, prompt='Choisir rôle')
                if new_val is None:
                    click.echo('Annulé')
                    continue
                upd = {'role_id': new_val}
            else:
                new_val = click.prompt(label, default=current_val if current_val is not None else '')
                # preserve current value when prompt returns empty string
                upd = {field: (new_val if new_val != '' else current_val)}
        try:
            with transactional(session):
                user_service.update(current_user, target.id, **upd)
            click.echo('Champ mis à jour')
            target = session.get(User, target_user_id)
        except Exception as e:
            click.echo(f'Erreur mise à jour: {e}')


def delete_user(current_user, session, perm_service, target_user_id):
    from app.models.user import User
    user_service = UserService(session, perm_service)
    target = session.get(User, target_user_id)
    if not target:
        click.echo('Utilisateur introuvable')
        return
    if not perm_service.user_has_permission(current_user, 'user:delete'):
        click.echo('Permission refusée')
        return
    try:
        confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
        if confirm.lower().startswith('o'):
            with transactional(session):
                user_service.delete(current_user, target.id)
            click.echo('Utilisateur supprimé')
    except Exception as e:
        click.echo(f'Erreur suppression: {e}')


def list_all_users(user, session, perm_service):
    user_service = UserService(session, perm_service)
    try:
        users = user_service.list_all(user)
        click.echo('\nListe des utilisateurs:')
        user_options = [(
            f"{u.id}: {u.user_first_name} {u.user_last_name} ({u.username})",
            u.id,
        ) for u in users]
        choice = prompt_select_option(user_options, prompt='Choisir utilisateur')
        if choice is None:
            return
        display_detail_users(user, session, perm_service, choice)
    except Exception as e:
        click.echo(f'Erreur: {e}')


def filter_user_by_id(user, session, perm_service):
    user_service = UserService(session, perm_service)
    try:
        sel = click.prompt('Saisir l\'ID utilisateur (0=Retour)', type=int)
        if sel == 0:
            return
        target = user_service.get_by_id(user, sel)
        if not target:
            click.echo('Utilisateur introuvable')
            return
        display_detail_users(user, session, perm_service, target.id)
    except Exception as e:
        click.echo(f'Erreur: {e}')



def display_detail_users(current_user, session, perm_service, target_user_id):
    from app.models.user import User
    target = session.get(User, target_user_id)
    if not target:
        click.echo('Utilisateur introuvable')
        return
    click.echo(f"\nID: {target.id}\nPrénom: {target.user_first_name}\nNom: {target.user_last_name}\nUsername: {target.username}\nEmail: {target.email}\nTéléphone: {target.phone_number}\nRole: {getattr(target.role, 'name', target.role_id)}")
    actions = []
    if perm_service.user_has_permission(current_user, 'user:update') and current_user.role.name == 'management':
        actions.append(('Modifier', 'update'))
    if perm_service.user_has_permission(current_user, 'user:delete') and current_user.role.name == 'management':
        actions.append(('Supprimer', 'delete'))
    action = prompt_select_option(actions, prompt='Choix')
    if action is None:
        return
    if action == 'update':
        update_user(current_user, session, perm_service, target.id)
    elif action == 'delete':
        delete_user(current_user, session, perm_service, target.id)
