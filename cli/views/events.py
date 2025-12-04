from app.services.event_service import EventService
import click
from cli.helpers import prompt_menu
from app.db.transaction import transactional
from sentry import report_exception

class EventsView:
    """
    Vue CLI pour la gestion des évènements.
    Permet aux utilisateurs de créer, lire, mettre à jour et supprimer des évènements
    en fonction de leurs permissions.
    """

    def __init__(self, session, perm_service):
        self.session = session
        self.perm_service = perm_service
        self.prompt_menu = prompt_menu
        self.click = click

    def main_event_menu(self, user):
        while True:
            self.click.echo('\n=== Gestion des évènements ===')
            options = self.get_event_menu_options(user)
            action = self.prompt_menu(options, prompt='Choix')
            if action is None:
                return
            if action == 'all':
                self.list_all_events(user)
            elif action == 'mine':
                self.my_events(user)
            elif action == 'create':
                self.create_event(user)
            elif action == 'nosupport':
                self.events_without_support(user)

    def get_event_menu_options(self, user):
        options = []
        if self.perm_service.user_has_permission(user, 'event:read'):
            options.append(('Afficher tous les évènements', 'all'))
            if getattr(user, 'role', None) and getattr(user.role, 'name', None) == 'support':
                options.append(('Mes évènements', 'mine'))
        if getattr(user, 'role', None) and getattr(user.role, 'name', None) == 'sales' and self.perm_service.user_has_permission(user, 'event:create'):
            options.append(('Créer un évènement', 'create'))
        if getattr(user, 'role', None) and getattr(user.role, 'name', None) == 'management' and self.perm_service.user_has_permission(user, 'event:read'):
            options.append(('Evènements sans support assigned', 'nosupport'))
        return options


    def create_event(self, user):
        event_service = EventService(self.session, self.perm_service)
        try:
            contract_id = self.click.prompt('ID du contrat lié')
            customer_id = self.click.prompt('ID du client lié')
            event_name = self.click.prompt("Nom de l'évènement")
            start_datetime = self.click.prompt('Date/heure de début (YYYY-MM-DD HH:MM)', default='')
            end_datetime = self.click.prompt('Date/heure de fin (YYYY-MM-DD HH:MM)', default='')
            location = self.click.prompt('Lieu', default='')
            attendees = self.click.prompt('Nombre participants', default='0')
            note = self.click.prompt('Note', default='')
            support_id = self.click.prompt('ID support', default='')
            fields = {
                'contract_id': contract_id,
                'customer_id': customer_id,
                'event_name': event_name,
                'start_datetime': start_datetime or None,
                'end_datetime': end_datetime or None,
                'location': location or None,
                'attendees': attendees or None,
                'note': note or None,
                'user_support_id': support_id or None,
            }
            from app.models.contract import Contract
            contract = self.session.get(Contract, contract_id)
            if not contract:
                self.click.echo('Contrat introuvable ou non accessible')
                return
            if not contract.signed or contract.customer.user_sales_id != user.id:
                self.click.echo("Impossible de créer l'évènement: le contrat doit être signé et appartenir au commercial")
                return
            with transactional(self.session):
                new_e = event_service.create(user, **fields)
            self.click.echo(f'Evènement créé id={new_e.id}')
        except Exception as e:
            report_exception(e)
            self.click.echo(f'Erreur création: {e}')

    def list_all_events(self, user):
        event_service = EventService(self.session, self.perm_service)
        try:
            events = event_service.list_all(user)
            self.click.echo('\n=== Liste des évènements ===\n-> Choisir un évènement pour afficher les détails\n')
            opts = [(f"ID: {e.id}: {e.event_name}", e.id) for e in events]
            choice = self.prompt_menu(opts, prompt='Choisir évènement', empty_message='Aucun évènement')
            if choice is None:
                return
            self.display_detail_events(user, choice)
        except Exception as e:
            report_exception(e)
            self.click.echo(f'Erreur: {e}')

    def my_events(self, user):
        event_service = EventService(self.session, self.perm_service)
        try:
            role_name = getattr(getattr(user, 'role', None), 'name', None)
            if role_name == 'support':
                events = event_service.list_by_support_user(user.id)
            elif role_name == 'sales':
                customer_ids = [c.id for c in getattr(user, 'customers', [])]
                events = []
                for cid in customer_ids:
                    events.extend(event_service.list_by_customer(cid))
            else:
                events = []
            self.click.echo('\n=== Liste des évènements ===\n-> Choisir un évènement pour afficher les détails\n')
            opts = [(f"ID: {e.id}: {e.event_name}", e.id) for e in events]
            choice = self.prompt_menu(opts, prompt='Choisir évènement', empty_message="Aucun évènement")
            if choice is None:
                return
            self.display_detail_events(user, choice)
        except Exception as e:
            report_exception(e)
            self.click.echo(f'Erreur: {e}')

    def events_without_support(self, user):
        event_service = EventService(self.session, self.perm_service)
        try:
            events = [e for e in event_service.list_all(user) if getattr(e, 'user_support_id', None) is None]
            self.click.echo('\n=== Liste des évènements ===\n-> Choisir un évènement pour afficher les détails\n')
            opts = [(f"ID: {e.id}: {e.event_name}", e.id) for e in events]
            choice = self.prompt_menu(opts, prompt='Choisir évènement', empty_message='Aucun évènement')
            if choice is None:
                return
            self.display_detail_events(user, choice)
        except Exception as e:
            report_exception(e)
            self.click.echo(f'Erreur: {e}')

    def display_detail_events(self, current_user, event_id):
        from app.models.event import Event
        event = self.session.get(Event, event_id)
        if not event:
            self.click.echo('Evènement introuvable')
            return
        self.click.echo("\n=== Détails de l'évènement sélectionné ===")
        support_display = getattr(event, 'user_support_id', None)
        support_display = support_display if support_display is not None else 'Aucun support'
        self.click.echo(
            f"ID: {event.id}\n"
            f"Nom: {event.event_name}\n"
            f"Contract: {event.contract_id}\n"
            f"Client: {event.customer_id}\n"
            f"Début: {event.start_datetime}\n"
            f"Fin: {event.end_datetime}\n"
            f"Lieu: {event.location}\n"
            f"Participants: {event.attendees}\n"
            f"Support: {support_display}"
        )
        actions = []
        if self.perm_service.user_has_permission(current_user, 'event:update'):
            support_role = getattr(getattr(current_user, 'role', None), 'name', None) == 'support'
            if not support_role or getattr(event, 'user_support_id', None) == getattr(current_user, 'id', None):
                actions.append(('Modifier', 'update'))
        if self.perm_service.user_has_permission(current_user, 'event:delete'):
            actions.append(('Supprimer', 'delete'))
        action = self.prompt_menu(actions, prompt='Choix')
        if action is None:
            return
        if action == 'update':
            self.update_event(current_user, event_id)
        elif action == 'delete':
            self.delete_event(current_user, event_id)

    def update_event(self, current_user, event_id):
        from app.models.event import Event
        event_service = EventService(self.session, self.perm_service)
        event = self.session.get(Event, event_id)
        if not event:
            self.click.echo('Evènement introuvable')
            return
        if getattr(getattr(current_user, 'role', None), 'name', None) == 'management':
            new_support = self.click.prompt('ID nouveau support (laisser vide pour annuler)', default='')
            if not new_support:
                self.click.echo('Annulé')
                return
            try:
                with transactional(self.session):
                    event_service.update(current_user, event.id, user_support_id=int(new_support))
                self.click.echo('Support mis à jour')
            except Exception as e:
                report_exception(e)
                self.click.echo(f'Erreur mise à jour: {e}')
            return
        mod_fields = [
            ('Client ID', 'customer_id'),
            ('Contrat ID', 'contract_id'),
            ('Nom', 'event_name'),
            ('Début (YYYY-MM-DD HH:MM)', 'start_datetime'),
            ('Fin (YYYY-MM-DD HH:MM)', 'end_datetime'),
            ('Lieu', 'location'),
            ('Participants', 'attendees'),
            ('Note', 'note'),
        ]
        while True:
            field_opts = [(label, field) for label, field in mod_fields]
            field_choice = self.prompt_menu(field_opts, prompt='Choisir champ')
            if field_choice is None:
                break
            label = next(lbl for lbl, fld in mod_fields if fld == field_choice)
            field = field_choice
            current_val = getattr(event, field)
            new_raw = self.click.prompt(label, default=str(current_val) if current_val is not None else '')
            optional_fields = {'start_datetime', 'end_datetime', 'location', 'attendees', 'note'}
            val = new_raw if field not in optional_fields else (new_raw or None)
            try:
                with transactional(self.session):
                    event_service.update(current_user, event.id, **{field: val})
                self.click.echo('Champ mis à jour')
                event = self.session.get(Event, event_id)
            except Exception as e:
                report_exception(e)
                self.click.echo(f'Erreur mise à jour: {e}')

    def delete_event(self, current_user, event_id):
        from app.models.event import Event
        event_service = EventService(self.session, self.perm_service)
        event = self.session.get(Event, event_id)
        if not event:
            self.click.echo('Evènement introuvable')
            return
        try:
            confirm = self.click.prompt('Confirmer suppression ? (o/n)', default='n')
            if confirm.lower().startswith('o'):
                with transactional(self.session):
                    event_service.delete(current_user, event.id)
                self.click.echo('Evènement supprimé')
        except Exception as e:
            report_exception(e)
            self.click.echo(f'Erreur suppression: {e}')