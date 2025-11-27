from app.services.user_service import UserService
import click


def manage_users_menu(user, session, perm_service):
    click.echo('\n=== Gestion des utilisateurs ===')
    user_service = UserService(session, perm_service)
    while True:
        click.echo('1. Afficher tous les utilisateurs')
        click.echo('2. Filtrer par ID')
        click.echo('3. Créer un utilisateur')
        click.echo('4. Retour')
        choice = click.prompt('Choix', type=int)
        if choice == 1:
            try:
                users = user_service.list_all(user)
                click.echo('\nListe des utilisateurs:')
                for u in users:
                    role_name = u.role.name if getattr(u, 'role', None) else str(getattr(u, 'role_id', ''))
                    click.echo(f"{u.id}: {u.user_first_name} {u.user_last_name} ({u.username}) - role={role_name}")
                # choose an id to view details
                sel = click.prompt('\nChoisissez un id d\'utilisateur (0 pour retour)', type=int)
                if sel == 0:
                    continue
                target = user_service.get_by_id(user, sel)
                if not target:
                    click.echo('Utilisateur introuvable')
                    continue
                _user_detail_loop(user, session, perm_service, user_service, target)
            except Exception as e:
                click.echo(f'Erreur: {e}')
        elif choice == 2:
            try:
                sel = int(click.prompt('Saisir l\'ID utilisateur'))
                target = user_service.get_by_id(user, sel)
                if not target:
                    click.echo('Utilisateur introuvable')
                    continue
                _user_detail_loop(user, session, perm_service, user_service, target)
            except Exception as e:
                click.echo(f'Erreur: {e}')
        elif choice == 3:
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
        else:
            break


def _user_detail_loop(current_user, session, perm_service, user_service, target_user):
    from app.models.user import User
    while True:
        # refresh
        target_user = session.get(User, target_user.id)
        click.echo(f"\nID: {target_user.id}\nPrénom: {target_user.user_first_name}\nNom: {target_user.user_last_name}\nUsername: {target_user.username}\nEmail: {target_user.email}\nTéléphone: {target_user.phone_number}\nRole: {getattr(target_user.role, 'name', target_user.role_id)}")
        click.echo('\n1. Modifier')
        click.echo('2. Supprimer')
        click.echo('3. Retour')
        choice = click.prompt('Choix', type=int)
        if choice == 1:
            # iterative field edits
            mod_fields = [
                ('Prénom', 'user_first_name'),
                ('Nom', 'user_last_name'),
                ('Email', 'email'),
                ('Téléphone', 'phone_number'),
                ('Role', 'role_name'),
                ('Mot de passe', 'password'),
            ]
            while True:
                click.echo('\nChamps modifiables:')
                for idx, (label, _) in enumerate(mod_fields, start=1):
                    click.echo(f"{idx}. {label}")
                click.echo(f"{len(mod_fields)+1}. Retour")
                fchoice = click.prompt('Choisir champ', type=int)
                if fchoice == len(mod_fields) + 1:
                    break
                if 1 <= fchoice <= len(mod_fields):
                    label, field = mod_fields[fchoice - 1]
                    current_val = getattr(target_user, field) if field != 'role_name' else getattr(target_user.role, 'name', '')
                    if field == 'password':
                        new_val = click.prompt(f"{label} (laisser vide pour annuler)", hide_input=True, default='')
                        if not new_val:
                            click.echo('Annulé')
                            continue
                        upd = {'password': new_val}
                    else:
                        new_val = click.prompt(label, default=current_val if current_val is not None else '')
                        if field == 'role_name':
                            upd = {'role_name': new_val}
                        else:
                            upd = {field: new_val or None}
                    try:
                        user_service.update(current_user, target_user.id, **upd)
                        click.echo('Champ mis à jour')
                        # refresh target_user
                        target_user = session.get(User, target_user.id)
                    except Exception as e:
                        click.echo(f'Erreur mise à jour: {e}')
                else:
                    click.echo('Choix invalide')
        elif choice == 2:
            try:
                confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
                if confirm.lower().startswith('o'):
                    user_service.delete(current_user, target_user.id)
                    click.echo('Utilisateur supprimé')
                    break
            except Exception as e:
                click.echo(f'Erreur suppression: {e}')
        else:
            break
