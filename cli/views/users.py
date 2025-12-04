from app.services.user_service import UserService
import click
from cli.helpers import prompt_menu
from app.db.transaction import transactional


class UsersView:
    """
    Vue CLI pour la gestion des utilisateurs.
    Permet aux utilisateurs de créer, lire, mettre à jour et supprimer des utilisateurs
    en fonction de leurs permissions.
    """
    def __init__(self, session, perm_service) -> None:
        self.session = session
        self.perm_service = perm_service
        self.prompt_menu = prompt_menu
        self.click = click

    def main_user_menu(self, user) -> None:
        while True:
            self.click.echo('\n=== Gestion des utilisateurs ===')
            options = self.get_user_menu_options(user)
            action = self.prompt_menu(options, prompt='Choix')
            if action is None:
                return
            if action == 'list_all':
                self.list_all_users(user)
            elif action == 'filter_id':
                self.filter_user_by_id(user)
            elif action == 'create':
                self.create_user(user)

    def get_user_menu_options(self, user) -> list:
        
        options = []
        if self.perm_service.user_has_permission(user, 'user:read'):
            options.append(('Afficher tous les utilisateurs', 'list_all'))
            options.append(('Filtrer par ID', 'filter_id'))
        if self.perm_service.user_has_permission(user, 'user:create'):
            options.append(('Créer un utilisateur', 'create'))
        return options



    def create_user(self, user) -> None:
        user_service = UserService(self.session, self.perm_service)
        try:
            first = self.click.prompt('Prénom')
            last = self.click.prompt('Nom')
            username = self.click.prompt('Nom d\'utilisateur')
            email = self.click.prompt('Email')
            phone = self.click.prompt('Téléphone')

            from app.models.role import Role
            roles = self.session.query(Role).all()
            if not roles:
                self.click.echo('Aucun rôle disponible en base, annulation')
                return
            role_options = [(r.name, r.id) for r in roles]
            role_id = self.prompt_menu(role_options, prompt='Choisir rôle')
            if role_id is None:
                self.click.echo('Annulé')
                return

            password = self.click.prompt('Mot de passe', hide_input=True)
            fields = {
                'user_first_name': first,
                'user_last_name': last,
                'username': username,
                'email': email,
                'phone_number': phone,
                'role_id': role_id,
                'password': password,
            }
            with transactional(self.session):
                new_user = user_service.create(user, **fields)
            self.click.echo(f'Utilisateur créé id={new_user.id}')
        except Exception as e:
            self.click.echo(f'Erreur création: {e}')

    def update_user(self, current_user, target_user_id) -> None:
        from app.models.user import User
        user_service = UserService(self.session, self.perm_service)
        target = self.session.get(User, target_user_id)
        if not target:
            self.click.echo('Utilisateur introuvable')
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
            field_choice = self.prompt_menu(field_opts, prompt='Choisir champ')
            if field_choice is None:
                break
            label = next(lbl for lbl, fld in update_fields if fld == field_choice)
            field = field_choice
            if field == 'password':
                new_val = self.click.prompt(f"{label} (laisser vide pour annuler)", hide_input=True, default='')
                if not new_val:
                    self.click.echo('Annulé')
                    continue
                upd = {'password': new_val}
            else:
                current_val = getattr(target, field) if field != 'role_id' else getattr(target.role, 'name', '')
                if field == 'role_id':
                    from app.models.role import Role
                    roles = self.session.query(Role).all()
                    role_opts = [(r.name, r.id) for r in roles]
                    new_val = self.prompt_menu(role_opts, prompt='Choisir rôle')
                    if new_val is None:
                        self.click.echo('Annulé')
                        continue
                    upd = {'role_id': new_val}
                else:
                    new_val = self.click.prompt(label, default=current_val if current_val is not None else '')
                    upd = {field: (new_val if new_val != '' else current_val)}
            try:
                with transactional(self.session):
                    user_service.update(current_user, target.id, **upd)
                self.click.echo('Champ mis à jour')
                target = self.session.get(User, target_user_id)
            except Exception as e:
                self.click.echo(f'Erreur mise à jour: {e}')

    def delete_user(self, current_user, target_user_id) -> None:
        from app.models.user import User
        user_service = UserService(self.session, self.perm_service)
        target = self.session.get(User, target_user_id)
        if not target:
            self.click.echo('Utilisateur introuvable')
            return
        try:
            confirm = self.click.prompt('Confirmer suppression ? (o/n)', default='n')
            if confirm.lower().startswith('o'):
                with transactional(self.session):
                    user_service.delete(current_user, target.id)
                self.click.echo('Utilisateur supprimé')
        except Exception as e:
            self.click.echo(f'Erreur suppression: {e}')

    def list_all_users(self, user) -> None:
        user_service = UserService(self.session, self.perm_service)
        try:
            users = user_service.list_all(user)
            user_options = [(
                f"{u.id}: {u.user_first_name} {u.user_last_name} ({u.username})",
                u.id,
            ) for u in users]
            choice = self.prompt_menu(user_options, empty_message='Aucun utilisateur')
            if choice is None:
                return
            self.display_detail_users(user, choice)
        except Exception as e:
            self.click.echo(f'Erreur: {e}')

    def filter_user_by_id(self, user) -> None:
        user_service = UserService(self.session, self.perm_service)
        try:
            sel = self.click.prompt('Saisir l\'ID utilisateur (0=Retour)', type=int)
            if sel == 0:
                return
            target = user_service.get_by_id(user, sel)
            if not target:
                self.click.echo('Utilisateur introuvable')
                return
            self.display_detail_users(user, target.id)
        except Exception as e:
            self.click.echo(f'Erreur: {e}')

    def display_detail_users(self, current_user, target_user_id) -> None:
        from app.models.user import User
        target = self.session.get(User, target_user_id)
        if not target:
            self.click.echo('Utilisateur introuvable')
            return
        self.click.echo(f"\nID: {target.id}\nPrénom: {target.user_first_name}\nNom: {target.user_last_name}\nUsername: {target.username}\nEmail: {target.email}\nTéléphone: {target.phone_number}\nRole: {getattr(target.role, 'name', target.role_id)}")
        actions = []
        if self.perm_service.user_has_permission(current_user, 'user:update') and current_user.role.name == 'management':
            actions.append(('Modifier', 'update'))
        if self.perm_service.user_has_permission(current_user, 'user:delete') and current_user.role.name == 'management':
            actions.append(('Supprimer', 'delete'))
        action = self.prompt_menu(actions, prompt='Choix')
        if action is None:
            return
        if action == 'update':
            self.update_user(current_user, target.id)
        elif action == 'delete':
            self.delete_user(current_user, target.id)

