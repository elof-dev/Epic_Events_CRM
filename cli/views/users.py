from app.services.user_service import UserService
import click
from cli.helpers import prompt_select_option


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
    user_service = UserService(session, perm_service)
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
    if not perm_service.user_has_permission(user, 'user:create'):
        click.echo("Permission refusée: création impossible")
        return
    try:
        first = click.prompt('Prénom')
        last = click.prompt('Nom')
        username = click.prompt('Nom d\'utilisateur')
        email = click.prompt('Email')
        phone = click.prompt('Téléphone', default='')
        role_name = click.prompt('Role (management|sales|support)')
        password = click.prompt('Mot de passe', hide_input=True)
        fields = {
            'user_first_name': first,
            'user_last_name': last,
            'username': username,
            'email': email,
            'phone_number': phone or None,
            'role_name': role_name,
            'password': password,
        }
        new_u = user_service.create(user, **fields)
        click.echo(f'Utilisateur créé id={new_u.id}')
    except Exception as e:
        click.echo(f'Erreur création: {e}')


def list_all_users(user, session, perm_service):
    user_service = UserService(session, perm_service)
    try:
        users = user_service.list_all(user)
        display_list_users(users)
        opts = [(f"{u.id}: {u.user_first_name} {u.user_last_name}", u.id) for u in users]
        choice = prompt_select_option(opts, prompt='Choisir utilisateur')
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


def display_list_users(users):
    click.echo('\nListe des utilisateurs:')
    for u in users:
        role_name = u.role.name if getattr(u, 'role', None) else str(getattr(u, 'role_id', ''))
        print_user(u)


def display_detail_users(current_user, session, perm_service, target_user_id):
    from app.models.user import User
    user_service = UserService(session, perm_service)
    target = session.get(User, target_user_id)
    if not target:
        click.echo('Utilisateur introuvable')
        return
    click.echo(f"\nID: {target.id}\nPrénom: {target.user_first_name}\nNom: {target.user_last_name}\nUsername: {target.username}\nEmail: {target.email}\nTéléphone: {target.phone_number}\nRole: {getattr(target.role, 'name', target.role_id)}")
    actions = []
    if perm_service.user_has_permission(current_user, 'user:update'):
        actions.append(('Modifier', 'update'))
    if perm_service.user_has_permission(current_user, 'user:delete'):
        actions.append(('Supprimer', 'delete'))
    action = prompt_select_option(actions, prompt='Choix')
    if action is None:
        return
    if action == 'update':
        update_user(current_user, session, perm_service, target.id)
    elif action == 'delete':
        delete_user(current_user, session, perm_service, target.id)


def update_user(current_user, session, perm_service, target_user_id):
    from app.models.user import User
    user_service = UserService(session, perm_service)
    target = session.get(User, target_user_id)
    if not target:
        click.echo('Utilisateur introuvable')
        return
    if not perm_service.user_has_permission(current_user, 'user:update'):
        click.echo('Permission refusée: mise à jour impossible')
        return
    mod_fields = [
        ('Prénom', 'user_first_name'),
        ('Nom', 'user_last_name'),
        ('Email', 'email'),
        ('Téléphone', 'phone_number'),
        ('Role', 'role_name'),
        ('Mot de passe', 'password'),
    ]
    while True:
        field_opts = [(label, field) for label, field in mod_fields]
        field_choice = prompt_select_option(field_opts, prompt='Choisir champ')
        if field_choice is None:
            break
        label = next(lbl for lbl, fld in mod_fields if fld == field_choice)
        field = field_choice
        if field == 'password':
            new_val = click.prompt(f"{label} (laisser vide pour annuler)", hide_input=True, default='')
            if not new_val:
                click.echo('Annulé')
                continue
            upd = {'password': new_val}
        else:
            current_val = getattr(target, field) if field != 'role_name' else getattr(target.role, 'name', '')
            new_val = click.prompt(label, default=current_val if current_val is not None else '')
            if field == 'role_name':
                upd = {'role_name': new_val}
            else:
                upd = {field: new_val or None}
        try:
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
        click.echo('Permission refusée: suppression impossible')
        return
    try:
        confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
        if confirm.lower().startswith('o'):
            user_service.delete(current_user, target.id)
            click.echo('Utilisateur supprimé')
    except Exception as e:
        click.echo(f'Erreur suppression: {e}')


def print_user(u):
    role_name = u.role.name if getattr(u, 'role', None) else str(getattr(u, 'role_id', ''))
    click.echo(f"{u.id}: {u.user_first_name} {u.user_last_name} ({u.username}) - role={role_name}")
