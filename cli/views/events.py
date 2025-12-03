from app.services.event_service import EventService
import click
from datetime import datetime
from cli.helpers import prompt_select_option, prompt_list_or_empty, prompt_detail_actions
from app.db.transaction import transactional


class EventsView:
    def __init__(self, session, perm_service):
        self.session = session
        self.perm_service = perm_service

    def get_event_menu_options(self, user):
        options = []
        if self.perm_service.user_has_permission(user, 'event:read'):
            options.append(('Afficher tous les évènements', 'all'))
            if user.role.name == 'support':
                options.append(('Mes évènements', 'mine'))
        if user.role.name == 'sales' and self.perm_service.user_has_permission(user, 'event:create'):
            options.append(('Créer un évènement', 'create'))
        if user.role.name == 'management' and self.perm_service.user_has_permission(user, 'event:read'):
            options.append(('Evènements sans support assigned', 'nosupport'))
        return options

    def main_event_menu(self, user):
        click.echo('\n=== Gestion des évènements ===')
        while True:
            options = self.get_event_menu_options(user)
            action = prompt_select_option(options, prompt='Choix')
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

    def create_event(self, user):
        event_service = EventService(self.session, self.perm_service)
        try:
            contract_id = click.prompt('ID du contrat lié')
            customer_id = click.prompt('ID du client lié')
            event_name = click.prompt('Nom de l\'évènement')
            start_datetime = click.prompt('Date/heure de début (YYYY-MM-DD HH:MM)', default='')
            end_datetime = click.prompt('Date/heure de fin (YYYY-MM-DD HH:MM)', default='')
            location = click.prompt('Lieu', default='')
            attendees = click.prompt('Nombre participants', default='0')
            support_id = click.prompt('ID support', default='')
            fields = {
                'contract_id': contract_id,
                'customer_id': customer_id,
                'event_name': event_name,
                'start_datetime': start_datetime or None,
                'end_datetime': end_datetime or None,
                'location': location or None,
                'attendees': attendees or None,
                'user_support_id': support_id or None,
            }
            from app.models.contract import Contract
            contract = self.session.get(Contract, contract_id)
            if not contract:
                click.echo('Contrat introuvable ou non accessible')
                return
            if not contract.signed or contract.customer.user_sales_id != user.id:
                click.echo("Impossible de créer l'évènement: le contrat doit être signé et appartenir au commercial")
                return
            with transactional(self.session):
                new_e = event_service.create(user, **fields)
            click.echo(f'Evènement créé id={new_e.id}')
        except Exception as e:
            click.echo(f'Erreur création: {e}')

    def list_all_events(self, user):
        event_service = EventService(self.session, self.perm_service)
        try:
            events = event_service.list_all(user)
            opts = [(f"{e.id}: {e.event_name}", e.id) for e in events]
            choice = prompt_list_or_empty(opts, empty_message='Aucun évènement', prompt_text='Choisir évènement')
            if choice is None:
                return
            self.display_detail_events(user, choice)
        except Exception as e:
            click.echo(f'Erreur: {e}')

    def my_events(self, user):
        event_service = EventService(self.session, self.perm_service)
        try:
            if user.role.name == 'support':
                events = event_service.list_by_support_user(user.id)
            elif user.role.name == 'sales':
                customer_ids = [c.id for c in user.customers]
                events = []
                for cid in customer_ids:
                    events.extend(event_service.list_by_customer(cid))
            else:
                events = []
            if not events:
                click.echo('\nAucun évènement')
                try:
                    while True:
                        c = click.prompt('Choix (0=Retour)', type=int)
                        if c == 0:
                            break
                except Exception:
                    pass
                return
            opts = [(f"{e.id}: {e.event_name}", e.id) for e in events]
            choice = prompt_list_or_empty(opts, empty_message='Aucun évènement', prompt_text='Choisir évènement')
            if choice is None:
                return
            self.display_detail_events(user, choice)
        except Exception as e:
            click.echo(f'Erreur: {e}')

    def events_without_support(self, user):
        event_service = EventService(self.session, self.perm_service)
        try:
            events = [e for e in event_service.list_all(user) if e.user_support_id is None]
            if not events:
                click.echo('\nAucun évènement')
                try:
                    while True:
                        c = click.prompt('Choix (0=Retour)', type=int)
                        if c == 0:
                            break
                except Exception:
                    pass
                return
            opts = [(f"{e.id}: {e.event_name}", e.id) for e in events]
            choice = prompt_list_or_empty(opts, empty_message='Aucun évènement', prompt_text='Choisir évènement')
            if choice is None:
                return
            self.display_detail_events(user, choice)
        except Exception as e:
            click.echo(f'Erreur: {e}')

    def display_detail_events(self, current_user, event_id):
        from app.models.event import Event
        event = self.session.get(Event, event_id)
        if not event:
            click.echo('Evènement introuvable')
            return
        click.echo(f"\nID: {event.id}\nNom: {event.event_name}\nContract: {event.contract_id}\nClient: {event.customer_id}\nDébut: {event.start_datetime}\nFin: {event.end_datetime}\nLieu: {event.location}\nParticipants: {event.attendees}\nSupport: {event.user_support_id}")
        actions = []
        if self.perm_service.user_has_permission(current_user, 'event:update'):
            support_role = getattr(current_user, 'role', None) and getattr(current_user.role, 'name', None) == 'support'
            if not support_role or getattr(event, 'user_support_id', None) == getattr(current_user, 'id', None):
                actions.append(('Modifier', 'update'))
        if self.perm_service.user_has_permission(current_user, 'event:delete'):
            actions.append(('Supprimer', 'delete'))
        action = prompt_detail_actions(actions, prompt_text='Choix')
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
            click.echo('Evènement introuvable')
            return
        if current_user.role.name == 'management':
            new_support = click.prompt('ID nouveau support (laisser vide pour annuler)', default='')
            if not new_support:
                click.echo('Annulé')
                return
            try:
                with transactional(self.session):
                    event_service.update(current_user, event.id, user_support_id=int(new_support))
                click.echo('Support mis à jour')
            except Exception as e:
                click.echo(f'Erreur mise à jour: {e}')
            return
        mod_fields = [
            ('Client', 'customer_id'),
            ('Contrat', 'contract_id'),
            ('Nom', 'event_name'),
            ('Début (YYYY-MM-DD HH:MM)', 'start_datetime'),
            ('Fin (YYYY-MM-DD HH:MM)', 'end_datetime'),
            ('Lieu', 'location'),
            ('Participants', 'attendees'),
        ]
        while True:
            field_opts = [(label, field) for label, field in mod_fields]
            field_choice = prompt_select_option(field_opts, prompt='Choisir champ')
            if field_choice is None:
                break
            label = next(lbl for lbl, fld in mod_fields if fld == field_choice)
            field = field_choice
            current_val = getattr(event, field)
            new_raw = click.prompt(label, default=str(current_val) if current_val is not None else '')
            if field in ('start_datetime', 'end_datetime') and new_raw:
                val = new_raw
            elif field == 'attendees':
                val = new_raw or None
            elif field == 'user_support_id':
                val = new_raw or None
            else:
                val = new_raw
            try:
                with transactional(self.session):
                    event_service.update(current_user, event.id, **{field: val})
                click.echo('Champ mis à jour')
                event = self.session.get(Event, event_id)
            except Exception as e:
                click.echo(f'Erreur mise à jour: {e}')

    def delete_event(self, current_user, event_id):
        from app.models.event import Event
        event_service = EventService(self.session, self.perm_service)
        event = self.session.get(Event, event_id)
        if not event:
            click.echo('Evènement introuvable')
            return
        try:
            confirm = click.prompt('Confirmer suppression ? (o/n)', default='n')
            if confirm.lower().startswith('o'):
                with transactional(self.session):
                    event_service.delete(current_user, event.id)
                click.echo('Evènement supprimé')
        except Exception as e:
            click.echo(f'Erreur suppression: {e}')
